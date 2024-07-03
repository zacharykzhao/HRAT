import os
import numpy as np
import pickle
from scipy import sparse
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from tqdm import tqdm

if __name__ == '__main__':
    data_path = "csr_dict_families.pkl"
    df = open(data_path, "rb")
    data3 = pickle.load(df)
    apk_name_list = list(data3)

    X_train = []
    node_idx_train = []
    y_train = []
    train_apk_sha = []
    train_feature = []

    print("get all data and feature")
    for a in tqdm(range(len(apk_name_list))):
        tmp = data3[apk_name_list[a]]
        train_apk_sha.append(apk_name_list[a])
        X_train.append(tmp["adjacent_matrix"])
        y_train.append(tmp["label"])
        node_idx_train.append(tmp["idx"])
        feature = tmp["feature"]
        train_feature.append(feature)

    malware_id = [i for i in range(len(y_train)) if y_train[i] == 0]
    benign_id = [i for i in range(len(y_train)) if y_train[i] == 1]

    train_data_am = []
    train_label = []
    train_feature_n = []
    train_sha256 = []
    train_node_idx = []
    print("get benign data")
    for i in range(len(benign_id)):
        train_sha256.append(train_apk_sha[benign_id[i]])
        train_data_am.append(X_train[benign_id[i]])
        train_label.append(y_train[benign_id[i]])
        train_feature_n.append(train_feature[benign_id[i]])
        train_node_idx.append(node_idx_train[benign_id[i]])
    for i in range(1000):
        train_sha256.append(train_apk_sha[malware_id[i]])
        train_data_am.append(X_train[malware_id[i]])
        train_label.append(y_train[malware_id[i]])
        train_feature_n.append(train_feature[malware_id[i]])
        train_node_idx.append(node_idx_train[malware_id[i]])

    clf = KNeighborsClassifier(n_neighbors=1)
    clf.fit(np.squeeze(train_feature_n), train_label)

    size = len(malware_id) - 1000

    test_sha256 = []
    test_data_am = []
    test_node_idx = []

    for i in range(size):
        data_tmp = train_feature[malware_id[i + 1000]][:, np.newaxis].transpose()
        if clf.predict(data_tmp)[0] == 0 :
            test_sha256.append(train_apk_sha[malware_id[i + 1000]])
            test_data_am.append(X_train[malware_id[i + 1000]])
            test_node_idx.append(node_idx_train[malware_id[i + 1000]])
        else:
            train_sha256.append(train_apk_sha[malware_id[i + 1000]])
            train_data_am.append(X_train[malware_id[i + 1000]])
            train_feature_n.append(train_feature[malware_id[i + 1000]])
            train_node_idx.append(node_idx_train[malware_id[i + 1000]])
            train_label.append(0)

    print("begin writing train")
    train_all = dict()
    train_all["adjacent_matrix"] = train_data_am
    train_all["data"] = train_feature_n
    train_all["node_idx"] = train_node_idx
    train_all["label"] = train_label
    pickle.dump(train_all, open("mamadroid_train.pkl", "wb"))

    print("begin writing test")

    test_candidate = dict()
    test_candidate["sha256"] = test_sha256
    test_candidate["adjacent_matrix"] = test_data_am
    test_candidate["node_idx"] = test_node_idx
    pickle.dump(test_candidate, open("mamadroid_test.pkl", "wb"))
