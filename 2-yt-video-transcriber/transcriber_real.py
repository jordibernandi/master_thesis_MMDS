import os
import sys
import argparse
import json
import pandas as pd
from math import ceil
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
        wav_filename = f"{yt.video_id}.wav"
        wav_filepath = os.path.join(output_dir, wav_filename)
        audio.export(wav_filepath, format="wav")
        
        # Remove the original downloaded file
        os.remove(audio_file)
        
        print(f"Download and conversion completed! Saved as: {wav_filepath}")
        return wav_filepath, yt.length
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None

def read_csv_and_split(csv_file, num_chunks):
    df = pd.read_csv(csv_file)
    yt_video_ids = df['VIDEO_ID'].tolist()
    chunk_size = ceil(len(yt_video_ids) / num_chunks)
    chunks = [yt_video_ids[i:i + chunk_size] for i in range(0, len(yt_video_ids), chunk_size)]
    return chunks

def save_chunks_to_files(chunks, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for i, chunk in enumerate(chunks):
        chunk_file_path = os.path.join(output_dir, f'chunk_{i}.json')
        with open(chunk_file_path, 'w') as chunk_file:
            json.dump(chunk, chunk_file)
    return [os.path.join(output_dir, f'chunk_{i}.json') for i in range(len(chunks))]

def main():
    parser = argparse.ArgumentParser(description="Run Whisper model")
    parser.add_argument('--covid', action='store_true', help='Include --covid argument if set')
    parser.add_argument('--csv_file', type=str, required=True, help='Path to the CSV file containing yt_video_id')
    parser.add_argument('--num_chunks', type=int, default=5, help='Number of chunks to divide the records into')
    parser.add_argument('--chunk_index', type=int, required=True, help='Index of the chunk to process')
    parser.add_argument('--whisper_model', type=str, default='medium.en', 
                        choices=['tiny.en', 'tiny', 'base.en', 'base', 'small.en', 'small', 'medium.en', 'medium', 'large-v1', 'large-v2', 'large-v3', 'large'],
                        help='Specify the whisper model to use')
    parser.add_argument('--cog', action='store_true', help='Include --cog argument if set')
    parser.add_argument('--wonly', action='store_true', help='Include --wonly argument if set')
    parser.add_argument('--no_stem', action='store_true', help='Include --no-stem argument if set')
    parser.add_argument('--suppress_numerals', action='store_true', help='Include --suppress_numerals argument if set')
    args = parser.parse_args()

    csv_file = args.csv_file
    num_chunks = args.num_chunks
    chunk_index = args.chunk_index

    chunk_dir = 'chunks'
    if not os.path.exists(chunk_dir):
        print("Splitting CSV file into chunks...")
        chunks = read_csv_and_split(csv_file, num_chunks)
        save_chunks_to_files(chunks, chunk_dir)

    chunk_file = os.path.join(chunk_dir, f'chunk_{chunk_index}.json')
    if not os.path.exists(chunk_file):
        print(f"Chunk file {chunk_file} does not exist.")
        sys.exit(1)

    with open(chunk_file, 'r') as file:
        yt_video_ids = json.load(file)

    videos = [{"link": f"https://www.youtube.com/watch?v={yt_video_id}", "file_name": yt_video_id, "yt_video_id": yt_video_id} for yt_video_id in yt_video_ids]

    if torch.cuda.is_available():
        print("CUDA AVAILABLE")
    else:
        print("CUDA NOT AVAILABLE")

    # (choose from 'tiny.en', 'tiny', 'base.en', 'base', 'small.en', 'small', 'medium.en', 'medium', 'large-v1', 'large-v2', 'large-v3', 'large')
    whisper_model = args.whisper_model

    covid = True if args.covid else False
    covid_flag = 'AFTER_COVID_' if covid else 'BEFORE_COVID_'

    cog = True if args.cog else False
    cog_flag = 'COG' if cog else ''

    wonly = True if args.wonly else False
    wonly_flag = 'WONLY' if wonly else ''

    no_stem_flag = '--no-stem' if args.no_stem else ''

    suppress_numerals_flag = '--suppress_numerals' if args.suppress_numerals else ''

    batch_size = 8

    device = "cuda" if torch.cuda.is_available() else "cpu"

    if cog:
        result_dir = "../result_audio_files_" + covid_flag + cog_flag
    elif wonly:
        result_dir = "../result_audio_files_" + covid_flag + wonly_flag
    else:
        result_dir = "../result_audio_files_" + covid_flag + whisper_model + no_stem_flag + suppress_numerals_flag  # Specify your temporary directory here

    # Create the temporary directory if it doesn't exist
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    failed_videos_file = os.path.join(result_dir, "failed_videos.csv")
    error_videos = []

    for video in videos:
        json_output_path = os.path.join(result_dir, f"{video['yt_video_id']}.json")
        if os.path.exists(json_output_path):
            print(f"File {json_output_path} already exists. Skipping...")
            continue

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
                    # Determine which diarization script to run based on 'old' flag
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

                if not os.path.exists(json_output_path):
                    with open(failed_videos_file, 'a') as file:
                        file.write(f"{video['yt_video_id']}\n")
            else:
                print(f"Could not find file: {audio_filepath}")
                with open(failed_videos_file, 'a') as file:
                    file.write(f"{video['yt_video_id']}\n")
        except Exception as e:
            print(f"An error occurred during the process: {e}")
            error_videos.append(video["file_name"] + " : " + str(e))
            with open(failed_videos_file, 'a') as file:
                file.write(f"{video['yt_video_id']}\n")

    print("ERROR: ", error_videos)

if __name__ == "__main__":
    main()

