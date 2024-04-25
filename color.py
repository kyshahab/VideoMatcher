
import cv2

import numpy as np

from sklearn.cluster import KMeans, MiniBatchKMeans

from skimage import io

from skimage import img_as_float

from joblib import Parallel, delayed

import math

import json

import argparse





'''
def main():



	ind = 4*(args.collection - 1) + 1
	videos =["/home1/kyshahab/project/videos/video" + str(i) + ".mp4" for i in range(ind, ind+4)]
	stats_file = 'colors_' + str(args.collection) + '.json'
	save_stats(videos, stats_file)

	input_file = "./video_6_1_filtered.mp4"
	stats_file = 'temp.json'
	compare_all(input_file, stats_file)
	

	


	#player = play_video('videos/video6.mp4', 12240)
	

# maybe step faster, save the 5 smallest error windows, and look around 20 windows of that for the final result?

'''



def get_best_color(color_input_dict, colors, k=5, step_size=600, videos=[]):

	best_videos = ['video6.mp4' for i in range(k)]
	best_frames = [0 for i in range(k)]
	best_errs = [math.inf for i in range(k)]


	num_frames = len(color_input_dict['order'])


	for video_name in videos:
		print("Checking the color of " + video_name)

		num_vid_frames = len(colors[video_name]['order'])

		start_index = 0
		while (start_index + num_frames <= num_vid_frames):
			total_err = compare_window(start_index, num_frames, color_input_dict, colors[video_name])

			idx = np.argmax(best_errs)
			if total_err < best_errs[idx]:
				best_errs[idx] = total_err
				best_frames[idx] = start_index
				best_videos[idx] = video_name


			start_index+=step_size


	return (best_videos, best_frames, best_errs)


def get_best_color_loc(color_input_dict, colors, k=5, video_locs={}):
	best_videos = []
	best_frames = []
	best_errs = []

	num_frames = len(color_input_dict['order'])

	for video_name in video_locs.keys():
		print("Checking the color of " + video_name)

		#num_vid_frames = len(colors[video_name]['order'])

		for loc in video_locs[video_name]:
			start_index = loc
			
			total_err = compare_window(start_index, num_frames, color_input_dict, colors[video_name])

			if len(best_errs) == k:
				idx = np.argmax(best_errs)
				if total_err < best_errs[idx]:
					best_errs[idx] = total_err
					best_frames[idx] = start_index
					best_videos[idx] = video_name
			else:
				best_errs.append(total_err)
				best_frames.append(start_index)
				best_videos.append(video_name)

	return (best_videos, best_frames, best_errs)



'''
	for i in range(0, k):
		start = max(0, best_frames[i] - step_size)
		end = min(len(all_vids[best_videos[i]]['order']), best_frames[i] + step_size)

		min_err = best_errs[i]
		best_start = best_frames[i]


		while start < end:
			total_err = compare_window(start, num_frames, input_dict, all_vids[best_videos[i]])

			if total_err < min_err:
				min_err = total_err
				best_start = start


			start += 10

		best_errs[i] = min_err
		best_frames[i] = best_start


	print("Fine-grained")
	print(best_errs)
	print(best_frames)
	'''
	




def get_audio_err(start_index, num_frames, input_dict, audio_dict):



	if (start_index + num_frames < len(audio_dict['norm_rms'])):
		query_features = np.concatenate([input_dict[feature] for feature in sorted(input_dict)])
		vid_features = np.concatenate([audio_dict[feature][start_index:start_index + num_frames] for feature in sorted(audio_dict)])
	else:
		query_features = np.concatenate([input_dict[feature] for feature in sorted(input_dict)])
		vid_features = np.concatenate([audio_dict[feature][start_index:start_index + num_frames] for feature in sorted(audio_dict)])

	distance = euclidean(query_features, vid_features)


	return distance



def compare_window(start_index, num_frames, input_dict, video_dict):
	total_window_error = 0
	for i in range(num_frames):
		err = get_error(input_dict['order'][i], video_dict['order'][start_index + i], 
			input_dict['colors'][i], video_dict['colors'][start_index + i], 
			input_dict['counts'][i], video_dict['counts'][start_index + i],
			input_dict['total_pixels'], video_dict['total_pixels'])

		total_window_error += err

	return total_window_error

def save_stats(videos, output_file):
	# do this for every video


	all_results = {}

	for video_path in videos:
		frames = extract_frames(video_path)

		num_colors = 8
		results = process_frames(frames, num_colors)


		result_dict = {
			'order': [results[i][0] for i in range(len(results))],
			'counts': [results[i][1] for i in range(len(results))],
			'colors': [results[i][2].tolist() for i in range(len(results))],
			'total_pixels': (np.shape(results[0][3])[0]*np.shape(results[0][3])[1])
		}

		all_results[video_path] = result_dict


	with open("temp.json", "w") as outfile: 
		json.dump(all_results, outfile)


def read_stats(json_file):
	f = open(json_file, 'r')
	data = json.load(f)
	f.close()
	return data


def get_stats(video_path):
	frames = extract_frames(video_path)
	num_colors = 8
	results = process_frames(frames, num_colors)


	total_pixels1 = np.shape(results[0][3])[0]*np.shape(results[0][3])[1]
	total_pixels2 = np.shape(results[1][3])[0]*np.shape(results[1][3])[1]



	result_dict = {
		'order': [results[i][0] for i in range(len(results))],
		'counts': [results[i][1] for i in range(len(results))],
		'colors': [results[i][2].tolist() for i in range(len(results))],
		'total_pixels': (np.shape(results[0][3])[0]*np.shape(results[0][3])[1])
	}
	return result_dict

def get_error(order1, order2, colors1, colors2, counts1, counts2, total_pixels1, total_pixels2):

	# for each color in frame1, find the color in frame2 most similar to it
		# get difference in those colors, times how many more one frame has than the other



	total_err = 0

	for ind1, c1 in enumerate(colors1):

		min_distance = math.inf
		best_c2 = colors2[0]
		best_i = 0

		for i, c2 in enumerate(colors2):
			c1 = np.array(c1)
			c2 = np.array(c2)
			distance = np.linalg.norm(c2 - c1)
			if distance < min_distance:
				best_c2 = c2
				min_distance = distance
				best_i = i


		count_c1 = counts1[ind1]

		if (best_i not in counts2):
			count_c2 = counts2[str(best_i)]
		else:
			count_c2 = counts2[best_i]

		p_c1 = (float)(count_c1) / total_pixels1
		p_c2 = (float)(count_c2) / total_pixels2


		d = (np.linalg.norm(best_c2 - c1))
		total_err += (d + abs(p_c1 - p_c2))

	return total_err




def process_frame(frame, num_colors):
	order, counts, colors, new_img = get_frame_color(frame, num_colors)
	return (order, counts, colors, new_img)

'''
def process_frames(frames, num_colors):
	return Parallel(n_jobs=-1)(delayed(process_frame)(frame, num_colors) for frame in frames)
'''

def process_frames(frames, num_colors, batch_size=10):
    processed_frames = []
    for i in range(0, len(frames), batch_size):
        batch_frames = frames[i:i+batch_size]
        results = Parallel(n_jobs=-1)(delayed(process_frame)(frame, num_colors) for frame in batch_frames)
        processed_frames.extend(results)
    return processed_frames


def extract_frames(video_path):
	# Open the video file
	video_capture = cv2.VideoCapture(video_path)

	# Read the video frame by frame
	success, frame = video_capture.read()

	frames = []

	# Iterate through frames
	while success:
		frames.append(frame)
		success, frame = video_capture.read()

	# Release the video capture object
	video_capture.release()

	return frames



def get_frame_color(frame, num_colors):

	frame = img_as_float(frame)
	pixels = frame.reshape(-1, 3)

	# Perform k-means clustering
	kmeans = MiniBatchKMeans(n_clusters=num_colors)
	kmeans.fit(pixels)

	# Get the cluster centers (colors)
	colors = kmeans.cluster_centers_

	# Assign each pixel to its nearest cluster center
	labels = kmeans.labels_

	# Replace each pixel with its corresponding cluster center color
	segmented_image = colors[labels]

	order, counts = dominant_colors(labels, num_colors)

	return (order, counts, colors, segmented_image.reshape(frame.shape))





def dominant_colors(labels, n_colors):
	color_counts = {}

	for i in range(0, n_colors):
		color_counts[i] = 0

	for label in labels:
		color_counts[label] += 1


	sorted_items = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)

	color_order = [key for key, value in sorted_items]

	return (color_order, color_counts)







# if __name__ == '__main__':
# 	main()