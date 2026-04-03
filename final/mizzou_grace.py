import whisper
from openai import OpenAI
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import pyttsx3
from dotenv import load_dotenv
import os
import io
import wave
import pvporcupine
import pyaudio
import warnings
from simulator2_execute import start_mouth, stop_mouth, set_talking, set_listening


warnings.filterwarnings("ignore", category=UserWarning)

# Load enviorments and models
load_dotenv()
model = whisper.load_model("tiny", device="cpu")
client = OpenAI()

# constants for silence detection
SILENCE_THRESHOLD = 600
SILENCE_DURATION = 2.0

# audio recording 
SAMPLE_RATE = 16000

load_dotenv()

keyword_path = os.path.join(
    os.path.dirname(__file__),  # folder where wake.py is at
    "..",                       # goes up to Grace/
    "Hey-Grace_en_mac_v4_0_0",  # enter Hey-Grace folder
    "Hey-Grace_en_mac_v4_0_0.ppn"
)

def listen_for_wake_word(pa):
    # Create Porcupine wake word engine
    porcupine = pvporcupine.create(
        access_key=os.getenv("PORCUPINE_ACCESS_KEY"),
        keyword_paths=[keyword_path]
    )

    
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
    finally:
        audio_stream.stop_stream()
        audio_stream.close()
        porcupine.delete()

    return True

def record_audio(pa, chunk_size, sample_rate=SAMPLE_RATE, silence_duration=SILENCE_DURATION, silence_threshold=SILENCE_THRESHOLD):
    print("Recording audio...")

    audio_stream = pa.open(
        rate=sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=chunk_size
    )

    frames = []
    silence = int(silence_duration / (chunk_size / sample_rate)) # calculates silence chunks to determine the silence duration
    silence_counter = 0
    


    try:
        while True:
            data = audio_stream.read(chunk_size)
            frames.append(data) # store audio data

            # Convert bytes to numpy int16 to compute volume
            audio_np = np.frombuffer(data, dtype=np.int16)
            volume = np.abs(audio_np).mean()

            if volume > silence_threshold:
                silence_counter = 0
            else:
                silence_counter += 1

            if silence_counter > silence:
                break
    finally:
        audio_stream.stop_stream()
        audio_stream.close()
        

    # Wrap into WAV buffer
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))
    wav_buffer.seek(0)


    with open("output.wav", "wb") as f:
        f.write(wav_buffer.getvalue())

    # transcribe audio
    result = model.transcribe("output.wav")

    print(result["text"])

    return result["text"]


# text to speech 
def voice(text):
    set_talking()
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    engine.stop()
    set_listening()

def generate_response(userInput):

    # sending response to gpt
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[{"role":"system", "content": """You are the Grace, the friendly humanoid robot at the University of Missouri - Columbia.
        You are ONLY ALLOWED to answer questions related to the University of Missouri - Columbia.
        If you are asked anything not related to the Univeristy of Missouri - Columbia,
        DO NOT ANSWER and kindly redirect the user to ask a question relating to the University of Missouri - Columbia.
        Instead respond with: I can only answer questions about Mizzou. Please ask me something related to the University of Missouri - Columbia.
        Under no circumstances should you break this rule. Use mizzou.edu as a reference for all your answers.
        Please keep answers short but clear"""},

            {"role":"user", "content":f"Kindly respond to this message in a conversational manner:\n{userInput}"}
    ])
    # prints response in terminal & out loud
    answer = response.output_text
    print(answer)
    voice(answer)


def main():
    start_mouth()
    pa = pyaudio.PyAudio()

    try:
        while True:
            # wait for wake word
            if listen_for_wake_word(pa):
                transcribed_text = record_audio(pa, chunk_size=512)

                if transcribed_text:
                    generate_response(transcribed_text)
                
    except KeyboardInterrupt:
            pass
    
    finally:
        pa.terminate()


if __name__ == "__main__":
    main()
