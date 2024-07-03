import os

os.environ['CUDA_VISIBLE_DEVICES'] = '1'

import numpy as np
import torch

import myenv_withconstraints
from lib import load_train_data, find_2nd_nn_l2, trans2triple_rw, load_all_test_data, katz_feature
from model import DQN

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# device = 'cpu'
'''
Parameters
'''
m = 100
steep = 1
MEMORY_CAPACITY = 50
actions_num = 4
if __name__ == '__main__':
    # load data
    train_data_file = "./train_o.pkl"
    test_data_file = "./test_o.pkl"
    constraints_path = "/Volumes/158.132.255.220/apk/testAPK_nodesAndCons/malware_cons_0308"
    seq_save_path = "results"

    X_train_am_ori, X_train_sen_idx_ori, y_train_ori, X_train_degree_cen_ori = load_train_data(
        train_data_file)
    X_test_sha256_all, X_test_am_all, X_test_sen_idx_all = load_all_test_data(
        test_data_file)

    if not os.path.exists(seq_save_path):
        os.mkdir(seq_save_path)

    y_train_ori = np.array(y_train_ori)
    X_train_degree_cen_ori = np.array(X_train_degree_cen_ori)
    for zidx in range(len(X_test_sha256_all)):
        X_test_sha256 = X_test_sha256_all[zidx]
        file_name1 = os.path.join(seq_save_path, 'action_seq', X_test_sha256 + '.txt')
        if os.path.exists(file_name1):
            continue
        print("get tirple set")
        X_test_am = X_test_am_all[zidx]
        triple_path = os.path.join(seq_save_path, "triple_set")
        if not os.path.exists(triple_path):
            os.makedirs(triple_path)
        X_test_triple = trans2triple_rw(X_test_am, X_test_sha256, triple_path, False)
        # print(X_test_triple)
        if X_test_triple is None:
            continue

        X_test_sen_idx = X_test_sen_idx_all[zidx]
        y_test = 0
        print(X_test_sha256)

        node_number = X_test_am.shape[0]
        if node_number > 5000:
            continue
        # get sensitive api index
        idx_matrix = np.zeros((X_test_sen_idx.size, X_test_am.shape[0]))
        ii = np.where(X_test_sen_idx != -1)
        idx_matrix[ii, X_test_sen_idx[ii]] = 1
        #
        all_degree = (np.sum(X_test_am, axis=0) + np.sum(X_test_am, axis=1).transpose()) / \
                     (X_test_am.shape[0] - 1)
        Q_fea = idx_matrix.dot(all_degree.transpose())

        katz_fea1 = katz_feature(X_test_am, X_test_sen_idx)
        Q_fea = np.array(Q_fea)
        Q_fea = np.append(Q_fea, katz_fea1)
        X_train_degree_cen = np.array(X_train_degree_cen_ori)
        y_train = y_train_ori
        # knn model
        nn = find_2nd_nn_l2(Q_fea, y_test, X_train_degree_cen_ori, y_train, m)
        target = X_train_degree_cen_ori[nn]
        target_label = y_train[nn]

        w = 2 * (y_train[nn] != y_test).astype(np.float32) - 1

        ## load constraints
        constraints_file = os.path.join(constraints_path, X_test_sha256 + ".txt")
        tmp = open(constraints_file, "r", encoding='utf-8').readlines()
        constraints = [int(a.replace("\n", "")) for a in tmp]
        constraints = np.array(constraints)

        target = torch.from_numpy(target).to(device, torch.float64)
        X_train_degree_cen = torch.from_numpy(np.squeeze(X_train_degree_cen)).to(device, torch.float64)
        y_train = torch.from_numpy(y_train).to(device).to(device)
        target_label = torch.from_numpy(target_label).to(device)
        w = torch.from_numpy(w).to(device)

        env = myenv_withconstraints.CFGModifierEnvConstraints(X_test_triple, y_test,
                                                              X_test_sen_idx, node_number,
                                                              target, target_label,
                                                              X_train_degree_cen, y_train,
                                                              w, steep,
                                                              constraints)

        dqn = DQN(states_dim=X_train_degree_cen_ori.shape[1], actions_num=actions_num, memory_capacity=1000,
                  learning_rate=0.01)

        print('\n Collecting experience ...')

        actions_store = []
        feature_name1 = seq_save_path + "/final_feature" + X_test_sha256 + ".txt"
        print("reset")
        state = env.reset()
        ep_r = 0
        count = 0
        while True:
            print("current ep:", 0, "current count:", count)
            action_type = dqn.choose_action(state, actions_num=actions_num)
            print("\tcur action:", action_type)
            state_, reward, done, info = env.step(action=action_type)

            if type(action_type) is np.ndarray:
                action_type = action_type[0]

            action = np.array([action_type] + info)
            dqn.store_transition(state, action, reward, state_, MEMORY_CAPACITY)
            print("\t", action.tolist())
            actions_store.append(action.tolist())
            ep_r += reward

            if dqn.memory_counter > MEMORY_CAPACITY:
                dqn.learn(MEMORY_CAPACITY, 32, N_STATES=state.shape[0])
                if done:
                    print("Ep:", 0,
                          ' | Ep_reward: ', round(ep_r, 2))

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
                file_feature.write(str(state.tolist()))
                file_feature.write('\n')
                file_feature.close()
                break
            if count > 500:
                break
            s = state_
            count += 1
