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

if "Deprecated Features:" in description:
    depracated = re.search(deprecated_feature_pattern, description, re.DOTALL)
    try:
        values0 = depracated.group(1).strip().split("\n")
    except Exception as e:
        print(e)
        print("Error parsing Deprecated features from Description.")
        print("PR Description is not Valid. Please check the link https://amagiengg.atlassian.net/wiki/spaces/CLOUD/pages/3408199746/ES+CRP-1292+Automate+Build+Note+Genration+for+Cloudport+applications to check the required format.")
        exit(1)
    if depracated and all("-" in value for value in values0) and len(values0) !=0:
        optional_pattern_keywords.remove("Deprecated Features:")
    else:
        print("Deprecated Features Field Format is wrong")
        print("PR Description is not Valid. Please check the link https://amagiengg.atlassian.net/wiki/spaces/CLOUD/pages/3408199746/ES+CRP-1292+Automate+Build+Note+Genration+for+Cloudport+applications to check the required format.")
        exit(1)
if "Dependencies:" in description:
    dependencies = re.search(dependencies_pattern, description, re.DOTALL)
    try:
        values1 = dependencies.group(1).strip().split("\n")
    except Exception as e:
        print(e)
        print("Error parsing Dependencies from Description.")
        print("PR Description is not Valid. Please check the link https://amagiengg.atlassian.net/wiki/spaces/CLOUD/pages/3408199746/ES+CRP-1292+Automate+Build+Note+Genration+for+Cloudport+applications to check the required format.")
        exit(1)
    if dependencies and all("-" in value for value in values1) and len(values1) !=0:
        optional_pattern_keywords.remove("Dependencies:")
    else:
        print("Dependencies Field Format is wrong")
        print("PR Description is not Valid. Please check the link https://amagiengg.atlassian.net/wiki/spaces/CLOUD/pages/3408199746/ES+CRP-1292+Automate+Build+Note+Genration+for+Cloudport+applications to check the required format.")
        exit(1)
if "Limitations:" in description:
    limitations = re.search(limitations_pattern, description, re.DOTALL)
    try:
        values2 = limitations.group(1).strip().split("\n")
    except Exception as e:
        print(e)
        print("Error parsing Limitations from Description.")
        print("PR Description is not Valid. Please check the link https://amagiengg.atlassian.net/wiki/spaces/CLOUD/pages/3408199746/ES+CRP-1292+Automate+Build+Note+Genration+for+Cloudport+applications to check the required format.")
        exit(1)
    if limitations and all("-" in value for value in values2) and len(values2) !=0:
        optional_pattern_keywords.remove("Limitations:")
    else:
        print("Limitations Field Format is wrong")
        print("PR Description is not Valid. Please check the link https://amagiengg.atlassian.net/wiki/spaces/CLOUD/pages/3408199746/ES+CRP-1292+Automate+Build+Note+Genration+for+Cloudport+applications to check the required format.")
        exit(1)
        
if any(pattern not in description for pattern in optional_pattern_keywords) or len(optional_pattern_keywords) == 0:
    if not any(pattern in description for pattern in compulsory_pattern_keywords) and not re.search(compulsory_pattern, description, re.DOTALL):
        print("PR description is valid.")
        exit(0)
    elif any(pattern in description for pattern in compulsory_pattern_keywords) and re.search(compulsory_pattern, description, re.DOTALL):
        print("PR description is valid.")
        exit(0)

print("PR Description is not Valid. Please check the link https://amagiengg.atlassian.net/wiki/spaces/CLOUD/pages/3408199746/ES+CRP-1292+Automate+Build+Note+Genration+for+Cloudport+applications to check the required format.")
exit(1)