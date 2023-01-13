import csv
import os
import subprocess
import sys
import re
from datetime import datetime

stdin = open(sys.argv[1], encoding='utf-8').readlines() if len(sys.argv) > 1 else sys.stdin

DELIMITER=','
ENCODING='utf-8-sig'
COLUMNS = (os.getenv("COLUMNS") or "module,full path, filename, commit message, deploy date").split(",")


sys.stdout.reconfigure(encoding = ENCODING)
today = datetime.today().strftime('%Y-%m-%d')

modified_files = []
added_files = []

# parse git diff file
for line in stdin:
    if line.startswith("+++ b/"):
        # extract added file path
        added_files.append(line.split("+++ b/")[1].strip())
    elif line.startswith("--- a/"):
        # extract modified file path
        modified_files.append(line.split("--- a/")[1].strip())

# create csv file
writer = csv.writer(sys.stdout, delimiter = DELIMITER, quoting = csv.QUOTE_ALL)
writer.writerow(COLUMNS)

for file_path in set(added_files + modified_files):
    # extract file name from path
    file_name = re.search(r"[^/]*$", file_path).group()
    # get last commit message for file
    commit_message = subprocess.run(["git", "log", "-1", "--pretty=%B", file_path], capture_output=True, text=True, encoding='utf-8').stdout.strip()
    # cut commit message if it's longer than 80 characters
    commit_message = commit_message[:80] + "..." if len(commit_message) > 80 else commit_message
    # remove some commit message prefix
    commit_message = re.sub(r"^[0-9]+\s+.+\s{0,}:\s+", "", commit_message)
    # extract first path of file and last word of that path
    if '/' in file_path and '-' in file_path:
        module = file_path.split("/")[0].split("-")[-1]
    else:
        module = ""
    writer.writerow([module, file_path, file_name, commit_message, today])