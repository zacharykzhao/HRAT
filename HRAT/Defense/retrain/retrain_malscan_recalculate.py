
import numpy as np
import pickle
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, accuracy_score

from algorithm_evaluation.libs import obtain_sensitive_apis
from formatData import get_sen_idx
from util import fcg2adj_return, degree_centrality_extraction, katz_feature
from sklearn.model_selection import train_test_split
import os

def getMalscanFeature(node_path, graph_path):
    tmp = open(node_path, "r", encoding='utf-8').readlines()
    node_list = [a.replace("\n", "") for a in tmp]
    graph = fcg2adj_return(graph_path, node_path)
    sen_idx = get_sen_idx(node_list, sensitive_apis)
    feature_deg = degree_centrality_extraction(graph, sen_idx)
    feature_katz = katz_feature(graph, sen_idx)
    feature = np.append(feature_deg, feature_katz)
    feature = np.array(feature)[:, np.newaxis].transpose()

    return feature

if __name__ == '__main__':
    ori_train = "C:/Users/Zachary/OneDrive - The Hong Kong Polytechnic University/Code/myattack_QL_win/dataset" \
                "/train_csr_dict_0310.pkl"
    df = open(ori_train, "rb")
    data = pickle.load(df)
    X_train = np.array(data["degree_feature_data"])
    y_train = np.array(data["label"])

    apk_path = "C:/Users/Zachary/Documents/A2MalwareStructuralAttack/results/modifi_seq/malscan/2011"
    apk_file = os.listdir(apk_path)
    sensitive_apis_path = '../../sensitive_apis_soot_signature.txt'
    sensitive_apis = obtain_sensitive_apis(sensitive_apis_path)

    new_feature_set = []
    for i in range(len(apk_file)):#len(apk_file)
        tmp = apk_file[i]
        sha256 = tmp.replace("_modifyGraph_attackseq.txt","")

        graph_path = "C:/Users/Zachary/Documents/A2MalwareStructuralAttack/results/apk/malscan/2011/" + sha256 + "_testGraph.txt"
        node_path = "C:/Users/Zachary/Documents/A2MalwareStructuralAttack/results/apk/malscan/2011/" + sha256 + "_testNodes.txt"
        if not os.path.exists(graph_path) or not os.path.exists(node_path):
            continue
        # feature = getMalscanFeature(node_path, graph_path)
        try:
            feature = getMalscanFeature(node_path, graph_path)
        except Exception:
            print(Exception)
        new_feature_set.append(feature)

    new_label = np.zeros((len(new_feature_set), 1))
    results = []
    results = []
    for zi in range(10):
        cv_train, cv_test, cv_y_train, cv_sy_test = train_test_split(
            new_feature_set, new_label, test_size=0.5, random_state=zi)
        cv_train = np.squeeze(np.array(cv_train))
        cv_test = np.squeeze(np.array(cv_test))
        data_new = np.append(X_train, cv_train, axis=0)
        label_new = np.append(y_train, cv_y_train)

        clf = KNeighborsClassifier(n_neighbors=1)
        clf.fit(np.squeeze(data_new), label_new)
        y_pred = clf.predict(cv_test)
        y_pred = list(y_pred)
        results.append([y_pred.count(0.0), y_pred.count(1.0)])
        print(accuracy_score(y_true=cv_sy_test, y_pred=y_pred))
    print(results)




