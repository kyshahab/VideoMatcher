# Index a file from dataset

import numpy as np
import sys
import os
import glob
from calc_shots import calc_shotlist


# build inverted index
def build_invind(filename, shot_list):
    index = {}
    lines = []
    for start, length in shot_list:
        if length not in index:
            index[length] = list()
        index[length].append(start)
    
    for key in index.keys():
        line = str(key) + ":" + ",".join(str(start) for start in index[key]) + "\n"
        lines.append(line)
    
    f = open(filename, "w")
    f.writelines(lines)
    f.close()


if __name__ == "__main__":

    # VIDEO_DIR = '/Users/C1/classes/CSCI576/csci576_project/videos/video'
    VIDEO_DIR = 'videos'

    if len(sys.argv) == 2:
        files = [sys.argv[1]]
    else:
        files = glob.glob(os.path.join(VIDEO_DIR, "*.mp4"))

    os.makedirs('index', exist_ok=True)
    for file in files:
        video_name = os.path.basename(file).split(".")[0]

        # calculate and save shot list
        shot_list = calc_shotlist(file)

        list_filename = os.path.join("index", video_name + "_list.csv")
        np.savetxt(list_filename, shot_list, delimiter=",", fmt="%d")

        # build inverse index
        index_filename = os.path.join("index", video_name + "_ind.txt")
        build_invind(index_filename, shot_list)
