# -*- coding: utf-8 -*-
import time
import json
from docplex.mp.model import Model


class Path:
    def __init__(self, id, source, target, seq, p1, p2, p3, delay_p1, delay_p2, delay_p3):
        self.id = id
        self.source = source
        self.target = target
        self.seq = seq
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.delay_p1 = delay_p1
        self.delay_p2 = delay_p2
        self.delay_p3 = delay_p3

    def __str__(self):
        return "ID: {}\tSEQ: {}\t P1: {}\t P2: {}\t P3: {}\t dP1: {}\t dP2: {}\t dP3: {}".format(self.id, self.seq,
                                                                                                 self.p1, self.p2,
                                                                                                 self.p3, self.delay_p1,
                                                                                                 self.delay_p2,
                                                                                                 self.delay_p3)


class CR:
    def __init__(self, id, cpu, num_BS):
        self.id = id
        self.cpu = cpu
        self.num_BS = num_BS
        # self.ram = ram

    def __str__(self):
        return "ID: {}\tCPU: {}".format(self.id, self.cpu)


class DRC:
    def __init__(self, id, cpu_CU, cpu_DU, cpu_RU, ram_CU, ram_DU, ram_RU, Fs_CU, Fs_DU, Fs_RU, delay_BH, delay_MH,
                 delay_FH, bw_BH, bw_MH, bw_FH, q_CRs):
        self.id = id

        self.cpu_CU = cpu_CU
        self.ram_CU = ram_CU
        self.Fs_CU = Fs_CU

        self.cpu_DU = cpu_DU
        self.ram_DU = ram_DU
        self.Fs_DU = Fs_DU

        self.cpu_RU = cpu_RU
        self.ram_RU = ram_RU
        self.Fs_RU = Fs_RU

        self.delay_BH = delay_BH
        self.delay_MH = delay_MH
        self.delay_FH = delay_FH

        self.bw_BH = bw_BH
        self.bw_MH = bw_MH
        self.bw_FH = bw_FH

        self.q_CRs = q_CRs


class FS:
    def __init__(self, id, f_cpu, f_ram):
        self.id = id
        self.f_cpu = f_cpu
        self.f_ram = f_ram


class RU:
    def __init__(self, id, CR):
        self.id = id
        self.CR = CR

    def __str__(self):
        return "RU: {}\tCR: {}".format(self.id, self.CR)


# Global vars
links = []
capacity = {}
delay = {}
crs = {}
paths = {}
conj_Fs = {}


def read_topology():
    with open('T2_25_links.json') as json_file:
        data = json.load(json_file)
        json_links = data["links"]
        for item in json_links:
            link = item
            source_node = link["fromNode"]
            destination_node = link["toNode"]
            if source_node < destination_node:
                capacity[(source_node, destination_node)] = link["capacity"]
                delay[(source_node, destination_node)] = link["delay"]
                links.append((source_node, destination_node))
                # ADD THIS CODE FOR T1 TOPOLOGY
                # capacity[(destination_node, source_node)] = link["capacity"]
                # delay[(destination_node, source_node)] = link["delay"]
                # links.append((destination_node, source_node))
            else:
                capacity[(destination_node, source_node)] = link["capacity"]
                delay[(destination_node, source_node)] = link["delay"]
                links.append((destination_node, source_node))
                # ADD THIS CODE FOR T1 TOPOLOGY
                # capacity[(source_node, destination_node)] = link["capacity"]
                # delay[(source_node, destination_node)] = link["delay"]
                # links.append((source_node, destination_node))
        with open('T2_25_CRs.json') as json_file:
            data = json.load(json_file)
            json_nodes = data["nodes"]
            for item in json_nodes:
                node = item
                CR_id = node["nodeNumber"]
                node_CPU = node["cpu"]
                cr = CR(CR_id, node_CPU, 0)
                crs[CR_id] = cr
        crs[0] = CR(0, 0, 0)
        with open('paths.json') as json_paths_file:
            json_paths_f = json.load(json_paths_file)
            json_paths = json_paths_f["paths"]
            for item in json_paths:
                path = json_paths[item]
                path_id = path["id"]
                path_source = path["source"]
                if path_source == "CN":
                    path_source = 0
                path_target = path["target"]
                path_seq = path["seq"]
                paths_p = [path["p1"], path["p2"], path["p3"]]
                list_p1 = []
                list_p2 = []
                list_p3 = []
                for path_p in paths_p:
                    aux = ""
                    sum_delay = 0
                    for tup in path_p:
                        aux += tup
                        tup_aux = tup
                        tup_aux = tup_aux.replace('(', '')
                        tup_aux = tup_aux.replace(')', '')
                        tup_aux = tuple(map(int, tup_aux.split(', ')))
                        if path_p == path["p1"]:
                            list_p1.append(tup_aux)
                        elif path_p == path["p2"]:
                            list_p2.append(tup_aux)
                        elif path_p == path["p3"]:
                            list_p3.append(tup_aux)
                        sum_delay += delay[tup_aux]
                    if path_p == path["p1"]:
                        delay_p1 = sum_delay
                    elif path_p == path["p2"]:
                        delay_p2 = sum_delay
                    elif path_p == path["p3"]:
                        delay_p3 = sum_delay
                    if path_seq[0] == 0:
                        delay_p1 = 0
                    if path_seq[1] == 0:
                        delay_p2 = 0
                p = Path(path_id, path_source, path_target, path_seq, list_p1, list_p2, list_p3, delay_p1, delay_p2,
                         delay_p3)
                paths[path_id] = p


def DRC_structure():
    DRC1 = DRC(1, 0.49, 2.058, 2.352, 0.01, 0.01, 0.01, ['f8'], ['f7', 'f6', 'f5', 'f4', 'f3', 'f2'], ['f1', 'f0'], 10, 10, 0.25, 9.9, 13.2, 42.6, 3)
    DRC2 = DRC(2, 0.98, 1.568, 2.352, 0.01, 0.01, 0.01, ['f8', 'f7'], ['f6', 'f5', 'f4', 'f3', 'f2'], ['f1', 'f0'], 10, 10, 0.25, 9.9, 13.2, 42.6, 3)
    DRC4 = DRC(4, 0.49, 1.225, 3.185, 0.01, 0.01, 0.01, ['f8'], ['f7', 'f6', 'f5', 'f4', 'f3'], ['f2', 'f1', 'f0'], 10, 10, 0.25, 9.9, 13.2, 13.6, 3)
    DRC5 = DRC(5, 0.98, 0.735, 3.185, 0.01, 0.01, 0.01, ['f8', 'f7'], ['f6', 'f5', 'f4', 'f3'], ['f2', 'f1', 'f0'], 10, 10, 0.25, 9.9, 13.2, 13.6, 3)
    DRC6 = DRC(6, 0, 0.49, 4.41, 0, 0.01, 0.01, [0], ['f8'], ['f7', 'f6', 'f5', 'f4', 'f3', 'f2', 'f1', 'f0'], 0, 10, 10, 0, 9.9, 13.2, 2)
    DRC7 = DRC(7, 0, 3, 3.92, 0, 0.01, 0.01, [0], ['f8', 'f7'], ['f6', 'f5', 'f4', 'f3', 'f2', 'f1', 'f0'], 0, 10, 10, 0, 9.9, 13.2, 2)
    DRC8 = DRC(8, 0, 0, 4.9, 0, 0, 0.01, [0], [0], ['f8', 'f7', 'f6', 'f5', 'f4', 'f3', 'f2', 'f1', 'f0'], 0, 0, 10, 0, 0, 9.9, 1)
    DRC9 = DRC(9, 0, 2.54, 2.354, 0, 0.01, 0.01, [0], ['f8', 'f7', 'f6', 'f5', 'f4', 'f3', 'f2'], ['f1', 'f0'], 0, 10, 0.25, 0, 9.9, 42.6, 2)
    DRC10 = DRC(10, 0, 1.71, 3.185, 0, 0.01, 0.01, [0], ['f8', 'f7', 'f6', 'f5', 'f4', 'f3'], ['f2', 'f1', 'f0'], 0, 10, 0.25, 0, 3, 13.6, 2)
    DRCs = {1: DRC1, 2: DRC2, 4: DRC4, 5: DRC5, 6: DRC6, 7: DRC7, 8: DRC8, 9: DRC9, 10: DRC10}
    return DRCs

# ADD THIS CODE FOR T1 TOPOLOGY
# def DRC_structure():
#     # IMPLEMENTS T1 Topology DRCs
#     # Implements the DRCs defined with cpu usage, ram usage, VNFs splits and network resources requirements, for T1 Topology
#     # :rtype: Dict with the DRCs informations
#     # Creates the DRCs
#     # DRCs MAP (id: DRC): 1 = DRC1, 2 = DRC2, 4 = DRC7 and 5 = DRC8 -- DRCs with 3 independents CRs [CU]-[DU]-[RU]
#     DRC1 = DRC(1, 0.49, 2.058, 2.352, 0.01, 0.01, 0.01, ['f8'], ['f7', 'f6', 'f5', 'f4', 'f3', 'f2'], ['f1', 'f0'], 10, 10, 0.25, 3, 5.4, 17.4, 3)
#     DRC2 = DRC(2, 0.98, 1.568, 2.352, 0.01, 0.01, 0.01, ['f8', 'f7'], ['f6', 'f5', 'f4', 'f3', 'f2'], ['f1', 'f0'], 10, 10, 0.25, 3, 5.4, 17.4, 3)
#     DRC4 = DRC(4, 0.49, 1.225, 3.185, 0.01, 0.01, 0.01, ['f8'], ['f7', 'f6', 'f5', 'f4', 'f3'], ['f2', 'f1', 'f0'], 10, 10, 0.25, 3, 5.4, 5.6, 3)
#     DRC5 = DRC(5, 0.98, 0.735, 3.185, 0.01, 0.01, 0.01, ['f8', 'f7'], ['f6', 'f5', 'f4', 'f3'], ['f2', 'f1', 'f0'], 10, 10, 0.25, 3, 5.4, 5.6, 3)
#
#     # DRCs MAP (id: DRC): 6 = DRC12, 7 = DRC13, 9 = DRC18 and 10 = DRC17  -- DRCs with 2 CRs [CU/DU]-[RU] or [CU]-[DU/RU]
#     DRC6 = DRC(6, 0, 0.49, 4.41, 0, 0.01, 0.01, [0], ['f8'], ['f7', 'f6', 'f5', 'f4', 'f3', 'f2', 'f1', 'f0'], 0, 10, 10, 0, 3, 5.4, 2)
#     DRC7 = DRC(7, 0, 3, 3.92, 0, 0.01, 0.01, [0], ['f8', 'f7'], ['f6', 'f5', 'f4', 'f3', 'f2', 'f1', 'f0'], 0, 10, 10, 0, 3, 5.4, 2)
#     DRC9 = DRC(9, 0, 2.54, 2.354, 0, 0.01, 0.01, [0], ['f8', 'f7', 'f6', 'f5', 'f4', 'f3', 'f2'], ['f1', 'f0'], 0, 10, 0.25, 0, 3, 17.4, 2)
#     DRC10 = DRC(10, 0, 1.71, 3.185, 0, 0.01, 0.01, [0], ['f8', 'f7', 'f6', 'f5', 'f4', 'f3'], ['f2', 'f1', 'f0'], 0, 10, 0.25, 0, 3, 5.6, 2)
#
#     # DRCs MAP (id: DRC): 8 = DRC19 -- D-RAN with 1 CR [CU/DU/RU]
#     DRC8 = DRC(8, 0, 0, 4.9, 0, 0, 0.01, [0], [0], ['f8', 'f7', 'f6', 'f5', 'f4', 'f3', 'f2', 'f1', 'f0'], 0, 0, 10, 0, 0, 3, 1)
#
#     # Creates the set of DRCs
#     DRCs = {1: DRC1, 2: DRC2, 4: DRC4, 5: DRC5, 6: DRC6, 7: DRC7, 8: DRC8, 9: DRC9, 10: DRC10}
#
#     return DRCs


def RU_location():
    rus = {}
    count = 1
    with open('T2_25_CRs.json') as json_file:
        data = json.load(json_file)
        json_crs = data["nodes"]
        for item in json_crs:
            node = item
            num_rus = node["RU"]
            num_cr = node["nodeNumber"]
            for i in range(0, num_rus):
                rus[count] = RU(count, int(num_cr))
                count += 1
    return rus


DRC_f1 = 0
f1_vars = []
f2_vars = []


def run_model():
    print("Running Stage - 1")
    print("------------------------------------------------------------------------------------------------------------")
    alocation_time_start = time.time()
    read_topology()
    DRCs = DRC_structure()
    rus = RU_location()
    F1 = FS('f8', 2, 2)
    F2 = FS('f7', 2, 2)
    F3 = FS('f6', 2, 2)
    F4 = FS('f5', 2, 2)
    F5 = FS('f4', 2, 2)
    F6 = FS('f3', 2, 2)
    F7 = FS('f2', 2, 2)
    F8 = FS('f1', 2, 2)
    F9 = FS('f0', 2, 2)
    conj_Fs = {'f8': F1, 'f7': F2, 'f6': F3, 'f5': F4, 'f4': F5, 'f3': F6, 'f2': F7}
    mdl = Model(name='NGRAN Problem', log_output=True)
    mdl.parameters.mip.tolerances.mipgap = 0
    mdl.parameters.emphasis.mip = 2
    i = [(p, d, b) for p in paths for d in DRCs for b in rus if paths[p].seq[2] == rus[b].CR]
    mdl.x = mdl.binary_var_dict(keys=i, name='x')
    mdl.y = mdl.continuous_var_dict(keys=i, name='y')
    phy1 = mdl.sum(mdl.min(1, mdl.sum(mdl.x[it] for it in i if c in paths[it[0]].seq)) for c in crs if crs[c].id != 0)
    phy2 = mdl.sum(mdl.sum(mdl.max(0, mdl.sum(mdl.min(1, mdl.sum(mdl.x[it] for it in i if (
                (paths[it[0]].seq[0] == crs[c].id and it[2] == b and f in DRCs[it[1]].Fs_CU) or (
                    paths[it[0]].seq[1] == crs[c].id and it[2] == b and f in DRCs[it[1]].Fs_DU) or (
                            paths[it[0]].seq[2] == crs[c].id and it[2] == b and f in DRCs[it[1]].Fs_RU)))) for b in
                                              rus) - 1) for f in conj_Fs) for c in crs)
    mdl.minimize(phy1 - phy2)
    for b in rus:
        mdl.add_constraint(mdl.sum(mdl.x[it] for it in i if it[2] == b) >= 1, 'at least one path')
    for p in paths:
        mdl.add_constraint(mdl.sum(mdl.sum(mdl.x[it] for it in i if it[2] == b and it[0] == p) for b in rus) <= 1.0,
                           'path unicity')
    for b in rus:
        mdl.add_constraint(
            mdl.sum(mdl.min(mdl.sum(mdl.x[it] for it in i if it[2] == b and it[1] == d), 1) for d in DRCs) == 1.0, 'no duplicate DRCs to the same RU')
    for b in rus:
        mdl.add_constraint(mdl.sum(mdl.y[it] for it in i if it[2] == b) == 1.0, 'split total')
    for it in i:
        mdl.add_constraint(mdl.y[it] >= 0, 'y_var definition')
    for it in i:
        mdl.add_constraint(mdl.y[it] <= mdl.x[it], 'y_var and x_var match')
    for it in i:
        mdl.add_constraint(mdl.x[it] - mdl.y[it] <= 0.990, 'minimum split y_var')
    for b in rus:
        mdl.add_constraint(mdl.sum(
            mdl.min(1, mdl.sum(mdl.x[it] for it in i if c in paths[it[0]].seq and it[2] == b and c != 0)) for c in
            crs) == mdl.sum(mdl.y[it] * DRCs[it[1]].q_CRs for it in i if it[2] == b), 'no duplicate VNFs')
    for l in links:
        k = (l[1], l[0])
        mdl.add_constraint(mdl.sum(mdl.y[it] * DRCs[it[1]].bw_BH for it in i if l in paths[it[0]].p1 or k in paths[it[0]].p1)
                           + mdl.sum(mdl.y[it] * DRCs[it[1]].bw_MH for it in i if l in paths[it[0]].p2 or k in paths[it[0]].p2)
                           + mdl.sum(mdl.y[it] * DRCs[it[1]].bw_FH for it in i if l in paths[it[0]].p3 or k in paths[it[0]].p3)
                           <= capacity[l], 'links_bw')
    mdl.add_constraint(mdl.sum(mdl.x[it] for it in i if paths[it[0]].target != rus[it[2]].CR) == 0, 'path')
    mdl.add_constraint(mdl.sum(mdl.x[it] for it in i if paths[it[0]].seq[0] != 0 and (
            it[1] == 6 or it[1] == 7 or it[1] == 8 or it[1] == 9 or it[1] == 10)) == 0, 'DRCs_path_pick')
    mdl.add_constraint(mdl.sum(mdl.x[it] for it in i if
                               paths[it[0]].seq[0] == 0 and it[1] != 6 and it[1] != 7 and it[1] != 8 and it[
                                   1] != 9 and it[1] != 10) == 0, 'DRCs_path_pick2')
    mdl.add_constraint(
        mdl.sum(mdl.x[it] for it in i if paths[it[0]].seq[0] == 0 and paths[it[0]].seq[1] == 0 and it[1] != 8) == 0,
        'DRCs_path_pick3')
    mdl.add_constraint(
        mdl.sum(mdl.x[it] for it in i if paths[it[0]].seq[0] == 0 and paths[it[0]].seq[1] != 0 and it[1] == 8) == 0,
        'DRCs_path_pick4')
    for ru in rus:
        mdl.add_constraint(
            mdl.sum(mdl.x[it] for it in i if paths[it[0]].seq[2] != rus[ru].CR and it[2] == rus[ru].id) == 0, 'path destination')
    for it in i:
        mdl.add_constraint((mdl.x[it] * paths[it[0]].delay_p1) <= DRCs[it[1]].delay_BH, 'delay_req_p1')
    for it in i:
        mdl.add_constraint((mdl.x[it] * paths[it[0]].delay_p2) <= DRCs[it[1]].delay_MH, 'delay_req_p2')
    for it in i:
        mdl.add_constraint((mdl.x[it] * paths[it[0]].delay_p3 <= DRCs[it[1]].delay_FH), 'delay_req_p3')
    for c in crs:
        mdl.add_constraint(mdl.sum(mdl.sum(mdl.min(DRCs[D].cpu_CU, mdl.sum(mdl.x[it] * DRCs[D].cpu_CU for it in i if
                                                                           c == paths[it[0]].seq[0] and it[2] == b and
                                                                           it[1] == D)) + mdl.min(DRCs[D].cpu_DU,
                                                                                                  mdl.sum(
                                                                                                      mdl.x[it] * DRCs[
                                                                                                          D].cpu_DU for
                                                                                                      it in i if c ==
                                                                                                      paths[it[0]].seq[
                                                                                                          1] and it[
                                                                                                          2] == b and
                                                                                                      it[
                                                                                                          1] == D)) + mdl.min(
            DRCs[D].cpu_RU,
            mdl.sum(mdl.x[it] * DRCs[D].cpu_RU for it in i if c == paths[it[0]].seq[2] and it[2] == b and it[1] == D))
                                           for D in DRCs) for b in rus) <= crs[c].cpu, 'crs_cpu_usage')
    alocation_time_end = time.time()
    start_time = time.time()
    mdl.solve()
    end_time = time.time()
    print("Stage 1 - Alocation Time: {}".format(alocation_time_end - alocation_time_start))
    print("Stage 1 - Enlapsed Time: {}".format(end_time - start_time))
    for it in i:
        if mdl.x[it].solution_value > 0:
            print("x{} -> {}".format(it, mdl.x[it].solution_value))
            print(paths[it[0]].seq)
    for it in i:
        if mdl.y[it].solution_value > 0:
            print("y{} -> {}".format(it, mdl.y[it].solution_value))
    disp_Fs = {}
    for cr in crs:
        disp_Fs[cr] = {'f8': 0, 'f7': 0, 'f6': 0, 'f5': 0, 'f4': 0, 'f3': 0, 'f2': 0, 'f1': 0, 'f0': 0}
    for it in i:
        for cr in crs:
            if mdl.x[it].solution_value > 0:
                if cr in paths[it[0]].seq:
                    seq = paths[it[0]].seq
                    if cr == seq[0]:
                        Fs = DRCs[it[1]].Fs_CU
                        for o in Fs:
                            if o != 0:
                                dct = disp_Fs[cr]
                                dct["{}".format(o)] += 1
                                disp_Fs[cr] = dct
                    if cr == seq[1]:
                        Fs = DRCs[it[1]].Fs_DU
                        for o in Fs:
                            if o != 0:
                                dct = disp_Fs[cr]
                                dct["{}".format(o)] += 1
                                disp_Fs[cr] = dct
                    if cr == seq[2]:
                        Fs = DRCs[it[1]].Fs_RU
                        for o in Fs:
                            if o != 0:
                                dct = disp_Fs[cr]
                                dct["{}".format(o)] += 1
                                disp_Fs[cr] = dct
    print("FO: {}".format(mdl.solution.get_objective_value()))
    for cr in disp_Fs:
        print(str(cr) + str(disp_Fs[cr]))
    global f1_vars
    for it in i:
        if mdl.x[it].solution_value > 0:
            f1_vars.append(it)
    return mdl.solution.get_objective_value()


if __name__ == '__main__':
    start_all = time.time()
    run_model()
    end_all = time.time()
    print("TOTAL TIME: {}".format(end_all - start_all))
