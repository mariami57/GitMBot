import os
import json
from datetime import datetime, timedelta, timezone

from github import Github, Auth

event_path = os.environ['GITHUB_EVENT_PATH']

with open(event_path, 'r') as f:
    event = json.load(f)

DRY_RUN = False

comment_text = event['comment']['body']
comment_author = event['comment']['user']['login']
issue_number = event['issue']['number']
repo_name = event['repository']['full_name']
event_name = os.environ.get('GITHUB_EVENT_NAME')
print(f'Bot triggered by event: {event_name}')

gh = Github(auth=Auth.Token(os.environ['GH_TOKEN']))
repo = gh.get_repo(repo_name)

print(f'Comment on {repo_name} issue #{issue_number}')
print(f'Author: {comment_author}')
print(f'Text: {comment_text}')


def label_names(issue):
    return  [label.name for label in issue.get_labels()]

def create_comment(issue, comment_text):
    return issue.create_comment(comment_text)

def check_in_reply_by_assignee(issue, comment_author):
    labels= label_names(issue)

    if 'bot:awaiting-response' not in labels or not issue.assignees:
        return False

    return comment_author == issue.assignees[0].login

def ensure_label(repo, name, color='ededed', description=''):
    try:
        repo.get_label(name)
    except Exception:
        repo.create_label(name=name, color=color, description=description)

if event_name == 'issue_comment':
    issue = repo.get_issue(number=event['issue']['number'])

    ensure_label(repo, 'bot:assigned', '0e8a16', 'Assigned by bot')
    ensure_label(repo, 'bot:dropped', 'b60205', 'Unassigned by bot')
    ensure_label(repo, 'bot:checkin-sent', 'cfd3d7', 'Check-in sent')
    ensure_label(repo, 'bot:awaiting-response', 'fbca04', 'Waiting for assignee reply')

    if check_in_reply_by_assignee(issue, comment_author):
        issue.remove_from_labels('bot:checkin-sent', 'bot:awaiting-response')
        create_comment(
            issue,
            f'Thanks @{comment_author} for checking in! ✅\n\n'
            '*This comment was automatically generated.*'
        )
        exit(0)



if 'assign me' in comment_text.lower():

    issue = repo.get_issue(number=issue_number)
    assignees = [u.login for u in issue.assignees]
    if comment_author not in issue.assignees:
        assignees = [u.login for u in issue.assignees]

        if comment_author not in assignees:
            issue.add_to_assignees(comment_author)
            issue.add_to_labels('bot:assigned')

            if 'bot:dropped' in label_names(issue):
                issue.remove_from_labels('bot:dropped')

            create_comment(
                issue,
                f'✅ Assigned to @{comment_author}.\n\n'
                '*This comment was automatically generated.*'
            )

        exit(0)

def check_in():
    if event_name == 'schedule':
        now = datetime.now(timezone.utc)

        for issue in repo.get_issues(state='open'):
            labels = label_names(issue)

            if not issue.assignees or 'bot:assigned' not in labels:
                continue

            assignee = issue.assignees[0].login

            if 'bot:checkin-sent' not in labels:
                assigned_at = issue.updated_at

                if now >= assigned_at + timedelta(days=7):
                    create_comment(
                        issue,
                        f'Hi @{assignee} 👋\n\n'
                        'Just checking in — are you still working on this issue?\n\n'
                        'Please reply within **3 days**, otherwise I’ll unassign you so someone else can take it.\n\n'
                        '*This comment was automatically generated.*'
                    )
                    issue.add_to_labels('bot:checkin-sent', 'bot:awaiting-response')
                continue


            if 'bot:awaiting-response' in labels:
                comments = list(issue.get_comments())
                checkin_comment = next(
                    (
                        c for c in reversed(comments)
                        if c.user.type == 'Bot' and 'Just checking in' in c.body
                    ),
                    None
                )

                if checkin_comment and now >= checkin_comment.created_at + timedelta(days=3):
                    if DRY_RUN:
                        print(f'[DRY-RUN] Would unassign {assignee} from issue #{issue.number}')
                    else:
                        issue.remove_from_assignees(assignee)
                        issue.remove_from_labels(
                            'bot:assigned',
                            'bot:checkin-sent',
                            'bot:awaiting-response'
                        )
                        issue.add_to_labels('bot:dropped')

                        create_comment(
                            issue,
                            '⏳ No response received in the last 3 days.\n\n'
                            'The assignee has been removed so others can pick up this issue.\n\n'
                            '*This comment was automatically generated.*'
                        )