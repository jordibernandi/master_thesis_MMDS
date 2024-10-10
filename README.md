### Decoding YouTube Political Content: Understanding Topics in Different Ideologies

This research introduces a novel dataset of political YouTube video transcripts, categorized by political ideologies, addressing the need for scalable analysis of political content on the platform. Using advanced Automated Speech Recognition (ASR) technology, specifically Whisper, in conjunction with speaker diarization (SD) tools, the study evaluates the accuracy of transcript generation in the context of political content. These tools were used to generate over 10,000 transcripts focused on COVID-19-related content. A web app was developed to provide easy access to the dataset, enabling researchers to explore YouTube political content across ideological groups. Preliminary experiments using TopicGPT for topic modeling revealed key themes and shifts in discourse during major events like COVID-19.

---
This research is divided into 4 components:

#### 1. Scraping (yt-video-scraper)
Process of how we scraped 3 millons metadata of political videos on YouTube, and selected around 10,000 videos of COVID-19 case study dataset.

#### 2. Transcribing (yt-video-transcriber)
Process of how we generated the transcripts of COVID-19 case study dataset.

#### 3. Analysing (yt-video-analyser)
Process of how we did a preliminary experiment to analyse the topic discussed between political ideological groups before and after the COVID-19 outbreak using topic modelling.

#### Show Casing (yt-video-webapp)
To facilitate easy dissemination and provide a more readable version of the transcripts, the dataset is available in multiple file formats.
