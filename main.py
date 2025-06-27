import requests 
from datetime import datetime 

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

    all_commits.sort(key=lambda c: datetime.fromisoformat(c["date"].replace("Z","+00:00"), reverse = True ))    
    return all_commits[:10]

username = input("Enter github username: ")
latest_commits = fetch_last_10_commits(username)

for i, commit in enumerate(latest_commits, 1):
    print(f"{i}. [{commit['repo']}] {commit['message']} ({commit['date']})")
    print(f"   {commit['url']}")
