import subprocess

# List of ideologies; should contain actual ideology names instead of an empty string.
# ideologies = ["ANTI_SJW", "ANTI_THEIST", "BLACK", "CONSPIRACY", "LGBT", "LIBERTARIAN", "MRA"]
ideologies = ["ANTI_SJW", "ANTI_THEIST", "BLACK", "CONSPIRACY", "LGBT", "LIBERTARIAN", "MRA", "PARTISAN_RIGHT", "PARTISAN_LEFT", "QANON", "RELIGIOUS_CONSERVATIVE", "SOCIAL_JUSTICE", "SOCIALIST", "WHITE_IDENTITARIAN"]
# ideologies = ["ANTI_SJW"]

data = "../../../transcripts_summarized_AFTER_COVID.json"
folder = "FINAL"

for ideology in ideologies:
    # Create the command string using Python's f-string for formatting
    command = f"CUDA_VISIBLE_DEVICES=3 python assignment_FINAL.py --data {data} " \
              f"--prompt_file ../prompt/assignment.txt " \
              f"--topic_file ../data/output/{folder}/generation_1_global_topics.md " \
              f"--out_file ../data/output/{folder}/assignment_after_{ideology}_FULL.jsonl " \
              f"--ideology {ideology} " \
              f"--verbose True " \
    
    # Execute the command using subprocess
    subprocess.run(command, shell=True)