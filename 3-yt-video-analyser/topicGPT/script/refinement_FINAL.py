import pandas as pd
import torch
from utils import *
import regex
import traceback
from sentence_transformers import SentenceTransformer, util
import argparse
import os
from tqdm import tqdm

os.environ["TOKENIZERS_PARALLELISM"] = "false"


def topic_pairs(topic_sent, all_pairs, threshold=0.5, num_pair=2):
    """
    Return the most similar topic pairs and the pairs that have been prompted so far
    - topic_sent: List of topic sentences (topic label + description)
    - all_pairs: List of all topic pairs being prompted so far
    - threshold: Threshold for cosine similarity
    - num_pair: Number of pairs to return
    """
    print("topic_sent", topic_sent)
    print("all_pairs",  all_pairs)
    # Calculate cosine similarity between all pairs of sentences
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # sbert = SentenceTransformer("all-MiniLM-L6-v2", device=device)
    sbert = SentenceTransformer("Alibaba-NLP/gte-large-en-v1.5", trust_remote_code=True)
    embeddings = sbert.encode(topic_sent, convert_to_tensor=True)
    cosine_scores = util.cos_sim(embeddings, embeddings).cpu()
    over, pairs = [], []
    for i in range(len(cosine_scores)):
        for j in range(i+1, len(cosine_scores)):
            pairs.append({"index": [i, j], "score": cosine_scores[i][j].item()})

    # Sort and choose num_pair pairs with scores higher than a certain threshold
    pairs = sorted(pairs, key=lambda x: x["score"], reverse=True) # TODO: do w/ numpy argsort
    count, idx = 0, 0
    while count < num_pair and idx < len(pairs):
        i, j = pairs[idx]["index"]
        if float(pairs[idx]["score"]) > threshold:
            if (sorted([topic_sent[i], topic_sent[j]]) not in all_pairs) and (
                topic_sent[i] != topic_sent[j]
            ):
                over.append([topic_sent[i], topic_sent[j]])
                all_pairs.append(sorted([topic_sent[i], topic_sent[j]]))
                count += 1
        idx += 1
    return [item for sublist in over for item in sublist], all_pairs


def merge_topics(
    topics_root,
    topics_node,
    prompt,
    max_tokens,
    verbose,
):
    """
    Prompt model to merge similar topics
    - topics_root: Root node of topic tree
    - topics_node: List of all nodes in topic tree
    - prompt: Prompt to be used for refinement
    - max_tokens: Max tokens to generate
    - verbose: Whether to print out results
    """
    # Get new pairs to be merged
    topic_sent = [
        f"[{topic.lvl}] {topic.name}: {topic.desc}" for topic in topics_root.descendants
    ]
    labels = [f"[{topic.lvl}] {topic.name}" for topic in topics_root.descendants]
    new_pairs, all_pairs = topic_pairs(
        topic_sent, all_pairs=[], threshold=0.8, num_pair=2
    )

    responses, removed, orig_new = [], [], {}
    # Pattern to match generations
    top_pattern = regex.compile(
        "^\[(\d+)\]([\w\s\-',]+)(?:[:\(\)\w\s\/])*?:([\w\s,\.\-\/;']+) \(((?:\[\d+\] [\w\s\-',]+(?:, )*)+)\)$"
    )
    # Pattern to match original topics being merged
    orig_pattern = regex.compile("(\[(?:\d+)\](?:[\w\s\-',]+)),?")

    iteration = 0
    max_iterations = len(topic_sent) // 2  # Rough estimation of max iterations
    
    # Wrap the main loop with tqdm to track progress
    with tqdm(total=max_iterations, desc="Merging topic pairs") as pbar:  
        print("new_pairs", new_pairs)          
        while len(new_pairs) > 1:
            iteration += 1
            # Format topics to be merged in the prmpt
            inp, inp_label = [], []
            for topic in new_pairs:
                label = topic.split(":")[0]
                if label not in inp_label:
                    inp.append(topic)
                    inp_label.append(label)
            refiner_input = "\n".join(inp)
            refiner_prompt = prompt.format(Topics=refiner_input)
            if verbose:
                print(refiner_input)
    
            try:
                response = generate_text(refiner_prompt, max_tokens)
                print("RESPONSE", response)
                responses.append(response)
                merges = response.split("\n")
                for merge in merges:
                    match = regex.match(regex.compile(top_pattern), merge.strip())
                    if match:
                        lvl, name, desc = (
                            int(match.group(1)),
                            match.group(2).strip(),
                            match.group(3).strip(),
                        )
                        origs = [
                            t.strip(", ")
                            for t in regex.findall(orig_pattern, match.group(4).strip())
                        ]
                        orig_count = 0
                        add = False
                        if len(origs) > 1:
                            for node in topics_root.descendants:
                                if (
                                    f"[{node.lvl}] {node.name}" in origs
                                    and f"[{node.lvl}] {node.name}" != f"[{lvl}] {name}"
                                ):
                                    orig_new[
                                        f"[{node.lvl}] {node.name}:"
                                    ] = f"[{lvl}] {name}:"
                                    if (
                                        f"[{node.lvl}] {node.name}: {node.desc}"
                                        in topic_sent
                                    ):
                                        if verbose:
                                            print(
                                                f"Removing [{node.lvl}] {node.name}: {node.desc}\n"
                                            )
                                        topic_sent.remove(
                                            f"[{node.lvl}] {node.name}: {node.desc}"
                                        )
                                    if f"[{node.lvl}] {node.name}" != f"[{lvl}] {name}":
                                        removed.append(f"[{node.lvl}] {node.name}")
                                    orig_count += node.count
                                    topics_node.remove(node)
                                    node.parent = None
                                    add = True
                            if add and f"[{lvl}] {name}" not in removed:
                                if (
                                    f"[{lvl}] {name}: {desc}" not in topic_sent
                                    and f"[{lvl}] {name}" not in labels
                                ):
                                    new_node = Node(
                                        parent=topics_root,
                                        lvl=lvl,
                                        name=name,
                                        desc=desc,
                                        count=orig_count,
                                    )
                                    if verbose:
                                        print(f"Adding [{lvl}] {name}: {desc}\n")
                                    topic_sent.append(f"[{lvl}] {name}: {desc}")
                                    topics_node.append(new_node)
                                else:
                                    if verbose:
                                        print(f"[{lvl}] {name} already exists!\n")
                                    for node in topics_root.descendants:
                                        if f"[{node.lvl}] {node.name}" == f"[{lvl}] {name}":
                                            node.count += orig_count
            except:
                print("Error when calling API!")
                traceback.print_exc()
            print("--------------------")
            # Choose new pairs
            new_pairs, all_pairs = topic_pairs(
                topic_sent, all_pairs, threshold=0.8, num_pair=2
            )
            print("new_pairs 2", new_pairs)
            pbar.update(1)
            print("#Iteration: " + str(iteration))
    return responses, topics_root, orig_new


def remove_topics(topics_root, verbose, threshold=0.01):
    """
    Remove low-frequency topics from topic tree
    - topics_root: Root node of topic tree
    - verbose: Whether to print out results
    - Threshold: Percentage of all topic counts
    """
    topic_count = sum([node.count for node in topics_root.descendants])
    threshold = topic_count * threshold
    for node in topics_root.descendants:
        if node.count < threshold and node.lvl == 1:
            if verbose:
                print(f"Removing {node.name} ({node.count} counts)")
            node.parent = None
    return topics_root


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--max_tokens", type=int, default=500, help="max tokens to generate"
    )
    parser.add_argument(
        "--prompt_file",
        type=str,
        default="prompt/refinement.txt",
        help="file to read prompts from",
    )
    parser.add_argument(
        "--generation_file",
        type=str,
        default="data/output/generation_1.jsonl",
        help="file to read generation results from",
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
        default="data/output/refinement_1.md",
        help="file to write merged topics to",
    )
    parser.add_argument(
        "--updated_file",
        type=str,
        default="data/output/refinement_1.jsonl",
        help="file to update merged topics to",
    )
    parser.add_argument(
        "--verbose", type=bool, default=False, help="whether to print out results"
    )
    parser.add_argument(
        "--remove", type=bool, default=False, help="option to remove minor topics"
    )
    parser.add_argument(
        "--mapping_file",
        type=str,
        default="data/output/refiner_mapping.json",
        help="file to write refined mapping to",
    )
    parser.add_argument(
        "--refined_again",
        type=str,
        default="refiner",
        help="Is this the second time you run refinement on the topics?",
    )

    args = parser.parse_args()

    # Model configuration ----
    max_tokens = args.max_tokens

    # Load data ----
    topics_root, topics_node = generate_tree(read_seed(args.topic_file))

    # Prompting ----
    refinement_prompt = open(args.prompt_file, "r").read()
    responses, updated_topics_root, mapping = merge_topics(
        topics_root,
        topics_node,
        refinement_prompt,
        max_tokens,
        args.verbose,
    )
    if args.remove:
        updated_topics_root = remove_topics(
            updated_topics_root, args.verbose, threshold=0.01
        )

    if len(responses) > 0:
        # Writing updated topics ----
        with open(args.out_file, "w") as f:
            print(tree_view(updated_topics_root), file=f)

        # Writing orig-new mapping ----
        try:
            current = open(args.mapping_file).read().strip().split("\n")
            if args.verbose:
                print(f"Writing to existing mapping file {args.mapping_file}")
        except:
            current = []
        with open(args.mapping_file, "w") as f:
            for key, value in mapping.items():
                current.append(f"{key} -> {value}")
            for topic in current:
                print(topic, file=f)

        # Updating generation.jsonl with new topics ----
        updated_responses = []
        df = pd.read_json(args.generation_file, lines=True)
        if args.refined_again == True:
            responses = df["refined_responses"].tolist()
        else:
            responses = df["responses"].tolist()
        for response in responses:
            splitted = response.split("\n")
            sub_list = []
            for s in splitted:
                for key, value in mapping.items():
                    if key != value and s.startswith(key):
                        s = s.replace(key, value)
                        if args.verbose:
                            print(f"Replacing {key} with {value}")
                sub_list.append(s)
            updated_responses.append("\n".join(sub_list))
        df["refined_responses"] = updated_responses
        df.to_json(args.updated_file, lines=True, orient="records")
    else: 
        print("No updated/merged topics!")


if __name__ == "__main__":
    main()
