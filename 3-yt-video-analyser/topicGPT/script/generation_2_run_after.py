import subprocess

# List of ideologies; should contain actual ideology names instead of an empty string.
ideologies = ["ANTI_SJW", "ANTI_THEIST", "BLACK", "CONSPIRACY", "LGBT", "LIBERTARIAN", "MRA", "PARTISAN_RIGHT", "PARTISAN_LEFT", "QANON", "RELIGIOUS_CONSERVATIVE", "SOCIAL_JUSTICE", "SOCIALIST", "WHITE_IDENTITARIAN"] 
# ideologies = ["MRA", "PARTISAN_RIGHT", "PARTISAN_LEFT", "QANON", "RELIGIOUS_CONSERVATIVE", "SOCIAL_JUSTICE", "SOCIALIST", "WHITE_IDENTITARIAN"] 

folder = "FINAL_SUMMARY"

for ideology in ideologies:
    # Create the command string using Python's f-string for formatting
    command = f"CUDA_VISIBLE_DEVICES=4 python generation_2_FINAL.py --data ../data/output/{folder}/assignment_after_{ideology}.jsonl " \
            f"--seed_file ../data/output/{folder}/generation_1_after_{ideology}_seed.md " \
            f"--prompt_file ../prompt/generation_2.txt " \
            f"--out_file ../data/output/{folder}/generation_2_after_{ideology}_1TOPIC_ASS.jsonl " \
            f"--topic_file ../data/output/{folder}/generation_2_after_{ideology}_1TOPIC_ASS.md " \
            f"--verbose True"
    
    # Execute the command using subprocess
    subprocess.run(command, shell=True)