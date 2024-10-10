## YouTube Video Scraper

This section details the key Python scripts and data files used for scraping and processing YouTube video metadata, particularly for the COVID-19 case study.

### Python Scripts:

- **`scraper.py`**: 
  - Implements channel chunking and leverages multi-processing to efficiently scrape YouTube videos.
  
- **`functions.py`**: 
  - Contains helper functions used by `scraper.py` for scraping video metadata with the PyTube library.

- **`EDA.ipynb`**
  - Contains some data analysis and selection for COVID-19 case study dataset.

### Data Files:

- **`vis_channel_stats.csv`**: 
  - The original list of YouTube videos sourced from [GitHub](https://github.com/markledwich2/Recfluence).
  
- **`checked_channels_v2.csv`**: 
  - A filtered version of `vis_channel_stats.csv`, focusing on independent YouTubers.

- **`3mil_videos_metadata`**
  - Contains 3 million rows metadata, the results of scraping all YouTube videos metadata from YouTube channels listed in `checked_channels_v2.csv`. Can be downloaded [here](https://drive.google.com/drive/u/0/folders/11XkzCTerbk3651zyY_K6DHBNsGtB266B).

- **`before_covid_top_videos_df.csv`**: 
  - Contains metadata for the top YouTube videos used in the COVID-19 case study, **before COVID-19** (February 1, 2019 – January 31, 2020).
  
- **`after_covid_top_videos_df.csv`**: 
  - Contains metadata for the top YouTube videos used in the COVID-19 case study, **after COVID-19** (February 1, 2020 – January 31, 2021).
