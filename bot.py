import os
import json
from datetime import datetime, timedelta, timezone

from github import Github, Auth

event_path = os.environ['GITHUB_EVENT_PATH']

with open(event_path, 'r') as f:
    event = json.load(f)


comment_text = event['comment']['body']
comment_author = event['comment']['user']['login']
issue_number = event['issue']['number']
repo_name = event['repository']['full_name']
assignment_date = event['comment']['created_at']

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


def check_in(issue):
    label_names = [label.name for label in issue.get_labels()]
    if not issue.assignees and not "bot:assigned"  in label_names:
        return

    assignee = issue.assignees[0].login
    now = datetime.now(timezone.utc)
    checkin_date = now

    if 'bot:checkin-sent' not in label_names:
        assigned_at = issue.updated_at
        if now >= assigned_at + timedelta(days=1):
            issue.create_comment(f'Hi @assignee 👋\n'
            f' Just checking in — are you still working on this issue?'
            f'Please reply within **3 days**, otherwise I’ll unassign you so someone else can take it.'
            f'*This comment was automatically generated.*')
            issue.add_to_labels('bot:awaiting-response', 'bot:checkin-sent')

        return
    elif 'bot:awaiting-response' in label_names:
        if now >= checkin_date + timedelta(days=1):
            issue.remove_from_assignees(assignee)
            issue.remove_from_labels('bot:checkin-sent', 'bot:assigned', 'bot:awaiting-response')
            issue.create_comment(f'⏳ No response received in the last 3 days.'
            f'The assignee has been removed so others can pick up this issue.'
            f'*This comment was automatically generated.*')
