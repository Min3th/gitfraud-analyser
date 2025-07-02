import requests 
from datetime import datetime 
from dotenv import load_dotenv
import os
import tempfile
import platform
import subprocess

load_dotenv()

def open_in_editor(text):
    with tempfile.NamedTemporaryFile('w+',delete=False,suffix='.txt') as tmp_file:
        tmp_file.write(text)
        tmp_filename = tmp_file.name

    # In future check whether this works for all OSes
    if platform.system() == "Windows":
        os.startfile(tmp_filename)
    elif platform.system() == 'Darwin':
        subprocess.call(['open',tmp_filename])
    else:
        subprocess.call(['xdg-open',tmp_filename])

def fetch_last_10_commits(username,token=None):
    headers = {
        "Accept":"application/vnd.github + json"
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    repos_url = f"https://api.github.com/users/{username}/repos"
    repos_response = requests.get(repos_url,headers = headers)
    repos = repos_response.json()

    if not isinstance(repos, list):
        print("Error fetching repositories:", repos)
        return[]
    
    all_commits = []

    for repo in repos:
        repo_name = repo["name"]
        commits_url = f"https://api.github.com/repos/{username}/{repo_name}/commits?author={username}&per_page=10"
        commits_response = requests.get(commits_url,headers=headers)
        commits = commits_response.json()

        if isinstance(commits,list):
            for commit in commits:
                commit_data = {
                    "repo":repo_name,
                    "message": commit["commit"]["message"],
                    "date":commit["commit"]["author"]["date"],
                    "url":commit["html_url"]
                }
                all_commits.append(commit_data)

    all_commits.sort(key=lambda c: datetime.fromisoformat(c["date"].replace("Z","+00:00")), reverse = True )   
    return all_commits[:10]

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

username = input("Enter github username: ")
token = os.getenv("GITHUB_TOKEN")
latest_commits = fetch_last_10_commits(username)
global_commits = fetch_global_commits(username,token)

# for i, commit in enumerate(latest_commits, 1):
#     print(f"{i}. [{commit['repo']}] {commit['message']} ({commit['date']})")
#     print(f"   {commit['url']}")

# For global commits
# for i, commit in enumerate(lates_global_commits, 1):
#     print(f"{i}. [{commit['repo']}] {commit['message']} ({commit['date']})")
#     print(f"   {commit['url']}")

output = ""
for i, commit in enumerate(commits, 1):
    output += f"{i}. [{commit['repo']}] {commit['message']} ({commit['date']})\n"
    output += f"   {commit['url']}\n"
    if commit['diffs']:
        for diff in commit['diffs']:
            output += f"     - {diff['filename']}\n"
            output += f"{diff['patch']}\n\n"
    else:
        output += "     (No diffs)\n\n"

open_in_editor(output)
