import os
import pickle

import numpy as np
import torch
from scipy import sparse


def load_all_test_data(data_path):
    df = open(data_path, "rb")
    data3 = pickle.load(df)
    apk_name_list = list(data3)

    X_test_sha256 = data3["sha256"]
    X_test_am = data3["adjacent_matrix"]
    X_test_sen_idx = data3["sensitive_api_idx"]

    return X_test_sha256, X_test_am, X_test_sen_idx


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