import subprocess

# List of ideologies; should contain actual ideology names instead of an empty string.
# ideologies = ["ANTI_SJW", "ANTI_THEIST", "BLACK", "CONSPIRACY", "LGBT", "LIBERTARIAN", "MRA", "PARTISAN_RIGHT", "PARTISAN_LEFT", "QANON", "RELIGIOUS_CONSERVATIVE", "SOCIAL_JUSTICE", "SOCIALIST", "WHITE_IDENTITARIAN"]  # Replace with actual ideologies, e.g., ["liberal", "conservative"]
ideologies = ["ANTI_SJW"]  # Replace with actual ideologies, e.g., ["liberal", "conservative"]

folder = "MORE"

for ideology in ideologies:
    # Create the command string using Python's f-string for formatting
    command = f"CUDA_VISIBLE_DEVICES=3 python refinement_FINAL.py --prompt_file ../prompt/refinement.txt " \
              f"--generation_file ../data/output/{folder}/refinement_1_updated_before_{ideology}_08.jsonl " \
              f"--topic_file ../data/output/{folder}/refinement_1_before_{ideology}_08.md " \
              f"--out_file ../data/output/{folder}/refinement_2_before_{ideology}_08.md " \
              f"--updated_file ../data/output/{folder}/refinement_2_updated_before_{ideology}_08.jsonl " \
              f"--mapping_file ../data/output/{folder}/refinement_2_mapping_before_{ideology}_08.txt " \
              f"--refined_again True " \
              f"--verbose True " \
              f"--remove False"
    
    # Execute the command using subprocess
    subprocess.run(command, shell=True)