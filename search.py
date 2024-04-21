# Search index with query video

from calc_shots import calc_shotlist


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
def match_shotlist(src, query):

    possible_locs = []

    # brute force
    for i in range(len(src)-len(query)):
        for j in range(len(query)):
            if j == 0:
                if src[i][1] < query[0][1]:
                    break
            elif j == len(query) - 1:
                if src[i+j][1] >= query[j][1]:
                    possible_locs.append(src[i][0])
                    break
            else:
                if src[i+j][1] != query[j][1]:
                    break
    return possible_locs


if __name__ == "__main__":
    filename = "dataset/Queries/video_6_1_filtered.mp4"

    shot_list = calc_shotlist(filename)
    print("Query shot list:")
    print(shot_list)

    src_shot_list = read_shotlist("index/video6_list.csv")

    possible_locs = match_shotlist(src_shot_list, shot_list)

    print()
    print("Possible locations:")
    print(possible_locs)
