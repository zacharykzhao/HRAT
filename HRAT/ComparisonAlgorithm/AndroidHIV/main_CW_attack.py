# -*- coding: UTF-8 -*-

# author: Zachary Kaifa ZHAO
# e-mail: kaifa dot zhao (at) connet dot polyu dot hk
# datetime: 2021/7/19 4:50 PM
# software: PyCharm
import os
import pickle

import numpy as np
import torch

from preprocess import get_call_number, extract_feature, extract_feature_torch
from Substitute_model import Substitute

from HRAT.ComparisonAlgorithm.AndroidHIV.CW_model import CW_Attack

'''
Parameters from Android-HIV
'''

ATTACK_STRENGTH = 10  # default 0,100
UPPER_BOUND = 70  # C default 0:10:100
ALPHA = 1
MAX_ITER = 1000  #
NUM_STATE = 11


def load_train(file_path):
    df = open(file_path, "rb")
    train_data = pickle.load(df)
    feature = train_data["data"]
    label = train_data["label"]
    return feature, label


if __name__ == '__main__':
    # import train
    train_feature, train_label = load_train("../data/train_csr_dict_families.pkl")

    # import test
    df = open("../data/test_csr_dict_2011_families.pkl", "rb")
    data = pickle.load(df)
    test_sha256_all = data["sha256"]
    test_adj_all = data["adjacent_matrix"]
    test_idx_all = data["node_idx"]
    # load pretrained original classifier (1NN)
    knn_1 = pickle.load(open("knn1_2021.pkl", 'rb'))
    # load pretrained substitute
    substitute = Substitute(121)
    substitute.load_state_dict(torch.load("../model/substitute_model.pth"))
    train_data_all = np.array(train_feature)
    train_label_all = np.array(train_label)
    # save
    save_dict = "results_0803_substitute"
    save_feature = "feature_results_substitute"
    if not os.path.exists(save_dict):
        os.mkdir(save_dict)
    if not os.path.exists(save_feature):
        os.mkdir(save_feature)

    count = 0

    for z_idx, test_sha256 in enumerate(test_sha256_all):
        test_adj = test_adj_all[z_idx]
        state_idx = test_idx_all[z_idx]

        X_ori = get_call_number(test_adj, state_idx)
        feature = extract_feature(X_ori)
        feature = torch.from_numpy(np.array(feature)[np.newaxis, :]).float()
        y = int(torch.max(substitute(feature), 1)[1])
        # y = knn_1.predict(feature.reshape(1, -1))

        if y == 1:
            # print(test_sha256)
            print(z_idx, "/", len(test_sha256_all), "\t", test_sha256, ":", str(y))
            with open("false_detection.txt", "a") as f:
                f.write(test_sha256)
                f.write('\n')
            continue
        count += 1
        # print(z_idx, "/", len(test_sha256_all), "\t", test_sha256, ":", str(y))
        save_file = save_dict + "/" + test_sha256 + ".txt"
        if os.path.exists(save_file):
            continue
        # attack
        c = 0.1
        attack_model = CW_Attack(test_adj, X_ori, state_idx,
                                          substitute,
                                          ATTACK_STRENGTH, ALPHA, c,
                                          knn_1)
        # initialization
        X_adv = torch.from_numpy(X_ori)
        w = torch.zeros((11, 11))
        while c < UPPER_BOUND and y == 0:

            for _iter in range(MAX_ITER):

                w, loss = attack_model.step(X_adv, w)  # line 7

                w = torch.ceil(w)

                X_adv = X_adv + w   # line 8
                # obtain label
                feature = extract_feature_torch(X_adv)
                # _, y = torch.max(substitute(feature), 1)
                # y = int(y)
                # if _iter % 50 == 0:
                #     print("iter %d, c %f, loss %f max(w) %f" % (_iter, c, loss, torch.max(w)))
                if True in feature.isnan():
                    with open("false_detection.txt", "a") as f:
                        f.write(test_sha256)
                        f.write("\tnan exist")
                        f.write('\n')
                    break
                # try:
                y = knn_1.predict(feature.reshape(1, -1))
                # except Exception:
                #     print(Exception)
                if y != 0:
                    break
            c = c * 10
        if y == 1:
            print("\tsave %s" % test_sha256)
            tmp = w.numpy()
            np.savetxt(save_file, w)
            final_feature = np.array(feature)
            np.savetxt(save_feature + "/" + test_sha256 + ".txt", final_feature)

    print("identified app:", count)