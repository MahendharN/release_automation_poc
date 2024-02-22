import os
import json
from github import Github
import sys

def create_tag(branch, repo_full_name, token, sha):
    # Load pull request event payload
    event_path = os.getenv('GITHUB_EVENT_PATH')
    with open(event_path, 'r') as f:
        try:
            event_payload = json.load(f)
        except Exception as e:
            print("Error loading event payload, {e}")

    if not event_payload or not event_payload['pull_request']:
        print("Event payload or Pull Request Found is None")
        exit(1)

    title = event_payload['pull_request']['title']
    if "Pr for Release Notes of" not in title:
        print("Not a PR for Release Generation. Thus exiting.")
        exit(0)

    description = event_payload['pull_request']['body']
    if not description:
        print("PR Description is None")
        exit(1)
    
    tag_name = description
    g = Github(token)
    repo_owner, repo_name = repo_full_name.split('/')
    repo = g.get_repo(f"{repo_owner}/{repo_name}")
    release_tag = repo.create_git_tag_and_release(tag_name, tag_name, tag_name, "Release", sha, 'commit', draft=False)
    release = repo.get_release(tag_name)
    if release:
        print(f'The link to the created release: {release_tag.html_url}')
    else:
        print(f"Release was not tagged succesfully for tag: {tag_name}")

if __name__ == "__main__":
    branch = sys.argv[1]
    repo_full_name = sys.argv[2]
    token = sys.argv[3]
    sha = sys.argv[4]
    try:
        create_tag(branch, repo_full_name, token, sha)
    except Exception as e:
        print(f"Error while creating tag. Exception {e}")
        print(e)
        exit(1)