import ntpath
import os

VERIFY_APK_SIGN = True
LOCAL_SIGNER = dict(
    keystore="polyuDev.keystore",
    password="123456",
    key_alias="polyuDev"
)


def sign_single_apk(raw_apk, output_apk):
    keystore_file = LOCAL_SIGNER["keystore"]
    ks_pw = LOCAL_SIGNER["password"]
    alias_name = LOCAL_SIGNER["key_alias"]
    apk_signer_command = f"./apksigner sign -ks {keystore_file} -ks-key-alias {alias_name} -key-pass pass:{ks_pw} -ks-pass pass:{ks_pw} -out {output_apk} {raw_apk}"
    p = os.system(apk_signer_command)
    print(p)
    if VERIFY_APK_SIGN:
        verify_cmd = f"./apksigner verify -v {output_apk}"
        pv = os.system(verify_cmd)
        print(pv)


def sign_apks(apk_folder, output_folder):
    for i in os.listdir(apk_folder):
        cur_file = os.path.join(apk_folder, i)
        if os.path.isfile(cur_file) and i.endswith('.apk'):
            out_put_file = os.path.join(output_folder, i)
            print(f"signing {cur_file} ==> \n\t\t {out_put_file}")
            sign_single_apk(cur_file, out_put_file)
        elif os.path.isdir(cur_file):
            sign_apks(cur_file, output_folder)


if __name__ == '__main__':
    # please try to run sign_apk.py first
    adv_apk_folder = "./adv_apk"
    output_path = "signed_apk"
    if not os.path.exists(output_path):
        os.mkdir(output_path)

    sign_apks(adv_apk_folder, output_path)
