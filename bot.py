import os
import json

event_path = os.environ['GITHUB_EVENT_PATH']

with open(event_path, 'r') as f:
    event = json.load(f)


comment_text = event['comment']['body']
comment_author = event['comment']['user']['login']
issue_number = event['issue']['number']
repo_name = event['repository']['full_name']

print(f"Comment on {repo_name} issue #{issue_number}")
print(f"Author: {comment_author}")
print(f"Text: {comment_text}")

if 'assign me' in comment_text.lower():
    print(f'Assigning {comment_author} to issue {issue_number}')