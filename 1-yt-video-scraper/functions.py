from pytube import Channel
import os
from tqdm import tqdm
import pandas as pd

def check_video(chunk_id, row):
  channel_id = row['CHANNEL_ID']
  channel_title = row['CHANNEL_TITLE']

  channel_url = f'https://www.youtube.com/channel/{channel_id}'

  channel = Channel(channel_url)

  data = []

  print(f"{channel_title}  - Download started...")

  for v in tqdm(channel.videos, desc="Processing videos - " + row['CHANNEL_TITLE']):
    try:
      print("Chunk: " + str(chunk_id) + " - " + v.title)
      s = v.streams
      title = v.title
    except KeyError:
        title = ""
    except:
        title = ""

    view_count = v.vid_info.get("videoDetails", {}).get("viewCount")
    views = int(view_count) if view_count is not None else 0

    length_seconds = v.vid_info.get('videoDetails', {}).get('lengthSeconds')
    length = int(length_seconds) if length_seconds is not None else 0
    
    d = {
        "CHANNEL_ID": channel_id,
        "VIDEO_ID": v.video_id,
        "VIDEO_TITLE": title,
        "VIDEO_VIEWS": views,
        "VIDEO_PUBLISH_DATE": v.publish_date,
        "VIDEO_DESCRIPTION": v.description,
        "VIDEO_KEYWORDS": v.keywords,
        "VIDEO_LENGTH": length,
        "VIDEO_RATING": v.rating,
    }
    data.append(d)

  return data

def check(i, chunk):
  data = []
  for row in tqdm(chunk.iterrows(), total=len(chunk), desc="Processing chunk " + str(i)):
    new_row = check_video(i, row[1])
    data.extend(new_row)
  
  new_df = pd.DataFrame(data)
  new_df.to_csv(f'./results/videos_chunk_{i}.csv', index=False)