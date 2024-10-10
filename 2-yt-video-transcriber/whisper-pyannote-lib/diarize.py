import argparse
import base64
import datetime
import os
import subprocess
import time
import requests
import re
import torch
import json
from pygments import highlight, lexers, formatters
from faster_whisper import WhisperModel
from pyannote.audio import Pipeline

def convert_time(secs, offset_seconds=0):
    return datetime.timedelta(seconds=(round(secs) + offset_seconds))

def speech_to_text(
    model, diarization_model, audio_file_wav, num_speakers=None, prompt="",
    offset_seconds=0, group_segments=True, language=None, word_timestamps=True,
    transcript_output_format="both"
):
    time_start = time.time()
    options = {
        "vad_filter": True,
        "vad_parameters": {"min_silence_duration_ms": 1000},
        # "initial_prompt": prompt,
        "word_timestamps": word_timestamps,
        "language": language,
    }
    segments, transcript_info = model.transcribe(audio_file_wav, **options)
    segments = list(segments)
    segments = [
        {
            "avg_logprob": s.avg_logprob,
            "start": float(s.start + offset_seconds),
            "end": float(s.end + offset_seconds),
            "text": s.text,
            "words": [
                {
                    "start": float(w.start + offset_seconds),
                    "end": float(w.end + offset_seconds),
                    "word": w.word,
                    "probability": w.probability,
                }
                for w in s.words
            ],
        }
        for s in segments
    ]

    diarization = diarization_model(audio_file_wav, num_speakers=num_speakers)
    margin = 0.1
    final_segments = []
    diarization_list = list(diarization.itertracks(yield_label=True))
    unique_speakers = {speaker for _, _, speaker in diarization.itertracks(yield_label=True)}
    detected_num_speakers = len(unique_speakers)
    speaker_idx = 0
    n_speakers = len(diarization_list)

    for segment in segments:
        segment_start = segment["start"] + offset_seconds
        segment_end = segment["end"] + offset_seconds
        segment_text = []
        segment_words = []

        for word in segment["words"]:
            word_start = word["start"] + offset_seconds - margin
            word_end = word["end"] + offset_seconds + margin

            while speaker_idx < n_speakers:
                turn, _, speaker = diarization_list[speaker_idx]

                if turn.start <= word_end and turn.end >= word_start:
                    segment_text.append(word["word"])
                    word["word"] = word["word"].strip()
                    segment_words.append(word)

                    if turn.end <= word_end:
                        speaker_idx += 1
                    break
                elif turn.end < word_start:
                    speaker_idx += 1
                else:
                    break

        if segment_text:
            combined_text = "".join(segment_text)
            cleaned_text = re.sub("  ", " ", combined_text).strip()
            new_segment = {
                "avg_logprob": segment["avg_logprob"],
                "start": segment_start - offset_seconds,
                "end": segment_end - offset_seconds,
                "speaker": speaker,
                "text": cleaned_text,
                "words": segment_words,
            }
            final_segments.append(new_segment)

    segments = final_segments
    output = []
    current_group = {
        "start": str(segments[0]["start"]),
        "end": str(segments[0]["end"]),
        "speaker": segments[0]["speaker"],
        "avg_logprob": segments[0]["avg_logprob"],
    }

    if transcript_output_format in ("segments_only", "both"):
        current_group["text"] = segments[0]["text"]
    if transcript_output_format in ("words_only", "both"):
        current_group["words"] = segments[0]["words"]

    for i in range(1, len(segments)):
        time_gap = segments[i]["start"] - segments[i - 1]["end"]

        if segments[i]["speaker"] == segments[i - 1]["speaker"] and time_gap <= 2 and group_segments:
            current_group["end"] = str(segments[i]["end"])
            if transcript_output_format in ("segments_only", "both"):
                current_group["text"] += " " + segments[i]["text"]
            if transcript_output_format in ("words_only", "both"):
                current_group.setdefault("words", []).extend(segments[i]["words"])
        else:
            output.append(current_group)
            current_group = {
                "start": str(segments[i]["start"]),
                "end": str(segments[i]["end"]),
                "speaker": segments[i]["speaker"],
                "avg_logprob": segments[i]["avg_logprob"],
            }
            if transcript_output_format in ("segments_only", "both"):
                current_group["text"] = segments[i]["text"]
            if transcript_output_format in ("words_only", "both"):
                current_group["words"] = segments[i]["words"]

    output.append(current_group)
    time_end = time.time()
    time_diff = time_end - time_start
    print(f"Processing time: {time_diff:.5} seconds")
    return output, detected_num_speakers, transcript_info.language

def pretty_json(data):
    formatted_json = json.dumps(data, sort_keys=True, indent=4)
    colorful_json = highlight(formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter())
    print(colorful_json)

def main():
    parser = argparse.ArgumentParser(description="Audio file transcription and speaker diarization")
    parser.add_argument("--file", type=str, help="Path to the audio file")
    parser.add_argument("--file_url", type=str, help="URL of the audio file")
    parser.add_argument("--file_string", type=str, help="Base64 encoded audio file")
    parser.add_argument("--group_segments", type=bool, default=True, help="Group segments of the same speaker")
    parser.add_argument("--transcript_output_format", type=str, choices=["words_only", "segments_only", "both"], default="both", help="Format of the transcript output")
    parser.add_argument("--num_speakers", type=int, default=None, help="Number of speakers to detect")
    parser.add_argument("--language", type=str, default=None, help="Language code for the spoken words")
    parser.add_argument("--prompt", type=str, default=None, help="Vocabulary for the transcription")
    parser.add_argument("--offset_seconds", type=int, default=0, help="Offset in seconds for chunked inputs")
    parser.add_argument("--yt-video-id", dest="yt_video_id", default="", help="YouTube video id")

    args = parser.parse_args()

    print("TORCH: ", torch.cuda.is_available())

    model_name = "large-v3"
    model = WhisperModel(model_name, device="cuda" if torch.cuda.is_available() else "cpu", compute_type="float16")
    diarization_model = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token="PUT_YOUR_PYANNOTE_AUTH_TOKEN").to(torch.device("cuda"))

    temp_wav_filename = f"temp-{time.time_ns()}.wav"
    if args.file:
        subprocess.run(["ffmpeg", "-i", args.file, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", temp_wav_filename])
    elif args.file_url:
        response = requests.get(args.file_url)
        temp_audio_filename = f"temp-{time.time_ns()}.audio"
        with open(temp_audio_filename, "wb") as file:
            file.write(response.content)
        subprocess.run(["ffmpeg", "-i", temp_audio_filename, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", temp_wav_filename])
        if os.path.exists(temp_audio_filename):
            os.remove(temp_audio_filename)
    elif args.file_string:
        audio_data = base64.b64decode(args.file_string.split(",")[1] if "," in args.file_string else args.file_string)
        temp_audio_filename = f"temp-{time.time_ns()}.audio"
        with open(temp_audio_filename, "wb") as f:
            f.write(audio_data)
        subprocess.run(["ffmpeg", "-i", temp_audio_filename, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", temp_wav_filename])
        if os.path.exists(temp_audio_filename):
            os.remove(temp_audio_filename)

    segments, detected_num_speakers, detected_language = speech_to_text(
        model, diarization_model, temp_wav_filename, args.num_speakers, args.prompt, args.offset_seconds,
        args.group_segments, args.language, word_timestamps=True, transcript_output_format=args.transcript_output_format
    )

    # print(f"Segments: {pretty_json(segments)}")

    with open(f"{os.path.splitext(args.file)[0]}.json", "w", encoding="utf-8-sig") as j:
        write_json(segments, j, args.yt_video_id)

    print(f"Detected Number of Speakers: {detected_num_speakers}")
    print(f"Detected Language: {detected_language}")

    if os.path.exists(temp_wav_filename):
        os.remove(temp_wav_filename)

def format_timestamp(
    milliseconds: float, always_include_hours: bool = False, decimal_marker: str = "."
):
    assert milliseconds >= 0, "non-negative timestamp expected"

    hours = milliseconds // 3_600_000
    milliseconds -= hours * 3_600_000

    minutes = milliseconds // 60_000
    milliseconds -= minutes * 60_000

    seconds = milliseconds // 1_000
    milliseconds -= seconds * 1_000

    hours_marker = f"{hours:02d}:" if always_include_hours or hours > 0 else ""
    return (
        f"{hours_marker}{minutes:02d}:{seconds:02d}{decimal_marker}{milliseconds:03d}"
    )


def write_json(transcript, file, yt_video_id):
    transcripts = []
    current_transcript = {"start_time": "", "end_time": "", "text": "", "speaker": {"name": transcript[0]["speaker"]}}

    for segment in transcript:
        # segment['start'] = float(segment['start'] * 1000)
        # segment['end'] = float(segment['end'] * 1000)
        # start_time = format_timestamp(segment['start'], always_include_hours=True, decimal_marker=',')
        # end_time = format_timestamp(segment['end'], always_include_hours=True, decimal_marker=',')

        start_time = segment["start"]
        end_time = segment["end"]
        sentence = segment["text"]
        speaker = segment["speaker"]

        # If the current speaker doesn't match the previous one, save the current transcript and start a new one
        if speaker != current_transcript["speaker"]["name"]:
            transcripts.append(current_transcript)
            current_transcript = {"start_time": start_time, "end_time": end_time, "text": sentence, "speaker": {"name": speaker}}
        else:
            # If the speaker is the same, append the current sentence
            if current_transcript["text"]:
                current_transcript["text"] += " " + sentence
            else:
                current_transcript["text"] = sentence

    # Append the last transcript
    transcripts.append(current_transcript)

    # Write the transcripts to the file as JSON
    json.dump({"yt_video_id": yt_video_id, "transcripts": transcripts}, file, indent=4)

if __name__ == "__main__":
    main()
