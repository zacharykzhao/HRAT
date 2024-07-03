import pickle
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from random import sample
if __name__ == '__main__':
    ori_train = "C:/Users/Zachary/OneDrive - The Hong Kong Polytechnic University/Code/myattack_QL_win" \
                "/CCS2020EnhanceMalscan/train_csr_dict_0322.pkl"
    df = open(ori_train, "rb")
    data = pickle.load(df)
    X_train = np.array(data["degree_feature_data"])
    y_train = np.array(data["label"])

    benign_data = X_train[:100]

    X_train = X_train[100:]
    y_train = y_train[100:]

    # featrue_file = "C:/Users/Zachary/Documents/A2MalwareStructuralAttack/results/malscan_enhanced/actionseq2012"
    featrue_file = "C:/Users/Zachary/OneDrive - The Hong Kong Polytechnic University/Code/gpushareIns2/malscan_enhanced_prob3/actionseq2012"

    feature = []
    for zi in os.listdir(featrue_file):
        if not zi.__contains__("feature"):
            continue
        file1 = featrue_file + "/" + zi
        a = open(file1, 'r')
        a = a.readlines()
        a = a[0].replace("[", "").replace("]", "")
        a = a.split(",")
        # if len(a) < 40000:
        #     continue
        d1 = [float(i) for i in a]
        d1 = np.array(d1)[:, np.newaxis].transpose()
        feature.append(d1)
    # feature = feature[:400]
    feature_raw = feature
    clf = KNeighborsClassifier(n_neighbors=1)
    clf.fit(np.squeeze(X_train), y_train)
    y_pred = clf.predict(np.squeeze(feature))
    # yt = []
    # for i in feature:
    #     yt.append(clf.predict(i))
    print(np.unique(y_pred))
    new_label = np.ones((len(feature), 1))
    test_partio = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
    for partio in test_partio:
        results = []
        acc = []
        acc_benign = []
        for zi in range(10):

            # feature = sample(feature_raw, 400)
            feature = feature_raw
            new_label = np.zeros((len(feature), 1))
            cv_train, cv_test, cv_y_train, cv_sy_test = train_test_split(
                feature, new_label, test_size=partio, random_state=zi)
            cv_train = np.squeeze(np.array(cv_train))
            cv_test = np.squeeze(np.array(cv_test))
            data_new = np.append(X_train, cv_train, axis=0)
            label_new = np.append(y_train, cv_y_train)
            print("sample num train: "+str(len(cv_y_train)) + ";test:"+ str(len(cv_sy_test)))
            clf = KNeighborsClassifier(n_neighbors=1)
            clf.fit(np.squeeze(data_new), label_new)
            y_pred = clf.predict(cv_test)
            y_pred = list(y_pred)
            results.append([y_pred.count(0.0), y_pred.count(1.0)])
            acc.append(accuracy_score(y_true=cv_sy_test, y_pred=y_pred))
            # print(accuracy_score(y_true=cv_sy_test, y_pred=y_pred))

            # benign_data = X_train[:100]
            # y_benign = np.ones((100,1))
            # y_pred = clf.predict(benign_data)
            # y_pred = list(y_pred)
            # results.append([y_pred.count(0.0), y_pred.count(1.0)])
            # acc_benign.append(accuracy_score(y_true=y_benign, y_pred=y_pred))

        print(str(partio) + "  results:" + str(np.mean(acc)) + " std:" + str(np.std(acc)))
        # print("\t"+str(partio) + "  results benign:" + str(np.mean(acc_benign)) + " std:" + str(np.std(acc_benign)))