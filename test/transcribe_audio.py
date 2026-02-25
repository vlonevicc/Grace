import whisper
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import pyttsx3

# sample rate
sample_rate = 44100
seconds = 5

# audio
print("Recording...")
recording = sd.rec(int(seconds * sample_rate), samplerate=sample_rate, channels=1)
sd.wait()

# saves the audio
write("test.wav", sample_rate, np.int16(recording * 32767))

model = whisper.load_model("base")
result = model.transcribe("test.wav")

# prints the transcription result
print(result["text"])

# speaks the audio
engine = pyttsx3.init()
engine.say(result["text"])
engine.runAndWait()


