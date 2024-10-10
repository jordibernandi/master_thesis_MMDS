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
    sbert = SentenceTransformer("all-MiniLM-L6-v2")
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
    temperature,
    max_tokens,
    top_p,
    verbose,
    early_stop=500,
):
    """
    Generate topics from documents using LLMs
    - topics_root, topics_list: Tree and list of topics generated from previous iteration
    - context_len: Max length of prompt
    - docs: List of documents to generate topics from
    - seed_file: File to read seed topics from
    - generation_prompt: Prompt to generate topics with
    - verbose: Whether to print out results
    - early_stop: Threshold for topic drought (Modify if necessary)
    """
    top_emb = {}
    responses = []
    running_dups = 0
    topic_format = regex.compile("^\[(\d+)\] ([\w\s]+):(.+)")

    for i, doc in enumerate(tqdm(docs)):
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
            for t in topics:
                t = t.strip()
                if regex.match(topic_format, t):
                    groups = regex.match(topic_format, t)
                    lvl, name, desc = (
                        int(groups[1]),
                        groups[2].strip(),
                        groups[3].strip(),
                    )
                    if lvl == 1:
                        dups = [s for s in topics_root.descendants if s.name == name]
                        if len(dups) > 0:  # Update count if topic already exists
                            print("Topic exists, updating...")
                            dups[0].count += 1
                            running_dups += 1
                            if running_dups > early_stop:
                                print("Too many duplicates, early stopping...")
                                return responses, topics_list, topics_root
                        else:  # Add new topic if topic doesn't exist
                            print("Topic not exists, adding...")
                            new_node = Node(
                                name=name,
                                parent=topics_root,
                                lvl=lvl,
                                count=1,
                                desc=desc,
                            )
                            topics_list.append(f"[{new_node.lvl}] {new_node.name}")
                            running_dups = 0
                    else:
                        if verbose:
                            print("Lower-level topics detected. Skipping...")
            if verbose:
                print(f"Document: {i+1}")
                print(f"Topics: {response}")
                print("--------------------")
            responses.append(response)

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
        "--temperature", type=float, default=0.0, help="temperature for generation"
    )
    parser.add_argument("--top_p", type=float, default=0.0, help="top-p for generation")
    parser.add_argument(
        "--data",
        type=str,
        default="data/input/sample.jsonl",
        help="data to run generation on",
    )
    parser.add_argument(
        "--prompt_file",
        type=str,
        default="prompt/generation_1.txt",
        help="file to read prompts from",
    )
    parser.add_argument(
        "--seed_file",
        type=str,
        default="prompt/seed_1.md",
        help="markdown file to read the seed topics from",
    )
    parser.add_argument(
        "--out_file",
        type=str,
        default="data/output/generation_1.jsonl",
        help="file to write results to",
    )
    parser.add_argument(
        "--topic_file",
        type=str,
        default="data/output/generation_1.md",
        help="file to write topics to",
    )
    parser.add_argument(
        "--verbose", type=bool, default=False, help="whether to print out results"
    )
    args = parser.parse_args()

    # Model configuration ----
    max_tokens, temperature, top_p = (
        args.max_tokens,
        args.temperature,
        args.top_p,
    )
    context = 10000
    context_len = context - max_tokens

    # Load data ----
    # Load JSON files
    with open(str(args.data), 'r') as file:
        covid_data = json.load(file)
    
    # Convert to DataFrame
    df = pd.json_normalize(covid_data)
    
    print(df.shape)
    
    # Extract necessary columns
    texts = df[['summary', 'channel.ideology']]

    texts = texts[texts['channel.ideology'] == "BLACK"]
    
    # List of ideologies
    ideologies = ["BLACK"]

    # df = pd.read_json(str(args.data), lines=True)
    # docs = df["text"].tolist()

    if 'summary' in texts.columns:
        print("The 'summary' column is available in the DataFrame.")
        docs = texts['summary'].tolist()
    else:
        print("The 'summary' column is not available in the DataFrame. Using 'transcripts'")
        docs = texts['transcripts'].tolist()

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
        temperature,
        max_tokens,
        top_p,
        args.verbose,
    )

    # Writing results ----
    with open(args.topic_file, "w") as f:
        print(tree_view(topics_root), file=f)

    try:
        df = df.iloc[: len(responses)]
        df["responses"] = responses
        df.to_json(args.out_file, lines=True, orient="records")
    except Exception as e:
        traceback.print_exc()
        with open(f"data/output/generation_1_backup.txt", "w") as f:
            for line in responses:
                print(line, file=f)


if __name__ == "__main__":
    main()
