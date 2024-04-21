
from mp4_to_wav import load_signatures, generate_audio_sig, create_query_wav, get_best_audio

from color import read_stats, get_stats, get_best_color

from calc_shots import calc_shotlist

from search import read_shotlist, match_shotlist


import os

root_dir = '/Users/C1/Classes/CSCI576/csci576_project/'

def main():

	# folder where audio wav files and jsons (use mp4_to_wav to generate this)
	audio_folder = os.path.join(root_dir, 'audio')

	# color json 
	color_file = os.path.join(root_dir, 'colors.json')

	# shot list indexes
	shot_list_dir = os.path.join(root_dir, 'index')

	# input file path
	query_file = os.path.join(root_dir, 'video_6_1_filtered.mp4')

	# if this path doesn't exist, the code will generate a wav file to this path
	query_wav_path = os.path.join(root_dir, 'video_6_1_filtered.wav')



	
	if not os.path.isfile(query_wav_path):
		create_query_wav(query_file, query_wav_path)



	# dictionaries indexed by video name, these have data for all the database videos
	colors = read_stats(color_file)
	audios = load_signatures(audio_folder)

	video_names = list(colors.keys())



	# input dicts, these generate stats for the input file
	color_input_dict = get_stats(query_file)
	audio_input_dict = generate_audio_sig(query_wav_path)
	input_shot_list = calc_shotlist(query_file)



	# get shotlists for each video in video_names
	# returns dictionary with video name key, possible locations as value
	possible_locs = match_multiple_shotlists(input_shot_list, shot_list_dir, videos=video_names)
	print(possible_locs)


	# get the k best results using color, each as a list of 5 video names, start frames, errors, where the same index corresponds to the same value
	# for example, top_k_color_video_names[i] is best video, with best start frame top_k_color_start_frames[i] and error top_k_color_errors[i]
	# note these lists aren't sorted by error, so the 0th index might not necessarily be the best error video
	# only searches videos specified in video_names list
	top_k_color_video_names, top_k_color_start_frames, top_k_color_errors = get_best_color(color_input_dict, colors, k=5, step_size=600, videos=video_names)
	
	print(top_k_color_video_names)
	print(top_k_color_start_frames)
	print(top_k_color_errors)
	
	
	# same as above for audio
	# only searches videos specified in video_names list
	top_k_audio_video_names, top_k_audio_start_frames, top_k_audio_errors = get_best_audio(audio_input_dict, audios, k=5, videos=video_names)

	print(top_k_audio_video_names)
	print(top_k_audio_start_frames)
	print(top_k_audio_errors)



def match_multiple_shotlists(input_shot_list,shot_list_dir, videos=[]):

	outputs = {}

	for video in videos:
		print("Checking shot list for " + video)
		shot_list_path = os.path.join(shot_list_dir, video + "_list.csv")

		src_shot_list = read_shotlist(shot_list_path)
		possible_locs = match_shotlist(src_shot_list, input_shot_list)

		outputs[video] = possible_locs

	return outputs




if __name__ == '__main__':
	main()