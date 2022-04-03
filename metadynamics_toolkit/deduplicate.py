import argparse
import glob
import os
import sys

import natsort
import numpy as np


def initialize():
    parser = argparse.ArgumentParser(
        description="This code deduplicates the data in PLUMED COLVAR and HILLS files when restarting a simulation."
    )
    parser.add_argument(
        "-c",
        "--cpt",
        default="state.cpt",
        help="The filname of the checkpoint file used for extension.",
    )
    parser.add_argument(
        "-hh",
        "--hills",
        default=glob.glob("HILLS*")[0],
        help="The filename of the HILLS file to be modified.",
    )
    parser.add_argument(
        "-cc",
        "--colvar",
        default=glob.glob("COLVAR*")[0],
        help="The filename of the COLVAR file to be modified.",
    )
    args_parse = parser.parse_args()

    return args_parse


def get_n_last(filename, t):
    infile = open(filename, "r")
    lines = infile.readlines()
    infile.close()

    n_total = 0  # total number of the lines
    for line in lines:
        n_total += 1
        if t in line:
            cpt_line = n_total

    print(t)
    n_last = n_total - cpt_line  # we delete the last n_last lines

    return n_last


if __name__ == "__main__":
    args = initialize()

    print("Running deduplicate.py ...")
    print("==========================")
    print(f"The .cpt file to be used: {args.cpt}")
    print(f"The HILLS file to be modified: {args.hills}")
    print(f"The COLVAR file to be modified: {args.colvar}")

    if args.cpt is None:
        print(".cpt file not specified or not found!")
        sys.exit()

    print("\nStep 1: Get the last checkpoint")
    if os.path.isfile("nohup.out"):
        os.system("rm nohup.out")

    os.system(f"nohup gmx check -f {args.cpt}")

    infile = open("nohup.out", "r")
    lines = infile.readlines()
    infile.close()

    for line in lines:
        if "Last frame" in line:
            cpt_frame = float(line.split("time")[-1])

    print(f"The lastly saved checkpoint is at {cpt_frame} ps.")

    print(f'\nStep 2: Modify {args.colvar}')
    time = np.transpose(np.loadtxt(args.colvar))[0]
    print(f'The last time frame saved in {args.colvar} is {time[-1]}.')
    print(f'Therefore, the data between {cpt_frame} and {time[-1]} will be deleted, if any.')
    diff = np.abs(time - cpt_frame)
    t = str(time[np.argmin(diff)])

    n_last = get_n_last(args.colvar, t)

    if os.path.isdir("backup_files"):
        n = int(natsort.natsorted(os.listdir("backup_files"))[-1].split("_")[-1])
        dir_bkp = f"backup_files/backup_{n + 1}"
        os.system(f"mkdir {dir_bkp}")
    else:
        os.system("mkdir backup_files")
        dir_bkp = "backup_files/backup_1"
        os.system(f"mkdir {dir_bkp}")

    os.system(f"cp {args.colvar} {dir_bkp}/.")
    os.system(f"rm {args.colvar}")
    os.system(f"head {dir_bkp}/{args.colvar} -n-{n_last} > {args.colvar}")
    
    if n_last == 0:
        print('There is no need to truncate the bottom of the file.')
    else:
        print(f'The last {n_last} lines in {args.colvar} has been discarded!')

    print(f'\nStep 3: Modify {args.hills}')
    time = np.transpose(np.loadtxt(args.hills))[0]
    print(f'The last time frame saved in {args.hills} is {time[-1]}.')
    print(f'Therefore, the data between {cpt_frame} and {time[-1]} will be deleted, if any.')
    
    diff = time - cpt_frame

    for i in range(len(diff)):
        if diff[-1] <= 0:  # no need to truncate
            n_last = 0
            break
        else:
            if diff[i] > 0:
                t = str(time[i])
                n_last = get_n_last(args.hills, t)
                break

    os.system(f"cp {args.hills} {dir_bkp}/.")
    os.system(f"rm {args.hills}")
    os.system(f"head {dir_bkp}/{args.hills} -n-{n_last} > {args.hills}")

    if n_last == 0:
        print('There is no need to truncate the bottom of the file.')
    else:
        print(f'The {n_last} lines of {args.hills} has been dicarded!')
