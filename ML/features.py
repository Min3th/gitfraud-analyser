import re
from datetime import datetime

GENERIC_COMMIT = {"update","fix","test",".","temp","change","_"}
SUS_PATTERNS = [r"print\(",r"console\.log(",r"System\.out\.println\(",r"echo"]

def extract_features(commit):

    features = {}

    message = commit.get("message","").strip().lower()
    features["msg_length"] = len(message.split())
    features["is_generic_msg"] = int(message in GENERIC_COMMIT) # Gives 1(True) or 0(False)

    date_str = commit.get("date")

    try:
        committed_time = datetime.fromisoformat(date_str.replace("Z","+00:00"))
        features["hour_of_day"] = committed_time.hour # For better accuracy change this to the exact time , not just hr
    except:
        features["hour_of_day"] = -1

    tot_lines = 0
    sus_lines = 0

    for diff in commit.get("diffs",[]):
        patch = diff.get("patch","")
        added_lines = [line for line in patch.split("\n") if line.startswith("+") and not line.startswith("+")]
        tot_lines += len(added_lines)

        for line in added_lines:
            if any(re.search(pattern, line) for pattern in SUS_PATTERNS):
                sus_lines += 1

    features["lines_added"] = tot_lines
    features["sus_lines"] = sus_lines
    features["files_changed"] = len(commit.get("diffs",[]))

    return features
