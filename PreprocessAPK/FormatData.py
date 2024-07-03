import os
import numpy as np
import pickle

from scipy import sparse

def check_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)


def obtain_sensitive_apis(file):
    sensitive_apis = []
    with open(file, 'r') as f:
        for line in f.readlines():
            if line.strip() == '':
                continue
            else:
                sensitive_apis.append(line.strip())
    return sensitive_apis


def get_sen_idx(node_list, sensitive_apis):
    senapi_idx = -1 * np.ones([len(sensitive_apis), 1], dtype=int)
    for idx in range(len(sensitive_apis)):
        api = sensitive_apis[idx]
        if api in node_list:
            senapi_idx[idx] = node_list.index(api)

    return senapi_idx


def get_data(graph, data, adj_path_2, node_path_2, sensitive_apis, type):
    sha256 = graph.split(".")[0]
    print(type, ":", sha256)
    graph_file = adj_path_2 + "/" + graph
    node_file = node_path_2 + "/" + sha256 + ".txt"
    adj_graph = sparse.load_npz(graph_file)
    tmp = open(node_file, "r", encoding='utf-8').readlines()
    node_list = [a.replace("\n", "") for a in tmp]
    sen_idx = get_sen_idx(node_list, sensitive_apis)
    label = 0
    if type == "benign":
        label = 1
    print("size adj:", adj_graph.shape[0], " ?=? nodes", len(node_list))
    data[sha256] = dict()
    data[sha256]["adjacent_matrix"] = adj_graph
    data[sha256]["sensitive_api_list"] = sen_idx
    data[sha256]["label"] = label
    print("\t", len(data))
    return data


if __name__ == '__main__':
    adj_path = "adj_save_path"
    node_path = 'apk_parse_path'
    save_path = 'save_formated_data'
    #
    # adj_path = "./demo/adjacentmatrix/"
    # node_path = "./demo/apk_parse_results"
    # save_path = "./demo/formated_data"
    check_folder(save_path)
    #
    sensitive_apis_path = 'sensitive_apis_soot_signature.txt'
    sensitive_apis = obtain_sensitive_apis(sensitive_apis_path)

    SenAPI_index = []
    Labels = []
    data = dict()
    for apk_type in os.listdir(adj_path):
        adj_path_2 = os.path.join(adj_path, apk_type, 'adj')

        for graph in os.listdir(adj_path_2):
            sha256 = graph.split(".")[0]
            print(apk_type, ":", sha256)
            graph_file = adj_path_2 + "/" + graph
            node_file = os.path.join(node_path, apk_type, 'nodes', sha256 + '.txt')
            # node_file = node_path + "/" + sha256 + ".txt"
            adj_graph = sparse.load_npz(graph_file)
            tmp = open(node_file, "r", encoding='utf-8').readlines()
            node_list = [a.replace("\n", "") for a in tmp]
            sen_idx = get_sen_idx(node_list, sensitive_apis)
            label = 0
            if apk_type == "benign":
                label = 1
            # print("size adj:", adj_graph.shape[0], " ?=? nodes", len(node_list))
            data[sha256] = dict()
            data[sha256]["adjacent_matrix"] = adj_graph
            data[sha256]["sensitive_api_list"] = sen_idx
            data[sha256]["label"] = label
            print("%s \t %s " % (apk_type, sha256))

    #
    save_file = os.path.join(save_path, 'csr_dict.pkl')
    pickle.dump(data, open(save_file, "wb"))
