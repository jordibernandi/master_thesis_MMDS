import os
import json

# Define paths
target = "refinement_1"
folder_path = "../data/output/FINAL"  # Change this to your folder path
output_jsonl_path = f"{folder_path}/{target}_combined_08.jsonl"
output_md_path = f"{folder_path}/{target}_combined_08.md"

# List of unique names
ideologies = ["ANTI_SJW", "ANTI_THEIST", "BLACK", "CONSPIRACY", "LGBT", "LIBERTARIAN", "MRA", "PARTISAN_RIGHT", "PARTISAN_LEFT", "QANON", "RELIGIOUS_CONSERVATIVE", "SOCIAL_JUSTICE", "SOCIALIST", "WHITE_IDENTITARIAN"]  # Replace with actual ideologies, e.g., ["liberal", "conservative"]
# ideologies = ["WHITE_IDENTITARIAN"]  # Replace with actual ideologies, e.g., ["liberal", "conservative"]

# Lists to store combined jsonl and markdown content
combined_jsonl = []
combined_md = []

# Iterate over unique names
for ideology in ideologies:
    for time_phase in ["after", "before"]:  # Check both after and before files
        
        # Combine JSONL Files
        jsonl_filename = f"{target}_updated_{time_phase}_{ideology}_08.jsonl"  # Construct JSONL filename
        jsonl_file_path = os.path.join(folder_path, jsonl_filename)

        if os.path.exists(jsonl_file_path):
            with open(jsonl_file_path, "r", encoding="utf-8") as f:
                for line in f:
                    data = json.loads(line)
                    combined_jsonl.append(data)  # Store each jsonl line
        else:
            print(f"JSONL file not found: {jsonl_filename}")
        
        # Combine Markdown Files
        md_filename = f"{target}_{time_phase}_{ideology}_08.md"  # Construct Markdown filename
        md_file_path = os.path.join(folder_path, md_filename)

        if os.path.exists(md_file_path):
            with open(md_file_path, "r", encoding="utf-8") as f:
                # Read the .md file and append its content to the combined markdown
                combined_md.append(f"## {ideology} ({time_phase})\n\n" + f.read() + "\n")
        else:
            print(f"Markdown file not found: {md_filename}")

# Write the combined JSONL file
with open(output_jsonl_path, "w", encoding="utf-8") as out_jsonl:
    for entry in combined_jsonl:
        out_jsonl.write(json.dumps(entry) + "\n")

# Write the combined Markdown file
with open(output_md_path, "w", encoding="utf-8") as out_md:
    out_md.write("\n".join(combined_md))

print(f"Combined JSONL saved to: {output_jsonl_path}")
print(f"Combined MD saved to: {output_md_path}")
