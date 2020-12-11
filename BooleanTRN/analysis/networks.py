#  Copyright (c) 2020
#  Rohit Suratekar, Winata Lab, IIMCB, Warsaw
#
#  This file is part of BooleanTRN project.
#  Analysis related to networks and related functionalities

import json
import os
import shutil
import uuid
from collections import defaultdict
from multiprocessing import Queue, Process

import networkx as nx

from BooleanTRN.helpers.common import load_networks, find_isomorphic_networks
from BooleanTRN.helpers.constants import *
from BooleanTRN.models.combinations import NetworkCombinations


def _save_to_file(que: Queue, networks, folder, show_progress):
    filename = f"{folder}/{uuid.uuid4()}"
    nets = find_isomorphic_networks(networks)
    if show_progress:
        print(f"PID :{os.getpid()} - Currently Generating : {filename}")
    with open(filename, "w") as f:
        for n in nets:
            print(json.dumps(n), file=f)
    que.put(filename)


def generate_ss_networks(no_of_nodes: int, no_of_edges: int,
                         steady_states: list, *,
                         interactions: list = None,
                         is_connected: bool = True,
                         gates: list = None,
                         show_progress: bool = True,
                         filename="networks.txt"):
    if interactions is None:
        interactions = [INTERACTION_POSITIVE]
    if gates is None:
        gates = [GATE_OR]
    nc = NetworkCombinations(no_of_nodes, no_of_edges,
                             only_connected=is_connected)
    nc.interactions = interactions
    nc.gates = gates
    with open(filename, "w") as f:
        for n in nc.find(steady_states, show_progress=show_progress):
            data = json.dumps(n)
            print(data, file=f)


def _wrap_generate_iso_networks(networks: list,
                                *,
                                chunks=1000,
                                show_progress=True,
                                clean_old=True,
                                filename="isomorphs.txt",
                                temp_folder="_temp",
                                change_factor=2,
                                previous_count=None):
    if not os.path.exists(temp_folder):
        os.mkdir(temp_folder)
    else:
        if clean_old and previous_count is None:
            shutil.rmtree(temp_folder)
            os.mkdir(temp_folder)

    network_split = []
    tmp = []
    main_queue = Queue()
    for n in networks:
        tmp.append(n)
        if len(tmp) >= chunks:
            p = Process(target=_save_to_file,
                        args=(main_queue, tmp, temp_folder, show_progress))
            p.start()
            network_split.append(1)
            tmp = []
    if len(tmp) > 0:
        p = Process(target=_save_to_file,
                    args=(main_queue, tmp, temp_folder, show_progress))
        p.start()
        network_split.append(1)

    all_files = []
    for _ in network_split:
        all_files.append(main_queue.get())

    # Combine all temporary files
    with open(filename, 'w') as wfd:
        for f in all_files:
            with open(f, 'r') as fd:
                shutil.copyfileobj(fd, wfd)

    if len(networks) <= chunks:
        return
    else:
        chunks = change_factor * chunks

    new_nets = load_networks(filename)

    if len(new_nets) == len(networks):
        chunks = len(networks) + 1

    if previous_count is not None:
        print("=========================================")
        print("Starting next round of isomorph searching")

    _wrap_generate_iso_networks(new_nets,
                                chunks=chunks,
                                show_progress=show_progress,
                                filename=filename,
                                clean_old=clean_old,
                                temp_folder=temp_folder,
                                previous_count=len(networks))


def generate_iso_networks(networks: list,
                          *,
                          chunks=1000,
                          show_progress=True,
                          clean_old=True,
                          filename="isomorphs.txt",
                          temp_folder="_temp",
                          change_factor=2,
                          previous_count=None):
    print("Starting first round of searching")
    print("==================================")
    _wrap_generate_iso_networks(networks, chunks=chunks,
                                show_progress=show_progress,
                                clean_old=clean_old,
                                filename=filename,
                                temp_folder=temp_folder,
                                previous_count=previous_count,
                                change_factor=change_factor)

    print("====================================")
    print("Analysis finished, cleaning up temporary files")
    shutil.rmtree(temp_folder)


def _wrap_ss_isomorphs(q: Queue, networks: list,
                       nc: NetworkCombinations, chunk_no: int):
    print(f"Analysing chunk {chunk_no + 1}")
    graphs = []
    nets = defaultdict(list)
    for n in networks:
        g = nx.MultiDiGraph()
        for ss in nc.get_state_space(n).items():
            g.add_edge(ss[0], ss[1])
        if len(graphs) == 0:
            graphs.append(g)
            nets[g].append(n)
        else:
            tmp = [nx.is_isomorphic(x, g) for x in graphs]
            if not any(tmp):
                graphs.append(g)
                nets[g].append(n)
            else:
                nets[graphs[tmp.index(True)]].append(n)
    del graphs
    q.put(list(nets.values()))


def get_steady_state_isomorphs(networks,
                               nc: NetworkCombinations,
                               chunks=200,
                               filename="ss_isomorphs.txt"):
    main_queue = Queue()
    current = []
    all_process = []
    for n in networks:
        current.append(n)
        if len(current) >= chunks:
            p = Process(target=_wrap_ss_isomorphs,
                        args=(main_queue, current, nc, len(all_process)))
            p.start()
            all_process.append(1)
            current = []

    if len(current) > 0:
        p = Process(target=_wrap_ss_isomorphs,
                    args=(main_queue, current, nc, len(all_process)))
        p.start()
        all_process.append(1)

    sub_iso = []
    for _ in all_process:
        sub_iso.append(main_queue.get())
        print(f"Collected results for {len(sub_iso)} chunks")

    final_ss = []
    rep_ss = []
    print("Combining chunks...")
    for sub in sub_iso:
        for s in sub:
            rep = s[0]
            g = nx.MultiDiGraph()
            for ss in nc.get_state_space(rep).items():
                g.add_edge(ss[0], ss[1])
            if len(final_ss) == 0:
                final_ss.append(s)
                rep_ss.append(g)
                continue
            else:
                tmp = [nx.is_isomorphic(x, g) for x in rep_ss]
                if not any(tmp):
                    rep_ss.append(g)
                    final_ss.append(s)
                else:
                    final_ss[tmp.index(True)].extend(s)

    print(f"Finished Analysing. Total '{len(final_ss)}' SS-isomorphs found.")
    count = -1
    with open(filename, "w") as f:
        for s in final_ss:
            count += 1
            for x in s:
                print(f"{count}:{json.dumps(x)}", file=f)

    del rep_ss
    return final_ss


def compress_steady_state(ss: str):
    letters = list(ss.strip())
    tmp = []
    numbers = []
    for ltr in letters:
        if len(tmp) == 0:
            tmp.append(ltr)
            numbers.append(1)
            continue
        if ltr == tmp[-1]:
            numbers[-1] += 1
        else:
            tmp.append(ltr)
            numbers.append(1)

    final_str = ""
    tmp = ["T" if x == '1' else "F" for x in tmp]
    for m, k in zip(tmp, numbers):
        if k == 1:
            final_str += m
        else:
            final_str += f"{k}{m}"

    return final_str


def full_analysis(no_of_nodes: int, no_of_edges: int, steady_states: list,
                  chunks=20000, out_folder="out"):
    if not os.path.exists(out_folder):
        os.mkdir(out_folder)
    print("Generating all possible networks")
    ss_string = "_".join([compress_steady_state(x) for x in steady_states])
    filename = f"{out_folder}/net_n{no_of_nodes}e{no_of_edges}_{ss_string}.txt"
    generate_ss_networks(no_of_nodes, no_of_edges, steady_states,
                         interactions=[0, 1],
                         gates=[0, 1],
                         is_connected=True,
                         filename=filename)
    print(f"\nAll networks stored in file: {filename}")
    data = load_networks(filename)
    iso_file = filename.replace("net", "iso")
    print("Searching for Isomorphic Networks")
    generate_iso_networks(data, chunks=chunks, filename=iso_file)
    print(f"All isomorphs stored in file: {iso_file}")
    del data
    print("Searching for SS-isomorphs")
    iso_data = load_networks(iso_file)
    nc = NetworkCombinations(no_of_nodes, no_of_edges)
    nc.is_connected = True
    nc.interactions = [0, 1]
    nc.gates = [0, 1]
    ss_file = filename.replace("net", "ss_iso")
    get_steady_state_isomorphs(iso_data, nc, chunks=10000, filename=ss_file)
    print("Analysis finished")
    print(f"SS-isomorphs saved in file : {ss_file}")


def run():
    full_analysis(5, 6, ["11111", "10100"], chunks=3000)
