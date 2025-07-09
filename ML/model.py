import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()

def build_commit_prompt(features, code_diff):
    return f"""
A developer made the following commit:

Commit Message: "{features['message']}"
Lines Changed: {features['lines_added']}
Suspicious Lines: {features['sus_lines']}
Files Changed: {features['files_changed']}
Time of Commit: {features['time_of_day']}
Repo: {features['repo']}
Possible Copy: {features.get('possible_copy', False)}

Code Changes:
{code_diff}

Based on the features and the code diff, does this commit appear to be fake or automated,
The response should be in the format commit_message | one line reasoning | verdict. The verdict should be "FAKE" or 
"GENUINE". No other response should be given other than the format i gave.
"""

def llm_response(features,code_diff):
    client = InferenceClient(
        provider="novita",
        api_key=os.getenv("HF_TOKEN"),
    )

    prompt = build_commit_prompt(features,code_diff)

    completion = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.3",
        messages=[
            {
                "role": "user",
                "content": f"""
        {prompt}
    """
            }
        ],
    )

    return completion.choices[0].message

