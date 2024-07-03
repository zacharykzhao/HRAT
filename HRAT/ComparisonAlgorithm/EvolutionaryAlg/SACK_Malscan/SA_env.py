# -*- coding:utf-8 -*-
# Author: Kaifa Zachary ZHAO
# Date: 7/24/2021
# -*- coding:utf-8 -*-
# Author: Kaifa Zachary ZHAO
# Date: 6/27/2021

import numpy as np
import torch
from torch.autograd import Variable
import pandas as pd

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def find_nn_torch(Q, X, y, k=1):
    dist = torch.sum((np.squeeze(X) - np.squeeze(Q)).pow(2.), 1)
    ind = torch.argsort(dist)
    label = y[ind[:k]]
    unique_label = torch.unique(y)
    unique_label = unique_label.long()
    count = np.zeros(unique_label.shape[0])
    for i in label:
        count[unique_label[i.long()]] += 1
    ii = torch.argmax(torch.from_numpy(count))
    final_label = unique_label[ii]
    return final_label


class SA_env(object):
    """
    Description:

    Source:
        Self designed. This environments is designed to modify function call graph in programming.

    Observations:
        Type: vector:
            the centrality of sensitive apis (attention nodes)

    Actions:
        Type: list(4)
        Num     Action
        0       add an edge between two nodes
        1       rewiring
        2       add an nodes, and connect it to another nodes
        3       delete an nodes


    Reward:
        Reward is


    Episode Termination:
        The observation is classified as target class.
        Episode length is greater than 200.

    """
    torch.manual_seed(6666)
    np.random.seed(6666)

    def __init__(self, target_graph, label,
                 target_sen_api_idx, node_num,
                 X_train, y_train,
                 train_set, train_label,
                 w, steep, constraints):
        self.adj_sparse = target_graph
        self.label = label
        self.adj_size = node_num
        self.X_train = X_train
        self.y_train = y_train
        self.train_set = train_set
        self.train_label = train_label
        self.sen_api_idx = target_sen_api_idx
        self.sen_api_idx_ori = target_sen_api_idx
        self.w = w
        self.steep = steep
        self.constraints = constraints
        self.action_space = ['add_edge', 'rewiring', 'add_nodes', 'delete_nodes']
        self.cur_graph = target_graph

    def step(self, action, k=1):
        assert len(self.action_space) >= action + 1

        if action == 0:  # add dege
            self.cur_graph, node_info = self.add_edge(self.cur_graph)

        elif action == 1:  # rewiring
            self.cur_graph, node_info = self.rewiring(self.cur_graph)

        elif action == 2:  # add node
            self.cur_graph, node_info = self.add_node(self.cur_graph)

        elif action == 3:  # delete node
            self.cur_graph, node_info = self.del_node(self.cur_graph)

        self.state = self.getDegreeCentrality(self.cur_graph, self.sen_api_idx)
        katz_fea = self.getDegreeCentrality(self.to_adjmatrix(self.cur_graph), self.sen_api_idx)
        self.state = torch.cat((self.state, np.squeeze(katz_fea)), 0)
        cur_label = self.getlabel(self.state, k)

        done = (cur_label != self.label)
        # print("\t\t if done:", cur_label, self.label)

        if done:
            reward = 1
        else:
            reward = self.getReward(self.cur_graph)

        return self.state, reward, done, node_info

    def reset(self):
        self.state = self.getDegreeCentrality(self.adj_sparse, self.sen_api_idx)
        katz_fea = self.katz_feature_torch(self.to_adjmatrix(self.adj_sparse), self.sen_api_idx)
        self.state = torch.cat((self.state, np.squeeze(katz_fea)), 0)
        self.cur_graph = self.adj_sparse
        self.sen_api_idx = self.sen_api_idx_ori
        # t = self.getlabel(self.state, 1)
        return self.state

    def to_adjmatrix(self, adj_sparse):
        A = torch.sparse_coo_tensor(adj_sparse[:, :2].T, adj_sparse[:, 2],
                                    size=[self.adj_size, self.adj_size]).to_dense()

        return A

    def getDegreeCentrality(self, adj, sen_api_idx):
        idx_matrix = np.zeros((len(sen_api_idx), self.adj_size))

        ii = np.where(sen_api_idx != -1)
        idx_matrix[ii, sen_api_idx[ii]] = 1
        idx_matrix = torch.from_numpy(idx_matrix).to(device)

        adj_dense = self.to_adjmatrix(adj)
        if adj_dense.shape[0] > len(idx_matrix):
            _sub = adj_dense.shape[0] - len(idx_matrix)
            for za in range(_sub):
                idx_matrix.append[0]

        all_degree = torch.div((torch.sum(adj_dense, 0) + torch.sum(adj_dense, 1)).float(),
                               float(adj_dense.shape[0] - 1))
        degree_centrality = torch.matmul(idx_matrix, all_degree.type_as(idx_matrix))
        return degree_centrality

    def getlabel(self, feature, k=1):
        y = find_nn_torch(feature, self.train_set, self.train_label, k)
        return y

    def getReward(self, graph, budget_node=1, budget_edge=1):
        n_edge = np.where(graph[:, -1] == 1)[0].size
        n_node = np.max([len(np.unique(graph[:, 0])), len(np.unique(graph[:, 1]))])
        raw_n_edge = np.where(self.cur_graph[:, -1] == 1)[0].size
        raw_n_node = np.max([len(np.unique(self.cur_graph[:, 0])), len(np.unique(self.cur_graph[:, 1]))])

        if n_edge == raw_n_edge:
            edge_r = 0
        else:
            edge_r = 1 / budget_edge * (n_edge - raw_n_edge)

        if n_node == raw_n_node:
            node_r = 0
        else:
            node_r = 1 / budget_node * (n_node - raw_n_node)

        reward = -(edge_r + node_r)
        return reward

    def del_node(self, graph):
        # cal grad of all edges
        grad = self.get_gradient(graph)
        tmp_grad = self.to_adjmatrix(grad)
        # get the grad of nodes
        node_grad = (torch.sum(tmp_grad, 0) + torch.sum(tmp_grad, 1))
        node_id = list(range(node_grad.shape[0]))

        # sort node_grad
        grad_tmp = np.array([node_id, node_grad.tolist()]).transpose()

        a = grad_tmp[grad_tmp[:, -1].argsort()]
        a = a[::-1]
        tar_node = -1
        for zi in a:
            flag = 0

            if self.constraints[int(zi[0])] == 0 or self.constraints[
                int(zi[0])] == -1:  # caller cannot be contained in constraints; -1为新constraints
                flag = 1
            # find functions that call target nodes
            ind_caller = np.where(graph[:, 0] == int(zi[0]))
            caller_idx = graph[ind_caller, 0]
            for zi2 in caller_idx:
                if self.constraints[int(zi2[0])] == 0:  # caller cannot be contained in constraints
                    flag = 1
                    break
            if flag == 1:
                continue
            else:
                tar_node = zi[0].astype(np.int64)
                break
        if tar_node < 0:
            print("zkf no nodes to delete")
            return graph, [-1, -1, -1]
        # tar_node = torch.argmax(node_grad).item()
        # find edges to tar node
        tmp_ind_to = np.where(graph[:, 1] == tar_node)
        edge_to_tar_node = graph[tmp_ind_to, :]
        edge_to_tar_node = np.squeeze(edge_to_tar_node)
        tmp_ind = np.where(edge_to_tar_node[:, 2] == 1)
        edge_to_tar_node = np.squeeze(edge_to_tar_node[tmp_ind, :], axis=0)

        # find edges from tar node
        tmp_ind_from = np.where(graph[:, 0] == tar_node)
        edge_from_tar_node = graph[tmp_ind_from, :]
        edge_from_tar_node = np.squeeze(edge_from_tar_node)
        tmp_ind = np.where(edge_from_tar_node[:, 2] == 1)
        edge_from_tar_node = np.squeeze(edge_from_tar_node[tmp_ind, :], axis=0)

        # 如果该节点调用了其他节点，且该节点存在调用
        if edge_from_tar_node.size != 0 and edge_to_tar_node.size != 0:
            # 对于所有调用了改节点的函数
            for zind_beg in edge_to_tar_node[:, 0]:
                tmp_ind = np.where(graph[:, 0] == zind_beg)
                tmp_ind = np.squeeze(tmp_ind)
                edge_tmp = np.squeeze(graph[tmp_ind, :])
                # 对于所有该结点调用的结点
                for zind_end in edge_from_tar_node[:, 1]:

                    tmp_ind1 = np.where(edge_tmp[:, 1] == zind_end)
                    tmp_ind1 = np.squeeze(tmp_ind1)
                    if tmp_ind1.size != 0:
                        # edge = tmp_ind[tmp_ind1]
                        # ii = np.where(np.all((graph[:, :2] == edge), axis=1) == True)
                        # graph[ii, 2] = 1
                        graph[tmp_ind[tmp_ind1], 2] = 1
                    else:
                        # graph.append([zind_beg, zind_end, 1])
                        graph = np.append(graph, np.array([zind_beg, zind_end, 1])[:, np.newaxis].transpose(), axis=0)
        # del nodes
        tmp_ind_to = np.where(graph[:, 1] == tar_node)
        graph = np.delete(graph, tmp_ind_to, axis=0)
        tmp_ind_from = np.where(graph[:, 0] == tar_node)
        graph = np.delete(graph, tmp_ind_from, axis=0)

        graph[np.where(graph[:, 1] > tar_node), 1] -= 1
        graph[np.where(graph[:, 0] > tar_node), 0] -= 1

        self.sen_api_idx[np.where(self.sen_api_idx > tar_node)] -= 1

        self.constraints = np.delete(self.constraints, tar_node)
        self.adj_size -= 1

        # print("len con:", str(len(self.constraints)), "  size graph:", str(max(graph[:, 0])), ',',
        #       str(max(graph[:, 1])),
        #       ', sen_api_idx:', str(np.max(self.sen_api_idx)))
        # print("\t\t graph idx:", np.min(graph[:, 0]), ", ", np.min(graph[:, 1]), ", ", np.min(graph[:, 2]), ", ")

        return graph, [-3, -1, tar_node]

    def add_node(self, graph):
        self.adj_size += 1
        # add one nodes to the sparse adjacent matrix
        triple_copy = graph.copy()
        a = [i for i in range(self.adj_size - 1)]
        # a = a.reverse()
        ii = np.ones_like(a)
        tmp_row = [ii * (self.adj_size - 1), a, (ii - 1)]
        tmp_row = np.array(tmp_row).transpose()
        tmp_col = [a, ii * (self.adj_size - 1), (ii - 1)]
        tmp_col = np.array(tmp_col).transpose()

        tmpz = np.concatenate((triple_copy, tmp_col, tmp_row), axis=0)
        # tmpz.append([self.adj_size - 1, self.adj_size - 1, 0])
        # tmpz = torch.from_numpy(tmpz).to(device).float()

        grad = self.get_gradient(tmpz)

        # find the edge with max graient and add the edge
        idx = np.where(grad[:, 1] == self.adj_size - 1)
        grad_tmp = grad[idx, :]
        grad_tmp = np.squeeze(grad_tmp)

        # sort grad_tmp
        a = grad_tmp[grad_tmp[:, 2].argsort()]
        a = a[::-1]
        edge = []
        for zi in a:
            if self.constraints[int(zi[0])] == 0:  # caller cannot be contained in constraints
                continue
            else:
                edge = zi[:2].astype(np.int64)
                break

        # ii = np.argmax(grad_tmp[:, -1])
        # beg_node = grad_tmp[ii, 0]
        # edge = [beg_node, self.adj_size - 1]
        ii = np.where(np.all((tmpz[:, :2] == edge), axis=1) == True)
        tmpz[ii, 2] = 1
        # self.cur_graph = tmpz
        self.constraints = np.append(self.constraints, 1)
        # print("len con:", str(len(self.constraints)),
        #       "  size graph:", str(max(tmpz[:, 0])), ',', str(max(tmpz[:, 1])),
        #       ', sen_api_idx:', str(np.max(self.sen_api_idx)))

        return tmpz, [tmpz[ii, 0], tmpz[ii, 1], self.adj_size - 1]

    def add_edge(self, graph):
        '''
             Here we consider it as a white-box attack
             we chose the edge which possess highest gradient to add
        '''
        triple_copy = graph.copy()
        tmpz = torch.from_numpy(triple_copy).float()
        triple_torch = Variable(tmpz, requires_grad=True)
        grad = self.get_gradient(graph)
        # get the add edge with max grad
        add_edge_index = np.where(triple_torch[:, -1] == 0.)
        grad_add = grad[add_edge_index, :]
        grad_add = np.squeeze(grad_add)

        # sort grad_add
        a = grad_add[grad_add[:, 2].argsort()]
        a = a[::-1]
        edge = []
        for zi in a:
            # if self.constraints[int(zi[0])] == 0 or self.constraints[
            #     int(zi[1])] == 0:  # caller cannot be contained in constraints
            if self.constraints[int(zi[0])] == 0 or self.constraints[int(zi[1])] == 0:
                continue
            else:
                edge = zi[:2].astype(np.int64)
                break
        # max_ind = np.argmax(grad_add[:, -1])
        # edge = grad_add[max_ind, :2].astype(np.int64)
        if edge == []:
            print("zkf no edge to add")
            return graph, [-1, -1, -1]
        ii = np.where(np.all((graph[:, :2] == edge), axis=1) == True)
        graph[ii, 2] = 1
        # self.cur_graph = graph
        # print("len con:", str(len(self.constraints)), "  size graph:", str(max(graph[:, 0])), ',',
        #       str(max(graph[:, 1])),
        #       ', sen_api_idx:', str(np.max(self.sen_api_idx)))

        # zkf 2021-03-03 调整新的constraints，添加了虚假调用的结点不能被删除，但可以继续添加调用、作为中间结点等
        # self.constraints[edge[0]] = -1
        self.constraints[edge[1]] = -1

        return graph, [-1, int(np.squeeze(edge[0])), int(np.squeeze(edge[1]))]

    def rewiring(self, graph):
        '''
        :param graph: spare graph
        :return: modified graph

            The rewiring operation consists of two steps:
            1. find the edge with max gradient, delete edge <v1, v2>
            2. calculate the gradient of each edge from node v1 -- <v1, v3> and calculate the gradient of each edge to
            node v2 --<v3, v2> , find the node v3 and add the edge <v1,v3> and <v3, v2>
        '''
        triple_copy = graph.copy()
        tmpz = torch.from_numpy(triple_copy).float()
        triple_torch = Variable(tmpz, requires_grad=True)

        grad = self.get_gradient(graph)
        # get the delete edge with max grad
        delete_edge_index = np.where(triple_torch[:, -1] == 1.)
        grad_add = grad[delete_edge_index, :]
        grad_add = np.squeeze(grad_add)
        # sort grad_add, find the deleteable edge
        a = grad_add[grad_add[:, 2].argsort()]
        a = a[::-1]
        del_edge = []
        for zi in a:
            if self.constraints[int(zi[0])] == 0:  # caller cannot be contained in constraints
                continue
            else:
                del_edge = zi[:2].astype(np.int64)
                break

        # max_ind = np.argmax(grad_add[:, -1])
        # del_edge = grad_add[max_ind, :2].astype(np.int64)
        # delete the edge
        ii = np.where(np.all((graph[:, :2] == del_edge), axis=1) == True)

        graph[ii, 2] = 0

        # get the add edge
        add_edge_ind = np.where(graph[:, -1] == 0.)[0]
        tmp_add = grad[add_edge_ind, :]
        tmp_add = np.squeeze(tmp_add)
        beg_node = del_edge[0]
        tar_node = del_edge[1]

        beg_idx = np.where(tmp_add[:, 0] == beg_node)[0]
        beg_grad = grad[add_edge_ind[beg_idx], :]
        mid1 = grad[:, 1]

        end_idx = np.where(tmp_add[:, 1] == tar_node)[0]
        end_grad = grad[add_edge_ind[end_idx], :]
        mid2 = grad[:, 0]

        inter = np.intersect1d(mid1, mid2)
        tt = inter.tolist()
        grad_tmp = []
        for za in tt:
            ibeg = np.where(beg_grad[:, 1] == za)[0]
            iend = np.where(end_grad[:, 0] == za)[0]
            if ibeg.size == 0 or iend.size == 0:
                grad_tmp.append(-1)
            else:
                grad_tmp.append((beg_grad[ibeg, -1] + end_grad[iend, -1])[0])

        # max_idx_mid = np.argmax(grad_tmp)

        # sort grad_add
        grad_tmp = np.array([inter, grad_tmp]).transpose()
        a = grad_tmp[grad_tmp[:, -1].argsort()]
        a = a[::-1]
        mid_node = -1
        for zi in a:
            if self.constraints[int(zi[0])] == 0:  # caller cannot be contained in constraints
                continue
            else:
                mid_node = zi[0].astype(np.int64)
                break

        # mid_node = inter[max_idx_mid].astype(np.int64)
        ii1 = np.where(np.all((graph[:, :2] == [beg_node, mid_node]), axis=1) == True)
        graph[ii1, 2] = 1
        ii2 = np.where(np.all((graph[:, :2] == [mid_node, tar_node]), axis=1) == True)
        graph[ii2, 2] = 1

        # zkf 2021-03-03 调整新的constraints，被虚假调用的结点不能被删除,但可以添加虚假调用
        # self.constraints[beg_node] = -1
        self.constraints[mid_node] = -1

        # print("len con:", str(len(self.constraints)), "  size graph:", str(max(graph[:, 0])), ',',
        #       str(max(graph[:, 1])),
        #       ' sen_api_idx:', str(np.max(self.sen_api_idx)))

        return graph, [beg_node, tar_node, mid_node]

    def katz_feature_torch(self, graph, sen_api_idx, alpha=0.1, beta=1.0, normalized=True):
        n = self.adj_size
        graph = graph.T
        b = torch.ones((n, 1)) * float(beta)
        b = b.to(device)
        graph = graph.to(device)
        A = torch.eye(n, n).to(device).float() - (alpha * graph.float())
        L, U = torch.solve(b, A)
        if normalized:
            norm = torch.sign(sum(L)) * torch.norm(L)
        else:
            norm = 1.0
        # centrality = dict(zip(nodelist, map(float, centrality / norm)))
        centrality = torch.div(L, norm.to(device)).to(device)

        idx_matrix = np.zeros((len(sen_api_idx), self.adj_size))

        ii = np.where(sen_api_idx != -1)
        idx_matrix[ii, sen_api_idx[ii]] = 1
        idx_matrix = torch.from_numpy(idx_matrix).to(device)
        katz_centrality = torch.matmul(idx_matrix, centrality.type_as(idx_matrix))
        return katz_centrality

    def get_gradient(self, graph):
        # calculate the grade of each edge
        triple_copy = graph.copy()
        tmpz = torch.from_numpy(triple_copy).float().to(device)
        triple_torch = Variable(tmpz, requires_grad=True)
        feature = self.getDegreeCentrality(triple_torch, self.sen_api_idx).to(device)

        densegraph = self.to_adjmatrix(triple_torch)
        feature_katz = self.katz_feature_torch(densegraph, self.sen_api_idx).to(device)
        feature = torch.cat((feature, np.squeeze(feature_katz)), 0)

        feature = torch.reshape(feature, (1, -1))
        dist = (torch.sum(feature.float() - np.squeeze(self.X_train.float()), 1)).pow(2)
        loss = torch.sum(self.w * (torch.sigmoid(self.steep * dist)))
        loss = torch.reshape(loss, (1, -1))
        loss.backward()

        tmp = triple_torch.grad.data.cpu().numpy()
        grad = np.concatenate((triple_torch.cpu()[:, :2].data.numpy(), tmp[:, 2:]), 1)
        return grad

    def check_state_exist(self, state):
        if state not in self.q_table.index:
            # append new state to q table
            self.q_table = self.q_table.append(
                pd.Series(
                    [0] * len(self.actions),
                    index=self.q_table.columns,
                    name=state,
                )
            )

    def learn(self, s, a, r, s_):
        self.check_state_exist(s_)
