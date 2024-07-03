import os
import shutil


def parse_method_sig(method_soot_sig):
    sig = method_soot_sig.replace('<', '').replace('>', '')
    pkg = sig.split(':')[0].split('.')
    method_name = sig.split(' ')[2].split('(')[0]
    results = {
        'package_name': pkg,
        'method_name': method_name
    }
    return results


def parse_modify_seq(modify_file):
    f = open(modify_file, 'r')
    tmp = f.readlines()
    f.close()
    results = {}
    for i in tmp:
        i = i.replace('\n', '')
        action_type = i.split(',')[0]
        if action_type == 'delete_edge':
            if action_type not in results:
                results[action_type] = []
            tmp1 = i.split(',:')[1]
            tmp1 = tmp1.split(' ==> ')
            caller = tmp1[0]
            callee = tmp1[1]
            mid = tmp1[2]
            results[action_type].append([caller, callee, mid])

        elif action_type == 'add_node':
            if action_type not in results:
                results[action_type] = []
            tmp1 = i.split(',:')[1]
            tmp1 = tmp1.split(' ==> ')
            caller = tmp1[0]
            new_node = tmp1[1]
            results[action_type].append([caller, new_node])

        elif action_type == 'add_edge':
            if action_type not in results:
                results[action_type] = []
            tmp1 = i.split(',:')[1]
            tmp1 = tmp1.split(' ==> ')
            caller = tmp1[0]
            callee = tmp1[1]
            results[action_type].append([caller, callee])

        elif action_type == 'delete_node':
            if action_type not in results:
                results[action_type] = []
            tmp1 = i.split(',:')[1]
            target_method = tmp1.strip()
            results[action_type].append([target_method])
    return results


def clear_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)


def reverse_single_apk(adv_apk, raw_apk, results_folder):
    adv_ra_folder = os.path.join(results_folder, "adv_apk")
    raw_ra_folder = os.path.join(results_folder, "raw_apk")
    clear_folder(adv_ra_folder)
    clear_folder(raw_ra_folder)
    # parsing adv apk
    apktool_cmd = f"apktool d {adv_apk} -o {adv_ra_folder}"
    p_ac_adv = os.system(apktool_cmd)
    # if LOG_DEBUG:
    #     print("parsing adv apk: \n\t" + p_ac_adv)
    # parsing raw apk
    apktool_cmd = f"apktool d {raw_apk} -o {raw_ra_folder}"
    p_ac_raw = os.system(apktool_cmd)
    # if LOG_DEBUG:
    #     print("parsing raw apk: \n\t" + p_ac_raw)
    #


def find_target_method(code_file, method_name):
    with open(code_file, 'r') as f:
        code_list = f.readlines()
    for code in code_list:
        if method_name + '(' in code:
            return False
    return True


def get_invoke_stmt(code_file, caller_method, callee_method):
    with open(code_file, 'r') as f:
        code_list = f.readlines()
    # /Users/fkd/Documents/Code/AdvApkChecker/reverse_results/adv_apk/smali/com/waps/AppConnect.smali
    caller_idx = -1
    caller_stmt = ''
    callee_idx = -1
    callee_stmt = ''
    for idx, code in enumerate(code_list):
        if caller_method + '(' in code:
            caller_idx, caller_stmt = idx, code
        if callee_method + '(' in code:
            callee_idx, callee_stmt = idx, code
        if callee_idx != -1 and caller_idx != -1:
            break
    return caller_idx, caller_stmt, callee_idx, callee_stmt


def get_method_file(method_sig, results_folder):
    method_path = os.path.join(results_folder, 'adv_apk/smali', '/'.join(method_sig['package_name'][:-1]))
    method_file = os.path.join(method_path, method_sig['package_name'][-1] + '.smali')
    return method_file


def statistic_check(adv_apk_file, raw_apk_file, modify_seq_file):
    modify_seq = parse_modify_seq(modify_seq_file)
    results_folder = './reverse_results'
    #
    reverse_single_apk(adv_apk_file, raw_apk_file, results_folder)
    for ms in modify_seq:
        for cur_seq in modify_seq[ms]:
            if ms == 'add_node':
                caller = cur_seq[0]
                added_node = cur_seq[1]
                callee = 'zkf' + str(added_node)
                package = caller.split(':')[0].replace('<', '')
                pkg_path = package.split('.')
                caller_path = os.path.join(results_folder, 'adv_apk/smali', '/'.join(pkg_path[:-1]))
                caller_file = os.path.join(caller_path, pkg_path[-1] + '.smali')
                caller_idx, caller_stmt, callee_idx, callee_stmt = get_invoke_stmt(caller_file, caller, callee)
                if callee_idx == -1:
                    return False
            elif ms == "add_edge":
                caller = parse_method_sig(cur_seq[0])
                callee = parse_method_sig(cur_seq[1])
                caller_file = get_method_file(caller, results_folder)
                caller_idx, caller_stmt, callee_idx, callee_stmt = get_invoke_stmt(caller_file, caller['method_name'],
                                                                                   callee['method_name'])
                if caller_idx == -1 or callee_idx == -1:
                    return False
            elif ms == 'delete_edge':  # rewiring
                caller = parse_method_sig(cur_seq[0])
                callee = parse_method_sig(cur_seq[1])
                mid_mtd = parse_method_sig(cur_seq[2])
                caller_file = get_method_file(caller, results_folder)
                mid_mtd_file = get_method_file(mid_mtd, results_folder)
                caller_idx, caller_stmt, caller_mid_idx, caller_mid_stmt = get_invoke_stmt(caller_file,
                                                                                           caller['method_name'],
                                                                                           mid_mtd['method_name'])
                mid_idx, mid_stmt, callee_idx, callee_stmt = get_invoke_stmt(mid_mtd_file, mid_mtd['method_name'],
                                                                             callee['method_name'])
                if caller_idx == -1 or caller_mid_idx == -1 or callee_idx == -1 or mid_idx == -1:
                    return False
            elif ms == 'delete_node':
                mtd = parse_method_sig(cur_seq[0])
                mtd_file = get_method_file(mtd, results_folder)
                print(os.path.exists(mtd_file))
                deleted = find_target_method(mtd_file, mtd['method_name'])
                if not deleted:
                    return False
    return True


if __name__ == '__main__':

    adv_apk_path = './adv_apk'
    raw_apk_path = './raw_apk'
    mod_seq_path = './mod_seq'

    for mod_type in os.listdir(adv_apk_path):
        if '.DS_Store' in mod_type:
            continue
        path_1 = os.path.join(adv_apk_path, mod_type)
        for apk_sha in os.listdir(path_1):
            if apk_sha.endswith('.apk'):
                sha_256 = apk_sha.split('.')[0]
                #
                seq_file = os.path.join(mod_seq_path, mod_type, sha_256 + '.txt')

                adv_apk = os.path.join(adv_apk_path, mod_type, apk_sha)
                raw_apk = os.path.join(raw_apk_path, apk_sha)
                print(adv_apk)
                pass_check = statistic_check(adv_apk, raw_apk, seq_file)
                if pass_check:
                    print(f'{sha_256} pass check {seq_file}')
                else:
                    print(f'{sha_256} fail check')