import os
import json
from datetime import datetime, timedelta, timezone

from github import Github, Auth

DRY_RUN = False

def get_github():
    return Github(auth=Auth.Token(os.environ['GH_TOKEN']))

def get_repo(repo_name):
    return get_github().get_repo(repo_name)

def ensure_label(repo, name, color='ededed', description=''):
    try:
        repo.get_label(name)
    except Exception:
        repo.create_label(name=name, color=color, description=description)

def label_names(issue):
    return  [label.name for label in issue.get_labels()]

def create_comment(issue, comment_text):
    return issue.create_comment(comment_text)

def check_in_reply_by_assignee(issue, comment_author):
    labels= label_names(issue)

    if 'bot:awaiting-response' not in labels or not issue.assignees:
        return False

    return comment_author == issue.assignees[0].login

def handle_issue_comment(event):
    comment_text = event['comment']['body']
    comment_author = event['comment']['user']['login']
    issue_number = event['issue']['number']
    repo_name = event['repository']['full_name']

    gh = get_github()
    repo = gh.get_repo(repo_name)
    issue = repo.get_issue(number=issue_number)

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
        handle_assign(issue, comment_author)


def handle_assign(issue, comment_author):
    assignees = [a.login for a in issue.assignees]
    if comment_author in assignees:
        return

    if len(assignees) > 0:
        return

    issue.add_to_assignees(comment_author)
    issue.add_to_labels('bot:assigned')
    labels = label_names(issue)
    if 'bot:dropped' in labels:
        issue.remove_from_labels('bot:dropped')

    create_comment(issue, f'Assigned to @{comment_author}.\n\n This comment was automatically generated.*')



def check_in(repo):

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

def main():
    event_path = os.environ['GITHUB_EVENT_PATH']
    event_name = os.environ.get('GITHUB_EVENT_NAME')
    print(f'Bot triggered by event: {event_name}')

    gh = get_github()

    if event_name == 'issue_comment':
        with open(event_path) as f:
            event = json.load(f)
        handle_issue_comment(event)
    elif event_name == 'schedule':
        repo_name = os.environ['GITHUB_REPOSITORY']
        repo = gh.get_repo(repo_name)
        check_in(repo)

if __name__ == '__main__':
    main()





