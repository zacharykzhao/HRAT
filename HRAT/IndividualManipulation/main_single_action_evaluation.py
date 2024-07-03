# -*- coding:utf-8 -*-
# Author: Kaifa Zachary ZHAO
# Date: 6/27/2021
import os

import numpy as np
import torch

from IMA_Utils import load_train_data, load_all_test_data, trans2triple_rw, katz_feature, find_2nd_nn_l2
from SingleActionAttackGrad import SingleActionGrad

action_name = ['add_edge', 'rewiring', 'add_nodes', 'delete_nodes']
action_type = 0

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

if __name__ == '__main__':
    ###
    save_folder = "2011_actions_" + action_name[action_type] + "_0627"
    if not os.path.exists(save_folder):
        os.mkdir(save_folder)

    m = 100
    steep = 1
    actions_num = 4
    ###
    X_train_am_ori, X_train_sen_idx_ori, y_train_ori, X_train_degree_cen_ori = load_train_data(
        "../dataset/train_csr_dict_0310.pkl")
    X_test_sha256_all, X_test_am_all, X_test_sen_idx_all = load_all_test_data(
        "../dataset/test_csr_dict_2011.pkl")
    y_train_ori = np.array(y_train_ori)
    X_train_degree_cen_ori = np.array(X_train_degree_cen_ori)


    for zidx, X_test_sha256 in enumerate(X_test_sha256_all):

        X_test_sha256 = X_test_sha256_all[zidx]
        file_name1 = save_folder + "/" + X_test_sha256 + "action_list.txt"
        feature_name1 = save_folder + "/final_feature" + X_test_sha256 + ".txt"
        if os.path.exists(file_name1):
            continue
        print(zidx)
        triple_path = "/results/triple_set2011/"+X_test_sha256+".npy"

        X_test_am = X_test_am_all[zidx]
        X_test_triple = trans2triple_rw(X_test_am, X_test_sha256,triple_path, False)
        if X_test_triple is None:
            continue

        X_test_sen_idx = X_test_sen_idx_all[zidx]
        y_test = 0
        # X_test_degree_cen = degree_centrality_extraction(X_test_am, X_test_sen_idx)
        # katz_fea = katz_feature(X_test_am, X_test_sen_idx)
        # X_test_degree_cen = np.append(X_test_degree_cen, katz_fea)
        print(X_test_sha256)

        node_number = X_test_am.shape[0]
        if node_number > 5000:
            continue
        # get sensitive api index
        idx_matrix = np.zeros((X_test_sen_idx.size, X_test_am.shape[0]))
        ii = np.where(X_test_sen_idx != -1)
        idx_matrix[ii, X_test_sen_idx[ii]] = 1
        # get w
        all_degree = (np.sum(X_test_am, axis=0) + np.sum(X_test_am, axis=1).transpose()) / \
                     (X_test_am.shape[0] - 1)
        Q_fea = idx_matrix.dot(all_degree.transpose())

        katz_fea1 = katz_feature(X_test_am, X_test_sen_idx)
        Q_fea = np.array(Q_fea)
        Q_fea = np.append(Q_fea, katz_fea1)
        X_train_degree_cen = np.array(X_train_degree_cen_ori)
        y_train = y_train_ori
        nn = find_2nd_nn_l2(Q_fea, y_test, X_train_degree_cen_ori, y_train, m)
        target = X_train_degree_cen_ori[nn]
        target_label = y_train[nn]

        w = 2 * (y_train[nn] != y_test).astype(np.float32) - 1

        ## load constraints
        constraints_path = "F:/graphs/2011/malware/cons/" + X_test_sha256 + ".txt"
        tmp = open(constraints_path, "r", encoding='utf-8').readlines()
        constraints = [int(a.replace("/n", "")) for a in tmp]
        constraints = np.array(constraints)

        target = torch.from_numpy(target).to(device, torch.float64)
        X_train_degree_cen = torch.from_numpy(np.squeeze(X_train_degree_cen)).to(device, torch.float64)
        y_train = torch.from_numpy(y_train).to(device).to(device)
        target_label = torch.from_numpy(target_label).to(device)
        # idx_matrix = torch.from_numpy(idx_matrix).to(device)
        w = torch.from_numpy(w).to(device)


        env = SingleActionGrad(X_test_triple, y_test,
                               X_test_sen_idx, node_number,
                               target, target_label,
                               X_train_degree_cen, y_train,
                               w, steep,
                               constraints)

        actions_store = []
        ep_r = 0
        count = 0
        while True:
            # print("current step：%d th %s" % (count, action_name[action_type]))
            try:
                state_, reward, done, info = env.step(action=action_type)
            except:
                continue
            if count %10 == 0:
                print("current step：%d th %s" % (count, action_name[action_type]))

            tmp = [action_type]
            tmp.extend(info)
            actions_store.append(tmp)
            if done:
                file = open(file_name1, 'w')
                for az in actions_store:
                    file.write(str(az))
                    file.write('\n')
                file.write(str(done))
                file.write('\n')
                file.close()
                file_feature = open(feature_name1, 'w')

                file_feature.write(str(state_.tolist()))
                file_feature.write('\n')
                file_feature.close()
                break
            if count > 500:
                break
            count += 1
