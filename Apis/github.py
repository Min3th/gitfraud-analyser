import aiohttp
import asyncio

async def fetch_commit_diff(session,username,repo,sha,token=None):
    headers = {
        "Accept":"application/vnd.github+json"
    }
    if token:
        headers["Authorization"]=f"Bearer {token}"
    
    url = f"https://api.github.com/repos/{username}/{repo}/commits/{sha}"
    async with session.get(url,headers=headers) as response:
        if response.status != 200:
            print(f"Error fetching commit diff: {response.status}")
            return None
        data = await response.json()
        return [
            {
                "filename":file["filename"],
                "patch":file["patch"]
            }
            for file in data.get("files",[])
            if "patch" in file
        ]

async def fetch_global_commits(username,token):
    headers = {
        "Accept":"application/vnd.github.cloak-preview",
        "Authorization": f"Bearer {token}"
    }

    url = f"https://api.github.com/search/commits?q=author:{username}&sort=author-date&order=desc&per_page=10"

    async with aiohttp.ClientSession() as session:
        async with session.get(url,headers=headers) as response:
            if response.status != 200 :
                print(f"Error: {response.status} - {await response.text}")
                return[]
            
            results = await response.json()
            commits = []

            tasks = []
            for item in results.get("items", []):
                commit = item["commit"]
                repo = item["repository"]["full_name"]
                sha = item["sha"]
                owner, repo_name = repo.split("/")

                # Schedule diff fetch
                tasks.append(fetch_commit_diff(session, owner, repo_name, sha, token))

                commits.append({
                    "repo": repo,
                    "message": commit["message"],
                    "date": commit["author"]["date"],
                    "url": item["html_url"]
                    # "diffs": will be added after gathering
                })

            # Await all diff fetches
            diffs_list = await asyncio.gather(*tasks)

            # Attach diffs to each commit
            for i in range(len(commits)):
                commits[i]["diffs"] = diffs_list[i]

            return commits
    