import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

client = InferenceClient(
    provider="novita",
    api_key=os.getenv("HF_TOKEN"),
)

code_snip = """
def add(a,b):
    return a+b
"""

completion = client.chat.completions.create(
    model="mistralai/Mistral-7B-Instruct-v0.3",
    messages=[
        {
            "role": "user",
            "content": f"""
    Please check if the below function will return the addition of two numbers.
    {code_snip}
"""
        }
    ],
)

print(completion.choices[0].message)
