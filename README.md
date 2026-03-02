# Grace - Voice Assistant

A Python-based voice assistant that can capture audio, transcribe speech using OpenAI's Whisper, and provide text-to-speech responses.

## Prerequisites

- Python 3.11 (recommended)
- macOS (for Homebrew installation)
- Microphone access
- OpenAI API key

## Installation

### 1. Create python 3.11 venv
- brew install python@3.11
- python3.11 -m venv venv

### 2. Install python dependencies
- pip install -r requirements.txt

### 3. Install system dependencies
- brew install ffmpeg

### 3. Set Up Environment Variables 
- Create a `.env` file in the root directory
- Add your OpenAI API key to the `.env` file
- Add your venv into the `.env` file

### 4. Installation Issues
   - Try using `pip3` instead of `pip`
   - Make sure your virtual environment is activated

### Activating Virtual Environment
```bash
# Activate
source venv/bin/activate

# Deactivate
deactivate
```
