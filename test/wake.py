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

# constants for silence detection
SILENCE_THRESHOLD = 200
SILENCE_DURATION = 0.5

# audio recording 
SAMPLE_RATE = 44100
RECORDING_SECONDS = 20

load_dotenv()

keyword_path = os.path.join(
    os.path.dirname(__file__),  # folder where wake.py is at
    "..",                       # goes up to Grace/
    "Hey-Grace_en_mac_v4_0_0",  # enter Hey-Grace folder
    "Hey-Grace_en_mac_v4_0_0.ppn"
)

def listen_for_wake_word():
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

    try:
        while True:
            pcm = np.frombuffer(audio_stream.read(porcupine.frame_length), dtype=np.int16)
            keyword_index = porcupine.process(pcm)
            if keyword_index >= 0:
                print("Wake word detected!")
                break
    except Exception as e:
            print(f"Error occurred: {e}")
    finally:
        audio_stream.stop_stream()
        audio_stream.close()
        pa.terminate()
        porcupine.delete()

    return True

def record_audio():
    print("Recording audio...")
    audio = sd.rec(int(SAMPLE_RATE * RECORDING_SECONDS), samplerate=SAMPLE_RATE, channels=1)
    sd.wait()


    # save audio
    write("output.wav", SAMPLE_RATE, np.int16(audio * 32767))

    # load whisper model and transcribe audio
    model = whisper.load_model("base", device="cpu")
    result = model.transcribe("output.wav")

    print(result["text"])

    return result["text"]

def speak_response(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    engine.stop()

def main():
    while True:
        # wait for wake word
        if listen_for_wake_word():
            transcribed_text = record_audio()

            if transcribed_text:
                speak_response(transcribed_text)
                break

if __name__ == "__main__":
    main()