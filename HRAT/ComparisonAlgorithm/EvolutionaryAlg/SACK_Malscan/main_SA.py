# -*- coding:utf-8 -*-
# Author: Kaifa Zachary ZHAO
# Date: 7/24/2021


"""
Comparison Experiments:
    Evolutionary algorithm -- simulated Annealing
    Cost: distance from target malware to software in training data
"""
import math
import random

from HRAT.ComparisonAlgorithm.EvolutionaryAlg.SACK_Malscan.SACK_Utils import *
from SA_env import SA_env
from HRAT.ComparisonAlgorithm.EvolutionaryAlg.EA_Utils import check_folder, malscan_feature_extraction, cal_cost,  laod_constraints
import os
import numpy as np

ACTION = ['add_edge', 'rewiring', 'add_nodes', 'delete_nodes']
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

if __name__ == '__main__':

    save_folder = "simulated_annealing_malscan_2011"
    check_folder(save_folder)

    X_train_am_ori, X_train_sen_idx_ori, y_train_ori, X_train_feature_ori = load_train_data(
        "./dataset/train.pkl")
    X_test_sha256_all, X_test_am_all, X_test_sen_idx_all = load_all_test_data(
        "./test.pkl")

    for zidx, X_test_sha256 in enumerate(X_test_sha256_all):
        if zidx < 178:
            continue
        save_file_name = save_folder + "/" + X_test_sha256 + "action_list.txt"
        save_feature_name = save_folder + "/final_feature" + X_test_sha256 + ".txt"
        if os.path.exists(save_file_name):
            continue
        print(zidx, "/", len(X_test_sha256_all), " ... ", X_test_sha256)
        triple_path = "C:/Users/Zachary/Documents/A2MalwareStructuralAttack/" \
                      "results/triple_set2011/" + X_test_sha256 + ".npy"

        X_test_am = X_test_am_all[zidx]
        X_test_triple = trans2triple_rw(X_test_am, X_test_sha256, triple_path, False)
        if X_test_triple is None:
            continue

        X_test_sen_idx = X_test_sen_idx_all[zidx]
        y_test = 0
        node_number = X_test_am.shape[0]
        if node_number > 5000:
            continue

        X_test_feature = malscan_feature_extraction(X_test_sen_idx, X_test_am)
        X_test_feature = np.array(X_test_feature)
        X_train_feature = np.array(X_train_feature_ori)

        nn, cost = cal_cost(X_test_feature, X_train_feature, np.array(y_train_ori))
        y_train_ori = np.array(y_train_ori)
        target = X_train_feature[nn]
        target_label = y_train_ori[nn]
        w = 2 * (y_train_ori[nn] != y_test).astype(np.float32) - 1
        steep = 1
        ## load constraints
        constraints = laod_constraints("F:/graphs/2011/malware/cons/" + X_test_sha256 + ".txt")

        # init
        X_train_feature = torch.from_numpy(np.squeeze(X_train_feature)).to(device, torch.float64)
        y_train = torch.from_numpy(np.array(y_train_ori)).to(device).to(device)
        target_label = torch.from_numpy(target_label).to(device)
        target = torch.from_numpy(target).to(device, torch.float64)
        w = torch.from_numpy(w).to(device)

        env = SA_env(X_test_triple, y_test,
                     X_test_sen_idx, node_number,
                     target, target_label,
                     X_train_feature, y_train,
                     w, steep,
                     constraints)

        actions_store = []
        T = 10000.0
        cool = 0.98
        count = 0

        while T > 0.1:
            env_tmp = env
            action_type = random.randint(0, len(ACTION) - 1)
            try:
                state_, reward, done, info = env.step(action=action_type)
            except Exception:
                print("error: ", X_test_sha256 )

            _nn, _cost = cal_cost(state_.cpu().numpy(), X_train_feature.cpu().numpy(), y_train_ori)

            if _cost < cost or random.random() < math.exp(-(_cost - cost) / T):
                tmp = [action_type]
                tmp.append(info)
                actions_store.append(tmp)
                cost = _cost
                env_tmp = env
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
