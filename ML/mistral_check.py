# import os
# from dotenv import load_dotenv
# from huggingface_hub import InferenceClient

# load_dotenv()

# client = InferenceClient(
#     provider="novita",
#     api_key=os.getenv("HF_TOKEN"),
# )

# code_snip = """
# def add(a,b):
#     return a+b
# """

# code_check = """
# username|repo|message|msg_length|is_generic_msg|hour_of_day|lines_added|sus_lines|files_changed
# Min3th|Min3th/gitfraud-analyser|add fetch commit diff function to github.py|7|0|22|0|0|3
# Min3th|Min3th/gitfraud-analyser|minor fix|2|0|0|0|0|1
# Min3th|Min3th/gitfraud-analyser|fix main.py to use collect and save|7|0|23|0|0|3
# Min3th|Min3th/gitfraud-analyser|add function to collect and save data from commits.|9|0|22|0|0|1
# Min3th|Min3th/gitfraud-analyser|add function to extract features|5|0|22|0|0|2
# Min3th|Min3th/gitfraud-analyser|fix issues in setup.py|4|0|0|0|0|2
# Min3th|Min3th/gitfraud-analyser|modify main.py to use click|5|0|23|0|0|2
# Min3th|Min3th/gitfraud-analyser|add files related for packaging|5|0|23|0|0|5
# Min3th|Min3th/gitfraud-analyser|add function to check for fraudulent commits|7|0|15|0|0|1
# Min3th|Min3th/gitfraud-analyser|fix minor issues and removed unused functions|7|0|15|0|0|1
# """

# completion = client.chat.completions.create(
#     model="mistralai/Mistral-7B-Instruct-v0.3",
#     messages=[
#         {
#             "role": "user",
#             "content": f"""
#     Below are details related to last 10 commits of a repo. Each value is seperated by a |.For each commit , can you estimate
# whether its a real commit , or whether it could be a fake commit (some people fake commits to increase the no of contributions).The output 
# should be  "real" or "fake" , take a row for each commit.
#     {code_check}
# """
#         }
#     ],
# )

# print(completion.choices[0].message)

import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()

client = InferenceClient(
    provider="hf-inference",
    api_key=os.getenv("HF_TOKEN"),
)

result = client.feature_extraction(
    "Today is a sunny day and I will get some ice cream.",
    model="intfloat/multilingual-e5-large-instruct",
)

print(result)
