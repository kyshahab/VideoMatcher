# Calculate all shots in provided video

import cv2
import numpy as np
from tqdm import tqdm

def calc_shotlist(filename):
    video = cv2.VideoCapture(filename)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_diffs = []
    shot_list = []  # list of tuples (start, len)

    success, frame = video.read()
    curr_frame = None
    prev_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)  # LAB color space
    success, frame = video.read()

    # create tqdm progress bar
    pbar = tqdm(desc=filename, total=total_frames-1)

    # calculate diffs between each frame
    while success:
        curr_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)

        diff = cv2.absdiff(curr_frame, prev_frame)

        # use norm to find euclidian distance
        norm = np.linalg.norm(diff, axis=2)
        val = np.mean(norm)

        frame_diffs.append(val)

        prev_frame = curr_frame
        success, frame = video.read()

        pbar.update(1)
    video.release()
    pbar.close()

    # process diffs in 17 (8+1+8) frame window
    # look at prev 8 and next 8 frames
    last_boundary = -1
    for i in range(8, len(frame_diffs)-7):
        mean = np.mean(frame_diffs[i-8:i] + frame_diffs[i+1:i+8])
        if frame_diffs[i] > 5 and frame_diffs[i] > 3 * mean:
            start_frame = last_boundary + 1  # starting frame
            length = i - last_boundary       # num frames in shot
            shot_list.append((start_frame, length))
            last_boundary = i
            i += 7
    # add last shot
    shot_list.append((last_boundary+1, len(frame_diffs)-last_boundary))

    return shot_list
    
