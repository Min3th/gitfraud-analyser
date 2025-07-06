import os
import csv
from dotenv import load_dotenv 
from .features import extract_features
from Apis.github import fetch_global_commits

load_dotenv()

def collect_and_save(username,output_file="data/commits2.csv"):
    token = os.getenv("GITHUB_TOKEN")
    commits = fetch_global_commits(username,token)

    if not commits:
        print("No commits found for the user!")
        return
    
    field_names = ["username","repo","message","msg_length","is_generic_msg","hour_of_day","lines_added",
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
