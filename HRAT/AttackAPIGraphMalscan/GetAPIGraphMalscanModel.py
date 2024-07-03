
import os
import pickle
from scipy import sparse
import numpy as np
from tqdm import tqdm

from HRAT.AttackAPIGraphMalscan.APIGraph_Utils import obtain_sensitive_apis, get_new_sen_idx


def laod_constraints(constraints_file_path):
    tmp = open(constraints_file_path, "r", encoding='utf-8').readlines()
    constraints = [int(a.replace("/n", "")) for a in tmp]
    constraints = np.array(constraints)
    return constraints


def get_sen_idx(node_list, sensitive_apis):
    senapi_idx = -1 * np.ones([len(sensitive_apis), 1], dtype=int)
    for idx in range(len(sensitive_apis)):
        api = sensitive_apis[idx]
        if api in node_list:
            senapi_idx[idx] = node_list.index(api)
    return senapi_idx


if __name__ == '__main__':
    # train
    adj_path = '../../PreprocessAPK/demo/adjacentmatrix'
    node_path = '../../PreprocessAPK/demo/apk_parse_results/benign/nodes'
    node_relation = '../../PreprocessAPK/demo/apk_parse_results/benign/nodes_relation'
    cons_path = './'
    #
    adj_path = "F:/apk/testAPK_nodesAndCons/malscan_enhancing_data/adj"
    node_path = "F:/apk/testAPK_nodesAndCons/malscan_enhancing_data/node"
    node_relation = "F:/apk/testAPK_nodesAndCons/malscan_enhancing_data/node_relation/"
    sensitive_apis_path = 'sensitive_apis_java.txt'
    sensitive_apis = obtain_sensitive_apis(sensitive_apis_path)
    data = {}
    for type in os.listdir(adj_path):
        node_path_2 = node_path + "/" + type
        adj_path_2 = adj_path + "/" + type
        nr_path_2 = node_relation + "/" + type
        for graph in tqdm(os.listdir(adj_path_2)):
            try:
                sha256 = graph.split(".")[0]
                print(type, ":", sha256)
                graph_file = adj_path_2 + "/" + graph
                node_file = node_path_2 + "/" + sha256 + ".txt"
                node_map_file = nr_path_2 + "/" + sha256 + ".npz"
                node_map = sparse.load_npz(node_map_file)
                constraints = laod_constraints(cons_path + sha256 + ".txt")
                tmp = open(node_file, "r", encoding='utf-8').readlines()
                node_list = [a.replace("\n", "") for a in tmp]
                sen_idx_ori = get_sen_idx(node_list, sensitive_apis)

                adj_graph = sparse.load_npz(graph_file)
                sen_idx = get_new_sen_idx(sen_idx_ori, node_map)
            except Exception:
                continue
            label = 0
            if type == "benign":
                label = 1
            print("size adj:", adj_graph.shape[0], " ?=? nodes", len(node_list))
            data[sha256] = dict()
            data[sha256]["adjacent_matrix"] = adj_graph
            data[sha256]["sensitive_api_list"] = sen_idx
            data[sha256]["label"] = label
            print("\t", len(data))
    pickle.dump(data, open("csr_dict_APIGraph.pkl", "wb"))
