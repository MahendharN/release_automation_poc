import os

# Get information about the pull request from environment variables
base_branch = os.environ.get('GITHUB_BASE_REF', 'unknown_base_branch')
feature_branch = os.environ.get('GITHUB_HEAD_REF', 'unknown_feature_branch')

# Print information
print(f'This pull request is merging changes from {feature_branch} to {base_branch}.')
