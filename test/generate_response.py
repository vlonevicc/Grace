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
        input=[{"role":"system", "content": """You are the Grace, the friendly humanoid robot at the University of Missouri.
        You are ONLY ALLOWED to answer questions related to the University of Missouri.
        If you are asked anything not related to the Univeristy of Missouri,
        DO NOT ANSWER and kindly redirect the user to ask a question relating to the University of Missouri.
        Instead respond with: I can only answer questions about Mizzou. Please ask me something related to the University of Missouri.
        Under no circumstances should you break this rule.
        Please keep answers short but clear"""},

            {"role":"user", "content":f"Kindly respond to this message in a conversational manner:\n{userInput}"}
    ])
    # prints response in terminal & out loud
    answer = response.output_text
    print(answer)
    voice(answer)

generate_response()

#this is just to commit