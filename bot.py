import os
import json


from checkins import check_in_reply_by_assignee, check_in
from handlers import handle_assign, handle_unassign
from helpers import get_github, ensure_label, create_comment

COMMANDS = {
    'assign me': handle_assign,
    '/unassign' : handle_unassign,

}

def handle_issue_comment(event):
    if event['comment']['user']['type'] == 'Bot':
        return
    
    comment_text = event['comment']['body'].strip().lower()
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


    for command, handler in COMMANDS.items():
        if comment_text.startswith(command):
            handler(issue, comment_author)
            return


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





