import os
import json
from github import Github, Auth

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

def ensure_label(repo, name, color='ededed', description=''):
    try:
        repo.get_label(name)
    except Exception:
        repo.create_label(name=name, color=color, description=description)

if 'assign me' in comment_text.lower():
    gh = Github(auth=Auth.Token(os.environ['GH_TOKEN']))
    repo = gh.get_repo(repo_name)
    issue = repo.get_issue(number=issue_number)

    ensure_label(repo, 'bot:assigned', '0e8a16', 'Assigned by bot')
    ensure_label(repo, 'bot:dropped', 'b60205', 'Unassigned by bot')


    try:
        issue.add_to_assignees(comment_author)
        issue.add_to_labels('bot:assigned')

        existing_labels = [label.name for label in issue.get_labels()]
        if 'bot:dropped' in existing_labels:
            issue.remove_from_labels('bot:dropped')

        issue.create_comment(f'Assigned to {comment_author}.\n \n'
        f'*This comment was automatically generated*')
        print(f'Assigned to {comment_author} successfully, - issue #{issue_number}\n')

    except Exception as e:
        print(f'Error assigning: {e}')


