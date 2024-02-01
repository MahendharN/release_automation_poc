#!/bin/bash

# Read the sample event JSON
GITHUB_EVENT_PATH="sample_event.json"

# Extract PR description
description=$(jq --raw-output .pull_request.body "$GITHUB_EVENT_PATH")

echo "$description"
# Define compulsory and optional patterns
compulsory_pattern="Title:.*Description:.*Jira:.*Test Report:.*"
optional_pattern="(Deprecated Features:|Dependencies:|Limitations:).*"

# Check PR description
if [[ "$description" =~ $compulsory_pattern ]]; then
echo "PR description is valid."

if [[ "$description" =~ Deprecated\ Features || "$description" =~ Dependencies || "$description" =~ Limitations ]]; then
    echo "PR description includes optional information. Approval granted."
else
    echo "PR description does not include optional information. Additional approval may be required."
fi
elif [[ "$description" =~ $optional_pattern ]]; then
echo "PR description does not include compulsory information, but includes optional information. Approval granted."
else
echo "PR description is not valid. Please ensure it follows the required format."
exit 1
fi
