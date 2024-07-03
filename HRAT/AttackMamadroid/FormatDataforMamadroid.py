import pickle
import os
import numpy as np
from scipy import sparse


def extract_feature(adj, pack_idx):
    '''
    adj: csr_matrix: adjacent matrix
    pack_idx: nparray: node number * 1, the package index of each node
    '''
    nn = 11
    idx_one_hot = np.zeros((pack_idx.size, nn))
    idx_one_hot[np.arange(pack_idx.size), pack_idx] = 1
    #
    call_relation = idx_one_hot.transpose().dot(adj.dot(idx_one_hot))
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


if __name__ == '__main__':
    node_list_path = "path_to_node_list"
    graph_path = "path_to_graph_data"
    adj_path = "path_to_adjacent_npz_file"
    save_idx_path = "path_to_save_mamadorid_node_idx"
    #
    node_list_path = "../../PreprocessAPK/demo/apk_parse_results"
    graph_path = "../../PreprocessAPK/demo/apk_parse_results"
    adj_path = "../../PreprocessAPK/demo/adjacentmatrix"
    save_idx_path = "mamadroid_fun_idx"
    #
    reference_family_file = "./Families.txt"
    #
    families_list = []
    f = open(reference_family_file, 'r')
    tmp = f.readlines()
    for zi in tmp:
        tt = zi.split('\n')[0]
        tt = "<" + tt
        families_list.append(tt)
    families_list.append('obfuscated')
    families_list.append('selfdefined')
    #
    families_idx = []
    apk_type = ["benign", "malware"]
    for t in apk_type:
        apk_type_folder = os.path.join(node_list_path, t, 'nodes')
        sp_1 = os.path.join(save_idx_path, t)
        if not os.path.exists(sp_1):
            os.makedirs(sp_1)
        for i in os.listdir(apk_type_folder):
            node_list_file = os.path.join(apk_type_folder, i)
            print(node_list_file)
            f = open(node_list_file, 'r')
            tmp = f.readlines()
            f.close()
            families_one_hot = []
            families_idx = []

            for method in tmp:
                match = False
                for zf in range(len(families_list)):
                    f = families_list[zf]
                    if method.startswith(f):
                        match = f
                        break
                if match == False:
                    splitted = method.split('.')
                    obfcount = 0
                    for k in range(0, len(splitted)):
                        if len(splitted[k]) < 3:
                            obfcount += 1
                    if obfcount >= len(splitted) / 2:
                        match = 'obfuscated'
                    else:
                        match = "selfdefined"
                families_idx.append(match)
            families_one_hot = np.array([families_list.index(i) for i in families_idx])
            print(np.unique(families_one_hot), "  ", len(families_one_hot))
            sf = os.path.join(sp_1, i.split(".")[0])
            np.save(sf, families_one_hot)
    ############
    data = dict()
    label = []
    for apkt in apk_type:
        gp1 = os.path.join(graph_path, apkt, 'graph')
        tmp = os.listdir(gp1)
        adj_path_2 = os.path.join(adj_path, apkt, 'adj')
        node_path_2 = os.path.join(node_list_path, apkt, 'nodes')
        idx_path_2 = os.path.join(save_idx_path, apkt)
        for zi in range(len(tmp)):
            apk = tmp[zi]
            sha256 = apk.split(".")[0]
            adj = sparse.load_npz(os.path.join(adj_path_2, sha256 + ".npz"))
            idx_file = os.path.join(idx_path_2, sha256 + ".npy")
            idx = np.load(idx_file)
            if len(idx) == 0:
                continue
            feature = extract_feature(adj, idx)
            y = 0
            if apkt == "benign":
                y = 1
            data[sha256] = dict()
            data[sha256]["adjacent_matrix"] = adj
            data[sha256]["feature"] = feature
            data[sha256]["label"] = y
            data[sha256]["idx"] = idx

    pickle.dump(data, open("mamadroid_data.pkl", "wb"))
