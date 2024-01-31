import sys
import requests
import re

def get_list_of_description(pr_info_list):
    description_list = []
    for pr_info in pr_info_list:
        if pr_info.get("title").startswith("Build"):
            continue
        description = pr_info.get("body")
        if not description:
            print(f"Description of {pr_info.get('url')} is empty")
            continue
        description_dict = get_desciption_dict_from_str(description)
        description_list.append({description_dict.get("jira_id"),description_dict})
    return description_list

def get_desciption_dict_from_str(input_string):
    print(input_string)
    patterns = {
    "title": r"Title:\s*(.*?)\n",
    "description": r"Description:(.*?)Jira:",
    "jira": r"Jira:\s*\[(.*?)\]\((.*?)\)",
    "test_report": r"Test Report:\s*\[(.*?)\]\((.*?)\)",
    "deprecated_features": r"Deprecated Features:\s*(.*?)\n",
    "dependencies": r"Dependencies:\s*(.*?)\n",
    "limitations": r"Limitations:\s*(.*?)\n"
    }

    # Initialize an empty dictionary to store extracted information
    info_dict = {}

    # Iterate over the patterns and extract key-value pairs
    for key, pattern in patterns.items():
        match = re.search(pattern, input_string, re.DOTALL)
        if match:
            if key in ["jira", "test_report"]:
                info_dict[key + "_id"] = match.group(1).strip()
                info_dict[key + "_link"] = match.group(2).strip()
            elif key in ["deprecated_features", "dependencies", "limitations"]:
                # Split the comma-separated values and remove full stops from the end if present
                values = [value.strip().rstrip(".") for value in match.group(1).split(",")]
                info_dict[key] = values
            else:
                info_dict[key] = match.group(1).strip()

    return info_dict

if __name__ == "__main__":
    BASE_BRANCH = sys.argv[1]
    LAST_TAG = sys.argv[2]
    GIT_REPO = sys.argv[3]
    GIT_TOKEN = sys.argv[4]
    PRESENT_TAG = sys.argv[5]
    if BASE_BRANCH != "develop" and (not BASE_BRANCH.endswith(".x")) and (not BASE_BRANCH.startswith("rc")):
        print ("This workflow only applicable for .x, develop and rc branches")
        sys.exit(1)
    pr_list_res = requests.post(
        f"https://api.github.com/repos/{GIT_REPO}/releases/generate-notes",
        headers={
            "Authorization": f"Bearer {GIT_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        json={
            "tag_name": PRESENT_TAG,
            "target_commitish": BASE_BRANCH,
            "previous_tag_name": LAST_TAG,
            "configuration_file_path": ".github/release.yml",
        },
    ).json()
    lines = pr_list_res["body"].splitlines()
    pr_info_list = []
    for line in lines:
        if line.startswith('* '):
            res = line.rsplit('/',1)
            print (f"Pr number is {res[1]}")
            pr_info = requests.get(
            f"https://api.github.com/repos/{GIT_REPO}/pulls/{res[1]}",
            headers={
                "Authorization": f"Bearer {GIT_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
            },
            ).json()
            pr_info_list.append(pr_info)

    print(get_list_of_description(pr_info_list))