# -*- coding: UTF-8 -*-

# author: Zachary Kaifa ZHAO
# e-mail: kaifa dot zhao (at) connect dot polyu dot hk
# datetime: 2022/3/9 7:42 PM
# software: PyCharm
import os
import pickle
import numpy as np
from tqdm import tqdm
import torch

from Utils import degree_centrality_torch, katz_feature_torch, to_adjmatrix, check_folder,\
    find_nn_torch, trans2triple_rw
import myenv_withconstraints
import os

from model import DQN

m = 100
steep = 1
MEMORY_CAPACITY = 16
actions_num = 4

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

if __name__ == '__main__':

    save_path = "results"
    check_folder(save_path)

    ## load train data
    train_path = "data_train.pkl"
    df = open(train_path, "rb")
    data_train_dict = pickle.load(df)
    df.close()

    train_sha256 = data_train_dict["sha256"]
    train_feature = data_train_dict["feature"]
    train_label = data_train_dict["label"]

    # load test
    test_data = "data_test.pkl"
    df = open(test_data, "rb")
    data_test_dict = pickle.load(df)
    df.close()
    test_sha256_list = list(data_test_dict)
    print("==== loading test adjacent matrix ====")
    test_adj = [tmp["adjacent_matrix"] for tmp in tqdm(data_test_dict.values())]
    print("==== loading test sensitive api index ====")
    test_sensi_idx = [tmp["sensitive_api_list"] for tmp in tqdm(data_test_dict.values())]
    print(len(test_sha256_list))

    seq_save_path = save_path + "/actionseq"
    if not os.path.exists(seq_save_path):
        os.mkdir(seq_save_path)

    train_feature_torch = torch.from_numpy(np.array(train_feature)).to(device)
    train_label_torch = torch.from_numpy(np.array(train_label)).to(device)

    dqn = DQN(states_dim=train_feature_torch.shape[1],
                    actions_num=actions_num,
                    memory_capacity=MEMORY_CAPACITY,
                    learning_rate=0.01)

    for zidx in tqdm(range(1, len(test_sha256_list))):
        print("\ncurrent test number:\t " + str(zidx))

        X_test_sha256 = test_sha256_list[zidx]
        print(X_test_sha256)
        
        print("==== transfer adjacent matrix to triple set ====")
        X_test_am = test_adj[zidx]
        X_test_sen_idx = test_sensi_idx[zidx]
        triple_path = save_path + "/triple_set"
        check_folder(triple_path)
        if not os.path.exists(triple_path):
            os.mkdir(triple_path)
        X_test_triple = trans2triple_rw(X_test_am, X_test_sha256, triple_path, False)
        if X_test_triple is None:
            continue
        print("finish")

        node_number = X_test_am.shape[0]
        adj_torch = to_adjmatrix(X_test_triple, node_number)
        degree_fea = degree_centrality_torch(adj_torch, X_test_sen_idx, device)
        katz_fea = katz_feature_torch(adj_torch, X_test_sen_idx, device=device)
        X_test_feature = torch.cat((degree_fea, torch.squeeze(katz_fea)), 0)
        ##
        y, min_dist = find_nn_torch(X_test_feature, train_feature_torch, train_label_torch, k=1)

        if y != 0:
            print('==== data cannot be correctly classified as malware ====\t')
            continue
        y_test = 0
        # begin train something
        print('\t ==== get the nearest neighbors for optimization ====')

        w = (2 * (train_label_torch != y_test).int() - 1).float().to(device)

        # load constraints
        print('\t ===== loading constraints =====')
        constraints_path = "constraints/" + X_test_sha256 + ".txt"
        tmp = open(constraints_path, "r", encoding='utf-8').readlines()
        constraints = [int(a.replace("\n", "")) for a in tmp]
        constraints = np.array(constraints)

        env = myenv_withconstraints.CFGModifierEnvConstraints(target_graph=X_test_triple,
                                                              label=y_test,
                                                              target_sen_api_idx=X_test_sen_idx,
                                                              node_num=node_number,
                                                              X_train=train_feature_torch,
                                                              y_train=train_label_torch,
                                                              train_set=train_feature_torch,
                                                              train_label=train_label_torch,
                                                              w=w, steep=steep,
                                                              constraints=constraints)

        

        print('\t ==== Collecting experience ... ====')
        flag = 0
        for i_episode in range(30):
            actions_store = []
            print("reset")
            state = env.reset()
            ep_r = 0
            count = 0

            while True:
                print("current round:\t" + str(count) + "\t==========")
                if dqn.memory_counter <= MEMORY_CAPACITY:
                    action_type = np.random.randint(actions_num)
                else:
                    action_type = dqn.choose_action(state, actions_num=actions_num)
                state_, reward, done, info, cur_graph = env.step(action=action_type)
                print('reward：'+str(reward))
                if type(action_type) is np.ndarray:
                    action_type = action_type[0]

                action = np.array([action_type] + info)
                dqn.store_transition(state, action, reward, state_, MEMORY_CAPACITY)
                print("\t", action.tolist())
                actions_store.append(action.tolist())
                ep_r += reward

                if dqn.memory_counter > MEMORY_CAPACITY:
                    dqn.learn(MEMORY_CAPACITY, 16, N_STATES=state.shape[0])
                    
                    if done:
                        print("Ep:", i_episode,
                            ' | Ep_reward: ', round(ep_r, 2))
                if done:
                    if count<5:
                        flag = 1
                    # 220310 for check : can be commented
                    check_label,min_dist = find_nn_torch(state_, train_feature_torch, train_label_torch, k=1)
                    if check_label == 0:
                        print("something went wrong")

                    action_path = seq_save_path + "/" + X_test_sha256 + "action_list" + str(i_episode) + ".txt"

                    file = open(action_path, 'w')
                    for az in actions_store:
                        file.write(str(az))
                        file.write('\n')
                    file.write(str(done))
                    file.write('\n')
                    file.close()

                    graph_path = seq_save_path + "/final_graph" + str(i_episode)+"_" + X_test_sha256 + ".npy"
                    np.save(graph_path, cur_graph)
                    
                    feature_file_name = seq_save_path + "/final_feature_epi" + str(i_episode)+"_" + X_test_sha256 + ".txt"
                    file_feature = open(feature_file_name, 'w')
                    file_feature.write(str(state_.tolist()))
                    file_feature.write('\n')
                    file_feature.write(str(state.tolist()))
                    file_feature.write('\n')
                    file_feature.close()
                    print('!!!! finish within 5')

                    break
                if count > 500:
                    break
                s = state_
                count += 1
            if flag == 1:
                break

        
