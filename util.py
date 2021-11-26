# -*- coding:utf-8 -*-
# Author: Kaifa Zachary ZHAO
# Date: 11/18/2021
import os
from scipy import sparse
import numpy as np


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
