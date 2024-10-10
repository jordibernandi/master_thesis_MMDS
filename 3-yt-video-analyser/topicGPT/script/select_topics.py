import os
import re

# Define paths
folder_path = "../data/output/FINAL_SUMMARY"  # Change this to your folder path

# List of unique names
ideologies = ["ANTI_SJW", "ANTI_THEIST", "BLACK", "CONSPIRACY", "LGBT", "LIBERTARIAN", "MRA", "PARTISAN_RIGHT", "PARTISAN_LEFT", "QANON", "RELIGIOUS_CONSERVATIVE", "SOCIAL_JUSTICE", "SOCIALIST", "WHITE_IDENTITARIAN"] 

# List of topics to filter
# topics = ["Politics", "Government", "Identity", "Community", "Education", "Culture", "Media", "Economy", "Society", "Health", "Family", "Law Enforcement", "History", "Faith", "Social Justice", "Racism", "Relationships", "Morality", "Leadership", "Human Rights"]
# topics = ["Politics", "Government", "Identity", "Community", "Society", "Culture", "Education", "Morality", "Economy", "Media", "Business", "Health", "Human Rights", "Relationships", "History", "Law Enforcement", "Social Justice", "Family", "Leadership", "Personal Growth"]
# topics = ["Politics", "Government", "Identity", "Community", "Society", "Culture", "Education", "Morality", "Economy", "Media", "Business", "Health", "Human Rights", "Relationships", "History", "Law Enforcement", "Social Justice", "Family", "Leadership", "Personal Growth", "Law", "Faith", "Human Behavior", "Ethics", "Freedom", "Trade", "Technology", "Power", "Racism", "Human Nature"]
# topics = ["Politics", "Government", "Community", "Human Rights", "Identity", "Social Justice", "Culture", "Human Behavior", "Education", "Relationships", "Personal Growth", "Society", "Health", "Economy", "Law Enforcement", "Social Commentary", "Media", "Faith", "Leadership", "History"]
topics = ["Health"]

# Regular expression pattern to extract topic label and count
pattern = re.compile(r"\[\d+\]\s(.+?)\s\(Count:\s*(\d+)\)")

# Iterate over unique ideologies and time phases
for ideology in ideologies:
    for time_phase in ["after", "before"]:  # Check both after and before files
        
        # Construct markdown filename
        md_filename = f"generation_1_{time_phase}_{ideology}.md"
        md_file_path = os.path.join(folder_path, md_filename)

        # Check if the file exists
        if os.path.exists(md_file_path):
            # Read the .md file
            with open(md_file_path, "r", encoding="utf-8") as f:
                file_content = f.read()

            # Dictionary to store the maximum count for each topic
            topic_counts = {}

            # Find all topic labels and their counts in the file
            for match in pattern.findall(file_content):
                topic_label, count = match[0], int(match[1])

                # Check if the topic is in the predefined list
                if topic_label in topics:
                    # If the topic is already in the dictionary, update the count only if the new count is higher
                    if topic_label in topic_counts:
                        topic_counts[topic_label] = max(topic_counts[topic_label], count)
                    else:
                        topic_counts[topic_label] = count

            # If any topic matches, keep the structure but only save lines with the highest counts
            new_content = []
            lines = file_content.splitlines()
            for line in lines:
                match = pattern.search(line)
                if match:
                    # Get the topic label and count
                    topic_label, count = match.group(1), int(match.group(2))
                    # Check if the topic is in the predefined list and matches the highest count
                    if topic_label in topics and count == topic_counts[topic_label]:
                        new_content.append(line)  # Keep the line if the count matches the highest
                else:
                    new_content.append(line)  # Keep non-topic lines as well

            # Create new file name with _seed.md suffix
            new_filename = f"generation_1_{time_phase}_{ideology}_seed_health.md"
            new_file_path = os.path.join(folder_path, new_filename)

            # Write the filtered content into the new file
            with open(new_file_path, "w", encoding="utf-8") as new_file:
                new_file.write("\n".join(new_content))

            # Log the final counts for topics
            total_counts = sum(topic_counts.values())
            print(f"Filtered content saved in: {new_filename} with total topic count: {total_counts}")
        else:
            print(f"Markdown file not found: {md_filename}")
