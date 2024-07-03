# -*- coding:utf-8 -*-
# Author: Kaifa Zachary ZHAO
# Date: 7/27/2021

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


class CFGModifierEnvMamadroidCons(object):
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

    def __init__(self, target_graph, label, adj_size,
                 pack_idx,
                 X_train, y_train,
                 train_set, train_label,
                 w, steep, constraints):
        self.adj_sparse = target_graph
        self.label = label
        self.adj_size = adj_size
        self.X_train = X_train
        self.y_train = y_train
        self.train_set = train_set
        self.train_label = train_label
        self.w = w
        self.steep = steep
        self.constraints = constraints
        self.action_space = ['add_edge', 'rewiring', 'add_nodes', 'delete_nodes']
        self.cur_graph = target_graph
        self.cur_pack_idx = pack_idx
        self.ori_pack_idx = pack_idx

    def step(self, action, k=1):
        assert len(self.action_space) >= action + 1
        node_info = 0
        if action == 0:  # add dege
            self.cur_graph, node_info = self.add_edge(self.cur_graph)

        elif action == 1:  # rewiring
            self.cur_graph, node_info = self.rewiring(self.cur_graph)

        elif action == 2:  # add node
            self.cur_graph, node_info = self.add_node(self.cur_graph)

        elif action == 3:  # delete node
            self.cur_graph, node_info = self.del_node(self.cur_graph)

        self.state = self.extract_pack_feature(self.cur_graph, self.cur_pack_idx)
        cur_label = self.getlabel(self.state, k)

        done = (cur_label != self.label)
        # print("\t\t if done:", cur_label, self.label)

        if done:
            reward = 1
        else:
            reward = self.getReward(self.cur_graph)

        return self.state, reward, done, node_info

    def reset(self):
        self.cur_graph = self.adj_sparse
        self.state = self.extract_pack_feature(self.cur_graph, self.cur_pack_idx)
        self.cur_pack_idx = self.ori_pack_idx
        # t = self.getlabel(self.state, 1)
        return self.state

    def to_adjmatrix(self, adj_sparse):
        A = torch.sparse_coo_tensor(adj_sparse[:, :2].T, adj_sparse[:, 2],
                                    size=[self.adj_size, self.adj_size]).to_dense()
        return A

    def extract_pack_feature(self, adj, idx_one_hot):
        '''
        adj: csr_matrix: adjacent matrix, torch
        pack_idx: nparray: node number * 1, the package index of each node
        '''
        # idx_one_hot = torch.zeros((pack_idx.size, pack_idx.max()+1))
        # idx_one_hot[np.arange(pack_idx.size), pack_idx] = 1
        idx_one_hot = torch.from_numpy(idx_one_hot).to(device).float()
        #
        adj_dense = self.to_adjmatrix(adj).to(device).float()

        call_relation = torch.matmul(idx_one_hot.T,
                                     torch.matmul(adj_dense, idx_one_hot))
        pack_size = idx_one_hot.shape[1]
        MarkovFeats = torch.zeros((pack_size, pack_size))
        tmpaa = []
        Norma_all = torch.sum(call_relation, axis=1)
        for i in range(0, len(call_relation)):
            Norma = Norma_all[i]
            tmpaa.append(Norma)
            if (Norma == 0):
                MarkovFeats[i] = call_relation[i]
            else:
                MarkovFeats[i] = call_relation[i] / Norma

        feature = MarkovFeats.flatten()
        return feature

    def getlabel(self, feature, k=1):
        y = find_nn_torch(feature.to(device), self.train_set.to(device), self.train_label.to(device), k)
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
                int(zi[0])] == -1:  # caller cannot be contained in constraints
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
            # print("len con:", str(len(self.constraints)),
            #       "  size graph:", str(max(graph[:, 0])), ',',
            #       str(max(graph[:, 1])))
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

        self.cur_pack_idx = np.delete(self.cur_pack_idx, tar_node, axis=0)
        self.constraints = np.delete(self.constraints, tar_node)

        graph[np.where(graph[:, 0] > tar_node), 0] -= 1
        graph[np.where(graph[:, 1] > tar_node), 1] -= 1

        self.adj_size -= 1

        # print("len con:", str(len(self.constraints)), "  size graph:", str(max(graph[:, 0])), ',',
        #       str(max(graph[:, 1])))
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

        self.cur_pack_idx = np.append(self.cur_pack_idx,
                                      np.random.random((1, self.cur_pack_idx.shape[1])), axis=0)

        grad, pack_node = self.get_gradient_pack(tmpz, self.cur_pack_idx)

        # find the edge with max graient and add the edge
        idx = np.where(grad[:, 1] == self.adj_size - 1)
        grad_tmp = grad[idx, :]
        grad_tmp = np.squeeze(grad_tmp)

        # sort grad_tmp
        a = grad_tmp[grad_tmp[:, 2].argsort()]
        a = a[::-1]
        edge = []
        for zi in a:
            if int(zi[0]) >= len(self.constraints) or self.constraints[
                int(zi[0])] == 0:  # caller cannot be contained in constraints
                continue
            else:
                edge = zi[:2].astype(np.int64)
                break
        if edge == []:
            self.cur_pack_idx = np.delete(self.cur_pack_idx, -1, axis=0)
            self.adj_size -= 1
            # print("zkf no edge to add")
            # print("len con:", str(len(self.constraints)), "  size graph:", str(max(tmpz[:, 0])), ',',
            #       str(max(tmpz[:, 1])), " size ori graph:", str(max(graph[:, 0])))
            return graph, [-1, -1, -1]
        # ii = np.argmax(grad_tmp[:, -1])
        # beg_node = grad_tmp[ii, 0]
        # edge = [beg_node, self.adj_size - 1]
        ii = np.where(np.all((tmpz[:, :2] == edge), axis=1) == True)
        tmpz[ii, 2] = 1

        # 得到添加的结点所属的family/package
        if np.unique(pack_node[-1]).size == 1:
            node_pack_idx = pack_node.shape[1] - 2
        else:
            node_pack_idx = int(np.max(pack_node[-1]))
        tmp = np.zeros(((1, self.cur_pack_idx.shape[1])))
        tmp[0, node_pack_idx] = 1
        self.cur_pack_idx[-1] = tmp
        self.constraints = np.append(self.constraints, 1)

        # print("len con:", str(len(self.constraints)),
        #       "  size graph:", str(max(tmpz[:, 0])), ',', str(max(tmpz[:, 1])))

        return tmpz, [node_pack_idx, self.adj_size - 1, edge[0]]

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
            if self.constraints[int(zi[0])] == 0 or self.constraints[
                int(zi[1])] == 0:  # caller cannot be contained in constraints
                continue
            else:
                edge = zi[:2].astype(np.int64)
                break
        if edge == []:
            print("zkf no edge to add???")
            # print("len con:", str(len(self.constraints)), "  size graph:", str(max(graph[:, 0])), ',',
            #       str(max(graph[:, 1])))
            return graph, [-1, -1, -1]
        # max_ind = np.argmax(grad_add[:, -1])
        # edge = grad_add[max_ind, :2].astype(np.int64)
        ii = np.where(np.all((graph[:, :2] == edge), axis=1) == True)
        graph[ii, 2] = 1
        # self.cur_graph = graph

        # print("len con:", str(len(self.constraints)), "  size graph:", str(max(graph[:, 0])), ',',
        #       str(max(graph[:, 1])))

        self.constraints[edge[1]] = -1

        return graph, [-1, edge[0], edge[1]]

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
            elif self.constraints[int(zi[1])] == 0:  # callee should not be in constraints 2021-0326
                continue
            else:
                del_edge = zi[:2].astype(np.int64)
                break

        if del_edge == []:
            return graph, [-1, -1, -1]
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
        self.constraints[mid_node] = -1

        # print("len con:", str(len(self.constraints)), "  size graph:", str(max(graph[:, 0])), ',',
        #       str(max(graph[:, 1])))

        return graph, [beg_node, tar_node, mid_node]

    def get_gradient(self, graph):
        # calculate the grade of each edge
        triple_copy = graph.copy()
        tmpz = torch.from_numpy(triple_copy).float().to(device)
        triple_torch = Variable(tmpz, requires_grad=True)

        feature = self.extract_pack_feature(triple_torch, self.cur_pack_idx)
        feature = torch.reshape(feature, (1, -1)).to(device)

        dist = (torch.sum(feature.float() - np.squeeze(self.X_train.to(device).float()), 1)).pow(2)
        loss = torch.sum(self.w * (torch.sigmoid(self.steep * dist)))
        loss = torch.reshape(loss, (1, -1))
        loss.backward()

        tmp = triple_torch.grad.data.cpu().numpy()
        grad = np.concatenate((triple_torch.cpu()[:, :2].data.numpy(), tmp[:, 2:]), 1)
        return grad

    def get_gradient_pack(self, graph, pack_idx):
        # calculate the grade of each edge
        triple_copy = graph.copy()
        tmpz = torch.from_numpy(triple_copy).float().to(device)
        triple_torch = Variable(tmpz, requires_grad=True)
        pack_z = pack_idx.copy()
        pack = torch.from_numpy(pack_z).float().to(device)
        pack = Variable(pack, requires_grad=True)

        adj_dense = self.to_adjmatrix(triple_torch).float()

        call_relation = torch.matmul(pack.T,
                                     torch.matmul(adj_dense, pack))
        pack_size = pack.shape[1]
        MarkovFeats = torch.zeros((pack_size, pack_size))
        tmpaa = []
        Norma_all = torch.sum(call_relation, axis=1)
        for i in range(0, len(call_relation)):
            Norma = Norma_all[i]
            tmpaa.append(Norma)
            if (Norma == 0):
                MarkovFeats[i] = call_relation[i]
            else:
                MarkovFeats[i] = call_relation[i] / Norma

        feature = MarkovFeats.flatten()
        feature = torch.reshape(feature, (1, -1)).to(device)

        dist = (torch.sum(feature.float() - np.squeeze(self.X_train.to(device).float()), 1)).pow(2)
        loss = torch.sum(self.w * (torch.sigmoid(self.steep * dist)))
        loss = torch.reshape(loss, (1, -1))
        loss.backward()

        tmp = triple_torch.grad.data.cpu().numpy()
        grad = np.concatenate((triple_torch.cpu()[:, :2].data.numpy(), tmp[:, 2:]), 1)

        grad_pack = pack.grad.data.cpu().numpy()

        return grad, grad_pack

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
