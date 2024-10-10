import subprocess

# List of ideologies; should contain actual ideology names instead of an empty string.
ideologies = ["ANTI_SJW", "ANTI_THEIST", "BLACK", "CONSPIRACY", "LGBT", "LIBERTARIAN", "MRA", "PARTISAN_RIGHT", "PARTISAN_LEFT", "QANON", "RELIGIOUS_CONSERVATIVE", "SOCIAL_JUSTICE", "SOCIALIST", "WHITE_IDENTITARIAN"]  # Replace with actual ideologies, e.g., ["liberal", "conservative"]

folder = "FINAL"

for ideology in ideologies:
    # Create the command string using Python's f-string for formatting
    command = f"CUDA_VISIBLE_DEVICES=6 python refinement_FINAL.py --prompt_file ../prompt/refinement.txt " \
              f"--generation_file ../data/output/{folder}/generation_1_before_{ideology}.jsonl " \
              f"--topic_file ../data/output/{folder}/generation_1_before_{ideology}.md " \
              f"--out_file ../data/output/{folder}/refinement_1_before_{ideology}_05.md " \
              f"--updated_file ../data/output/{folder}/refinement_1_updated_before_{ideology}_05.jsonl " \
              f"--mapping_file ../data/output/{folder}/refinement_1_mapping_before_{ideology}_05.txt " \
              f"--refined_again False " \
              f"--verbose True " \
              f"--remove False"
    
    # Execute the command using subprocess
    subprocess.run(command, shell=True)