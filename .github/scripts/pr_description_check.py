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
    print("Title has 'Build', skipping description check.")
    exit(0)

# Extract PR description
description = event_payload['pull_request']['body']
if description is None:
    description=""

description = description.lower()

# Define a pattern for required fields in a text string using the 'compulsory_pattern' variable
compulsory_pattern = "title:.*\ndescription:.*\njira:.*\ntest report:.*"
optional_pattern = "dependencies:.*|limitations:.*|deprecated features:.*"


optional_pattern_found = re.search(optional_pattern,description)
compulsory_pattern_found = re.search(compulsory_pattern,description)

if compulsory_pattern_found or optional_pattern_found:
    print("PR description is valid.")
else:
    print("PR description is not valid. Please ensure it follows the required format.")
    exit(1)
