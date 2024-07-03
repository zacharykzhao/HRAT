# -*- coding:utf-8 -*-
# Author: Kaifa Zachary ZHAO
# Date: 7/27/2021

import pickle
import math
import random
import numpy as np
import torch

# from mamadroid import env_server
from HRAT.ComparisonAlgorithm.EvolutionaryAlg.EA_Utils import check_folder, cal_cost, laod_constraints
from SA_mamadroid_env import CFGModifierEnvMamadroidCons
from libs_mamadroid import extract_feature, find_2nd_nn_l2, trans2triple_rw

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

'''parameters'''
m = 75
steep = 1
ACTION = ['add_edge', 'rewiring', 'add_nodes', 'delete_nodes']
actions_num = 4
state_category = "families"
###


if __name__ == '__main__':
    date = "2011"
    save_folder = "simulated_annealing_mamadroid_2011"
    check_folder(save_folder)
    ##
    test_data_path = "./test_csr_dict_2011_families.pkl"
    df = open(test_data_path, "rb")
    data = pickle.load(df)
    test_sha256_all = data["sha256"]
    test_adj_all = data["adjacent_matrix"]
    test_idx_all = data["node_idx"]
    train_data_path = "./train_csr_dict_families.pkl"
    df = open(train_data_path, "rb")
    train_data = pickle.load(df)
    for zidx, test_sha256 in enumerate(test_sha256_all):
        if zidx < 933:
            continue
        save_file_name = save_folder + "/" + test_sha256 + "action_list.txt"
        save_feature_name = save_folder + "/final_feature" + test_sha256 + ".txt"
        X_test_am = test_adj_all[zidx]

        triple_path = "C:/Users/Zachary/Documents/A2MalwareStructuralAttack/" \
                      "results/triple_set2011/" + test_sha256 + ".npy"
        X_test_triple = trans2triple_rw(X_test_am, test_sha256, triple_path, False)

        train_data_all = np.array(train_data["data"])
        train_label_all = np.array(train_data["label"])
        y_train_ori = np.array(train_label_all)
        X_train_degree_cen_ori = np.array(train_data_all)

        test_adj = test_adj_all[zidx]
        pack_idx = test_idx_all[zidx]
        idx_one_hot = np.zeros((pack_idx.size, 11))
        idx_one_hot[np.arange(pack_idx.size), pack_idx] = 1
        ##
        test_feature = extract_feature(test_adj, pack_idx, state_category)
        test_label = 0
        # find m reference samples
        nn = find_2nd_nn_l2(test_feature, test_label, train_data_all, train_label_all, m)
        target = train_data_all[nn]
        target_label = train_label_all[nn]
        w = 2 * (train_label_all[nn] != test_label).astype(np.float32) - 1
        nn, cost = cal_cost(test_feature, train_data_all, np.array(y_train_ori))
        ## load constraints
        constraints = laod_constraints("F:/graphs/2011/malware/cons/" + test_sha256 + ".txt")

        node_path = "C:/graphs/2011/malware/nodes/" + test_sha256 + ".txt"
        tmp = open(node_path, "r", encoding='utf-8').readlines()
        node = [a.replace("\n", "") for a in tmp]
        ##
        # to torch tensor
        train_data_all = torch.from_numpy(train_data_all).to(device)
        train_label_all = torch.from_numpy(np.array(train_label_all)).to(device)
        target = torch.from_numpy(target).to(device)
        target_label = torch.from_numpy(target_label).to(device)
        test_triple = X_test_triple
        w = torch.from_numpy(w).to(device)

        node_number = test_adj.shape[0]
        test_pack_idx = idx_one_hot
        env = CFGModifierEnvMamadroidCons(test_triple, test_label, node_number,
                                          test_pack_idx,
                                          target, target_label,
                                          train_data_all, train_label_all,
                                          w, steep, constraints)
        actions_store = []
        T = 10000.0
        cool = 0.98
        count = 0
        print(zidx, "/", len(test_sha256_all), " ... ", test_sha256)

        while T > 0.1:
            env_tmp = env
            action_type = random.randint(0, len(ACTION) - 1)

            state_, reward, done, info = env.step(action=action_type)

            _nn, _cost = cal_cost(state_.cpu().numpy(), train_data_all.cpu().numpy(), y_train_ori)

            if _cost < cost or random.random() < math.exp(-(_cost - cost) / T):
                tmp = [action_type]
                tmp.append(info)
                actions_store.append(tmp)
                env_tmp = env
                cost = _cost
            else:
                env = env_tmp
            T = T * cool

            if count % 20 == 0:
                print("\tcurrent step：%d th %s" % (count, ACTION[action_type]))
                print("\t", info[0], ", ", info[1], ", ", info[2])
            if done:
                print("\tsaving ... ")
                file = open(save_file_name, 'w')
                for az in actions_store:
                    file.write(str(az))
                    file.write('\n')
                file.write(str(done))
                file.write('\n')
                file.close()
                file_feature = open(save_feature_name, 'w')

                file_feature.write(str(state_.tolist()))
                file_feature.write('\n')
                file_feature.close()
                break
            if count > 500:
                break
            count += 1
