import subprocess

# List of ideologies; should contain actual ideology names instead of an empty string.
ideologies = ["PARTISAN_RIGHT", "PARTISAN_LEFT", "QANON", "RELIGIOUS_CONSERVATIVE", "SOCIAL_JUSTICE", "SOCIALIST", "WHITE_IDENTITARIAN"]

data = "../../../transcripts_summarized_AFTER_COVID.json"
folder = "FINAL_SUMMARY"

for ideology in ideologies:
    # Create the command string using Python's f-string for formatting
    command = f"CUDA_VISIBLE_DEVICES=7 python generation_1_FINAL.py --data {data} " \
              f"--prompt_file ../prompt/generation_1.txt " \
              f"--seed_file ../prompt/seed_1.md " \
              f"--out_file ../data/output/{folder}/generation_1_after_{ideology}.jsonl " \
              f"--topic_file ../data/output/{folder}/generation_1_after_{ideology}.md " \
              f"--ideology {ideology} " \
              f"--summary True " \
              f"--verbose True " \
    
    # Execute the command using subprocess
    subprocess.run(command, shell=True)