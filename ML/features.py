import re
from datetime import datetime
from .constants import *

GENERIC_COMMIT = {"update","fix","test",".","temp","change","_","add"}
SUS_PATTERNS = [r"print\(",r"console\.log\s*\(",r"System\.out\.println\(",r"echo"]

def extract_features(commit):

    features = {}

    message = commit.get("message","").strip().lower()
    features[MSG_LENGTH] = len(message.split())
    features[IS_GENERIC_MSG] = int(message in GENERIC_COMMIT) # Gives 1(True) or 0(False)

    date_str = commit.get("date")

    try:
        committed_time = datetime.fromisoformat(date_str.replace("Z","+00:00"))
        features[COMMITED_DAY] = f"{committed_time.day}/{committed_time.month}/{committed_time.year}"
        features[TIME_OF_DAY] = f"{committed_time.hour}:{committed_time.minute}" 
    except:
        features[TIME_OF_DAY] = -1

    tot_lines = 0
    sus_lines = 0

    for diff in commit.get("diffs",[]):
        patch = diff.get("patch","")
        added_lines = [line for line in patch.split("\n") if line.startswith("+") and not line.startswith("+++")]
        tot_lines += len(added_lines)

        for line in added_lines:
            if any(re.search(pattern, line) for pattern in SUS_PATTERNS):
                sus_lines += 1

    features[LINES_ADDED] = tot_lines
    features[SUS_LINES] = sus_lines
    features[FILES_CHANGED] = len(commit.get("diffs",[]))
    features[REPO] = commit.get("repo", "unknown")

    return features

def compare_commits(features1,features2):
    score = 0
    feedback = {}
    if features1[TIME_OF_DAY] == features2[TIME_OF_DAY] and features1[COMMITED_DAY] != features2[COMMITED_DAY]:
        score += 2
        feedback["possible_automation"] = features1[REPO]
        return score

def check_copied_projects(features):
    score = 0
    feedback = {}
    if features[LINES_ADDED] > 10000:
        score +=2
        feedback["possible_copy"] = features[REPO]

    return score,feedback

def score_commit(features):
    score = 0
    if features[IS_GENERIC_MSG] == 1:
        score += 2

    sus_fraction = 0
    feedback = {}
    if features[LINES_ADDED] != 0 :
        sus_fraction = features[SUS_LINES]/features[LINES_ADDED]
    else :
        feedback["no_lines"] = features[REPO]

    # Check this
    if sus_fraction > 0.5:
        score +=2
    if features[LINES_ADDED] <= 2:
        score += 2
    
    # Decide whether to give points if less than 2 files were changed
    #
    # if features[FILES_CHANGED] <= 2:
    #     score +=2

    copy_score,copy_feedback = check_copied_projects(features)
    score += copy_score
    feedback.update(copy_feedback)

    return score,feedback
