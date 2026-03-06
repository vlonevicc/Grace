import whisper
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import pyttsx3
from dotenv import load_dotenv
import os
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

# sample rate
sample_rate = 44100
seconds = 5

model = whisper.load_model("base", device="cpu")

def transcribe_audio2():
    #audio
    print("Recording...")
    recording = sd.rec(int(seconds * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()
    # saves the audio
    write("test.wav", sample_rate, np.int16(recording * 32767))

    result = model.transcribe("test.wav")

    # prints the transcription result
    print(result["text"])
    return result["text"]

# speaks the audio
#engine = pyttsx3.init()
#engine.say(result["text"])
#engine.runAndWait()
#engine.stop()
