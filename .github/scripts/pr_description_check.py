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

# description = '''
# Title: Implementing AI based video portrait mode.
# Description: Some description about the above.
# Jira: CRP-100032987
# Test Report: AIO link

# Deprecated Features: 
# - abc
# - cdf

# Dependencies: 
# - dep1
# - dep1

# Limitations: 
# - lim1
# - lim2
# '''
if description is None:
    print("PR description is not valid. Please ensure it follows the required format.")
    exit(1)


# Define a pattern for required fields in a text string using the 'compulsory_pattern' variable
compulsory_pattern =  r"^(\n*|\s*)Title:.*\nDescription:.*\nJira:.*\nTest Report:[^\n]*($|\n*$|\n*Deprecated Features:|\n*Dependencies:|\n*Limitations:)"
compulsory_pattern_keywords = ["Jira:", "Title:", "Test Report:", "Description:"]
optional_pattern_keywords = ["Deprecated Features:","Dependencies:","Limitations:"]
deprecated_feature_pattern = r"Deprecated Features:(.*?)(Dependencies:|Limitations:|$)"
dependencies_pattern = r"Dependencies:(.*?)(Deprecated Features:|Limitations:|$)"
limitations_pattern = r"Limitations:(.*?)(Dependencies:|Deprecated Features:|$)"

def check_field(description, pattern, keyword):
    field = re.search(pattern, description, re.DOTALL)
    try:
        values = field.group(1).strip().split("\n")
    except Exception as e:
        print(e)
        print(f"Error parsing {keyword} from Description.")
        print("PR Description is not Valid. Please check the required format.")
        exit(1)
    if field and all("-" in value for value in values) and len(values) != 0:
        return True
    else:
        print(f"{keyword} Field Format is wrong")
        print("PR Description is not Valid. Please check the required format.")
        exit(1)
        
if "Deprecated Features:" in description:
    if check_field(description, deprecated_feature_pattern, "Deprecated Features"):
        optional_pattern_keywords.remove("Deprecated Features:")
if "Dependencies:" in description:
    if check_field(description, dependencies_pattern, "Dependencies"):
        optional_pattern_keywords.remove("Dependencies:")
if "Limitations:" in description:
    if check_field(description, limitations_pattern, "Limitations"):
        optional_pattern_keywords.remove("Limitations:")
        
if any(pattern not in description for pattern in optional_pattern_keywords) or len(optional_pattern_keywords) == 0:
    if not any(pattern in description for pattern in compulsory_pattern_keywords) and not re.search(compulsory_pattern, description, re.DOTALL) and len(optional_pattern_keywords) < 3:
        print("PR description is valid.")
        exit(0)
    elif any(pattern in description for pattern in compulsory_pattern_keywords) and re.search(compulsory_pattern, description, re.DOTALL):
        print("PR description is valid.")
        exit(0)

print("PR Description is not Valid. Please check the link https://amagiengg.atlassian.net/wiki/spaces/CLOUD/pages/3408199746/ES+CRP-1292+Automate+Build+Note+Genration+for+Cloudport+applications to check the required format.")
exit(1)