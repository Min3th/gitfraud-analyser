import asyncio
import requests 
from dotenv import load_dotenv
import os
import tempfile
import platform
import subprocess
import click
from Heuristics.features import extract_features, score_commit
import tkinter as tk
from tkinter import messagebox
import asyncio
import os
import re
from dotenv import load_dotenv 
from Apis.github import fetch_global_commits
from constants import GITHUB_TOKEN
from .ML.model import llm_response


load_dotenv()

def show_popup(title,message):
    """
     GUI to display result.

    Args:
        title: Title in header of GUI

    Returns:
        GUI

    """
    root=tk.Tk()
    root.withdraw()
    messagebox.showinfo(title,message)
    root.destroy()

def get_score(username):
    """
     Construct the score from both heuristics and the llm.

    Args:
        username: Username of the github user

    Returns:
        llm,heuristic score through GUI.

    """
    token = os.getenv(GITHUB_TOKEN)
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
        diffs = commit.get("diffs")
        response_text = llm_response(features, diffs)
        match = re.search(r"score:\s*(\d+)/10", response_text)
        if match:
            llm_score += int(match.group(1))
            llm_divisor += 10  
        else:
            print("⚠️ Could not extract score from LLM response. Skipping this commit.",response_text)
    
    final_score = (score/divisor)*100
    final_llm_score = (llm_score/llm_divisor)*100
    print(f"Heuristic Score: {final_score}%")
    print(feedback)
    print(f"LLM_Score: {final_llm_score}%")
    show_popup("GitFraud Analysis",f"Heuristic Score: {final_score:.2f}%\nLLM Score: {final_llm_score:.2f}%")

# Defines the CLI inputs.
@click.command()
@click.option('--username','-u',required=True,help="Github username")
def main_entry(username):
    get_score(username)

if __name__ == "__main__":
    # analyze()
    username = input("Enter github username: ")
    # collect_and_save(username)
    get_score(username)
