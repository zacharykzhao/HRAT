# -*- coding:utf-8 -*-
# Author: Kaifa Zachary ZHAO
# Date: 7/27/2021
import numpy as np
import torch
import os
from scipy import sparse


def extract_feature(adj, pack_idx, type):
    '''
    adj: csr_matrix: adjacent matrix
    pack_idx: nparray: node number * 1, the package index of each node
    num: package: 11; package: 446
    '''
    if type == "families":
        nn = 11
    else:
        nn = 446
    idx_one_hot = np.zeros((pack_idx.size, nn))

    idx_one_hot[np.arange(pack_idx.size), pack_idx] = 1

    #
    call_relation = idx_one_hot.transpose().dot(adj.dot(idx_one_hot))

    # MarkovFeats = np.zeros((max(pack_idx)+1, max(pack_idx)+1))
    MarkovFeats = np.zeros((nn, nn))
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


def trans2triple_rw(adjacent_matrix, sha256, file_name, overwrite_flag=True):
    '''

    :param adjacent_matrix:
    :param sha256:
    :param overwrite_flag: 决定是否重新计算triple matrix
    :return: triple matrix
    '''
    # file_name = "../tripleset/" + sha256 + ".npy"
    triple = []
    if type(adjacent_matrix) is sparse.coo_matrix:
        adjacent_matrix = adjacent_matrix.tocsr()

    if not overwrite_flag:
        if os.path.exists(file_name):
            print("\t loading data...")
            fsize = os.path.getsize(file_name)
            fsize = fsize / float(1024 * 1024)
            if fsize > 500:
                return None
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


def find_2nd_nn_l2(Q, y_Q, X, y_X, k):
    try:
        assert Q.shape[0] == X.shape[1]
    except Exception:
        za = 1
    if torch.is_tensor(Q):
        Q = Q.cpu().numpy()
    if torch.is_tensor(X):
        X = X.cpu().numpy()
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
