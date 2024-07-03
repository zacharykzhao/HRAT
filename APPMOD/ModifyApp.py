import os

if __name__ == '__main__':
    app_modification_sequence_path = "path_to_save_app_methods_modification_sequence"
    raw_apk_path = 'path to raw malware *.apk'
    save_path = "path_to_save_modified adversarial apps"
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    for seq in os.listdir(app_modification_sequence_path):

        if seq.__contains__("feature"):
            continue
        sha256 = seq.split("_")[0]
        print(sha256)
        command_to_modify_app = os.popen(
            "java -jar ./modifyAPKBatch.jar %s %s %s %s %s" % (
            sha256, app_modification_sequence_path, app_modification_sequence_path,
            raw_apk_path, app_modification_sequence_path)).readlines()
        print(command_to_modify_app)
