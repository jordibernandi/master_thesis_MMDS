## YouTube Video Analyser

This section provides a prelimary experiments that we conducted on our COVID-19 dataset. We performed topic modeling using [topicGPT](https://github.com/chtmp223/topicGPT) combined with LLM summarization.

### Python Scripts:

- **`summarizer.py`**: 
  - Summarize transcripts.

- **`topicGPT/script/generation_1_FINAL.py`**: 
  - We did some finetuning from the original `generation_1.py` and modify the code to work with Llama 3.1 & run with local GPU.

- **`topicGPT/script/assignment_FINAL.py`**: 
  - We did some finetuning from the original `assignment.py` and modify the code to work with Llama 3.1 & run with local GPU.

- **`topicGPT/script/refinement_FINAL.py`**: 
  - Modify the code to work with Llama 3.1 & run with local GPU. (did not use it at the end)

- **`topicGPT/script/generation_2_FINAL.py`**: 
  - We did some finetuning from the original `generation_2.py` and modify the code to work with Llama 3.1 & run with local GPU. (did not use it at the end)

- **`generation_1_run`**: 
  - Implement `generation_1_FINAL.py` on all political ideologies.

- **`assignment_run`**: 
  - Implement `assignment_FINAL.py` on all political ideologies.

- **`refinement_run`**: 
  - Implement `refinement_FINAL.py` on all political ideologies.

- **`generation_2_run`**: 
  - Implement `generation_2_FINAL.py` on all political ideologies.

- **`legacy`**: 
  - Contains some experiments of using BERTopic for topic modeling.

### Data Files:

- **`visualization/EDA.ipynb`**: 
  - Showing transcript statistics

- **`visualization/Topic_EDA.ipynb`**: 
  - Showing results from generation_1 across different ideologies and covid time period.
  
- **`Analysis.ipynb`**: 
  - Topic descriptions in topic assignments are combined together per ideology & a global topic --> summarize the topic descriptions --> compare the cosine similarity, and compare the results.

- **`UMAP_Subtopic`**: 
  - Experiments to cluster sub topics that are generated from running `generation_2`.

