# -*- coding:utf-8 -*-
# Author: Kaifa Zachary ZHAO
# Date: 5/14/2022
import os
import urllib
from multiprocessing.pool import ThreadPool
from functools import partial

AndroZooKey = "Put you AndroZooKey here"


def check_folder(folder_name):
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)


def download_apks(sha256, save_folder):
    sha256 = sha256.replace('\n', '')
    url = 'https://androzoo.uni.lu/api/download?apikey=' + AndroZooKey + '&sha256=' + sha256
    file_path = os.path.join(save_folder, sha256 + '.apk')
    if os.path.exists(file_path):
        print("File EXIST !!!! " + file_path)
        return
    # get_pic_by_url(save_folder, url)
    try:
        urllib.request.urlretrieve(url, file_path)
    except Exception:
        print("\t download fail:", sha256)
        return
    print(url)


if __name__ == '__main__':
    sha256_list_file = "Please input the path to downloaded sha256 list file"
    save_folder = "Please input the folder you want to save your apks"
    apk_year = "Please input the year of the apks you downloaded"
    apk_type = "Please input the type of apks, i.e., benign/malicious"

    check_folder(save_folder)
    #
    f = open(sha256_list_file, 'r')
    sha256_list = f.readlines()
    f.close()
    #
    f1 = os.path.join(save_folder, apk_year)
    check_folder(f1)
    final_save_folder = os.path.join(f1, apk_type)
    check_folder(final_save_folder)
    print(final_save_folder + '\t' + str(len(sha256_list)))
    #
    zpool = ThreadPool(15)
    zaa = zpool.map(partial(download_apks, save_folder=final_save_folder), sha256_list)
