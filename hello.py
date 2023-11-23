import os
import subprocess

# Get the name of the head branch
head_branch = os.environ.get('GITHUB_HEAD_REF', 'unknown_head_branch')

# Find a branch with "rc" in its name
rc_branch = None
with subprocess.Popen(['gh', 'repo', 'view', '--json', 'default_branch', '-q', '.default_branch'], stdout=subprocess.PIPE) as process:
    default_branch, _ = process.communicate()
    default_branch = default_branch.decode().strip()

with subprocess.Popen(['gh', 'repo', 'view', '--json', 'branches', '-q', '.branches[*].name'], stdout=subprocess.PIPE) as process:
    branches, _ = process.communicate()
    branches = branches.decode().strip().split()

for branch in branches:
    if 'rc' in branch:
        rc_branch = branch
        break

# Create a pull request from the head branch to the branch with "rc" in its name
if rc_branch:
    with subprocess.Popen(['gh', 'pr', 'create', '--base', default_branch, '--head', head_branch, '--title', f'Merge {head_branch} to {rc_branch}', '--body', f'This PR includes changes from {head_branch} to {rc_branch}.'], stdout=subprocess.PIPE) as process:
        output, _ = process.communicate()
        print(output.decode())
else:
    print(f'No branch found with "rc" in its name.')
