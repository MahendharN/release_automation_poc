import os

def get_pr_info():
    # Get information about the pull request from environment variables
    github_event_name = os.environ.get('GITHUB_EVENT_NAME')
    github_sha = os.environ.get('GITHUB_SHA')
    github_ref = os.environ.get('GITHUB_REF')
    github_head_ref = os.environ.get('GITHUB_HEAD_REF')
    github_base_ref = os.environ.get('GITHUB_BASE_REF')
    github_repository = os.environ.get('GITHUB_REPOSITORY')

    # Extract PR number from the ref
    pr_number = github_ref.split('/')[-1] if github_ref else None

    return {
        'github_event_name': github_event_name,
        'github_sha': github_sha,
        'github_ref': github_ref,
        'github_head_ref': github_head_ref,
        'github_base_ref': github_base_ref,
        'github_repository': github_repository,
        'pr_number': pr_number,
    }

if __name__ == '__main__':
    pr_info = get_pr_info()

    print("GitHub Event Name:", pr_info['github_event_name'])
    print("GitHub SHA:", pr_info['github_sha'])
    print("GitHub Ref:", pr_info['github_ref'])
    print("GitHub Head Ref:", pr_info['github_head_ref'])
    print("GitHub Base Ref:", pr_info['github_base_ref'])
    print("GitHub Repository:", pr_info['github_repository'])
    print("PR Number:", pr_info['pr_number'])
    print("Base Branch:", pr_info['github_base_ref'])
    print("Head Branch:", pr_info['github_head_ref'])
