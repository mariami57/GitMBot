from datetime import datetime, timedelta, timezone

from config import DRY_RUN
from helpers import label_names, create_comment


def check_in_reply_by_assignee(issue, comment_author):
    labels= label_names(issue)

    if 'bot:awaiting-response' not in labels or not issue.assignees:
        return False

    return comment_author == issue.assignees[0].login


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