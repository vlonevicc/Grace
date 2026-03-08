import whisper
import pyaudio
import wave
import numpy as np
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

# sample rate
sample_rate = 16000
seconds = 5
chunk_size = 1024

model = whisper.load_model("base", device="cpu")

def transcribe_audio2():
    #audio
    print("Recording...")
    pa = pyaudio.PyAudio()

    # Open audio stream
    stream = pa.open(
        rate=sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=chunk_size
    )

    frames = []
    num_chunks = int(sample_rate / chunk_size * seconds)

    # Record audio
    for _ in range(num_chunks):
        data = stream.read(chunk_size)
        frames.append(data)

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    pa.terminate()

    # Save the recorded audio to a WAV file
    with wave.open("test.wav", "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))

    # prints the transcription result
    result = model.transcribe("test.wav")
    print(result["text"])
    return result["text"]

# speaks the audio
#engine = pyttsx3.init()
#engine.say(result["text"])
#engine.runAndWait()
#engine.stop()
