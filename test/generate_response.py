from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
client = OpenAI()

def generate_response():
    # input given after transcribed

    userInput = "Hey, my name is Keh"
    #
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=f"Kindly respond to this message in a conversational manner:\n{userInput}"
    )

    answer = response.output_text
    print(answer)

    return answer
generate_response()

# Load environment variables from .env file
#load_dotenv()

# Get the OpenAI API key
# openai_api_key = os.getenv("OPENAI_API_KEY")

# client = OpenAI(api_key=openai_api_key)

# try:
#     response = client.responses.create(
#         model="gpt-4.1-mini",
#         input="hello",
#         max_output_tokens=20
#     )

#     print("API key is valid and working!")
#     print("Response:", response.output_text)

# except Exception as e:
#     print(f"API key test failed with error: {e}")