import whisper
from openai import OpenAI
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import pyttsx3
from dotenv import load_dotenv
import os
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

# Load environment variables from .env file
#load_dotenv()

# Get the OpenAI API key
# openai_api_key = os.getenv("OPENAI_API_KEY")

# client = OpenAI(api_key=openai_api_key)

# try:
#     response = client.responses.create(
#         model="gpt-4.1-mini",
#         input="hello",
#         max_output_tokens=20
#     )

#     print("API key is valid and working!")
#     print("Response:", response.output_text)

# except Exception as e:
#     print(f"API key test failed with error: {e}")

# sample rate
sample_rate = 44100
seconds = 5

# audio
print("Recording...")
recording = sd.rec(int(seconds * sample_rate), samplerate=sample_rate, channels=1)
sd.wait()

# saves the audio
write("test.wav", sample_rate, np.int16(recording * 32767))

model = whisper.load_model("base", device="cpu")
result = model.transcribe("test.wav")

# prints the transcription result
print(result["text"])

# speaks the audio
engine = pyttsx3.init()
engine.say(result["text"])
engine.runAndWait()
engine.stop()
