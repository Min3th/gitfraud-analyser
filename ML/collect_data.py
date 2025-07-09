import os
import csv
from dotenv import load_dotenv 
from .features import extract_features,score_commit
from Apis.github import fetch_global_commits
import asyncio
from .mistral_check import build_commit_prompt

load_dotenv()

def collect_and_save(username,output_file="data/commits2.csv"):
    token = os.getenv("GITHUB_TOKEN")
    commits = asyncio.run(fetch_global_commits(username,token))

    if not commits:
        print("No commits found for the user!")
        return
    
    field_names = ["username","repo","message","msg_length","is_generic_msg","time_of_day","lines_added",
                   "sus_lines","files_changed"]
    
    os.makedirs("data",exist_ok=True)

    with open(output_file,mode="a",newline="",encoding="utf-8") as file:
        writer = csv.DictWriter(file,fieldnames=field_names,delimiter='|')
        if file.tell() == 0:
            writer.writeheader()
        for commit in commits:
            features = extract_features(commit)
            row = {
                "username":username,
                "repo":commit["repo"],
                "message":commit["message"],
            }

            row.update(features)
            writer.writerow(row)

    print(f"✅ {len(commits)} commits saved for {username}.")

def get_score(username,output_file="data/score.csv"):
    token = os.getenv("GITHUB_TOKEN")
    commits = asyncio.run(fetch_global_commits(username,token))
    score = 0
    divisor = 0
    feedback = {}
    llm_response = ""
    for commit in commits:
        features = extract_features(commit)
        commit_score,commit_feedback = score_commit(features)
        score += commit_score
        feedback.update(commit_feedback)
        divisor += 8
        message = commit.get("message","").strip().lower()
        features["message"] = message
        diffs = commit.get("diffs")
        llm_response=build_commit_prompt(features,diffs)
    
    print(llm_response)
    final_score = (score/divisor)*100
    print(f"{final_score}%")
    print(feedback)
