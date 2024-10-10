import pandas as pd
from utils import *
import numpy as np
from tqdm import trange
import traceback
from sentence_transformers import SentenceTransformer, util
import argparse
import os
import json

os.environ["TOKENIZERS_PARALLELISM"] = "false"


def tree_formatting(topics_root):
    """
    Get the string representation of the topic tree & list of branch strings
    - topics_root: Root node of topic tree
    """
    tree_str = ""
    for node in topics_root.descendants:
        tree_str += "\t" * (node.lvl - 1) + f"""[{node.lvl}] {node.name}\n"""
    branch_str = branch_to_str(topics_root)
    tree_str = "\n".join(branch_str)
    return tree_str, branch_str


def assign_topics(
    topics_root,
    docs,
    assignment_prompt,
    context_len,
    max_tokens,
    verbose,
    max_top_len=1700,
):
    """
    Return documents with topics assigned to them
    - topics_root: Root node of topics
    - docs: List of documents to assign topics to
    - assignment_prompt: Prompt to assign topics with
    - context_len: Max length of prompt
    - max_tokens: Max tokens to generate
    - verbose: Whether to print out results
    - max_top_len: Max length of topics to include in prompt (Modify if necessary)
    """
    sbert = SentenceTransformer("Alibaba-NLP/gte-large-en-v1.5", trust_remote_code=True)
    tree_str, branch_str = tree_formatting(topics_root)
    prompted_docs, res = [], []
    topic_format = regex.compile("^\[(\d+)\] ([\w\s]+):(.+)")

    for i in trange(len(docs), desc="Processing Documents"):
        doc = docs[i]
        cos_sim = {}
        doc_emb = sbert.encode(doc, convert_to_tensor=True)

        # Include only most relevant topics such that the total length
        # of tree_str is less than max_top_len
        if num_tokens_from_messages(tree_str) > max_top_len:
            for top in branch_str:
                top_emb = sbert.encode(top, convert_to_tensor=True)
                cos_sim[top] = util.cos_sim(top_emb, doc_emb)
            top_top = sorted(cos_sim, key=cos_sim.get, reverse=True)

            seed_len = 0
            seed_str = ""
            while seed_len < max_top_len and len(top_top) > 0:
                new_seed = top_top.pop(0)
                if (
                    seed_len
                    + num_tokens_from_messages(new_seed)
                    > max_top_len
                ):
                    break
                else:
                    seed_str += new_seed + "\n"
                    seed_len += num_tokens_from_messages(seed_str)
        else:
            seed_str = tree_str

        # Truncate document if too long
        max_doc_len = (
            context_len
            - num_tokens_from_messages(assignment_prompt)
            - num_tokens_from_messages(seed_str)
        )
        if num_tokens_from_messages(doc) > max_doc_len:
            print(
                f"Truncating document from {num_tokens_from_messages(doc)} to {max_doc_len}"
            )
            doc = truncating(doc, max_doc_len)

        try:
            prompt = assignment_prompt.format(Document=doc, tree=seed_str)
            
            result = generate_text(prompt, max_tokens)
            topics = result.split("\n")
            unique_topics = list(set(topics))
            updated_results = []
            for t in unique_topics:
                t = t.strip()
                match = regex.match(topic_format, t)
                if match:
                    lvl, name, desc = (
                        int(match[1]),
                        match[2].strip(),
                        match[3].strip(),
                    )

                    # Compute cosine similarity with the string "No relevant topics found."
                    no_relevant_desc = "No relevant information found."
                    desc_emb = sbert.encode(desc, convert_to_tensor=True)
                    no_relevant_emb = sbert.encode(no_relevant_desc, convert_to_tensor=True)
                    desc_similarity = util.cos_sim(desc_emb, no_relevant_emb).item()
                    print(f"Desc: {desc} , Not relevant sim: {desc_similarity}")

                    # Skip processing if similarity > 0.65
                    if desc_similarity > 0.65:
                        print(f"Skipping topic '{name}' due to high similarity with 'No relevant topics found.'")
                        continue  # Do not add this topic to updated_response
                    else:
                        updated_results.append(t)
            
            updated_results_str = "\n".join(updated_results)
            res.append(updated_results_str)

            if verbose:
                print(f"Document: {i+1}")
                print(f"Response: {res}")
                print("--------------------")
        except Exception as e:
            result = "Error"
            res.append("Error")
            traceback.print_exc()
        prompted_docs.append(doc)
    return res, prompted_docs


def main():
    parser = argparse.ArgumentParser()
  
    parser.add_argument(
        "--max_tokens", type=int, default=2000, help="max tokens to generate"
    )
    parser.add_argument(
        "--data",
        type=str,
        default="data/input/sample.jsonl",
        help="data to run assignment on",
    )
    parser.add_argument(
        "--prompt_file",
        type=str,
        default="prompt/assignment.txt",
        help="file to read prompts from",
    )
    parser.add_argument(
        "--topic_file",
        type=str,
        default="data/output/generation_1.md",
        help="file to read topics from",
    )
    parser.add_argument(
        "--out_file",
        type=str,
        default="data/output/assignment.jsonl",
        help="file to write results to",
    )
    parser.add_argument(
        "--ideology", 
        choices=["ANTI_SJW", "ANTI_THEIST", "BLACK", "CONSPIRACY", "LGBT", "LIBERTARIAN", "MRA", "PARTISAN_RIGHT", "PARTISAN_LEFT", "QANON", "RELIGIOUS_CONSERVATIVE", "SOCIAL_JUSTICE", "SOCIALIST", "WHITE_IDENTITARIAN"], 
        help="specify ideology"
    )
    parser.add_argument(
        "--verbose", type=bool, default=False, help="whether to print out results"
    )

    args = parser.parse_args()

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

    assignment_prompt = open(args.prompt_file, "r").read()
    topics_root, _ = generate_tree(read_seed(args.topic_file))

    # Prompting ----
    responses, prompted_docs = assign_topics(
        topics_root,
        docs,
        assignment_prompt,
        context_len,
        max_tokens,
        args.verbose,
    )

    # Writing results ----
    try:
        df_ideology = df_ideology.iloc[: len(responses)]
        df_ideology["prompted_docs"] = prompted_docs
        df_ideology["responses"] = responses        
        df_ideology.to_json(args.out_file, lines=True, orient="records")
    except Exception as e:
        traceback.print_exc()
        backup_filename = args.out_file.replace(".jsonl", f"_backup.txt")
        with open(backup_filename, "w") as f:
            for line in responses:
                print(line, file=f)

if __name__ == "__main__":
    main()
