import os
from github import Github
import subprocess

GITHUB_EVENT_NAME = 'GITHUB_EVENT_NAME'
GITHUB_SHA = 'GITHUB_SHA'
GITHUB_REF = 'GITHUB_REF'
GITHUB_HEAD_REF = 'GITHUB_HEAD_REF'
GITHUB_BASE_REF = 'GITHUB_BASE_REF'
GITHUB_REPOSITORY = 'GITHUB_REPOSITORY'
GITHUB_MAJOR_PR_NUMBER = "pr_number"
GITHUB_TOKEN = 'GITHUB_TOKEN'


MAX_MAJOR_VERSION = 5
MAX_RC_BRANCH_FIND_RETRY = 10
def get_pr_info():
    # Get information about the pull request from environment variables
    github_event_name = os.environ.get(GITHUB_EVENT_NAME)
    github_ref = os.environ.get(GITHUB_REF)
    github_head_ref = os.environ.get(GITHUB_HEAD_REF)
    github_base_ref = os.environ.get(GITHUB_BASE_REF)
    github_repository = os.environ.get(GITHUB_REPOSITORY)
    github_token = os.environ.get(GITHUB_TOKEN)

    # Extract PR number from the ref
    try:
        pr_number = github_ref.split('/')[-2] if github_ref else None
    except Exception as e:
        print(f"Exception while getting PR number {e}")
        exit(0)

    return {
        GITHUB_EVENT_NAME: github_event_name,
        GITHUB_REF: github_ref,
        GITHUB_HEAD_REF: github_head_ref,
        GITHUB_BASE_REF: github_base_ref,
        GITHUB_REPOSITORY: github_repository,
        GITHUB_MAJOR_PR_NUMBER: pr_number,
        GITHUB_TOKEN: github_token
    }

def run_git_command(command):
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  # Ensure the output is in text mode
            check=True   # Raise an exception for non-zero return codes
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        # Handle the error (e.stderr contains the error message)
        print(f"Error running command: {e.stderr}")
        return None
    
class RCUpdate():
    def __init__(self):
        self.pr_info = get_pr_info()
        self.gitub = Github(self.pr_info.get(GITHUB_TOKEN))
        self.repo = self.gitub.get_repo(self.pr_info.get(GITHUB_REPOSITORY))
        try:
            self.mj_major_version = int(self.pr_info.get(GITHUB_BASE_REF).split("-")[-1].split(".")[0])
            self.mj_minor_version = int(self.pr_info.get(GITHUB_BASE_REF).split("-")[-1].split(".")[1])
        except Exception as e:
            print(f"Exception while getting vyuha version from branch name. Exception {e}. Improper branch name. Branch Name {self.pr_info[GITHUB_BASE_REF]}")
            exit(0)
        self.rc_branch_name = self.get_rc_branch()
        if self.rc_branch_name == None:
            print("No RC Branch . Thus exiting")
            exit(0)
        if self.pr_info.get(GITHUB_HEAD_REF,"") == "":
            print("No HEAD BRANCH . Thus exiting")
            exit(0)
        self.process()

    def get_rc_branch(self):
        for i in range(1,MAX_RC_BRANCH_FIND_RETRY):
            branch_name = f"rc_{self.mj_major_version}.{self.mj_minor_version+i}.0"
            print(branch_name)
            if self.check_if_branch_is_present(branch_name):
                return branch_name
        return None

    def check_if_branch_is_present(self,branch_name):
        try:
            self.repo.get_branch(branch_name)
            return True
        except:
            return False
        
    def check_if_rc_head_is_present(self):
        self.head_rc_branch = self.check_if_branch_is_present(f"{self.rc_branch_name}-{self.pr_info.get(GITHUB_HEAD_REF)}")
        return self.head_rc_branch
    
    def create_pr(self):
        self.create_new_branch(self.head_rc_branch,self.rc_branch_name)

    def create_new_branch(self, new_branch_name, base_branch):
        # Get the base branch
        base_ref = self.repo.get_git_ref(f'heads/{base_branch}')

        # Create a new branch based on the base branch
        new_branch_ref = self.repo.create_git_ref(f'refs/heads/{new_branch_name}', base_ref.object.sha)

        print(f"New branch '{new_branch_name}' created successfully from '{base_branch}'.")


    def update_pr(self):
        pass
  
    def process(self):
        if self.check_if_rc_head_is_present():
            self.update_pr()
        else:
            self.create_pr()



if __name__ == '__main__':
    rcupdate = RCUpdate()

