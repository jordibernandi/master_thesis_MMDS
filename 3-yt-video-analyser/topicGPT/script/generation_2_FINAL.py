import pandas as pd
from utils import *
import regex
import traceback
import argparse
from tqdm import tqdm
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm 

def doc_label(df, topics_list):
    """
    Add labels to each document based on the topics generated for it.
    - df: dataframe of documents
    - topics_list: list of topics
    """
    pattern = regex.compile("^\[(\d+)\] ([\w\s]+):(.+)")
    all_topics = []
    for line in df["responses"].tolist():
        if type(line) == str:
            line = line.split("\n")
            line_topics = []
            for topic in line:
                if regex.match(pattern, topic):
                    groups = regex.match(pattern, topic).groups()
                    lvl, name = int(groups[0]), groups[1]
                    if f"[{lvl}] {name}" in topics_list:
                        line_topics.append(f"[{lvl}] {name}")
            if len(line_topics) > 0:
                all_topics.append(line_topics)
            else:
                all_topics.append(["None"])
        else:
            all_topics.append(["None"])
    return all_topics

# Cosine similarity filtering function
def filter_similar_subtopics(subtopics, threshold=0.90):
    # Load a pre-trained sentence transformer model
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    embeddings = model.encode(subtopics)
    similarity_matrix = util.cos_sim(embeddings, embeddings).numpy()
    
    unique_subtopics = []
    seen_indices = set()
    
    for i, subtopic in enumerate(subtopics):
        if i in seen_indices:
            continue
        similar = False
        for j in range(i):
            if j in seen_indices:
                continue
            if similarity_matrix[i][j] > threshold:
                similar = True
                break
        if not similar:
            unique_subtopics.append(subtopic)
        seen_indices.add(i)
        
    return unique_subtopics

def generate_topics(
    df,
    topics_root,
    topics_node,
    gen_prompt,
    context_len,
    max_tokens,
    verbose,
    max_topic_num=50,
):
    """
    Generate subtopics for each top-level topic.
    - df: dataframe of documents
    - topics_root: root node of the topic tree
    - topics_node: current node of the topic tree
    - gen_prompt: generation prompt
    - context_len: length of the context
    - max_tokens: max tokens to generate
    - verbose: whether to print out results
    - max_topic_num: maximum number of subtopics to generate for each top-level topic

    """
    res, docs = [], []  # Containing document and result set for each prompt
    pattern = regex.compile(
        "^\[(\d+)\] ([\w\s\-'\&,]+)(\(Document(?:s)?: ((?:(?:\d+)(?:(?:, )?)|-)+)\)([:\-\w\s,.\n'\&]*?))?$"
    )
    second_pattern = regex.compile(
        "^\[(\d+)\] ([\w\s\-'\&,]+)(?:\(Document(?:s)?: ((?:(?:\d+)(?:(?:, )?)|-)+)\):([\-\n\w\s.,'\&]+))"
    )
    all_nodes = [node for node in topics_root.descendants]
    
    for parent_top in tqdm(all_nodes):
        if parent_top.count > len(df) * 0.01 and len(parent_top.children) == 0:
            # Current top-level topic ----
            current_topic = f"[{parent_top.lvl}] {parent_top.name}"
            if verbose:
                print("Current topic:", current_topic)

            # Retrieving documents for the current topic ----
            relevant_docs = df[df["most_relevant_topic"].apply(lambda x: current_topic in x)][
                "summary"
            ].tolist()
            doc_len = (
                context_len
                - num_tokens_from_messages(gen_prompt)
                - max_tokens
            )
            doc_prompt = construct_document(relevant_docs, doc_len)
            names = []

            # Iterating through relevant documents ----
            for doc in doc_prompt:
                sub_result, prompt_top = [], []
                adding_subtopic = False
                # Formatting previously generated subtopics ----
                if len(names) == 0:
                    prev = current_topic
                else:
                    list_top = list(set(names))[:max_topic_num]
                    prev = current_topic + "\n\t" + "\n\t".join(list_top)
                prompt = gen_prompt.format(Topic=prev, Document=doc)
                print("Prompt: ", prompt)
                if verbose:
                    print(
                        f"Prompt length: {num_tokens_from_messages(prompt)}"
                    )

                try:
                    result = generate_text(prompt, max_tokens)
                    if verbose:
                        print("Subtopics:", result)
                    if result.count("[2]") == 0 or result.count("[1]") > 1:
                        continue

                    # Split the result by lines for processing each subtopic
                    subtopics = result.strip().split("\n")

                    # Step 1: Find and remove the item that starts with "[1]"
                    first_level_topic = None
                    for topic in subtopics:
                        if topic.startswith('[1]'):
                            first_level_topic = topic
                            break

                    # Step 2: Remove the [1] topic from the list if it exists
                    if first_level_topic:
                        subtopics.remove(first_level_topic)

                    # Step 3: Convert the rest of the list to a set and back to a list to remove duplicates
                    unique_subtopics = list(set(subtopics))

                    # unique_subtopics = filter_similar_subtopics(unique_subtopics)

                    # Step 4: Insert the [1] topic at the beginning of the list
                    if first_level_topic:
                        unique_subtopics.insert(0, first_level_topic)

                    # Process valid subtopics
                    for top in unique_subtopics:
                        top = top.strip()
                        print("TOP: ", top)
                        if regex.match(pattern, top):
                            match = regex.match(pattern, top)
                            lvl, name = int(match.group(1)), match.group(2).strip()
                            if lvl == 2 and adding_subtopic:
                                if regex.match(second_pattern, top):
                                    second_groups = regex.match(second_pattern, top)
                                    source, desc = (
                                        second_groups.group(3).strip(),
                                        second_groups.group(4).strip(),
                                    )
                                    if desc != "":
                                        source = [
                                            list(
                                                range(
                                                    int(s.split("-")[0]),
                                                    int(s.split("-")[-1]) + 1,
                                                )
                                            )
                                            for s in source.split(", ")
                                        ]
                                        source = [s for i in source for s in i]
                                        names.append(f"[{lvl}] {name}")
                                        prompt_top.append(
                                            f"[{lvl}] {name} (Count: {len(source)}): {desc}"
                                        )
                                        if verbose:
                                            print(
                                                "Added topic:",
                                                f"[{lvl}] {name} (Count: {len(source)}): {desc}",
                                            )
                                else:
                                    if verbose:
                                        print(f"Not a match: {top}")
                            else:
                                if current_topic == f"[{lvl}] {name}":
                                    if verbose:
                                        print("Adding subtopics for", current_topic)
                                    prompt_top.append(
                                        f"{current_topic} (Count: 0): description"
                                    )
                                    adding_subtopic = True
                                else:
                                    if verbose:
                                        print(
                                            "Output doesn't match top-level topics:",
                                            current_topic,
                                            f"[{lvl}] {name}",
                                        )
                                    adding_subtopic = False
                        else:
                            if verbose:
                                print(f"Not a match: {top}")
                    unique_subtopics_str = "\n".join(unique_subtopics)
                    res.append(unique_subtopics_str)
                    docs.append(doc)
                    topics_root, topics_node = tree_addition(
                        topics_root, topics_node, prompt_top
                    )
                except Exception as e:
                    res.append("Error")
                    traceback.print_exc()
                    continue
                if verbose:
                    print("--------------------------------------------------")
    return res, docs

def get_most_relevant_topic(summary, topics):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    sbert = SentenceTransformer('Alibaba-NLP/gte-large-en-v1.5', trust_remote_code=True, device=device)
    # Combine the summary and topics into a list for encoding
    topic_sent = [summary] + topics

    # Encode the summary and topics using Sentence Transformer
    embeddings = sbert.encode(topic_sent, convert_to_tensor=True)
    
    # Calculate cosine similarity between the summary (first embedding) and the topics
    cosine_scores = util.cos_sim(embeddings[0], embeddings[1:])
    
    # Move cosine scores to CPU for further processing (argmax) and convert to numpy
    cosine_scores = cosine_scores.cpu().numpy().flatten()

    # Get the index of the most similar topic
    most_similar_index = cosine_scores.argmax()

    # Return the most related topic
    return topics[most_similar_index]

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--max_tokens", type=int, default=6000, help="max tokens to generate"
    )
    parser.add_argument(
        "--seed_file",
        type=str,
        default="data/output/generation_1.md",
        help="file to read seed from",
    )
    parser.add_argument(
        "--data",
        type=str,
        default="data/input/generation_1.jsonl",
        help="data to run generation on",
    )
    parser.add_argument(
        "--prompt_file",
        type=str,
        default="prompt/generation_2.txt",
        help="file to read prompts from",
    )
    parser.add_argument(
        "--out_file",
        type=str,
        default="data/output/generation_2.jsonl",
        help="file to write results to",
    )
    parser.add_argument(
        "--topic_file",
        type=str,
        default="data/output/generation_2.md",
        help="file to write topics to",
    )
    parser.add_argument(
        "--verbose", type=bool, default=False, help="whether to print out results"
    )
    args = parser.parse_args()

    # Model configuration ----
    max_tokens = args.max_tokens
    context = 16000
    context_len = context - max_tokens

    # Load data ----
    df = pd.read_json(str(args.data), lines=True)
    generation_prompt = open(args.prompt_file, "r").read()
    topics_root, topics_node = generate_tree(read_seed(args.seed_file))
    topics_list = [f"[{node.lvl}] {node.name}" for node in topics_root.descendants]
    df["topics"] = doc_label(df, topics_list)
    # Excluding rows with more than one unique topic//"None" ----
    df["num_topics"] = df["topics"].apply(lambda x: len(set(x)))
    df = df[df["topics"].apply(lambda x: x != ["None"])].reset_index(drop=True)
    print("DF", df)
    tqdm.pandas()
    df['most_relevant_topic'] = df.progress_apply(lambda row: get_most_relevant_topic(row['summary'], row['topics']), axis=1)
    # df = df[df["num_topics"] == 1].drop(columns=["num_topics"]).reset_index(drop=True)
    print("DF", df)
    if args.verbose:
        print("Number of remaining documents for prompting:", len(df))

    # Prompting ----
    res, docs = generate_topics(
        df,
        topics_root,
        topics_node,
        generation_prompt,
        context_len,
        max_tokens,
        args.verbose,
    )

    # Writing results ----
    with open(args.topic_file, "w") as f:
        print(tree_view(topics_root), file=f)

    result_df = pd.DataFrame({"summary": docs, "topics": res})
    result_df.to_json(args.out_file, orient="records", lines=True)


if __name__ == "__main__":
    main()
