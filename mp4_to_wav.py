import os
import json
import subprocess
import cv2 
import numpy as np
from tqdm import tqdm 
import librosa 
from scipy.spatial.distance import euclidean
import math

FFMPEG_PATH = 'ffmpeg'
# FFMPEG_PATH = '/Users/Caleb/Documents/ffmpeg-5.0-essentials_build/bin/ffmpeg.exe'

#convert mp4 files to wav 
def create_wav_files(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok = True)
    for file in os.listdir(input_folder):
        if file.endswith(".mp4"):
            input_file = os.path.join(input_folder, file)
            output_file = os.path.join(output_folder, f'{file.split(".")[0]}.wav')
            subprocess.run([
                FFMPEG_PATH, 
                '-i', input_file, 
                '-vn', 
                '-ar', '44100',  
                '-ac', '1',      
                '-f', 'wav',     
                output_file
            ], capture_output=True)


def create_query_wav(query_vid, output_file):
    subprocess.run([
        FFMPEG_PATH, 
        '-i', query_vid, 
        '-vn', 
        '-ar', '44100',  
        '-ac', '1',      
        '-f', 'wav',     
        output_file
    ], capture_output=True)


def vid_from_aud(audio_frame_index):

    audio_fps = 44100.0
    video_fps = 30.0
    # Calculate corresponding video frame number
    video_frame_index = int((audio_frame_index / audio_fps) * video_fps)
    return video_frame_index

def aud_from_vid(vid_frame_index):
    sample_rate = 44100.0
    video_fps = 30.0
    audio_sample_index = int((vid_frame_index / video_fps) * sample_rate)
    return audio_sample_index

# search through set of videos
def get_best_audio(audio_input_dict, audios, k=5, step_size=1, videos = []):
    best_videos = ['video6.mp4' for i in range(k)]
    best_frames = [0 for i in range(k)]
    best_errs = [math.inf for i in range(k)]

    num_input_audio_frames = len(audio_input_dict['norm_rms'])

    for video_name in videos:
        print("Checking the audio of " + video_name)

        num_audio_frames = len(audios[video_name]['norm_rms'])

        start_index = 0
        while (start_index + num_input_audio_frames <= num_audio_frames):
            
            audio_err = get_audio_err(start_index, num_input_audio_frames, audio_input_dict, audios[video_name])

            idx = np.argmax(best_errs)
            if audio_err < best_errs[idx]:
                best_errs[idx] = audio_err
                best_frames[idx] = vid_from_aud(start_index*512)
                best_videos[idx] = video_name
            start_index+=step_size
    
    return (best_videos, best_frames, best_errs)

# search through range of frames in videos
def get_best_audio_loc(audio_input_dict, audios, k=5, video_locs={}):
    step_size = 1

    best_videos = ['video6.mp4' for i in range(k)]
    best_frames = [0 for i in range(k)]
    best_errs = [math.inf for i in range(k)]

    num_input_audio_frames = len(audio_input_dict['norm_rms'])

    for video_name in video_locs.keys():
        print("Checking the audio of " + video_name)

        for loc in video_locs[video_name]:
            num_audio_frames = len(audios[video_name]['norm_rms'])

            start_index = max(0, aud_from_vid(loc[0]-2) // 512)
            end = aud_from_vid(loc[1]-2) // 512  # need -2 for some reason
            while (start_index + num_input_audio_frames <= num_audio_frames) and start_index < end:
                audio_err = get_audio_err(start_index, num_input_audio_frames, audio_input_dict, audios[video_name])

                idx = np.argmax(best_errs)
                if audio_err < best_errs[idx]:
                    best_errs[idx] = audio_err
                    best_frames[idx] = vid_from_aud(start_index*512)
                    best_videos[idx] = video_name
                start_index+=step_size
    
    return (best_videos, best_frames, best_errs)


def get_audio_err(start_index, num_frames, input_dict, audio_dict):



    if (start_index + num_frames < len(audio_dict['norm_rms'])):
        query_features = np.concatenate([input_dict[feature] for feature in sorted(input_dict)])
        vid_features = np.concatenate([audio_dict[feature][start_index:start_index + num_frames] for feature in sorted(audio_dict)])
    else:
        query_features = np.concatenate([input_dict[feature] for feature in sorted(input_dict)])
        vid_features = np.concatenate([audio_dict[feature][start_index:start_index + num_frames] for feature in sorted(audio_dict)])

    distance = euclidean(query_features, vid_features)


    return distance


#use wav file to generate audio sig (RMS and spectral centroid)
def generate_audio_sig(vid_path, frame_size = 2048, hop_size = 512):


    audio_sig_amp, sampling_rt = librosa.load(vid_path, sr = 44100)


    rms = librosa.feature.rms(y = audio_sig_amp, frame_length = frame_size, hop_length = hop_size)
    spectral_centroid = librosa.feature.spectral_centroid(y = audio_sig_amp, sr = sampling_rt, hop_length = hop_size)

    norm_rms = rms / np.max(rms)
    norm_spectral_centroid = spectral_centroid / np.max(spectral_centroid)



    sig = {
        'norm_rms': norm_rms.flatten().tolist(),
        'norm_spectral_centroid': norm_spectral_centroid.flatten().tolist()
    }
    
    return sig

#add + save signature to json 
def save_sig(sig, output_path):
    with open(output_path, 'w') as f:
        json.dump(sig, f, indent = 4)

#get all wav files processed + save their signatures
def compute_signatures(folder, folder_path):
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    
    signatures = {}
    for f in tqdm(os.listdir(folder)):
        if f.endswith(".wav"):
            vid_path = os.path.join(folder, f)
            sig = generate_audio_sig(vid_path)

            sig_path = os.path.join(folder_path, f"{f}.json")
            save_sig(sig, sig_path)

            signatures[vid_path] = sig
            
    return signatures


def load_signatures(folder):

    signatures = {}
    for f in tqdm(os.listdir(folder)):
        if f.endswith(".json"):
            json_path = os.path.join(folder, f)

            file = open(json_path, 'r')

            vid_path = f[:-9]
            signatures[vid_path] = json.load(file)

            file.close()
            
    return signatures


#sub-signature matching 

def match_sub_sig(query_sig, signatures):
    best_match = None
    min_dist = float('inf')

    query_features = np.concatenate([query_sig[feature] for feature in sorted(query_sig)])

    for vid_path, vid_sig in signatures.items():
        vid_features = np.concatenate([vid_sig[feature] for feature in sorted(vid_sig)])


        dist = euclidean(query_features, vid_features)

        if dist < min_dist:
            min_dist = dist
            best_match = vid_path

    return best_match, min_dist


def load_signature(file_path):
    with open(file_path, 'r') as f:
        sig = json.load(f)
    return np.array(sig['norm_rms'] + sig['norm_spectral_centroid'])


def main():

    # folder with all videos
    input_folder = '/Users/yih/Desktop/CSCI576_final_project_dataset/Queries'
    #input_folder = 'Queries'

    output_folder = "/Users/yih/Desktop/CSCI576_final_project_dataset/audio"
    #output_folder = 'audio'



    
    os.makedirs(output_folder, exist_ok=True)
    create_wav_files(input_folder, output_folder)
    #create_query_wav(query_mp4_path, query_wav_path)

    vid_sigs = compute_signatures(output_folder, output_folder)

if __name__ == "__main__":
    main()