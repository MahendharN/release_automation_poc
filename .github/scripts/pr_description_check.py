import os
import json
import re

# Load pull request event payload
with open(os.getenv('GITHUB_EVENT_PATH'), 'r') as f:
    event_payload = json.load(f)

# Extract PR title
title = event_payload['pull_request']['title']
title_pattern = "^Build"

# Skip description check if title contains 'Build'
if re.match(title_pattern, title):
    print("Title starts with 'Build', skipping description check.")
    exit(0)

# Extract PR description
description = event_payload['pull_request']['body']
if description is None:
    print("PR description is not valid. Please ensure it follows the required format.")
    exit(1)

processed_desc = "".join(description.lower().split("\n"))
print(os.environ.get("GITHUB_TOKEN"))

# Define a pattern for required fields in a text string using the 'compulsory_pattern' variable
compulsory_pattern = "title:.*description:.*jira:.*test report:.*"
keywords = ["Jira", "Title", "Test Report", "Description"]
incorrect_compulsary_pattern = r"\b(?:" + "|".join(keywords) + r")\b"
optional_pattern = "\\n\s*dependencies:.*|\\n\slimitations:.*|\\n\sdeprecated features:.*"


optional_pattern_found = re.search(optional_pattern,processed_desc)
compulsory_pattern_found = re.search(compulsory_pattern,processed_desc)

if compulsory_pattern_found:
    print("PR description is valid.")
elif not compulsory_pattern_found and any(keyword in description for keyword in keywords):
    print("PR description is not valid. Please ensure it follows the required format.")
    exit(1)
elif optional_pattern_found:
    print("PR description is valid.")
else:
    print("PR description is not valid. Please ensure it follows the required format.")
    exit(1)
    