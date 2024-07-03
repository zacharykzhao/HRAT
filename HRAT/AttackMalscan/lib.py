import os
import pickle

import numpy as np
import torch
from scipy import sparse

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
    if type(Q) is list:
        Q=np.array(Q)
    if type(X)   is list:
        X=np.array(X)
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


def trans2triple_rw(adjacent_matrix, sha256, triple_path, overwrite_flag=True):
    '''

    :param adjacent_matrix:
    :param sha256:
    :param overwrite_flag: 决定是否重新计算triple matrix
    :return: triple matrix
    '''
    file_name = triple_path+"/" + sha256 + ".npy"
    # print(file_name)
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
            print("\t getting triple data")
            node_number = adjacent_matrix.shape[0]
            print("\t\t node number ", node_number)
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

import os
import re

def check_modifiable(mfunc):
    if len(mfunc) < 5:
        return True
    flag = True
    framework = ["java.", "sun.", "android.", "org.apache.", "org.eclipse.", "soot.", "javax.",
                 "com.google.", "org.xml.", "junit.", "org.json.", "org.w3c.com"]
    for i in framework:
        i1 = "<" + i
        if mfunc.startswith(i1):
            flag = False
            break

    lifecycle = ["onCreate", "onClick", "onStart", "onResume", "onPause", "onStop", "onRestart", "onDestroy"]
    methodname = mfunc.split(" ")[2].split("(")[0]

    for i in lifecycle:
        if methodname.__contains__(i):
            flag = False
            break

    return flag


def alg2apk(sha256,file_path, node_path, save_path, fPrint=True):
    # sha256 = "8DC0BB0EC7EA342FA2232D1749B4B60DD7E6148AAB95CA41032821F0D228746E"
    modification_record = file_path + "/" + sha256
    if sha256.endswith("action_list0.txt"):
        sha256 = sha256.replace("action_list0.txt", "")
    else:
        sha256 = sha256.replace("action_list.txt", "")
    node_file = node_path+ "/" + sha256 + "_testNodes.txt"

    tmp = open(node_file, "r", encoding='utf-8').readlines()
    node_list = [a.replace("\n", "") for a in tmp]

    modification = []


    f = open(modification_record, "r")
    az = f.readline()

    add_count = 0
    cur_m = 0
    while az:
        cur_m+= 1
        print("zkf cur:", cur_m)
        if az.__contains__("array([["):
            az = az.replace("array([[", "")
            az = az.replace("]])", "")
        tmp = re.findall(r"\[(.*?)\]", az)
        if len(tmp) > 0:
            t = tmp[0].split(",")
            type = int(t[0])

            if type == 0:
                # add_edge
                beg = int(t[2])
                tar = int(t[3])
                modification.append("add_edge,:" + node_list[beg] + " ==> " + node_list[tar])
                if fPrint:
                    print("add_edge,:" + node_list[beg] + " ==> " + node_list[tar] + "\n\t node length:" + str(
                        len(node_list)))
            elif type == 1:
                # delete_dedge
                beg = int(t[1])
                end = int(t[2])
                mid = int(t[3])
                modification.append("delete_edge,:" + node_list[beg] + " ==> "
                                    + node_list[end] + " ==> "
                                    + node_list[mid])
                if fPrint:
                    print("delete_edge,:" + node_list[beg] + " ==> "
                          + node_list[end] + " \n\tmid node "
                          + node_list[mid] + "\n\t node length:" + str(len(node_list)))
            elif type == 2:
                # add_node
                caller = int(t[1])
                new_node_id = add_count
                modification.append("add_node,:" + node_list[caller] + " ==> "
                                    + str(new_node_id))
                add_count += 1

                node_list.append(str(new_node_id))
                if fPrint:
                    print("add_node,:" + node_list[caller] + " ==> "
                          + str(new_node_id) + "\n\t node length:" + str(len(node_list)))
            elif type == 3:
                # delete_node
                target = int(t[-1])
                if target == -1:
                    az = f.readline()
                    continue
                modification.append("delete_node,:" + node_list[target])

                if fPrint:
                    print("delete_node,:" + node_list[target] + "\n\t node length:" + str(len(node_list)))
                del node_list[target]

            # if not check_modifiable(node_list[int(t[2])]):
            #     print(node_list[int(t[2])])
            # if not check_modifiable(node_list[int(t[3])]):
            #     print(node_list[int(t[3])])
        az = f.readline()

    file_name = save_path +"/" + sha256 + "_modifyGraph_attackseq.txt"
    f1 = open(file_name, "w", encoding='utf-8')

    for i in modification:
        f1.write(i)
        f1.write('\n')