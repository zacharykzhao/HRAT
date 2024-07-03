import os
import random

import numpy as np
import pickle
from scipy import sparse
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from tqdm import tqdm


def degree_centrality_extraction(adjacent_matrix, sen_idx):
    centrality = (adjacent_matrix.sum(axis=0) + adjacent_matrix.sum(axis=1).transpose()) / (
            adjacent_matrix.shape[0] - 1)
    centrality = np.array(centrality)
    centrality = np.squeeze(centrality)
    idx_matrix = np.zeros((len(sen_idx), adjacent_matrix.shape[0]))
    ii = np.where(sen_idx != -1)
    idx_matrix[ii, sen_idx[ii]] = 1
    feature = np.matmul(idx_matrix, centrality)
    return feature


def extract_data_am_test(data_path):
    df = open(data_path, "rb")
    data3 = pickle.load(df)
    df.close()
    apk_name_list = list(data3)

    X_train = []
    Idx_train = []
    y_train = []
    train_apk_sha = []
    train_feature = []

    print("get all data and feature")
    for a in tqdm(range(len(apk_name_list))):
        tmp = data3[apk_name_list[a]]
        train_apk_sha.append(apk_name_list[a])
        X_train.append(tmp["adjacent_matrix"])
        Idx_train.append(tmp["sensitive_api_list"])
        y_train.append(tmp["label"])
        feature_deg = degree_centrality_extraction(tmp["adjacent_matrix"], tmp["sensitive_api_list"])
        # feature = np.append(feature_deg)
        train_feature.append(feature_deg)

    malware_id = [i for i in range(len(y_train)) if y_train[i] == 0]
    benign_id = [i for i in range(len(y_train)) if y_train[i] == 1]
    random.shuffle(malware_id)
    random.shuffle(benign_id)
    train_data_am = []
    train_label = []
    train_sen_id = []
    train_feature_n = []
    train_sha256 = []
    print("get benign data")
    for i in benign_id:
        train_sha256.append(train_apk_sha[benign_id[i]])

        train_data_am.append(X_train[benign_id[i]])
        train_label.append(y_train[benign_id[i]])
        train_sen_id.append(Idx_train[benign_id[i]])
        train_feature_n.append(train_feature[benign_id[i]])
    for i in range(1000):
        train_sha256.append(train_apk_sha[malware_id[i]])

        train_data_am.append(X_train[malware_id[i]])
        train_label.append(y_train[malware_id[i]])
        train_sen_id.append(Idx_train[malware_id[i]])
        train_feature_n.append(train_feature[malware_id[i]])

    clf = KNeighborsClassifier(n_neighbors=1)
    scores = cross_val_score(clf, np.squeeze(train_feature_n), train_label, cv=10)
    print(scores)

    clf = KNeighborsClassifier(n_neighbors=1)
    clf.fit(np.squeeze(train_feature_n), train_label)

    size = len(malware_id) - 1000

    test_sha256 = []
    test_data_am = []
    test_sen_idx = []

    for i in range(size):
        data_tmp = train_feature[malware_id[i + 1000]][:, np.newaxis].transpose()

        if clf.predict(data_tmp)[0] == 0:
            test_sha256.append(train_apk_sha[malware_id[i + 1000]])
            test_data_am.append(X_train[malware_id[i + 1000]])
            test_sen_idx.append(Idx_train[malware_id[i + 1000]])

        else:
            train_sha256.append(train_apk_sha[malware_id[i + 1000]])
            train_data_am.append(X_train[malware_id[i + 1000]])
            train_feature_n.append(train_feature[malware_id[i + 1000]])
            train_label.append(0)
            train_sen_id.append(Idx_train[malware_id[i + 1000]])

    print("begin writing train")
    train_all = dict()
    train_all["adjacent_matrix"] = train_data_am
    train_all["degree_feature_data"] = train_feature_n
    train_all["sensitive_api_index"] = train_sen_id
    train_all["label"] = train_label
    pickle.dump(train_all, open("train_o.pkl", "wb"))

    print("begin writing test")

    test_candidate = dict()
    test_candidate["sha256"] = test_sha256
    test_candidate["adjacent_matrix"] = test_data_am
    test_candidate["sensitive_api_idx"] = test_sen_idx
    pickle.dump(test_candidate, open("test_o.pkl", "wb"))


if __name__ == '__main__':
    path_to_training_set = "the_path_to_your_formated_dataset"
    path_to_training_set = '../dataset/dataset_TREo.pkl'
    extract_data_am_test(data_path=path_to_training_set)
