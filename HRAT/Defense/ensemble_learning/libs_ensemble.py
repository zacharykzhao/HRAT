# -*- coding:utf-8 -*-
# Author: Kaifa Zachary ZHAO
# Date: 7/28/2021
import pickle
import numpy as np
import os


def load_train(data_path):
    df = open(data_path, "rb")
    data = pickle.load(df)
    X_train = np.array(data["data"])
    y_train = np.array(data["label"])
    return X_train, y_train


def load_test(data_path, compare=False, fea_num=0):
    feature = []
    for zi in os.listdir(data_path):
        if not zi.__contains__("feature"):
            continue
        file1 = data_path + "/" + zi
        a = open(file1, 'r')
        a = a.readlines()
        a = a[0].replace("[", "").replace("]", "")
        a = a.split(",")
        # if len(a) < 40000:
        #     continue
        d1 = [float(i) for i in a]
        if compare:
            if len(d1) != fea_num:
                continue
        d1 = np.array(d1)[:, np.newaxis].transpose()
        feature.append(d1)
    return feature