import whisper
import numpy as np
import pyaudio
import pvporcupine
import time
import os
from dotenv import load_dotenv
from mizzou_db import MizzouKnowledge
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.audio.g1_audio_client import AudioClient

# load env and models
load_dotenv()

model = whisper.load_model("base", device="cpu")
knowledge = MizzouKnowledge(ingest=False)

# Audio settings
MIC_INDEX = None  # Set to None to use default input device
SAMPLE_RATE = 16000
CHUNK_SIZE = 1024
SILENCE_THRESHOLD = 700
SILENCE_DURATION = 1.5

# Unitree setup
ChannelFactoryInitialize(0, "eth0")
client = AudioClient()
client.Init()
client.SetTimeout(10.0)
client.SetVolume(100)

# Wake word model
keyword_path = os.path.join(
    os.path.dirname(__file__),
    "..",
    "Hey-Grace_en_raspberry-pi_v4_0_0.ppn"
)


def record_audio(pa):
    print("Listening...")

    stream = pa.open(
        rate=SAMPLE_RATE,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=CHUNK_SIZE,
        input_device_index=MIC_INDEX
    )

    # To clear initial noise
    for _ in range(int(SAMPLE_RATE / CHUNK_SIZE * 0.5)): 
        stream.read(CHUNK_SIZE, exception_on_overflow=False)    

    frames = []
    last_voice_time = time.time()

    while True:
        data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
        frames.append(data)

        audio_np = np.frombuffer(data, dtype=np.int16)
        volume = np.abs(audio_np).mean()

        if volume > SILENCE_THRESHOLD:
            last_voice_time = time.time()

        if time.time() - last_voice_time > SILENCE_DURATION:
            break

    stream.stop_stream()
    stream.close()

    audio = np.frombuffer(b"".join(frames), dtype=np.int16).astype(np.float32) / 32768.0 #whispers format
    return audio

# transcribe using whisper
def transcribe(audio):
    result = model.transcribe(audio, fp16=False)
    text = result["text"].strip()
    print("You:", text)
    return text

# respond using robot TTS
def speak(text):
    print("Grace:", text)
    client.TtsMaker(text, 1)

# handle user query by asking mizzou questions and responding with TTS
def handle_query(text):
    if not text:
        return
    answer = knowledge.ask(text)
    speak(answer)


def main():
    pa = pyaudio.PyAudio()
    porcupine = pvporcupine.create(
        access_key=os.getenv("PORCUPINE_ACCESS_KEY"),
        keyword_paths=[keyword_path]
    )

    stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length,
        input_device_index=MIC_INDEX
    )

    print("Say 'Hey Grace'...")
    last_wake_time = 0
    wake_cool = 2


    try:
        while True:
            pcm = np.frombuffer(
                stream.read(porcupine.frame_length, exception_on_overflow=False),
                dtype=np.int16
            )

            if porcupine.process(pcm) >= 0:
                speak("Yes?")
                stream.stop_stream()
                time.sleep(0.5)  # brief pause before recording
                audio = record_audio(pa)
                text = transcribe(audio)
                handle_query(text)
                stream.start_stream()
                print("Listening for wake word...")

    except KeyboardInterrupt:
        print("Exiting...")

    finally:
        stream.stop_stream()
        stream.close()
        porcupine.delete()
        pa.terminate()


if __name__ == "__main__":
    main()