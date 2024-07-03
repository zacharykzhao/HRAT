import pickle
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

if __name__ == '__main__':
    ori_train = "C:/Users/Zachary/OneDrive - The Hong Kong Polytechnic University/Code/HRAT/myattack_QL_win/dataset" \
                "/train_csr_dict_0310.pkl"
    df = open(ori_train, "rb")
    data = pickle.load(df)
    X_train = np.array(data["degree_feature_data"])
    y_train = np.array(data["label"])

    featrue_file = "C:/Users/Zachary/Documents/A2MalwareStructuralAttack/results/malscan/actionseq2011"
    feature = []
    for zi in os.listdir(featrue_file):
        if not zi.__contains__("feature"):
            continue
        file1 = featrue_file + "/" + zi
        a = open(file1, 'r')
        a = a.readlines()
        a = a[0].replace("[", "").replace("]", "")
        a = a.split(",")
        if len(a) < 40000:
            continue
        d1 = [float(i) for i in a]
        d1 = np.array(d1)[:, np.newaxis].transpose()
        feature.append(d1)

    feature = feature[:200]
    clf = KNeighborsClassifier(n_neighbors=1)
    clf.fit(np.squeeze(X_train), y_train)
    y_pred = clf.predict(np.squeeze(feature))
    # yt = []
    # for i in feature:
    #     yt.append(clf.predict(i))
    print(np.unique(y_pred))
    new_label = np.zeros((len(feature), 1))
    test_partio = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
    for partio in test_partio:
        results = []
        acc = []

        for zi in range(10):
            cv_train, cv_test, cv_y_train, cv_sy_test = train_test_split(
                feature, new_label, test_size=partio, random_state=zi)
            cv_train = np.squeeze(np.array(cv_train))
            cv_test = np.squeeze(np.array(cv_test))
            data_new = np.append(X_train, cv_train, axis=0)
            label_new = np.append(y_train, cv_y_train)

            clf = KNeighborsClassifier(n_neighbors=1)
            clf.fit(np.squeeze(data_new), label_new)
            y_pred = clf.predict(cv_test)
            y_pred = list(y_pred)
            results.append([y_pred.count(0.0), y_pred.count(1.0)])
            acc.append(accuracy_score(y_true=cv_sy_test, y_pred=y_pred))
            # print("count 0:" + str(y_pred.count(0.0)) + " count 1: "+str(y_pred.count(1.0)))
            #
            # print(accuracy_score(y_true=cv_sy_test, y_pred=y_pred))

        print(str(partio) + "  results:" + str(np.mean(acc)) + " std:" + str(np.std(acc)))
