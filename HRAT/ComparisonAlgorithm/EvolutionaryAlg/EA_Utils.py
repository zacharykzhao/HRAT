# -*- coding:utf-8 -*-
# Author: Kaifa Zachary ZHAO
# Date: 7/24/2021

import os
import numpy as np


def check_folder(folder_name):
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)


def katz_feature(graph, sen_idx, alpha=0.1, beta=1.0, normalized=True, weight=None):
    max_iter = 1000
    graph = graph.T
    n = graph.shape[0]
    nodelist = [i for i in range(n)]
    b = np.ones((n, 1)) * float(beta)

    centrality = np.linalg.solve(np.eye(n, n) - (alpha * graph), b)
    if normalized:
        norm = np.sign(sum(centrality)) * np.linalg.norm(centrality)
    else:
        norm = 1.0
    # centrality = dict(zip(nodelist, map(float, centrality / norm)))
    centrality = centrality / norm

    idx_matrix = np.zeros((len(sen_idx), n))
    ii = np.where(sen_idx != -1)
    idx_matrix[ii, sen_idx[ii]] = 1
    feature = np.matmul(idx_matrix, centrality)

    return feature


def malscan_feature_extraction(sen_idx, adjacen_matrix):
    idx_matrix = np.zeros((sen_idx.size, adjacen_matrix.shape[0]))
    ii = np.where(sen_idx != -1)
    idx_matrix[ii, sen_idx[ii]] = 1
    # get w
    all_degree = (np.sum(adjacen_matrix, axis=0) + np.sum(adjacen_matrix, axis=1).transpose()) / \
                 (adjacen_matrix.shape[0] - 1)
    Q_fea = idx_matrix.dot(all_degree.transpose())

    katz_fea1 = katz_feature(adjacen_matrix, sen_idx)
    Q_fea = np.array(Q_fea)
    Q_fea = np.append(Q_fea, katz_fea1)
    return Q_fea


def cal_cost(test_feature, X, Y,):
    """
    Here we define the cost in simulated annealing is:the distance from test_feature to the nearest
    benign samples in training feature
    :param test_feature:
    :param X: training feature
    :param Y: label
    :return: distance, nn
    """
    if type(test_feature) is list:
        test_feature = np.array(test_feature)
    if type(X) is list:
        X = np.array(X)

    assert test_feature.shape[0] == X.shape[1]
    class_num = 2
    axis = tuple(np.arange(1, X.ndim, dtype=np.int32))
    dist = np.sum(np.square(X - test_feature), axis=axis)
    dist = np.squeeze(dist)
    ind = np.argsort(dist)
    ind = np.squeeze(ind).transpose()
    mean_dist = np.zeros((class_num,))
    for j in range(class_num):
        ind_j = ind[Y[ind] == j]
        dist_j = dist[ind_j]
        mean_dist[j] = np.mean(dist_j)

    ind_dist = np.argsort(mean_dist)
    if ind_dist[0] == 0:
        nn = ind[Y[ind] == ind_dist[1]][:100]
    else:
        nn = ind[Y[ind] == ind_dist[0]][:100]
    return nn, dist[nn[0]]


def laod_constraints(constraints_file_path):
    tmp = open(constraints_file_path, "r", encoding='utf-8').readlines()
    constraints = [int(a.replace("/n", "")) for a in tmp]
    constraints = np.array(constraints)
    return constraints


