# Grace - Voice Assistant

A Python-based voice assistant that can capture audio, transcribe speech using OpenAI's Whisper, and provide text-to-speech responses.

## Prerequisites

- Python 3.11 (recommended)
- macOS (for Homebrew installation)
- Microphone access
- OpenAI API key

## Installation

### 1. Create python 3.11 venv
```bash
brew install python@3.11
python3.11 -m venv venv
source grace_env/bin/activate
```

### 2. Install python dependencies
```bash
pip install -r requirements.txt
```

### 3. Install system dependencies
```bash
brew install ffmpeg
```

### 3. Set Up Environment Variables 
- Create a `.env` file in the root directory
- Add your OpenAI API key to the `.env` file
- Add your venv into the `.env` file
```
OPENAI_API_KEY=your_api_key_here
venv/
```

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
