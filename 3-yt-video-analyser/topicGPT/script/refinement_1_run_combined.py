import subprocess

folder = "MORE"

command = f"CUDA_VISIBLE_DEVICES=3 python refinement_FINAL.py --prompt_file ../prompt/refinement.txt " \
            f"--generation_file ../data/output/{folder}/generation_1_combined.jsonl " \
            f"--topic_file ../data/output/{folder}/generation_1_combined.md " \
            f"--out_file ../data/output/{folder}/refinement_1_combined_08.md " \
            f"--updated_file ../data/output/{folder}/refinement_1_updated_combined_08.jsonl " \
            f"--mapping_file ../data/output/{folder}/refinement_1_mapping_combined_08.txt " \
            f"--refined_again False " \
            f"--verbose True " \
            f"--remove False"

# Execute the command using subprocess
subprocess.run(command, shell=True)