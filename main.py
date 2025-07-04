import requests 
from datetime import datetime 
from dotenv import load_dotenv
import os
import tempfile
import platform
import subprocess
import click
from ML.collect_data import collect_and_save



load_dotenv()

def open_in_editor(text):
    with tempfile.NamedTemporaryFile('w+',delete=False,suffix='.txt',encoding='utf-8') as tmp_file:
        tmp_file.write(text)
        tmp_filename = tmp_file.name

    # In future check whether this works for all OSes
    if platform.system() == "Windows":
        os.startfile(tmp_filename)
    elif platform.system() == 'Darwin':
        subprocess.call(['open',tmp_filename])
    else:
        subprocess.call(['xdg-open',tmp_filename])

def fetch_global_commits(username,token):
    headers = {
        "Accept":"application/vnd.github.cloak-preview",
        "Authorization": f"Bearer {token}"
    }

    url = f"https://api.github.com/search/commits?q=author:{username}&sort=author-date&order=desc&per_page=10"

    response = requests.get(url, headers=headers)
    if response.status_code != 200 :
        print(f"Error: {response.status_code} - {response.text}")
        return[]
    
    results = response.json()
    commits = []

    for item in results.get("items",[]):
        commit = item["commit"]
        repo = item["repository"]["full_name"]
        sha = item["sha"]
        owner,repo_name = repo.split("/")

        diffs = fetch_commit_diff(owner,repo_name,sha,token)

        commits.append({
            "repo":repo,
            "message": commit["message"],
            "date": commit["author"]["date"],
            "url": item["html_url"],
            "diffs": diffs
        })

    return commits

def fetch_commit_diff(username,repo,sha,token=None):
    headers = {
        "Accept":"application/vnd.github+json"
    }
    if token:
        headers["Authorization"]=f"Bearer {token}"
    
    url = f"https://api.github.com/repos/{username}/{repo}/commits/{sha}"
    response = requests.get(url,headers=headers)

    if response.status_code != 200:
        print(f"Error fetching commit diff: {response.status_code}")
        return None
    
    commit_detail = response.json()
    diffs = []
    for file in commit_detail.get("files",[]):
        if "patch" in file:
            diffs.append({
                "filename":file["filename"],
                "patch":file["patch"]
            })

    return diffs

def score_commit(commit):
    score = 0

    short_or_generic_messages = ["update","fix","test",".","temp","change"]
    if commit["message"].strip().lower() in short_or_generic_messages:
        score += 2

    total_lines = 0
    suspicious_patterns = ["print(","console.log(","System.out.println(","echo "]
    suspicious_lines = 0

    if commit["diffs"]:
        for diff in commit["diffs"]:
            patch = diff["patch"]
            added_lines = [line for line in patch.split("\n") if line.startswith("+") and not line.startswith("+++")]
            total_lines =+ len(added_lines)

            for line in added_lines:
                if any(p in line for p in suspicious_patterns):
                    suspicious_lines += 1

    if total_lines <= 3:
        score += 2
    if suspicious_lines > 0:
        score += 2
    if suspicious_lines > 3:
        score += 1 

    return score

@click.command()
@click.option('--username','-u',required=True,help="Github username")

def analyze(username):
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("⚠️  GitHub token not found in environment. Please set GITHUB_TOKEN in your .env file.")
        return

    global_commits = fetch_global_commits(username,token)
    output = ""
    for i, commit in enumerate(global_commits, 1):
        fraud_score = score_commit(commit)
        output += f"{i}. [{commit['repo']}] {commit['message']} ({commit['date']})\n"
        # output += f"   {commit['url']}\n"
        score_percentage = (fraud_score/5)*100
        output += f"   ⚠️ Suspicion Score: {score_percentage}%\n"
        if commit['diffs']:
            for diff in commit['diffs']:
                output += f"     - {diff['filename']}\n"
                # output += f"{diff['patch']}\n\n"
        else:
            output += "     (No diffs)\n\n"
    
    open_in_editor(output)

if __name__ == "__main__":
    # analyze()
    username = input("Enter github username: ")
    collect_and_save(username,label="real")
