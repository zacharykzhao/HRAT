import os
from scipy import sparse
import numpy as np
import glob
from multiprocessing import Pool as ThreadPool
from functools import partial


def fcg2adj_save(sha256, fcg_path_2, node_path_2, save_path_2):
    fcg_file = fcg_path_2 + "/" + sha256
    node_file = node_path_2 + "/" + sha256

    print(sha256)
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
    sparse.save_npz(save_path_2 + '/' + sha256.split(".")[0] + ".npz", adj_matrix)
    # np.save(save_path_2 + '/' + sha256.split(".")[0], adj_matrix)w


if __name__ == "__main__":
    apk_parse_path = "save_folder_path"  # the path you save the parse results for apks
    adj_save_path = "fcg_adj_save_path"  # the path your want to save the adjacent matrix
    apk_type = "benign"  # the type of apps you want to deal with
    #
    # apk_parse_path = "./demo/apk_parse_results"
    # adj_save_path = "./demo/adjacentmatrix"
    # apk_type = "benign"
    #
    fcg_path = os.path.join(apk_parse_path, apk_type, 'graph')
    node_path = os.path.join(apk_parse_path, apk_type, 'nodes')
    save_path = os.path.join(adj_save_path, apk_type, 'adj')
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    sha256list = os.listdir(fcg_path)

    pool = ThreadPool(15)
    pool.map(partial(fcg2adj_save, fcg_path_2=fcg_path, node_path_2=node_path, save_path_2=save_path), sha256list)
