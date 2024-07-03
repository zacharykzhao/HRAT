##
'''
suppose ori_node_list is : n * 1; enhanced_node_list is k *1
this file aims to build the connection between two list with a matrix: k * n
'''

import os
import numpy as np
import re
from scipy import sparse
from multiprocessing import Pool as ThreadPool
from functools import partial
import pickle


def getEntityEmbedding():
    ## get the cluster of each api
    # keys are cluster number
    f = open("APIGraph_Func_Cluster.txt", "r", encoding='utf-8')
    cluster_idx = dict()
    data = f.readlines()
    for i in data:
        tmp = i.split("/n")[0].split(" : ")
        if not cluster_idx.__contains__(tmp[0]):
            cluster_idx[tmp[0]] = []
        cluster_idx[tmp[0]].append(tmp[1])
    # keys are api
    with open('APIGraph_func_cluster_mapping.pkl', 'rb') as f:
        entity_embedding = pickle.load(f)
    return entity_embedding


def forMultiProcess(file_tmp, ori_node_dir, entity_embedding, apk_type, save_path):
    # print(ori_node_dir, "  ", file_tmp)
    save_path = save_path + "/" + apk_type + "/node_relation"
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    node_connection_file = save_path + "/" + file_tmp.split(".")[0] + ".npz"
    # if os.path.exists(node_connection_file):
    #     return
    node_file = ori_node_dir + "/" + file_tmp
    tmp = open(node_file, "r", encoding='utf-8').readlines()
    node = [a.replace("\n", "") for a in tmp]
    new_node = dict()
    new_node_list = []
    count = 0
    for i in range(len(node)):
        # <org.meteoroid.core.MeteoroidActivity: void onResume()>
        api = node[i]
        tmpz = re.findall(r'<(.+?)>', api)[0]
        tmp = tmpz.split(" ")
        class_name = tmp[0].split(":")[0]
        method_name = tmp[-1].split("(")[0]
        api_name = class_name + "." + method_name
        # print(api_name)
        if api_name in entity_embedding:
            new_node[api] = entity_embedding[api_name]
            count += 1
        else:
            new_node[api] = api
        if not new_node[api] in new_node_list:
            new_node_list.append(new_node[api])
    matrix = np.zeros((len(new_node_list), len(node)))
    new_row = []
    ori_col = []
    data = []
    for i in range(len(node)):
        new_row.append(new_node_list.index(new_node[node[i]]))
        ori_col.append(i)
        data.append(1)
    matrix = sparse.coo_matrix((data, (new_row, ori_col)),
                               shape=[len(new_node_list), len(node)])

    print(node_connection_file)
    sparse.save_npz(node_connection_file, matrix)


if __name__ == '__main__':
    raw_node_dir = '../../PreprocessAPK/demo/apk_parse_results/'
    save_path = raw_node_dir
    
    raw_node_dir = "/Volumes/apk/testAPK_nodesAndCons/malware_node_0308"
    save_path = '/Volumes/Samsung8702/testAPIGraph'
    entity_embedding = getEntityEmbedding()
    apk_apk_type = ["malware"]
    for t in apk_apk_type:
        raw_node_dir_2 = os.path.join(raw_node_dir, t, 'nodes')
        sha256 = os.listdir(raw_node_dir)
        pool = ThreadPool(15)
        pool.map(partial(forMultiProcess, ori_node_dir=raw_node_dir, entity_embedding=entity_embedding,
                         apk_type=t,  save_path=save_path), sha256)
