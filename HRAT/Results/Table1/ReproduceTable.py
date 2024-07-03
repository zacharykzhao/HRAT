import os
import pickle

'''
Please download the intermediate results from:
'''


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
    # Data
    test_malscan_o_file_malscan = '../IntermediateResults/test_csr_dict_malscan_TEo.pkl'
    test_malscan_1_file_malscan = '../IntermediateResults/test_csr_dict_malscan_TE1.pkl'
    test_malscan_2_file_malscan = '../IntermediateResults/test_csr_dict_malscan_TR2_TEo.pkl'
    #
    test_mamadroid_1_file = '../IntermediateResults/test_csr_dict_mamadroid_TE1.pkl'
    test_mamadroid_2_file = '../IntermediateResults/test_csr_dict_mamadroid_TE2.pkl'
    #
    test_apigraph_1_file = '../IntermediateResults/test_csr_dict_APIGraph_TE1.pkl'

    #
    ### Results
    # modify seq
    malscan_modify_seq_o = './modifySeq/malscan/TEo'
    malscan_modify_seq_1 = './modifySeq/malscan/TE1'
    malscan_modify_seq_TR2_TE1 = './modifySeq/malscan/TR2_TE1'
    #
    APIGraph_modify_seq_o = './modifySeq/malscan_enhanced/TEo'
    APIGraph_modify_seq_1 = './modifySeq/malscan_enhanced/TE1'
    #
    mamadroid_modify_seq_o = './modifySeq/mamadroid_families/TEo'
    mamadroid_modify_seq_1 = './modifySeq/mamadroid_families/TE1'
    mamadroid_modify_seq_2 = './modifySeq/mamadroid_families/TE2'
    # adv apk
    malscan_adv_apk_o = './advAPK/malscan/TEo'
    malscan_adv_apk_1 = './advAPK/malscan/TE1'
    malscan_adv_apk_2 = './advAPK/malscan/TR2_TE1'
    #
    APIgraph_adv_apk_o = './advAPK/malscan_enhanced/TEo'
    APIgraph_adv_apk_1 = './advAPK/malscan_enhanced/TE1'
    #
    mamadroid_adv_apk_o = './advAPK/mamadroid_families/TEo'
    mamadroid_adv_apk_1 = './advAPK/mamadroid_families/TE1'
    mamadroid_adv_apk_2 = './advAPK/mamadroid_families/TE2'

    ####
    ## get datasize
    malscan_TEo_size = get_test_data_size(test_malscan_o_file_malscan)
    malscan_TE1_size = get_test_data_size(test_malscan_1_file_malscan)
    malscan_TE2_size = get_test_data_size(test_malscan_2_file_malscan)
    #
    # mamadroid_TEo_size = get_test_data_size(test_mamadroid_o_file)
    mamadroid_TE1_size = get_test_data_size(test_mamadroid_1_file)
    mamadroid_TE2_size = get_test_data_size(test_mamadroid_2_file)
    #
    APIGraph_TE1_size = get_test_data_size(test_apigraph_1_file)

    #
    Init_ASR_Malscan_TRo_TEo = len(os.listdir(malscan_modify_seq_o)) / malscan_TEo_size
    Init_ASR_Malscan_TRo_TE1 = len(os.listdir(malscan_modify_seq_1)) / malscan_TE1_size
    Init_ASR_Malscan_TR2_TEo = len(os.listdir(malscan_modify_seq_TR2_TE1)) / malscan_TEo_size
    #
    Rela_ASR_Malscan_TRo_TEo = get_adv_size(malscan_adv_apk_o) / len(os.listdir(malscan_modify_seq_o))
    Rela_ASR_Malscan_TRo_TE1 = get_adv_size(malscan_adv_apk_1) / len(os.listdir(malscan_modify_seq_1))
    Rela_ASR_Malscan_TR2_TEo = get_adv_size(malscan_adv_apk_2) / len(os.listdir(malscan_modify_seq_TR2_TE1))
    #
    Init_ASR_APIGraph_TE1 = len(os.listdir(APIGraph_modify_seq_1)) / APIGraph_TE1_size
    #
    Rela_ASR_APIGraph_TEo = get_adv_size(APIgraph_adv_apk_o) / len(os.listdir(APIGraph_modify_seq_o))
    Rela_ASR_APIGraph_TE1 = get_adv_size(APIgraph_adv_apk_1) / len(os.listdir(APIGraph_modify_seq_1))
    #
    # Init_ASR_Mamadroid_TEo = len(os.listdir(mamadroid_modify_seq_o)) / mamadroid_TEo_size
    Init_ASR_Mamadroid_TE1 = len(os.listdir(mamadroid_modify_seq_1)) / mamadroid_TE1_size
    Init_ASR_Mamadroid_TE2 = len(os.listdir(mamadroid_modify_seq_2)) / mamadroid_TE2_size
    #
    Rela_ASR_Mamadroid_TEo = get_adv_size(mamadroid_adv_apk_o) / len(os.listdir(mamadroid_modify_seq_o))
    Rela_ASR_Mamadroid_TE1 = get_adv_size(mamadroid_adv_apk_1) / len(os.listdir(mamadroid_modify_seq_1))
    Rela_ASR_Mamadroid_TE2 = get_adv_size(mamadroid_adv_apk_2) / len(os.listdir(mamadroid_modify_seq_2))

    #

    print('Algorithm \t\t Training \t\t Testing \t Init ASR \t Rela ASR')
    print('Malscan \t\t TRo \t\t\t TEo \t\t %.4f \t\t %.4f' % (Init_ASR_Malscan_TRo_TEo, Rela_ASR_Malscan_TRo_TEo))
    print('Malscan \t\t TRo \t\t\t TE1 \t\t %.4f \t\t %.4f' % (Init_ASR_Malscan_TRo_TE1, Rela_ASR_Malscan_TRo_TE1))
    print('Malscan \t\t TR2 \t\t\t TEo \t\t %.4f \t\t %.4f' % (Init_ASR_Malscan_TR2_TEo, Rela_ASR_Malscan_TR2_TEo))
    print('APIGraph \t\t TRo \t\t\t TEo \t\t / \t\t\t %.4f' % ( Rela_ASR_APIGraph_TEo))
    print('APIGraph \t\t TRo \t\t\t TE1 \t\t %.4f \t\t %.4f' % (Init_ASR_APIGraph_TE1, Rela_ASR_APIGraph_TE1))
    print('Mamadroid \t\t TRo \t\t\t TEo \t\t / \t\t\t %.4f' % (Rela_ASR_Mamadroid_TEo))
    print('Mamadroid \t\t TRo \t\t\t TE1 \t\t %.4f \t\t %.4f' % (Init_ASR_Mamadroid_TE1, Rela_ASR_Mamadroid_TE1))
    print('Mamadroid \t\t TRo \t\t\t TE2 \t\t %.4f \t\t %.4f' % (Init_ASR_Mamadroid_TE2, Rela_ASR_Mamadroid_TE2))
