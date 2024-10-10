## YouTube Video Transcriber

This section provides an overview of the Python scripts and data files used for generating transcripts of YouTube videos, particularly for the COVID-19 case study dataset.

We evaluated two key Automatic Speech Recognition (ASR) and Speaker Diarization (SD) libraries for transcript generation:

- **`whisper-nemo-lib`**: 
  - Combines Whisper ASR with NeMo Diarization. Available on [GitHub](https://github.com/MahmoudAshraf97/whisper-diarization).

- **`whisper-pyannote-lib`**: 
  - Uses Whisper ASR with Pyannote Diarization. Available on [GitHub](https://github.com/thomasmol/cog-whisper-diarization).

### Python Scripts:

- **`transcriber.py`**: 
  - Pipeline script for downloading audio and running ASR + SD on `test_data` to evaluate transcription accuracy.
  
- **`transcriber_real.py`**: 
  - Pipeline for downloading audio and running ASR + SD on the full COVID-19 dataset.
  
- **`WER.ipynb`**: 
  - Jupyter notebook for evaluating the Word Error Rate (WER) of the ASR outputs.
  
- **`WDER.ipynb`**: 
  - Jupyter notebook for evaluating the Word Diarization Error Rate (WDER) of the SD outputs.

### Data Files:

- **`test_data`**: 
  - Ground truth dataset containing 28 manually annotated transcripts, reviewed by two independent annotators.
  
- **`Whisper-Nemo`**: 
  - Results from running `whisper-nemo-lib` on the 28 ground truth videos.

- **`Whisper-Pyannote`**: 
  - Results from running `whisper-pyannote-lib` on the same 28 ground truth videos.

- **`result_audio_files_BEFORE_COVID_large-v3`**: 
  - Transcription results using `whisper-nemo-lib` on the pre-COVID-19 dataset.

- **`result_audio_files_AFTER_COVID_large-v3`**: 
  - Transcription results using `whisper-nemo-lib` on the post-COVID-19 dataset.
