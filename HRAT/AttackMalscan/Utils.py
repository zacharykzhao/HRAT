# -*- coding: UTF-8 -*-

# author: Zachary Kaifa ZHAO
# e-mail: kaifa dot zhao (at) connect dot polyu dot hk
# datetime: 2022/3/9 7:33 PM
# software: PyCharm
import os
from scipy import sparse

import numpy as np
import torch


def degree_centrality_extraction(adjacent_matrix, sen_idx):
    centrality = (adjacent_matrix.sum(axis=0) + adjacent_matrix.sum(axis=1).transpose()) / (
        adjacent_matrix.shape[0] - 1)

    centrality = np.array(centrality)
    centrality = np.squeeze(centrality)
    idx_matrix = np.zeros((len(sen_idx), adjacent_matrix.shape[0]))
    ii = np.where(sen_idx != -1)
    idx_matrix[ii, sen_idx[ii]] = 1
    feature = np.matmul(idx_matrix, centrality)
    return feature


def katz_feature(graph, sen_idx, alpha=0.1, beta=1.0, normalized=True, weight=None):
    graph = graph.T
    n = graph.shape[0]
    b = np.ones((n, 1)) * float(beta)
    centrality = np.linalg.solve(np.eye(n, n) - (alpha * graph), b)
    if normalized:
        norm = np.sign(sum(centrality)) * np.linalg.norm(centrality)
    else:
        norm = 1.0
    centrality = centrality / norm
    idx_matrix = np.zeros((len(sen_idx), n))
    ii = np.where(sen_idx != -1)
    idx_matrix[ii, sen_idx[ii]] = 1
    feature = np.matmul(idx_matrix, centrality)
    return feature


def trans2triple_rw(adjacent_matrix, sha256, triple_path,  overwrite=False):
    file_name = triple_path+"/" + sha256 + ".npy"
    triple = []

    if os.path.exists(file_name) and not overwrite:
        print("loading")
        triple = np.load(file_name)
        if triple.shape[0] < adjacent_matrix.shape[0]:
            triple = trans2triple_rw(
                adjacent_matrix, sha256, triple_path,  overwrite=True)
    else:
        node_number = adjacent_matrix.shape[0]
        triple = []
        if type(adjacent_matrix) is sparse.coo_matrix:
            adjacent_matrix = adjacent_matrix.tocsr()
        for zi in range(node_number):
            # triple.append([zi, zi, adjacent_matrix[zi, zi]])
            for zj in range(zi + 1, node_number):
                triple.append([zi, zj, adjacent_matrix[zi, zj]])
                triple.append([zj, zi, adjacent_matrix[zj, zi]])
        triple = np.array(triple)
        np.save(file_name, triple)
    return triple




def find_nn_torch(Q, X, y, k=1):
    dist = torch.sum((np.squeeze(X) - np.squeeze(Q)).pow(2.), 1)
    ind = torch.argsort(dist)
    label = y[ind[:k]]
    
    label_total = y[ind]
    list_label = label_total.cpu().numpy()
    benign_idx = np.argwhere(list_label==1)
    min_dist = dist[ind[benign_idx[0][0]]]
    
    unique_label = torch.unique(y)
    unique_label = unique_label.long()
    count = np.zeros(unique_label.shape[0])
    for i in label:
        count[unique_label[i.long()]] += 1
    ii = torch.argmax(torch.from_numpy(count))
    final_label = unique_label[ii]
    return final_label, min_dist


def to_adjmatrix(adj_sparse, adj_size):
    A = torch.sparse_coo_tensor(adj_sparse[:, :2].T, adj_sparse[:, 2],
                                size=[adj_size, adj_size]).to_dense()
    return A


def degree_centrality_torch(adj, sen_api_idx, device='cuda:0'):
    adj_size = adj.shape[0]
    idx_matrix = np.zeros((len(sen_api_idx), adj_size))
    ii = np.where(sen_api_idx != -1)
    idx_matrix[ii, sen_api_idx[ii]] = 1
    idx_matrix = torch.from_numpy(idx_matrix).to(device)

    if adj.shape[0] > len(idx_matrix):
        _sub = adj.shape[0] - len(idx_matrix)
        for za in range(_sub):
            idx_matrix.append[0]

    all_degree = torch.div((torch.sum(adj, 0) + torch.sum(adj, 1)).float(),
                           float(adj.shape[0] - 1))
    degree_centrality = torch.matmul(
        idx_matrix, all_degree.type_as(idx_matrix))
    return degree_centrality


def katz_feature_torch(graph, sen_api_idx, alpha=0.1, beta=1.0, device='cuda:0', normalized=True):
    n = graph.shape[0]
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
    centrality = torch.div(L, norm.to(device)).to(device)
    idx_matrix = np.zeros((len(sen_api_idx), n))
    ii = np.where(sen_api_idx != -1)
    idx_matrix[ii, sen_api_idx[ii]] = 1
    idx_matrix = torch.from_numpy(idx_matrix).to(device)
    katz_centrality = torch.matmul(idx_matrix, centrality.type_as(idx_matrix))
    return katz_centrality


def obtain_sensitive_apis(file):
    sensitive_apis = []
    with open(file, 'r') as f:
        for line in f.readlines():
            if line.strip() == '':
                continue
            else:
                sensitive_apis.append(line.strip())
    return sensitive_apis


def extract_sensitive_api(sensitive_api_list, nodes_list):
    sample_sensitive_api = []
    for x in sensitive_api_list:
        if x in nodes_list:
            sample_sensitive_api.append(nodes_list.index(x))
        else:
            sample_sensitive_api.append(-1)
    return np.array(sample_sensitive_api)


def check_folder(folder_name):
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)



def check_folder(folder_name: str):
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)


def fcg_to_adjacent(node_file, fcg_file):
    tmp_node = open(node_file, "r", encoding='utf-8').readlines()
    node_list = [zn.replace("\n", "") for zn in tmp_node]
    tmp_graph = open(fcg_file, "r", encoding='utf-8')
    line = tmp_graph.readline()
    row_ind = []
    col_ind = []
    data = []
    while line:
        # print(line)
        line = line.split("\n")[0]
        nodes = line.split(" ==> ")
        row_ind.append(node_list.index(nodes[0]))
        col_ind.append(node_list.index(nodes[1]))
        data.append(1)
        line = tmp_graph.readline()
    adj_matrix = sparse.coo_matrix((data, (row_ind, col_ind)), shape=[len(node_list), len(node_list)])
    return adj_matrix, node_list


def load_constraints(cons_file):
    f = open(cons_file, "r", encoding='utf-8').readlines()
    constraints = [int(a.replace("\n", "")) for a in f]
    constraints = np.array(constraints)
    return constraints


def adj_to_triple(adj):
    """
    :param adj: adjacent matrix
    :return: triple set -- numpy array -- [row_index, col_index, edge_state]
    """
    if type(adj) is sparse.coo_matrix:
        adjacent_matrix = adj.tocsr()

    node_number = adjacent_matrix.shape[0]
    triple = []
    for zi in range(node_number):
        # triple.append([zi, zi, adjacent_matrix[zi, zi]])
        for zj in range(zi + 1, node_number):
            triple.append([zi, zj, adjacent_matrix[zi, zj]])
            triple.append([zj, zi, adjacent_matrix[zj, zi]])
    return np.array(triple)


def get_subset_of_training_set(test_feature, X_train, m):
    test_feature_tmp = np.array(test_feature)[np.newaxis, :]
    axis = tuple(np.arange(1, X_train.ndim, dtype=np.int32))
    dist = np.sum(np.square(X_train - test_feature_tmp), axis=axis)
    dist = np.squeeze(dist)
    ind = np.argsort(dist)
    ind = np.squeeze(ind).transpose()
    return ind[:m]
