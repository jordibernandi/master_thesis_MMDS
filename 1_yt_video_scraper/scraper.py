import os
from tqdm import tqdm
import pandas as pd

df_all = pd.read_csv('./data/checked_channels_V2.csv')
print("All data: ", df_all.shape)

df_all_filtered = df_all[(df_all['CHANNEL_AVAILABLE'] == 'YES')]
print("Filtered available: ", df_all_filtered.shape)

def chunk_dataframe(df, chunk_size):
    chunks = []
    current_chunk = pd.DataFrame()
    current_size = 0

    for _, row in df.iterrows():
        if current_size + row['CHANNEL_VIDEO_COUNT'] <= chunk_size:
            current_chunk = pd.concat([current_chunk, pd.DataFrame([row])], ignore_index=True)
            current_size += row['CHANNEL_VIDEO_COUNT']
        else:
            chunks.append(current_chunk)
            current_chunk = pd.DataFrame([row])
            current_size = row['CHANNEL_VIDEO_COUNT']

    if not current_chunk.empty:
        chunks.append(current_chunk)

    return chunks

chunk_size_limit = 10000
chunks = chunk_dataframe(df_all_filtered, chunk_size_limit)

def extract_file_ids(folder_path):
    file_ids = []
    # List all files in the folder
    files = os.listdir(folder_path)
    # Iterate over each file
    for file_name in files:
        # Check if it's a CSV file
        if file_name.endswith('.csv'):
            # Extract the file ID from the filename
            file_id = file_name.split('_')[-1].split('.')[0]
            file_ids.append(file_id)
    return file_ids

folder_path = './results_old'
file_ids = extract_file_ids(folder_path)
# print(file_ids)

filtered_chunks = []

for i, chunk in enumerate(chunks):
    if str(i) not in file_ids and str(i) != "179":
        chunk_obj = {"chunk_id": i, "chunk": chunk}
        filtered_chunks.append(chunk_obj)

# print("Chunks Size: ", len(filtered_chunks))

for i, chunk in enumerate(chunks):
    # if i == 238 or i == 236 or i == 361 or i == 189 or i == 232 or i == 309 or i == 241:
    # if chunk[0]['CHANNEL_TITLE'] == 'Hiroshi Hayashi':
        # print(f"Chunk {i}:")
        # print(chunk)
        # print('-' * 30)
    if 'CHANNEL_TITLE' in chunk.columns and chunk['CHANNEL_TITLE'].iloc[0] == 'Hiroshi Hayashi':
        print(f"Chunk {i}:")
        print(chunk)
        print('-' * 30)

# import multiprocessing
# from functions import check

# print("CPU: ", multiprocessing.cpu_count())

# with multiprocessing.Pool(32) as pool:
#     pool.starmap(check, [(chunk['chunk_id'], chunk['chunk']) for chunk in filtered_chunks])
