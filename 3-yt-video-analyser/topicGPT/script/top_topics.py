import re
from collections import defaultdict

# Path to the markdown file
md_file_path = "../data/output/FINAL_SUMMARY/generation_1_combined.md"

# Function to extract topics and their counts
def extract_topics_and_counts(md_file_path):
    topic_counts = defaultdict(int)  # To store topic and their total counts
    
    # Regex pattern to match topics and counts in the markdown structure
    pattern = r"\[\d+\] (.+?) \(Count: (\d+)\)"
    
    with open(md_file_path, "r", encoding="utf-8") as file:
        for line in file:
            match = re.search(pattern, line)
            if match:
                topic = match.group(1).strip()  # Extract topic
                count = int(match.group(2))     # Extract count
                topic_counts[topic] += count    # Sum counts for duplicate topics
    
    return topic_counts

# Function to get top K topics
def get_top_k_topics(topic_counts, k):
    # Sort topics by their total count in descending order
    sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_topics[:k]  # Return the top K topics

# Main script
if __name__ == "__main__":
    # Extract topics and counts from the markdown file
    topic_counts = extract_topics_and_counts(md_file_path)
    
    # Set the value of K
    k = 20  # Change this to the desired number of top topics
    
    # Get top K topics
    top_k_topics = get_top_k_topics(topic_counts, k)
    
    # Print the top K topics
    print(f"Top {k} Topics:")
    for topic, count in top_k_topics:
        print(f"{topic}: {count}")

