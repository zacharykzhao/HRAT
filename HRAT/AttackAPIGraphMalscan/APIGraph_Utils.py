import os
import pickle

import numpy as np
import torch
from scipy import sparse


def getEntityEmbedding():
    ## get the cluster of each api
    # keys are cluster number
    # f = open("cluster_txt_file.txt", "r", encoding='utf-8')
    # cluster_idx = dict()
    # data = f.readlines()
    # for i in data:
    #     tmp = i.split("/n")[0].split(" : ")
    #     if not cluster_idx.__contains__(tmp[0]):
    #         cluster_idx[tmp[0]] = []
    #     cluster_idx[tmp[0]].append(tmp[1])
    # # keys are api
    with open('method_cluster_mapping_2000_0319.pkl', 'rb') as f:
        entity_embedding = pickle.load(f)
    return entity_embedding


def find_2nd_nn_l2(Q, y_Q, X, y_X, k):
    if type(Q) is list:
        Q = np.array(Q)
    if type(X) is list:
        X = np.array(X)
    assert Q.shape[0] == X.shape[1]
    class_num = 2
    nn = np.zeros((1, k), dtype=np.int32)
    axis = tuple(np.arange(1, X.ndim, dtype=np.int32))
    # for i, q in enumerate(Q):
    dist = np.sum(np.square(X - Q), axis=axis)
    dist = np.squeeze(dist)
    ind = np.argsort(dist)
    ind = np.squeeze(ind).transpose()
    mean_dist = np.zeros((class_num,))
    for j in range(class_num):
        ind_j = ind[y_X[ind] == j]
        dist_j = dist[ind_j]
        mean_dist[j] = np.mean(dist_j)

    ind_dist = np.argsort(mean_dist)
    if ind_dist[0] == y_Q:
        nn = ind[y_X[ind] == ind_dist[1]][:k]
    else:
        nn = ind[y_X[ind] == ind_dist[0]][:k]
    return nn


def fcg2adj_return(fcg_file, node_file):

    tmp = open(node_file, "r", encoding='utf-8').readlines()
    node_list = [a.replace("\n", "") for a in tmp]

    fgraph = open(fcg_file, "r", encoding='utf-8')
    line = fgraph.readline()

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
        line = fgraph.readline()
    adj_matrix = sparse.coo_matrix((data, (row_ind, col_ind)), shape=[len(node_list), len(node_list)])
    return adj_matrix


def get_sen_idx(node_list, sensitive_apis):
    senapi_idx = -1 * np.ones([len(sensitive_apis), 1], dtype=int)
    for idx in range(len(sensitive_apis)):
        api = sensitive_apis[idx]
        if api in node_list:
            senapi_idx[idx] = node_list.index(api)

    return senapi_idx


def obtain_sensitive_apis(file):
    sensitive_apis = []
    with open(file, 'r') as f:
        for line in f.readlines():
            if line.strip() == '':
                continue
            else:
                sensitive_apis.append(line.strip())
    return sensitive_apis



def get_new_sen_idx(sen_idx, node_map):
    sen_map = sparse.load_npz("sen_api_map.npz")
    n_ori = node_map.shape[1]
    idx_matrix = np.zeros((len(sen_idx), n_ori))  # n_sen * n_node_ori
    ii = np.where(sen_idx != -1)
    for i in ii[0]:
        idx_matrix[i, sen_idx[i]] = 1
    # idx_matrix[[ii[0], sen_idx[ii]]] = 1
    new_sam = np.matmul(idx_matrix,
                        node_map.transpose().todense())  # n_sen * n_node_new, 每行应该表示原每个sensitive api，对应的新的node list

    # sen_map : 每行应表示，每个新的senapi包含的老sensitive api的位置
    #
    new_idx_m = np.matmul(sen_map.todense(), new_sam)
    new_idx_m[new_idx_m > 1] = 1
    new_idx = -1 * np.ones((new_idx_m.shape[0], 1))
    tmp = np.where(new_idx_m == 1)
    for i in range(len(tmp[0])):
        new_idx[tmp[0][i]] = tmp[1][i]
    return new_idx.astype(int)


def degree_centrality_extraction(adjacent_matrix, sen_idx, node_map):
    adjacent_matrix_new = node_map.dot(adjacent_matrix).dot(node_map.transpose())
    adjacent_matrix_new[adjacent_matrix_new > 1] = 1

    centrality = (adjacent_matrix_new.sum(axis=0) + adjacent_matrix_new.sum(axis=1).transpose()) / (
            adjacent_matrix_new.shape[0] - 1)

    centrality = np.array(centrality)
    centrality = np.squeeze(centrality)

    idx_matrix = np.zeros((len(sen_idx), node_map.shape[0]))
    ii = np.where(sen_idx != -1)
    idx_matrix[ii, sen_idx[ii]] = 1


    feature = np.matmul(idx_matrix, centrality)
    return feature


def katz_feature(graph, sen_idx, node_map, alpha=0.1, beta=1.0, normalized=True, weight=None):
    graph_new = node_map.dot(graph).dot(node_map.transpose())
    graph_new[graph_new > 1] = 1
    graph = graph_new
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

    # idx_matrix = np.matmul(idx_matrix, np.array(node_map.todense().transpose()))
    # idx_matrix[idx_matrix > 1] = 1

    feature = np.matmul(idx_matrix, centrality)

    return feature


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


def trans2triple_rw(adjacent_matrix, sha256, filepath, overwrite_flag=True):
    '''

    :param adjacent_matrix:
    :param sha256:
    :param overwrite_flag: 决定是否重新计算triple matrix
    :return: triple matrix
    '''
    file_name = filepath + "/" + sha256 + ".npy"

    if not overwrite_flag:
        if os.path.exists(file_name):
            print("\t loading data")
            fsize = os.path.getsize(file_name)
            fsize = fsize / float(1024 * 1024)
            if fsize > 500:
                return None
            triple = np.load(file_name)
        else:
            if type(adjacent_matrix) is sparse.coo_matrix:
                adjacent_matrix = adjacent_matrix.tocsr()
            node_number = adjacent_matrix.shape[0]
            triple = []
            for zi in range(node_number):
                # triple.append([zi, zi, adjacent_matrix[zi, zi]])
                for zj in range(zi + 1, node_number):
                    triple.append([zi, zj, adjacent_matrix[zi, zj]])
                    triple.append([zj, zi, adjacent_matrix[zj, zi]])
            triple = np.array(triple)
            np.save(file_name, triple)
            fsize = os.path.getsize(file_name)
            fsize = fsize / float(1024 * 1024)
            if fsize > 500:
                return None
    else:
        node_number = adjacent_matrix.shape[0]
        triple = []
        for zi in range(node_number):
            # triple.append([zi, zi, adjacent_matrix[zi, zi]])
            for zj in range(zi + 1, node_number):
                triple.append([zi, zj, adjacent_matrix[zi, zj]])
                triple.append([zj, zi, adjacent_matrix[zj, zi]])
        triple = np.array(triple)
        np.save(file_name, triple)
        fsize = os.path.getsize(file_name)
        fsize = fsize / float(1024 * 1024)
        if fsize > 500:
            return None
    return triple


def load_train_data(data_path):
    df = open(data_path, "rb")
    data3 = pickle.load(df)
    X_train = data3["adjacent_matrix"]
    Idx_train = data3["sensitive_api_index"]
    y_train = data3["label"]
    train_feature = data3["degree_feature_data"]
    return X_train, Idx_train, y_train, train_feature


def load_all_test_data(data_path):
    df = open(data_path, "rb")
    data3 = pickle.load(df)

    X_test_sha256 = data3["sha256"]
    X_test_am = data3["adjacent_matrix"]
    X_test_sen_idx = data3["sensitive_api_idx"]

    return X_test_sha256, X_test_am, X_test_sen_idx
