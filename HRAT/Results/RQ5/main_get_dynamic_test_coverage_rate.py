import os
import subprocess

from main_monkey_test import aapt_path


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


def get_log(log_file):
    with open(log_file, 'r') as f:
        mylog = f.readlines()
    return mylog


def get_method_keys(mtd):
    a = []
    if len(mtd['package_name']) > 2:
        a.append('.'.join(mtd['package_name'][:-2]))
    else:
        a.append('.'.join(mtd['package_name']))
    a.append(mtd['method_name'] + '(')
    for n in ['com', 'android', 'app', 'Activity']:
        if n in a:
            a.remove(n)
    return a


def parse_mod_sequence(mod_seq):
    mylist = []
    for ms in mod_seq:
        for cur_seq in modify_seq[ms]:
            if ms == 'add_node':
                caller = cur_seq[0]
                added_node = cur_seq[1]
                callee = 'zkf' + str(added_node)
                caller = parse_method_sig(caller)
                mylist.extend(get_method_keys(caller))
            elif ms == "add_edge":
                caller = parse_method_sig(cur_seq[0])
                callee = parse_method_sig(cur_seq[1])
                mylist.extend(get_method_keys(caller))
                mylist.extend(get_method_keys(callee))
            elif ms == 'delete_edge':  # rewiring
                caller = parse_method_sig(cur_seq[0])
                callee = parse_method_sig(cur_seq[1])
                mid_mtd = parse_method_sig(cur_seq[2])
                mylist.extend(get_method_keys(caller))
                mylist.extend(get_method_keys(callee))
                mylist.extend(get_method_keys(mid_mtd))
            elif ms == 'delete_node':
                mtd = parse_method_sig(cur_seq[0])
                mylist.extend(get_method_keys(mtd))
    return mylist


def get_coverage_rate(logs, mod_seq, pkg):
    mod_list = parse_mod_sequence(mod_seq)
    c = 0
    r = 0
    for l in logs:
        if pkg.lower() in l.lower():
            c += 1
            for j in mod_list:
                if j in l.lower():
                    r += 1
    if c == 0:
        return 0
    return r / c


if __name__ == '__main__':
    adv_apk_path = './adv_apk'
    mod_seq_path = './mod_seq'

    apk_num = 0
    cr_sta = 0
    for mod_type in os.listdir(adv_apk_path):
        if '.DS_Store' in mod_type:
            continue
        path_1 = os.path.join(adv_apk_path, mod_type)
        for apk_sha in os.listdir(path_1):
            if apk_sha.endswith('.apk'):
                sha_256 = apk_sha.split('.')[0]
                #
                seq_file = os.path.join(mod_seq_path, mod_type, sha_256 + '.txt')
                if not os.path.exists(seq_file):
                    continue
                modify_seq = parse_modify_seq(seq_file)
                apk_file = os.path.join(adv_apk_path, mod_type, apk_sha)

                adv_log_file = f'./logs/{sha_256}adv.log'
                if not os.path.exists(adv_log_file):
                    continue
                package_name_cmd = aapt_path + ' dump badging ' + apk_file + ' | awk \'/package/{gsub("name=","",$2); print $2}\''
                package_name = \
                    subprocess.check_output(package_name_cmd, shell=True).decode('utf-8').strip().strip('\'').split(
                        '.')[-1]
                adv_log = get_log(adv_log_file)
                cr = get_coverage_rate(adv_log, modify_seq, package_name)
                apk_num += 1
                cr_sta += cr
    print(cr_sta / apk_num)
