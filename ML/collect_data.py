import os
import csv
import re
from dotenv import load_dotenv 
from .features import extract_features,score_commit
from Apis.github import fetch_global_commits
import asyncio
from .model import llm_response
import tkinter as tk
from tkinter import messagebox


load_dotenv()

def show_popup(title,message):
    root=tk.Tk()
    root.withdraw()
    messagebox.showinfo(title,message)
    root.destroy()

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
    llm_score = 0
    divisor = 0
    llm_divisor = 0
    feedback = {}
    for commit in commits:
        features = extract_features(commit)
        commit_score,commit_feedback = score_commit(features)
        score += commit_score
        feedback.update(commit_feedback)
        divisor += 8
        message = commit.get("message","").strip().lower()
        features["message"] = message
        diffs = commit.get("diffs")
        response_text = llm_response(features, diffs)
        match = re.search(r"score:\s*(\d+)/10", response_text)
        if match:
            llm_score += int(match.group(1))
            llm_divisor += 10  # normalize out of 10
        else:
            print("⚠️ Could not extract score from LLM response. Skipping this commit.",response_text)
    
    final_score = (score/divisor)*100
    final_llm_score = (llm_score/llm_divisor)*100
    print(f"Heuristic Score: {final_score}%")
    print(feedback)
    print(f"LLM_Score: {final_llm_score}%")
    show_popup("GitFraud Analysis",f"Heuristic Score: {final_score:.2f}%\nLLM Score: {final_llm_score:.2f}%")
