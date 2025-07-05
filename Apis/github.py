import requests # change to asnycios in future

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
