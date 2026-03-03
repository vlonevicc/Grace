import whisper
from openai import OpenAI
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import pyttsx3
from dotenv import load_dotenv
import os
import pvporcupine
import pyaudio
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

load_dotenv()

keyword_path = os.path.join(
    os.path.dirname(__file__),  # folder where wake.py is at
    "..",                       # goes up to Grace/
    "Hey-Grace_en_mac_v4_0_0",  # enter Hey-Grace folder
    "Hey-Grace_en_mac_v4_0_0.ppn"
)

def main():
    # Create Porcupine wake word engine
    porcupine = pvporcupine.create(
        access_key=os.getenv("PORCUPINE_ACCESS_KEY"),
        keyword_paths=[keyword_path]
    )

    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

    print("Listening for wake word... Say 'Hey Grace'!")


if __name__ == "__main__":
    main()