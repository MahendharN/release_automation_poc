import sys
import requests
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
    print(pr_list_res)