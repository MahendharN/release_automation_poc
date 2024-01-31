import sys
import requests
import re
from datetime import datetime
from ruamel.yaml import YAML


def get_dict_to_update_in_build_notes(description_list,present_tag):
    build_dict = {}
    build_dict["Tag"] = present_tag
    current_datetime = datetime.now()
    build_dict["Date"] = current_datetime.strftime("%Y-%m-%d")
    build_dict["Author"] = "Blizzard"
    jira_dict = []
    for description in description_list:
        for key,value in description.items():
            jira_dict.append({"JiraID":key,"description":value.get("description")})
    build_dict["Changes"] = jira_dict
    return {"BuildNotes":build_dict}

    
def get_list_of_description(pr_info_list):
    description_list = []
    for pr_info in pr_info_list:
        if pr_info.get("title").startswith("Build"):
            continue
        description = pr_info.get("body")
        if not description:
            print(f"Description of {pr_info.get('url')} is empty")
            continue
        try:
            description_dict = get_desciption_dict_from_str(description)
        except Exception as e:
            print(f"Incorrect Description . Error {e} , Description {description} , PR {pr_info.get('url')}")
        description_list.append({description_dict.get("jira_id"):description_dict})
    return description_list

def get_desciption_dict_from_str(input_string):
    print(input_string)
    patterns = {
        "title": r"Title:\s*(.*?)\n",
        "description": r"Description:(.*?)\nJira:",
        "jira_2": r"Jira:\s*(.*?)\n",
        "test_report_2": r"Test Report:\s*(.*?)\n",
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
            if key == "jira_2":
                info_dict["jira_id"] = match.group(1).strip()
                if "atlassian" in info_dict["jira_id"]:
                    info_dict["jira_id"] = info_dict["jira_id"].split("/")[-1] if len(info_dict["jira_id"].split("/")[-1]) != 0 else info_dict["jira_id"]
            elif key == "test_report_2":
                info_dict["test_report_link"] = match.group(1).strip()
            elif key in ["jira", "test_report"]:
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
    data = get_dict_to_update_in_build_notes(get_list_of_description(pr_info_list),PRESENT_TAG)
    yaml = YAML(typ='safe')
    yaml.indent(sequence=4, offset=2)
    with open('build_notes.yml', 'w') as file:
        yaml.dump(data, file)
    with open('build_notes.yml', 'r') as file:
        print(file.read())

