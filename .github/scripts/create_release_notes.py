import sys
import requests
import re
from datetime import datetime
from ruamel.yaml import YAML


class ReleaseNotesGenerator:
    def __init__(self,base_branch,last_tag,git_repo,git_token,present_tag):
        self.base_branch = base_branch
        self.last_tag = last_tag
        self.git_repo = git_repo
        self.git_token = git_token
        self.present_tag = present_tag

    def __get_pr_list_from_github_api(self):
        """
        Get list of PR using generate release notes Github API
        """
        # Get list of PR using generate release notes Github API
        pr_list_res = requests.post(
                f"https://api.github.com/repos/{self.git_repo}/releases/generate-notes",
                headers={
                    "Authorization": f"Bearer {self.git_token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                json={
                    "tag_name": self.present_tag,
                    "target_commitish": self.base_branch,
                    "previous_tag_name": self.last_tag,
                    "configuration_file_path": ".github/release.yml",
                },
            ).json()
        
        lines = pr_list_res["body"].splitlines()
        pr_info_list = []
        
        # Extract PR body and title
        for line in lines:
            if line.startswith('* '):
                res = line.rsplit('/',1)
                print (f"Pr number is {res[1]}")
                pr_info = requests.get(
                f"https://api.github.com/repos/{self.git_repo}/pulls/{res[1]}",
                headers={
                    "Authorization": f"Bearer {self.git_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
                ).json()
                pr_info_list.append(pr_info)

        return pr_info_list
    
    def get_list_of_description(self,pr_info_list):
        description_list = []
        for pr_info in pr_info_list:
            if pr_info.get("title").startswith("Build"):
                continue
            description = pr_info.get("body")
            if not description:
                print(f"Description of {pr_info.get('url')} is empty")
                continue
            try:
                description_dict = self.get_desciption_dict_from_str(description)
            except Exception as e:
                print(f"Incorrect Description . Error {e} , Description {description} , PR {pr_info.get('url')}")
            description_list.append(description_dict)
        return description_list

    def get_desciption_dict_from_str(self,input_string):
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
    
    def get_release_notes_dict(self):
        pr_list = self.__get_pr_list_from_github_api()
        description_list = self.get_list_of_description(pr_list)
        print(description_list)
        return self.get_dict_to_update_in_build_notes(description_list)

    def get_dict_to_update_in_build_notes(self,description_list):
        build_dict = {}
        build_dict["Tag"] = self.present_tag
        current_datetime = datetime.now()
        build_dict["Date"] = current_datetime.strftime("%Y-%m-%d")
        build_dict["Author"] = "Blizzard"
        jira_dict = []
        deprecated_features = []
        dependencies = []
        limitations = []
        for description in description_list:
            if description.get("jira_id",None) is not None:
                jira_dict.append({"JiraID":description.get("jira_id",""),"description":description.get("description")})
            if description.get("dependencies",None) is not None:
                dependencies += description.get("dependencies")
            if description.get("limitations",None) is not None:
                limitations += deprecated_features.get("limitations")
            if description.get("deprecated_features") is not None:
                deprecated_features += description.get("deprecated_features")
        if len(jira_dict) != 0:
            build_dict["Changes"] = jira_dict
        if len(dependencies)!=0:
            build_dict["Dependencies"] = dependencies
        if len(limitations) !=0:
            build_dict["Limitations"] = limitations
        if len(deprecated_features) != 0:
            build_dict["Deprecated Features"] = deprecated_features
        return {"BuildNotes":build_dict}

    

if __name__ == "__main__":
    base_branch = sys.argv[1]
    last_tag = sys.argv[2]
    git_repo = sys.argv[3]
    git_token = sys.argv[4]
    present_tag = sys.argv[5]
    if base_branch != "develop" and (not base_branch.endswith(".x")) and (not base_branch.startswith("rc")):
        print ("This workflow only applicable for .x, develop and rc branches")
        sys.exit(1)

    release_notes_obj = ReleaseNotesGenerator(base_branch,last_tag,git_repo,git_token,present_tag)
    data = release_notes_obj.get_release_notes_dict()
    yaml = YAML()
    yaml.indent(sequence=4, offset=2)
    yaml.default_flow_style = False
    yaml.preserve_quotes = True
    with open('build_notes.yml', 'w') as file:
        yaml.dump(data, file)
    with open('build_notes.yml', 'r') as file:
        print(file.read())

