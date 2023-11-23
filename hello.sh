#!/bin/bash

GITHUB_EVENT_NAME=$GITHUB_EVENT_NAME
GITHUB_SHA=$GITHUB_SHA
GITHUB_REF=$GITHUB_REF
GITHUB_HEAD_REF=$GITHUB_HEAD_REF
GITHUB_BASE_REF=$GITHUB_BASE_REF
GITHUB_REPOSITORY=$GITHUB_REPOSITORY
GITHUB_MAJOR_PR_NUMBER="pr_number"
GITHUB_TOKEN=$GITHUB_TOKEN

MAX_MAJOR_VERSION=5
MAX_RC_BRANCH_FIND_RETRY=10

get_pr_info() {
    # Get information about the pull request from environment variables
    pr_number=$(echo "$GITHUB_REF" | cut -d'/' -f3)
    
    echo "GITHUB_EVENT_NAME=$GITHUB_EVENT_NAME"
    echo "GITHUB_REF=$GITHUB_REF"
    echo "GITHUB_HEAD_REF=$GITHUB_HEAD_REF"
    echo "GITHUB_BASE_REF=$GITHUB_BASE_REF"
    echo "GITHUB_REPOSITORY=$GITHUB_REPOSITORY"
    echo "GITHUB_MAJOR_PR_NUMBER=$pr_number"
    echo "GITHUB_TOKEN=$GITHUB_TOKEN"
}

run_git_command() {
    command=$1
    output=$(eval "$command")
    echo "$output"
}

RCUpdate() {
    pr_info=$(get_pr_info)
    github_token=$GITHUB_TOKEN

    mj_major_version=$(echo "$GITHUB_BASE_REF" | cut -d'-' -f3 | cut -d'.' -f1)
    mj_minor_version=$(echo "$GITHUB_BASE_REF" | cut -d'-' -f3 | cut -d'.' -f2)

    rc_branch_name=$(get_rc_branch "$mj_major_version" "$mj_minor_version")
    if [ -z "$rc_branch_name" ]; then
        echo "No RC Branch . Thus exiting"
        exit 0
    fi

    if [ -z "$GITHUB_HEAD_REF" ]; then
        echo "No HEAD BRANCH . Thus exiting"
        exit 0
    fi

    if check_if_rc_head_is_present; then
        update_pr
    else
        create_pr
    fi
}

get_rc_branch() {
    mj_major_version=$1
    mj_minor_version=$2

    for i in $(seq 1 $MAX_RC_BRANCH_FIND_RETRY); do
        branch_name="rc_${mj_major_version}.${mj_minor_version+i}.0"
        echo "$branch_name"
        if check_if_branch_is_present "$branch_name"; then
            echo "$branch_name"
            return 0
        fi
    done

    return 1
}

check_if_branch_is_present() {
    branch_name=$1

    for branch in $(git branch --format "%(refname)"); do
        if [ "$branch" = "$branch_name" ]; then
            return 0
        fi
    done

    return 1
}

check_if_rc_head_is_present() {
    check_if_branch_is_present "${rc_branch_name}-${GITHUB_HEAD_REF}"
}

create_pr() {
    create_new_branch "${rc_branch_name}-${GITHUB_HEAD_REF}" "$GITHUB_HEAD_REF"
    create_pull_request "Pull Request Title" "${rc_branch_name}-${GITHUB_HEAD_REF}" "$rc_branch_name" "Pull Request Body"
}

create_new_branch() {
    new_branch_name=$1
    base_branch=$2

    git checkout -b "$new_branch_name" "origin/$base_branch"
    echo "New branch '$new_branch_name' created successfully from '$base_branch'."
}

create_pull_request() {
    title=$1
    head_branch=$2
    base_branch=$3
    body=$4

    gh pr create --title "$title" --body "$body" --base "$base_branch" --head "$head_branch"
}

update_pr() {
    return 0
}

RCUpdate
echo "PR Branch: $pr_branch"
echo "PR Branch: $pr_branch"
