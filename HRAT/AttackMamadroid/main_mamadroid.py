import os

import numpy as np
import torch
import pickle
import networkx as nx

from MamadroidUtils import find_2nd_nn_l2, trans2triple_rw

from HRAT.AttackMamadroid.MamadroidUtils import extract_feature
from HRAT.AttackMamadroid.mamadroidEnv import CFGModifierEnvMamadroidCons
from model import DQN

# from preprocess.formatData import extract_feature

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

'''parameters'''
m = 75
steep = 1
MEMORY_CAPACITY = 30
actions_num = 4
state_category = "families"


###

def check_folder(tar_path):
    if not os.path.exists(tar_path):
        os.makedirs(tar_path)


if __name__ == '__main__':
    train_data_file = './mamadroid_train.pkl'
    test_data_file = './mamadroid_test.pkl'
    constraints_path = "/Volumes/158.132.255.220/apk/testAPK_nodesAndCons/malware_cons_0308"
    results_save_path = './results'
    triple_save_path = './tripleset'
    #
    check_folder(results_save_path)
    check_folder(triple_save_path)
    df = open(test_data_file, "rb")
    data = pickle.load(df)
    test_sha256_all = data["sha256"]
    test_adj_all = data["adjacent_matrix"]
    test_idx_all = data["node_idx"]

    func_num = 11
    df = open(train_data_file, "rb")
    train_data = pickle.load(df)

    for zidx in range(len(test_sha256_all)):
        test_sha256 = test_sha256_all[zidx]
        file_name1 = os.path.join(results_save_path, test_sha256 + "action_list" + ".txt")
        if os.path.exists(file_name1):
            continue
        train_data_all = np.array(train_data["data"])
        train_label_all = np.array(train_data["label"])
        y_train_ori = np.array(train_label_all)
        X_train = np.array(train_data_all)

        test_adj = test_adj_all[zidx]
        func_idx = test_idx_all[zidx]
        idx_one_hot = np.zeros((func_idx.size, func_num))
        idx_one_hot[np.arange(func_idx.size), func_idx] = 1

        test_feature = extract_feature(test_adj, func_idx, state_category)
        test_label = 1
        # find m reference samples
        nn = find_2nd_nn_l2(test_feature, test_label, train_data_all, train_label_all, m)
        target = train_data_all[nn]
        target_label = train_label_all[nn]
        w = 2 * (train_label_all[nn] != test_label).astype(np.float32) - 1

        ## load constraints
        constraints_file = os.path.join(constraints_path, test_sha256 + ".txt")
        f = open(constraints_file, 'r')
        tmp = f.readlines()
        constraints = np.array([int(i.split('\n')[0]) for i in tmp])
        if len(np.unique(constraints)) == 1:
            continue
        print(test_sha256)

        print("get tirple set")

        triple_set_file = os.path.join(triple_save_path, test_sha256 + '.npy')

        X_test_triple = trans2triple_rw(test_adj, triple_set_file)

        # to torch tensor
        train_data_all = torch.from_numpy(train_data_all).to(device)
        train_label_all = torch.from_numpy(np.array(train_label_all)).to(device)
        target = torch.from_numpy(target).to(device)
        target_label = torch.from_numpy(target_label).to(device)
        test_triple = X_test_triple

        test_label = torch.tensor(test_label).to(device)
        # test_func_idx = torch.tensor(func_idx).to(device)
        w = torch.from_numpy(w).to(device)

        test_func_idx = idx_one_hot
        node_number = test_adj.shape[0]

        print("initial environment")
        env = CFGModifierEnvMamadroidCons(test_triple, test_label, node_number,
                                          test_func_idx,
                                          target, target_label,
                                          train_data_all, train_label_all,
                                          w, steep, constraints)
        dqn = DQN(states_dim=X_train.shape[1], actions_num=actions_num, memory_capacity=1000,
                  learning_rate=0.01)

        print('\n Collecting experience ...')

        actions_store = []
        feature_name1 = os.path.join(results_save_path, "final_feature" + test_sha256 + ".txt")
        print("reset")
        state = env.reset()
        ep_r = 0
        count = 0
        while True:
            print("current ep:", 0, "current count:", count)

            # print("\t selecting action")
            action_type = dqn.choose_action(state, actions_num=actions_num)
            print("\tcur action:", action_type)
            # take action
            # print("\t taking action")
            state_, reward, done, info = env.step(action=action_type)
            if type(action_type) is np.ndarray:
                action_type = action_type[0]
            action = np.array([action_type] + info)
            # modify the reward
            # print("\t storing transitions")
            dqn.store_transition(state, action, reward, state_, MEMORY_CAPACITY)
            print("\t", action.tolist())
            actions_store.append(action.tolist())
            ep_r += reward

            if dqn.memory_counter > MEMORY_CAPACITY:
                print(" \tdqn learn ... ... ")
                dqn.learn(MEMORY_CAPACITY, 10, N_STATES=state.shape[0])
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
