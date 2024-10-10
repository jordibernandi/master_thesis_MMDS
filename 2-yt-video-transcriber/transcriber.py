import os
import sys
import argparse
import json
os.environ["MKL_THREADING_LAYER"] = "GNU"  # or "INTEL" or use MKL_SERVICE_FORCE_INTEL as per your requirement
script_dir = os.path.dirname(__file__)
whisper_diarization_dir = os.path.join(script_dir, '.', 'whisper-diarization')
sys.path.append(whisper_diarization_dir)
import numpy as np  # Import numpy first to initialize MKL correctly
import torch
import time
from pytubefix import YouTube
from pydub import AudioSegment

def download_audio(youtube_url, file_name, output_dir):
    try:
        # Create a YouTube object
        yt = YouTube(youtube_url, use_oauth=True, allow_oauth_cache=True)
        # Get the audio stream with the highest bitrate
        audio_stream = yt.streams.filter(only_audio=True).first()
        # Download the audio file
        print(f"Downloading audio: {yt.title}")
        audio_file = audio_stream.download(output_path=output_dir, filename='temp_audio')
        
        # Convert the audio file to WAV format
        audio = AudioSegment.from_file(audio_file)
        wav_filename = f"{file_name}_{yt.video_id}.wav"
        wav_filepath = os.path.join(output_dir, wav_filename)
        audio.export(wav_filepath, format="wav")
        
        # Remove the original downloaded file
        os.remove(audio_file)
        
        print(f"Download and conversion completed! Saved as: {wav_filepath}")
        return wav_filepath, yt.length
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None
    
def extract_yt_video_id(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        yt_video_id = data.get('yt_video_id', None)
    return yt_video_id

def main():
    parser = argparse.ArgumentParser(description="Run Whisper model")
    parser.add_argument('--whisper_model', type=str, default='medium.en', 
                        choices=['tiny.en', 'tiny', 'base.en', 'base', 'small.en', 'small', 'medium.en', 'medium', 'large-v1', 'large-v2', 'large-v3', 'large'],
                        help='Specify the whisper model to use')
    # Without flag cog, wonly by default will run Whisper-Nemo
    parser.add_argument('--cog', action='store_true', help='Include --cog argument if set') # Whisper-Pyannote
    parser.add_argument('--wonly', action='store_true', help='Include --wonly argument if set') # Whisper only
    parser.add_argument('--no_stem', action='store_true', help='Include --no-stem argument if set')
    parser.add_argument('--suppress_numerals', action='store_true', help='Include --suppress_numerals argument if set')
    args = parser.parse_args()

    if torch.cuda.is_available():
        print("CUDA AVAILABLE")
    else:
        print("CUDA NOT AVAILABLE")

    # (choose from 'tiny.en', 'tiny', 'base.en', 'base', 'small.en', 'small', 'medium.en', 'medium', 'large-v1', 'large-v2', 'large-v3', 'large')
    whisper_model = args.whisper_model

    cog = True if args.cog else False

    wonly = True if args.wonly else False

    no_stem_flag = '--no-stem' if args.no_stem else ''

    suppress_numerals_flag = '--suppress_numerals' if args.suppress_numerals else ''

    batch_size = 8

    device = "cuda" if torch.cuda.is_available() else "cpu"

    videos = [
        {
            "link": "https://www.youtube.com/watch?v=" + "uKErcUxBMb8",
            "file_name": "MISSING",
            "yt_video_id": "uKErcUxBMb8"
        }
    ]

    # TESTING DATA
    # test_folder_path = '../test_data'
    # test_json_files = [file for file in os.listdir(test_folder_path) if file.endswith('.json')]
    # for json_file in test_json_files:
    #     file_path = os.path.join(test_folder_path, json_file)
    #     yt_video_id = extract_yt_video_id(file_path)
    #     if yt_video_id:
    #         file_name = os.path.splitext(json_file)[0]  # Remove .json extension
    #         videos.append({
    #             "link": "https://www.youtube.com/watch?v=" + yt_video_id,
    #             "file_name": file_name,
    #             "yt_video_id": yt_video_id
    #         })

    if cog:
        result_dir = "../Whisper-Pyannote_large-v3" # default large-v3
    elif wonly:
        result_dir = "../Whisper" # default always large-v3
    else:
        result_dir = "../Whisper-Nemo" + whisper_model + no_stem_flag + suppress_numerals_flag  # Specify your temporary directory here

    # Create the temporary directory if it doesn't exist
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    error_videos = []

    # print(videos)

    for video in videos:
        try:
            start_time = time.time()
            audio_filepath, video_length = download_audio(video["link"], video["file_name"], result_dir)
            if audio_filepath:
                if cog:
                    diarization_script = "../whisper-pyannote-lib/diarize.py"

                    command = (
                        f'python {diarization_script} '
                        f'--file "{audio_filepath}" '
                        f'--language en '
                        f'--yt-video-id={video["yt_video_id"]}'
                    )
                elif wonly:
                    diarization_script = "../whisper-lib/transcribe.py"

                    command = (
                        f'python {diarization_script} '
                        f'--file "{audio_filepath}" '
                        f'--yt-video-id={video["yt_video_id"]}'
                    )
                else:
                    diarization_script = "../whisper-nemo-lib/diarize.py"

                    # Build the command string
                    command = (
                        f'python {diarization_script} '
                        f'-a "{audio_filepath}" '
                        f'{no_stem_flag} '
                        f'{suppress_numerals_flag} '
                        f'--whisper-model {whisper_model} '
                        f'--batch-size {batch_size} '
                        f'--device {device} '
                        f'--language en '
                        f'--yt-video-id={video["yt_video_id"]}'
                    )

                # Execute the command using os.system
                print("COMMAND: ", command)
                os.system(command)
                end_time = time.time()
                diarization_time = end_time - start_time
            
                print(f'Diarization time for video {video["link"]}: {diarization_time:.2f} seconds')
                print(f"Video length: {video_length} seconds")
                
                # Delete the audio file after the diarization process
                os.remove(audio_filepath)
                print(f"Deleted audio file: {audio_filepath}")
            else:
                print(f"Could not find file: {audio_filepath}")
        except Exception as e:
            print(f"An error occurred during the process: {e}")
            error_videos.append(video["file_name"] + " : " + e)
    print("ERROR: ", error_videos)

if __name__ == "__main__":
    main()

