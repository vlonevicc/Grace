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