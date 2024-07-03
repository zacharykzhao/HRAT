import os
import pickle


def get_test_data_size(data_File):
    f = open(data_File, 'rb')
    test_data = pickle.load(f)
    f.close()
    data_size = len(test_data['sha256'])
    return data_size


def get_adv_size(data_folder):
    adv_num = 0
    for i in os.listdir(data_folder):
        if i.endswith('.apk'):
            adv_num += 1
    return adv_num


if __name__ == '__main__':
    #
    HACK_malscan_modify_seq = './HACK/APK_modification_seq/Malscan'
    HACK_malscan_adv = './HACK/apk/Malscan'
    #
    EPACK_malscan_modify_seq = './EPACK/APK_modification_seq/Malscan'
    EPACK_malscan_adv = './EPACK/apk/Malscan'
    EPACK_mamadroid_modify_seq = './EPACK/APK_modification_seq/mamadroid'
    EPACK_mamadroid_adv = './EPACK/apk/mamadroid'
    #
    SACK_malscan_modify_seq = './SACK/APK_modification_seq/Malscan'
    SACK_malscan_adv = './SACK/apk/Malscan'
    SACK_mamadroid_modify_seq = './SACK/APK_modification_seq/mamadroid'
    SACK_mamadroid_adv = './SACK/apk/mamadroid'
    #h
    SACK_malscan_test_size = 1759
    SACK_mamadroid_test_size = 1838
    HACK_malscan_test_size = 500
    EPACK_malscan_test_size = 338
    EPACK_mamadroid_test_size = 500
    #
    SACK_malscan_seq_num = len(os.listdir(SACK_malscan_modify_seq))
    Init_ASR_Malscan_SACK = SACK_malscan_seq_num / SACK_malscan_test_size
    Rela_ASR_Malscan_SACK = get_adv_size(SACK_malscan_adv) / SACK_malscan_seq_num
    #
    SACK_mamadroid_seq_num = len(os.listdir(SACK_mamadroid_modify_seq))
    Init_ASR_Mamadroid_SACK = SACK_mamadroid_seq_num / SACK_mamadroid_test_size
    Rela_ASR_Mamadroid_SACK = get_adv_size(SACK_mamadroid_adv) / SACK_mamadroid_seq_num
    #
    HACK_malscan_seq_num = len(os.listdir(HACK_malscan_modify_seq))
    Init_ASR_Malscan_HACK = HACK_malscan_seq_num / HACK_malscan_test_size
    Rela_ASR_Malscan_HACK = get_adv_size(HACK_malscan_adv) / HACK_malscan_seq_num

    #
    EPACK_malscan_seq_num = len(os.listdir(EPACK_malscan_modify_seq))
    Init_ASR_Malscan_EPACK = EPACK_malscan_seq_num / EPACK_malscan_test_size
    Rela_ASR_Malscan_EPACK = get_adv_size(EPACK_malscan_adv) / EPACK_malscan_seq_num
    #
    EPACK_mamadroid_seq_num = len(os.listdir(EPACK_mamadroid_modify_seq))
    Init_ASR_Mamadroid_EPACK = EPACK_mamadroid_seq_num / EPACK_mamadroid_test_size
    Rela_ASR_Mamadroid_EPACK = get_adv_size(EPACK_mamadroid_adv) / EPACK_mamadroid_seq_num

    #
    print('System \t Algorithm \t Init ASR \t Rela ASR ')
    print('Malscan \t SACK \t %.4f \t %.4f' % (Init_ASR_Malscan_SACK, Rela_ASR_Malscan_SACK))
    print('Malscan \t HACK \t %.4f \t %.4f' % (Init_ASR_Malscan_HACK, Rela_ASR_Malscan_HACK))
    print('Malscan \t EPCAK \t %.4f \t %.4f' % (Init_ASR_Malscan_EPACK, Rela_ASR_Malscan_EPACK))
    print('Mamadroid \t SACK \t %.4f \t %.4f' % (Init_ASR_Mamadroid_SACK, Rela_ASR_Mamadroid_SACK))
    print('Mamadroid \t EPCAK \t %.4f \t %.4f' % (Init_ASR_Mamadroid_EPACK, Rela_ASR_Mamadroid_EPACK))
