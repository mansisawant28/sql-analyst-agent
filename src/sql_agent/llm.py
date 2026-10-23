
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

model= "openai/gpt-oss-120b"

def get_llm(messages:list[dict], tools:list[dict] | None=None):

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set.")   
    client= Groq(api_key=api_key)
    if tools:
        return client.chat.completions.create(model=model, messages=messages, tools=tools)
    return client.chat.completions.create(model=model, messages=messages)
    