import os
import json
import re

# Load pull request event payload
with open(os.getenv('GITHUB_EVENT_PATH'), 'r') as f:
    event_payload = json.load(f)

# Extract PR title
title = event_payload['pull_request']['title']
title_pattern = "Build.*"

# Skip description check if title contains 'Build'
if re.match(title_pattern, title):
    print("Title has 'Build', skipping description check.")
    exit(0)

# Extract PR description
description = event_payload['pull_request']['body']
if description is None:
    description=""

# Define compulsory and optional patterns for PR description
compulsory_pattern = r"Title:.*Description:.*Jira:.*Test Report:.*"
optional_pattern = r"(Deprecated Features:|Dependencies:|Limitations:).*"

# Check PR description
if re.search(compulsory_pattern, description):
    print("PR description is valid.")

    if re.search(r"Deprecated\ Features|Dependencies|Limitations", description):
        print("PR description includes optional information. Approval granted.")
    else:
        print("PR description does not include optional information. Approval granted.")
elif re.search(optional_pattern, description):
    print("PR description does not include compulsory information, but includes optional information. Approval granted.")
else:
    print("PR description is not valid. Please ensure it follows the required format.")
    exit(1)
