# Search index with query video

from calc_shots import calc_shotlist
import cv2
import os
import sys
import glob

def read_shotlist(filename):
    shot_list = []
    f = open(filename, "r")
    for line in f:
        shot = line.split(",")
        shot_list.append((int(shot[0]), int(shot[1])))
    f.close()
    return shot_list


# read inverted index from file
def read_invindex(filename):
    index = {}
    f = open(filename, "r")
    for line in f:
        args = line.split(":")
        length = int(args[0])
        frame_list = [int(frame) for frame in args[1].split(",")]
        index[length] = frame_list
    f.close()
    return index


# find possible locations based on shot list
# starting frame could be on or after the "possible location"
def match_shotlist(src, query, inv_ind):

    results = []

    if len(query) == 0:
        print("ERROR: No shots in list found")
    elif len(query) == 1:
        for key in inv_ind.keys():
            if key >= query[0][1]:
                results.extend(inv_ind[key])
    elif len(query) == 2:
        # find 2 suitable shots
        for i in range(1, len(src)):
            if src[i-1][1] >= query[0][1] and src[i][1] >= query[1][1]:
                # (2nd shot start) - (1st shot length)
                results.append(src[i][0] - query[0][1])
    else:
        # brute force
        for i in range(len(src)-len(query)):
            start = -1
            for j in range(len(query)):
                if j == 0:  # first shot
                    if src[i][1] < query[0][1]:
                        break
                    start = src[i+1][0] - query[0][1]
                elif j == len(query) - 1:  # last shot
                    if src[i+j][1] >= query[j][1]:
                        results.append(start)
                        break
                else:  # middle shots
                    if src[i+j][1] != query[j][1]:
                        break
    return results


if __name__ == "__main__":

    # file = "Queries/video2_1_modified.mp4"
    file = sys.argv[1]

    video_name = os.path.basename(file).split("_")[0]

    shot_list = calc_shotlist(file)
    print("Query shot list:")
    print(shot_list)

    src_shot_list = read_shotlist(os.path.join("index", video_name + "_list.csv"))
    inv_index = read_invindex(os.path.join("index", video_name + "_ind.txt"))
    possible_locs = match_shotlist(src_shot_list, shot_list, inv_index)

    print("Possible locations:")
    print(possible_locs)
