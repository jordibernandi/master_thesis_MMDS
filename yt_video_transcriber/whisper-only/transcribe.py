import os
import torch
import argparse
import json
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

def main():
    parser = argparse.ArgumentParser(description="Transcribe an audio file using Whisper model")
    parser.add_argument("--file", type=str, required=True, help="Path to the audio file")
    parser.add_argument("--yt-video-id", dest="yt_video_id", type=str, required=True, help="YouTube video ID")
    args = parser.parse_args()

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    model_id = "openai/whisper-large-v3"

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
    )
    model.to(device)

    processor = AutoProcessor.from_pretrained(model_id)

    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        max_new_tokens=128,
        torch_dtype=torch_dtype,
        device=device,
    )

    # Check if the audio file exists
    if not os.path.exists(args.file):
        raise FileNotFoundError(f"Audio file not found: {args.file}")
    else:
        print("File exists")

    result = pipe(args.file, generate_kwargs={"language": "english"})
    transcript_text = result["text"]

    # Save the result to a JSON file
    output_filename = os.path.splitext(args.file)[0] + ".json"
    with open(output_filename, "w", encoding="utf-8") as json_file:
        json.dump({"yt_video_id": args.yt_video_id, "transcripts": [{"text": transcript_text}]}, json_file, indent=4)

    print(f"Transcription saved to {output_filename}")

if __name__ == "__main__":
    main()
