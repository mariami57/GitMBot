import os
import json
from github import Github

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
    gh = Github(os.environ['GH_TOKEN'])
    repo = gh.get_repo(repo_name)
    issue = repo.get_issue(number=issue_number)

    try:
        issue.add_to_assignees(comment_author)
        issue.create_comment(f'Assigned to {comment_author}.')
        print(f'Assigned to {comment_author} successfully, - issue #{issue_number}')

    except Exception as e:
        print(f'Error assigning: {e}')