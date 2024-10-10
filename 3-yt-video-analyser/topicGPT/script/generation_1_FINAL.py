import pandas as pd
from utils import *
from tqdm import tqdm
import regex
import traceback
from sentence_transformers import SentenceTransformer, util
import argparse
import os
import json

os.environ["TOKENIZERS_PARALLELISM"] = "false"

def prompt_formatting(
    generation_prompt,
    doc,
    seed_file,
    topics_list,
    context_len,
    verbose,
    max_top_len=100,
):
    """
    Format prompt to include document and seed topics
    Handle cases where prompt is too long
    - generation_prompt: Prompt for topic generation
    - doc: Document to include in prompt
    - seed_file: File to read seed topics from
    - topics_list: List of topics generated from previous iteration
    - context_len: Max context length for model
    - verbose: Whether to print out results
    - max_top_len: Max length of topics to include in prompt (Modify if necessary)
    """
    sbert = SentenceTransformer("Alibaba-NLP/gte-large-en-v1.5", trust_remote_code=True)
    # Format seed topics to include manually written topics + previously generated topics
    topic_str = open(seed_file, "r").read() + "\n" + "\n".join(topics_list)

    # Calculate length of document, seed topics, and prompt ----
    doc_len = num_tokens_from_messages(doc)
    prompt_len = num_tokens_from_messages(generation_prompt)
    topic_len = num_tokens_from_messages(topic_str)
    total_len = prompt_len + doc_len + topic_len

    # Handle cases where prompt is too long ----
    if total_len > context_len:
        # Truncate document if too long
        if doc_len > (context_len - prompt_len - max_top_len):
            if verbose:
                print(f"Document is too long ({doc_len} tokens). Truncating...")
            doc = truncating(doc, context_len - prompt_len - max_top_len)
            prompt = generation_prompt.format(Document=doc, Topics=topic_str)

        # Truncate topic list to only include topics that are most similar to document
        # Determined by cosine similarity between topic string & document embedding
        else:
            if verbose:
                print(f"Too many topics ({topic_len} tokens). Pruning...")
            cos_sim = {}  # topic: cosine similarity w/ document
            doc_emb = sbert.encode(doc, convert_to_tensor=True)
            for top in topics_list:
                top_emb = sbert.encode(top, convert_to_tensor=True)
                cos_sim[top] = util.cos_sim(top_emb, doc_emb)
            sim_topics = sorted(cos_sim, key=cos_sim.get, reverse=True)

            max_top_len = context_len - prompt_len - doc_len
            seed_len, seed_str = 0, ""
            while seed_len < max_top_len and len(sim_topics) > 0:
                new_seed = sim_topics.pop(0)
                if (
                    seed_len
                    + num_tokens_from_messages(new_seed + "\n")
                    > max_top_len
                ):
                    break
                else:
                    seed_str += new_seed + "\n"
                    seed_len += num_tokens_from_messages(seed_str)
            prompt = generation_prompt.format(Document=doc, Topics=seed_str)
    else:
        prompt = generation_prompt.format(Document=doc, Topics=topic_str)
    return prompt

def generate_topics(
    topics_root,
    topics_list,
    context_len,
    docs,
    seed_file,
    generation_prompt,
    max_tokens,
    verbose,
    ideology,
    early_stop=500,
    max_new_topics=None,  # Allow None to signify no limit
):
    """
    Generate topics from documents using LLMs
    - topics_root, topics_list: Tree and list of topics generated from previous iteration
    - context_len: Max length of prompt
    - docs: List of documents to generate topics from
    - seed_file: File to read seed topics from
    - generation_prompt: Prompt to generate topics with
    - verbose: Whether to print out results
    - ideology: Transcript ideology
    - early_stop: Threshold for topic drought (Modify if necessary)
    - max_new_topics: Maximum number of new topics to add per document, or None for no limit
    """
    sbert = SentenceTransformer('Alibaba-NLP/gte-large-en-v1.5', trust_remote_code=True)
    responses = []
    running_dups = 0
    topic_format = regex.compile("^\[(\d+)\] ([\w\s]+):(.+)")
    
    for i, doc in enumerate(tqdm(docs, desc="Processing ideology " + ideology)):
        prompt = prompt_formatting(
            generation_prompt,
            doc,
            seed_file,
            topics_list,
            context_len,
            verbose,
        )
        try:
            response = generate_text(prompt, max_tokens)
            topics = response.split("\n")
            cos_sim = {}
            updated_response = []  # This will store both valid existing and new topics
            seen_topics = set()     # Track topics to avoid duplicates
            new_topic_count = 0     # Counter to track new topics added

            for t in topics:
                t = t.strip()
                match = regex.match(topic_format, t)
                if match:
                    lvl, name, desc = (
                        int(match[1]),
                        match[2].strip(),
                        match[3].strip(),
                    )

                    # Check if the topic has already been added (to avoid duplicates)
                    if name in seen_topics:
                        print(f"Duplicate topic '{name}' found, skipping...")
                        continue

                    # Compute cosine similarity with the string "No relevant topics found."
                    no_relevant_desc = "No relevant topics found."
                    desc_emb = sbert.encode(desc, convert_to_tensor=True)
                    no_relevant_emb = sbert.encode(no_relevant_desc, convert_to_tensor=True)
                    desc_similarity = util.cos_sim(desc_emb, no_relevant_emb).item()
                    print(f"Desc: {desc} , Not relevant sim: {desc_similarity}")

                    # Skip processing if similarity > 0.65
                    if desc_similarity > 0.65:
                        print(f"Skipping topic '{name}' due to high similarity with 'No relevant topics found.'")
                        continue  # Do not add this topic to updated_response

                    if lvl == 1:
                        # Check if the topic is an existing one (and update count)
                        dups = [s for s in topics_root.descendants if s.name == name]
                        if len(dups) > 0:  # Existing topic, update count
                            print(f"Topic {name} exists, updating...")
                            dups[0].count += 1
                            updated_response.append(t)  # Add to response regardless of max_new_topics
                            seen_topics.add(name)        # Mark this topic as added
                            running_dups += 1
                            if running_dups > early_stop:
                                print("Too many duplicates, early stopping...")
                                return responses, topics_list, topics_root
                        else:
                            # New topic, collect based on similarity
                            topic_emb = sbert.encode(name, convert_to_tensor=True)
                            doc_emb = sbert.encode(doc, convert_to_tensor=True)
                            similarity = util.cos_sim(topic_emb, doc_emb).item()
                            cos_sim[(name, desc)] = similarity

            # Sort new topics by cosine similarity
            sorted_new_topics = sorted(cos_sim.items(), key=lambda item: item[1], reverse=True)

            # Add new topics up to the max_new_topics limit
            for (name, desc), sim in sorted_new_topics:
                if max_new_topics is not None and new_topic_count >= max_new_topics:
                    break  # Respect the max_new_topics limit

                if name not in seen_topics:  # Only add if the topic is not a duplicate
                    print("Adding new topic:", name)
                    new_node = Node(
                        name=name,
                        parent=topics_root,
                        lvl=1,
                        count=1,
                        desc=desc,
                    )
                    topics_list.append(f"[{new_node.lvl}] {new_node.name}")
                    updated_response.append(f"[{new_node.lvl}] {new_node.name}: {desc}")
                    seen_topics.add(name)  # Mark this topic as added
                    new_topic_count += 1  # Increment new topic counter
                    running_dups = 0

            # Join the updated response back into a string
            updated_response_str = "\n".join(updated_response)

            if verbose:
                print(f"Ori: {response}")
                print(f"Document: {i+1}")
                print(f"Topics: {updated_response_str}")
                print(f"Topics List: {topics_list}")
                print("--------------------")

            # Append the updated response instead of the original response
            responses.append(updated_response_str)

        except Exception as e:
            traceback.print_exc()
            responses.append("Error")

    return responses, topics_list, topics_root


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--max_tokens", type=int, default=500, help="max tokens to generate"
    )
    parser.add_argument(
        "--data",
        type=str,
        default="../data/input/sample.jsonl",
        help="data to run generation on",
    )
    parser.add_argument(
        "--prompt_file",
        type=str,
        default="../prompt/generation_1.txt",
        help="file to read prompts from",
    )
    parser.add_argument(
        "--seed_file",
        type=str,
        default="../prompt/seed_1.md",
        help="markdown file to read the seed topics from",
    )
    parser.add_argument(
        "--out_file",
        type=str,
        default="../data/output/generation_1.jsonl",
        help="base filename to write results to",
    )
    parser.add_argument(
        "--topic_file",
        type=str,
        default="../data/output/generation_1.md",
        help="base filename to write topics to",
    )
    parser.add_argument(
        "--ideology", 
        choices=["ANTI_SJW", "ANTI_THEIST", "BLACK", "CONSPIRACY", "LGBT", "LIBERTARIAN", "MRA", "PARTISAN_RIGHT", "PARTISAN_LEFT", "QANON", "RELIGIOUS_CONSERVATIVE", "SOCIAL_JUSTICE", "SOCIALIST", "WHITE_IDENTITARIAN"], 
        help="specify ideology"
    )
    parser.add_argument(
        "--verbose", 
        type=bool, 
        default=False, 
        help="whether to print out results"
    )
    parser.add_argument(
        "--summary", 
        type=bool, 
        default=False, 
        help="whether to use summary transcripts or not"
    )
    args = parser.parse_args()

    # Model configuration ----
    max_tokens = args.max_tokens
    context = 20000
    context_len = context - max_tokens

    # Load data ----
    with open(str(args.data), 'r') as file:
        data = json.load(file)
    
    df = pd.json_normalize(data)

    ideology = str(args.ideology)

    # Filter DataFrame for the current ideology
    df_ideology = df[df['channel.ideology'] == ideology]

    # Check if there is any data for the current ideology
    if df_ideology.empty:
        print(f"No data found for ideology: {ideology}")
    
    # Extract documents
    docs = df_ideology['transcripts'].tolist()

    if args.summary:
        print("Using summary")
        docs = df_ideology['summary'].tolist()

    # Read prompt and seed topics
    generation_prompt = open(args.prompt_file, "r").read()
    topics_root, topics_list = generate_tree(read_seed(args.seed_file))

    # Prompting ----
    responses, topics_list, topics_root = generate_topics(
        topics_root,
        topics_list,
        context_len,
        docs,
        args.seed_file,
        generation_prompt,
        max_tokens,
        args.verbose,
        ideology,
    )

    # Writing results ----
    topic_filename = args.topic_file
    out_filename = args.out_file

    with open(topic_filename, "w") as f:
        print(tree_view(topics_root), file=f)

    try:
        df_ideology = df_ideology.iloc[: len(responses)]
        df_ideology["responses"] = responses
        df_ideology.to_json(out_filename, lines=True, orient="records")
    except Exception as e:
        traceback.print_exc()
        backup_filename = args.out_file.replace(".jsonl", f"_backup.txt")
        with open(backup_filename, "w") as f:
            for line in responses:
                print(line, file=f)

if __name__ == "__main__":
    main()
