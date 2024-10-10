import json
import pandas as pd
from transformers import pipeline, AutoTokenizer
import torch
from tqdm import tqdm
import argparse
import os
import csv

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Process transcripts before or after COVID.')
parser.add_argument('period', choices=['before', 'after'], help='Specify whether to process data before or after COVID.')
args = parser.parse_args()

# Determine the file to load based on the argument
input_file = f'transcripts_{args.period.upper()}_COVID.json'
output_file = f'summarized_{args.period.upper()}_COVID.json'
error_file = f'errors_{args.period.upper()}_COVID.csv'

# Load existing summarized data
if os.path.exists(output_file):
    with open(output_file, 'r') as file:
        summarized_data = json.load(file)
    summarized_ids = {item['yt_video_id'] for item in summarized_data}
else:
    summarized_data = []
    summarized_ids = set()

# Load input data
with open(input_file, 'r') as file:
    data = json.load(file)

# Convert to DataFrame
df = pd.json_normalize(data)

# Extract necessary columns
texts = df

model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
device = 0 if torch.cuda.is_available() else -1

pipeline1 = pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device=device,
    do_sample=False,  # No sampling
    temperature=None,  # Not needed when do_sample=False
    top_p=None,        # Not needed when do_sample=False
    pad_token_id=tokenizer.eos_token_id  # Ensure proper padding
)

def summarize_text(text):
    messages = [
        {"role": "system", "content": "You are equipped with advanced summarization techniques, your goal is to distill complex information of long YouTube transcriptions into concise summaries with maximum 384 tokens. You will only return the results without any additional comments."},
        {"role": "user", "content": f"Summarize the following text:\n\n{text}"},
    ]
    
    outputs = pipeline1(
        messages,
        max_new_tokens=384,
    )
    return outputs[0]["generated_text"][-1]["content"]

# Initialize tqdm with pandas
tqdm.pandas()

# Function to handle summarization and saving results
def process_and_save(row):
    yt_video_id = row['yt_video_id']
    if yt_video_id in summarized_ids:
        return

    try:
        summary = summarize_text(row['transcripts'])
        row['summary'] = summary
        summarized_data.append(row.to_dict())
        summarized_ids.add(yt_video_id)
        
        # Save the summarized data to JSON file after each iteration
        with open(output_file, 'w') as file:
            json.dump(summarized_data, file, indent=4)
    except Exception as e:
        with open(error_file, 'a', newline='') as csvfile:
            error_writer = csv.writer(csvfile)
            error_writer.writerow([yt_video_id, str(e)])

# Apply summarization to each transcript with tqdm for progress tracking
texts.progress_apply(process_and_save, axis=1)

# Print summaries to check
print(pd.DataFrame(summarized_data)[['summary', 'channel.ideology']].head())