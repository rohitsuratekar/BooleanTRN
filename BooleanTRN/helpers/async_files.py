#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#
#
#  This file is part of BooleanTRN project.
#  All async operations will go into this file

import os
import shutil
from multiprocessing import Process, Queue

TEMP_FOLDER = "_temp"
OUT_FILE = "out.temp"
NO_OF_ANALYSIS = 0


def _find_isomorph_in_chunk(q: Queue, iso_function, networks: list):
    if not os.path.exists(TEMP_FOLDER):
        os.mkdir(TEMP_FOLDER)

    filename = f"{TEMP_FOLDER}/{os.getpid()}_iso.txt"
    print(f"\rAnalysis started for : {filename}", end="")
    iso_function(networks,
                 show_progress=False,
                 filename=filename)
    print(f"\rAnalysis ended for : {filename}", end="")
    q.put(filename)


def _join_temp(filenames):
    with open(OUT_FILE, 'w') as wfd:
        for f in filenames:
            with open(f, 'r') as fd:
                shutil.copyfileobj(fd, wfd)


def async_isomorph_finder(networks, chunks=1000, override=True):
    if os.path.exists(TEMP_FOLDER) and override:
        print("Deleting Old Temp Folder")
        shutil.rmtree(TEMP_FOLDER)
    current_networks = []
    q = Queue()
    all_process = []
    for n in networks:
        if len(current_networks) <= chunks:
            current_networks.append(n)
        else:
            cn = [x for x in current_networks]
            p = Process(target=_find_isomorph_in_chunk, args=(q, cn))
            current_networks = []
            p.start()
            all_process.append(p)

    if len(current_networks) > 0:
        p = Process(target=_find_isomorph_in_chunk, args=(q, current_networks))
        p.start()
        all_process.append(p)

    all_files = []
    for _ in all_process:
        all_files.append(q.get())

    print("\nAnalysis Finished\n")
    print(f"Temporary out : {OUT_FILE}")
