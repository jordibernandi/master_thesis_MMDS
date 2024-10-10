import subprocess

folder = "FINAL"

command = f"CUDA_VISIBLE_DEVICES=3 python refinement_FINAL.py --prompt_file ../prompt/refinement.txt " \
            f"--generation_file ../data/output/{folder}/refinement_1_combined_08.jsonl " \
            f"--topic_file ../data/output/{folder}/refinement_1_combined_08.md " \
            f"--out_file ../data/output/{folder}/refinement_2_combined_05.md " \
            f"--updated_file ../data/output/{folder}/refinement_2_updated_combined_05.jsonl " \
            f"--mapping_file ../data/output/{folder}/refinement_2_mapping_combined_05.txt " \
            f"--refined_again True " \
            # f"--remove False"

# Execute the command using subprocess
subprocess.run(command, shell=True)