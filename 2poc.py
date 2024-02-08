import re

# Define a function to check if a string follows the specified format
def check_format(string):
    pattern = r'^[A-Z]+-\d+$'
    return re.match(pattern, string) is not None

# Example usage:
string = 'CRP-1000'
if check_format(string):
    print(f"The string '{string}' follows the specified format.")
else:
    print(f"The string '{string}' does not follow the specified format."