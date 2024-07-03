import os
import re


def alg2apk(sha256, file_path, node_path, save_path, fPrint=True):
    modification_record = file_path + "/" + sha256
    sha256 = sha256.replace("action_list0.txt", "")
    node_file = node_path + "/" + sha256 + ".txt"

    tmp = open(node_file, "r", encoding='utf-8').readlines()
    node_list = [a.replace("\n", "") for a in tmp]

    modification = []

    f = open(modification_record, "r")
    az = f.readline()

    add_count = 0
    cur_m = 0
    while az:
        cur_m += 1
        print("current ", cur_m)
        if az.__contains__("array([["):
            az = az.replace("array([[", "")
            az = az.replace("]])", "")
        tmp = re.findall(r"\[(.*?)\]", az)
        if len(tmp) > 0:
            t = tmp[0].split(",")
            type = int(t[0])

            if type == 0:
                # add_edge
                beg = int(t[2])
                tar = int(t[3])
                modification.append("add_edge,:" + node_list[beg] + " ==> " + node_list[tar])
                if fPrint:
                    print("add_edge,:" + node_list[beg] + " ==> " + node_list[tar] + "\n\t node length:" + str(
                        len(node_list)))
            elif type == 1:
                # delete_dedge
                beg = int(t[1])
                end = int(t[2])
                mid = int(t[3])
                modification.append("delete_edge,:" + node_list[beg] + " ==> "
                                    + node_list[end] + " ==> "
                                    + node_list[mid])
                if fPrint:
                    print("delete_edge,:" + node_list[beg] + " ==> "
                          + node_list[end] + " \n\tmid node "
                          + node_list[mid] + "\n\t node length:" + str(len(node_list)))
            elif type == 2:
                # add_node
                caller = int(t[1])
                new_node_id = add_count
                modification.append("add_node,:" + node_list[caller] + " ==> "
                                    + str(new_node_id))
                add_count += 1

                node_list.append(str(new_node_id))
                if fPrint:
                    print("add_node,:" + node_list[caller] + " ==> "
                          + str(new_node_id) + "\n\t node length:" + str(len(node_list)))
            elif type == 3:
                # delete_node
                target = int(t[-1])
                if target == -1:
                    az = f.readline()
                    continue
                modification.append("delete_node,:" + node_list[target])

                if fPrint:
                    print("delete_node,:" + node_list[target] + "\n\t node length:" + str(len(node_list)))
                del node_list[target]

        az = f.readline()

    file_name = save_path + "/" + sha256 + "_modifyGraph_attackseq.txt"
    f1 = open(file_name, "w", encoding='utf-8')

    for i in modification:
        f1.write(i)
        f1.write('\n')


if __name__ == '__main__':

    graph_modification_path = 'path_to_graph_modification_sequence_generated_by_HRAT'
    node_path = 'path to app node list, e.g., ./PreprocessAPK/demo/apk_parse_results/malware/nodes'
    graph_path = 'path to app graph list, e.g., ./PreprocessAPK/demo/apk_parse_results/malware/graph'
    save_path = 'path_to_save_app_methods_modification_sequence'
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    tmp_r = os.listdir(graph_modification_path)

    for r2 in tmp_r:
        if r2.startswith('final_feature') or r2.startswith('final_graph'):
            continue
        node_date = '18train'

        alg2apk(r2, graph_modification_path, node_path, save_path, fPrint=True)
