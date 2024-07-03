import os
import pickle

import numpy as np
import torch
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


def to_adjmatrix(adj_sparse, adj_size):
    A = torch.sparse_coo_tensor(adj_sparse[:, :2].T, adj_sparse[:, 2],
                                size=[adj_size, adj_size]).to_dense()
    return A


def extrac_degree_centrality_sparse(adj_sparse, sen_api_idx, adj_size):
    adj_tmp = to_adjmatrix(adj_sparse)
    adj_tmp = adj_tmp.float()
    all_degree = torch.div((torch.sum(adj_tmp, 0) + torch.sum(adj_tmp, 1)), (adj_tmp.shape[0] - 1))
    feature = torch.matmul(sen_api_idx, all_degree.float())
    # print("\t\t max feature:", torch.max(feature))
    return feature


def extract_degree_centrality(adj, sen_api_idx):
    adj_tmp = adj.float()
    all_degree = torch.div((torch.sum(adj_tmp, 0) + torch.sum(adj_tmp, 1)), (adj_tmp.shape[0] - 1))
    feature = torch.matmul(sen_api_idx, all_degree.float())
    # print("\t\t max feature:", torch.max(feature))
    return feature


def obtain_sensitive_apis(file):
    sensitive_apis = []
    with open(file, 'r') as f:
        for line in f.readlines():
            if line.strip() == '':
                continue
            else:
                sensitive_apis.append(line.strip())
    return sensitive_apis


def load_train_data(data_path):
    df = open(data_path, "rb")
    data3 = pickle.load(df)
    apk_name_list = list(data3)
    # tmp = data3[apk_name_list[a]]
    # X_train = []
    # Idx_train = []
    # y_train = []
    # train_apk_sha = []
    # train_feature = []
    # for a in range(len(apk_name_list)):
    #     # train_apk_sha.append(apk_name_list[a])
    #     X_train.append(tmp["adjacent_matrix"])
    #     Idx_train.append(tmp["sensitive_api_list"])
    #     y_train.append(tmp["label"])
    #     train_feature.append(tmp["sensitive_api_list"])

    X_train = data3["adjacent_matrix"]
    Idx_train = data3["sensitive_api_index"]
    y_train = data3["label"]
    train_feature = data3["degree_feature_data"]
    return X_train, Idx_train, y_train, train_feature


def degree_centrality_extraction(adjacent_matrix, sen_idx):
    centrality = (adjacent_matrix.sum(axis=0) + adjacent_matrix.sum(axis=1).transpose()) / (
            adjacent_matrix.shape[0] - 1)

    centrality = np.array(centrality)
    centrality = np.squeeze(centrality)
    # centrality = np.reshape(centrality, (np.max(centrality.shape), 1))
    feature = np.zeros_like(sen_idx, dtype=np.float32)
    for i in range(len(sen_idx)):
        tmp = sen_idx[i]
        if tmp != -1:
            feature[i] = centrality[tmp][0]

    return feature


def load_test_data(data_path, idx):
    df = open(data_path, "rb")
    data3 = pickle.load(df)
    apk_name_list = list(data3)

    X_test_sha256 = data3["sha256"][idx]
    X_test_am = data3["adjacent_matrix"][idx]
    X_test_sen_idx = data3["sensitive_api_idx"][idx]
    y_test = 0

    X_test_degree_cen = degree_centrality_extraction(X_test_am, X_test_sen_idx)
    return X_test_sha256, X_test_am, X_test_sen_idx, y_test, X_test_degree_cen

def load_all_test_data(data_path ):
    df = open(data_path, "rb")
    data3 = pickle.load(df)
    apk_name_list = list(data3)

    X_test_sha256 = data3["sha256"]
    X_test_am = data3["adjacent_matrix"]
    X_test_sen_idx = data3["sensitive_api_idx"]


    return X_test_sha256, X_test_am, X_test_sen_idx


def find_2nd_nn_l2(Q, y_Q, X, y_X, k):
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


def trans2triple_rw(adjacent_matrix, sha256):
    file_name = "tripleset/" + sha256 + ".npy"
    triple = []
    if os.path.exists(file_name):
        triple = np.load(file_name)
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
    return triple


import numpy as np
import networkx as nx

def extract_pack_feature(adj, pack_idx):
    '''
    adj: csr_matrix: adjacent matrix
    pack_idx: nparray: node number * 1, the package index of each node
    '''
    idx_one_hot = np.zeros((pack_idx.size, pack_idx.max()+1))
    idx_one_hot[np.arange(pack_idx.size), pack_idx] = 1
    #
    call_relation = idx_one_hot.transpose().dot(adj.dot(idx_one_hot))

    MarkovFeats = np.zeros((max(pack_idx)+1, max(pack_idx)+1))
    tmpaa = []
    Norma_all = np.sum(call_relation, axis=1)
    for i in range(0, len(call_relation)):
        Norma = Norma_all[i]
        tmpaa.append(Norma)
        if (Norma == 0):
            MarkovFeats[i] = call_relation[i]
        else:
            MarkovFeats[i] = call_relation[i] / Norma

    feature = MarkovFeats.flatten()
    return feature


def get_list(graph_file):
    packages_path = "packages.txt"
    package_list = []
    f = open(packages_path, 'r')
    tmp = f.readlines()
    for zi in tmp:
        tt = zi.split('\n')[0]
        tt = tt.replace(".", "/")
        tt = "L"+tt
        package_list.append(tt)


    CG = nx.read_gexf(graph_file)
    node_list = list(CG.nodes)

    packages_idx = []

    for zi in node_list:
        match = False
        for y in package_list:
            # x = y.partition('.')[2]
            x = y

            if zi.startswith(x):
                match = x
                break

        if match == False:
            splitted = zi.split('/')
            obfcount = 0
            for k in range(0, len(splitted)):
                if len(splitted[k]) < 3:
                    obfcount += 1
            if obfcount >= len(splitted) / 2:
                match = 'obfuscated'
            else:
                match = 'selfdefined'

        packages_idx.append(match)
    return packages_idx