from dotenv import load_dotenv
from openai import OpenAI
from transcribe_audio import transcribe_audio2
import pyttsx3

load_dotenv()
client = OpenAI()
engine = pyttsx3.init()

# text to speech 
def voice(text):
    engine.say(text)
    engine.runAndWait()

def generate_response():
    # input given after transcribed
    userInput = transcribe_audio2()
    # sending response to gpt
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=f"Kindly respond to this message in a conversational manner:\n{userInput}"
    )
    # prints response in terminal & out loud
    answer = response.output_text
    print(answer)
    voice(answer)

    return answer
generate_response()

#this is just to commit