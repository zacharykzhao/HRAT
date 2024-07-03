# -*- coding:utf-8 -*-
# Author: Kaifa Zachary ZHAO
# Date: 7/28/2021

import numpy as np
from sklearn.ensemble import BaggingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn import svm
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import VotingClassifier
from sklearn import tree
from sklearn.metrics import accuracy_score

from libs_ensemble import load_train, load_test

"""
    Evaluate defense performance with ensemble learning
    1. bagging ensemble learning with multiple knn
    2. bagging ensemble learning with knn, svm, dt
    3. voting: knn, dt, svm
"""

if __name__ == '__main__':
    # load training data set
    ori_train = "C:/Users/Zachary/OneDrive - The Hong Kong Polytechnic University/Code/" \
                "myattack_QL_mac_mamadroid/preprocess/train_csr_dict_families.pkl"
    X_train, y_train = load_train(ori_train)

    # load testing data set
    # featrue_file = "C:/Users/Zachary/Documents/A2MalwareStructuralAttack/results/" \
    #                "mamadroid_families/actionseq2012"
    featrue_file = "C:/Users/Zachary/Documents/A2MalwareStructuralAttack/results/" \
                   "mamadroid_families/actions_withConstraintsMain_new"

    X_test = load_test(featrue_file)
    X_test = np.squeeze(X_test)
    y_test = np.ones((len(X_test), 1))

    # original 1NN classifier
    clf_knn_ori = KNeighborsClassifier(n_neighbors=1)
    clf_knn_ori.fit(X_train, y_train)

    # bagging -- knn
    bagging_knn = BaggingClassifier(KNeighborsClassifier(n_neighbors=1),
                                    max_samples=0.5, max_features=0.5)
    bagging_knn.fit(X_train, y_train)

    # adaboost
    adaboost_clf = AdaBoostClassifier(n_estimators=100)
    # scores = cross_val_score(adaboost_clf, X_train, y_train, cv=5)
    # print("adaboost:", scores.mean())
    adaboost_clf.fit(X_train, y_train)

    # gradient boosting
    grad_boosting_clf = GradientBoostingClassifier(n_estimators=100, learning_rate=1.0,
                                                   max_depth=1, random_state=0).fit(X_train, y_train)
    # scores = cross_val_score(grad_boosting_clf, X_train, y_train, cv=5)
    # print("gradient boosting:", scores.mean())

    # voting
    clf_svm = svm.SVC()
    clf_knn = KNeighborsClassifier(n_neighbors=1)
    clf_dt = tree.DecisionTreeClassifier()

    eclf = VotingClassifier(
        estimators=[('svm', clf_svm), ('knn', clf_knn), ('dt', clf_dt)],
        voting='hard')

    # for clf, label in zip([clf_svm, clf_knn, clf_dt, eclf],
    #                       ['Support Vector Machine', 'k-Nearest Neighbors', 'Decision Tree', 'Ensemble']):
    #     scores = cross_val_score(clf, X_train, y_train, scoring='accuracy', cv=5)
    #     print("Accuracy: %0.2f (+/- %0.2f) [%s]" % (scores.mean(), scores.std(), label))
    eclf.fit(X_train, y_train)

    # evaluate
    pred_ori = clf_knn_ori.predict(X_test)
    pred_bagging_knn = bagging_knn.predict(X_test)
    pred_adaboost = adaboost_clf.predict(X_test)
    pred_grad_boosting = grad_boosting_clf.predict(X_test)
    pred_voting = eclf.predict(X_test)

    score_ori = accuracy_score(y_true=y_test, y_pred=pred_ori)
    score_bagging_knn = accuracy_score(y_true=y_test, y_pred=pred_bagging_knn)
    score_adaboost = accuracy_score(y_true=y_test, y_pred=pred_adaboost)
    score_grad_boosting = accuracy_score(y_true=y_test, y_pred=pred_grad_boosting)
    score_voting = accuracy_score(y_true=y_test, y_pred=pred_voting)

    print(" original: \t %.4f \n bagging: \t %.4f \n adaboost: \t %.4f \n grad boosting: \t %.4f \n"
          " voting: \t %.4f \n" % (score_ori, score_bagging_knn, score_adaboost, score_grad_boosting, score_voting))
