import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
from ML.constants import HF_TOKEN

load_dotenv()

def build_commit_prompt(features, code_diff):
    """
     Builds the prompt.

    Args:
        features: Features extracted from the commit.
        code_diff: Code in the commit.

    Returns:
        string: LLM Prompt.

    """
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

Using a manual scoring heuristic, evaluate how suspicious this commit is. The scoring rules are:

- Add 2 points if the commit message is very short or generic (e.g., "update", "fix", "test", ".", "temp", "change")
- Add 2 points if the number of lines changed is 2 or fewer
- Add 2 points if suspicious patterns like print/debug/log statements are found
- Add 2 points if the percentage of suspicious lines found is greater than 50%
- Add 2 points if the lines changed in the commit is greater than 10000

Maximum possible score: 10

⚠️ DO NOT explain your reasoning. DO NOT include any text other than the score line.
Just return the score in this format: 
score: <score>/10

"""

def llm_response(features,code_diff):
    """
     Derives a commit score from a llm.

    Args:
        features: Features extracted from the commit.
        code_diff: Code in the commit.

    Returns:
        string: LLM Response.

    """
    client = InferenceClient(
        provider="novita",
        api_key=os.getenv(HF_TOKEN),
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

    return completion.choices[0].message.content
