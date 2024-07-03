import os

VERIFY_APK_SIGN = True


def generate_signer_key():
    key_name = "test"
    key_path = "./test.keystore"
    gs_cmd = f"keytool -genkeypair -alias {key_name} -keyalg RSA -validity 400 -keystore {key_path}"
    p_cmd = os.system(gs_cmd)
    print(p_cmd)


if __name__ == '__main__':
    # pw for polyuDev.keystore : 123456
    apk_name = '4FBA3B8996A5D6DAD85350EB506CBBDBE28A3CF0AA162F1DC2218BABE4535382'
    target_apk = f"/Volumes/Data/RQ5/dynamictest/test_apk/{apk_name}.apk"
    if not os.path.exists("signed_apk_test"):
        os.mkdir("signed_apk_test")
    output_apk = f"signed_apk_test/{apk_name}.apk"
    keystore_file = "polyuDev.keystore"
    ks_pw = "123456"
    #
    if not os.path.exists(keystore_file):
        generate_signer_key()
    #
    apk_signer_command = f"./apksigner sign -ks {keystore_file} -ks-key-alias polyuDev -key-pass pass:{ks_pw} " \
                         f"-ks-pass pass:{ks_pw} -out {output_apk} {target_apk}"

    p = os.system(apk_signer_command)
    print(p)
    if VERIFY_APK_SIGN:
        verify_cmd = f"./apksigner verify -v {output_apk}"
        # verify_cmd = f"apksigner verify -v {output_apk}"
        pv = os.system(verify_cmd)
        print(pv)

