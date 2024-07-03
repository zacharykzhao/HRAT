# -*- coding:utf-8 -*-
# Author: Kaifa Zachary ZHAO
# Date: 11/18/2021
import argparse
import os


def check_folder(folder_name):
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Extract function call graph, node list and node constraints from APK files.')
    parser.add_argument('--apk_path', type=str, help="The path of folder containing APK files to be processed.")
    parser.add_argument('--output_path', type=str, help="The path to store parse results.")
    return parser.parse_args()


def main_preprocess_APK(args):
    if type(args) is argparse.Namespace:
        apk_path = args.apk_path
        output_path = args.output_path
    elif args is None:
        apk_path = "demo/apk"
        output_path = "demo/apk_parse_results"
    else:
        apk_path = args[0]
        output_path = args[1]
    check_folder(apk_path)
    check_folder(output_path)
    for sha256 in os.listdir(apk_path):
        if sha256.startswith('.'):
            continue
        print(sha256)
        if not sha256.endswith(".apk"):
            tmp = ["", ""]
            tmp[0] = apk_path + '/' + sha256
            tmp[1] = output_path + '/' + sha256
            main_preprocess_APK(tmp)
        else:
            apk_file = apk_path + '/' + sha256
            print(apk_file)
            print(output_path)
            os.popen(
                "java -jar ./libs/PreprocessAPK.jar %s %s" % (apk_file, output_path)).readlines()


if __name__ == '__main__':
    global args
    args = parse_args()
    main_preprocess_APK(args)
