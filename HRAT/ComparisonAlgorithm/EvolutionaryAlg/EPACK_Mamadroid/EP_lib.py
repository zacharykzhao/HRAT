# -*- coding:utf-8 -*-
# Author: Kaifa Zachary ZHAO
# Date: 8/13/2021


import random


def random_generation(action_num):
    cur_gen = []
    for i in range(action_num):
        cur_gen.append(random.random())
    return cur_gen