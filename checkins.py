from datetime import datetime, timezone

from config import DRY_RUN
from helpers import create_comment, label_names, days_since_assignment, get_assignee_logins
from handlers import handle_unassign



def check_in_reply_by_assignee(issue, comment_author):
    labels = label_names(issue)
    assignees_logins = get_assignee_logins(issue)

    has_awaiting = 'bot:awaiting-response' in labels

    if not has_awaiting or not assignees_logins:
        return False

    return comment_author in assignees_logins


def check_in(repo):

    now = datetime.now(timezone.utc)

    for issue in repo.get_issues(state='open'):
        labels = label_names(issue)

        has_assigned = 'bot:assigned' in labels
        has_checkin = 'bot:checkin-sent' in labels
        has_awaiting = 'bot:awaiting-response' in labels
        has_warning = 'bot:warning-sent' in labels

        if not issue.assignees or not has_assigned:
            continue

        assignee = issue.assignees[0].login
        age = days_since_assignment(issue, now, assignee)

        if not has_checkin:
            if age == 3:
                create_comment(
                    issue,
                    f'Hi @{assignee} 👋\n\n'
                    'Just checking in — are you still working on this issue?\n\n'
                    'Please reply within **1 day**, otherwise I’ll unassign you so someone else can take it.'
                    'Please confirm you are working on the issue using the command: /working \n\n'
                    '*This comment was automatically generated.*'
                )
                issue.add_to_labels('bot:checkin-sent', 'bot:awaiting-response')
            continue


        if age == 7 and has_checkin and has_awaiting and not has_warning:
            create_comment(
                issue,
                f'Final reminder @{assignee}\n\n'
                'I haven’t heard back yet. If there’s no reply by tomorrow, '
                'I’ll unassign this issue.'
                'Please confirm you are working on the issue using the command: /working \n\n'
                '*This comment was automatically generated.*'
            )
            issue.add_to_labels('bot:warning-sent')
            continue

        if age == 8 and has_checkin and has_awaiting and has_warning:
            comments = list(issue.get_comments())
            checkin_comment = next(
                (
                    c for c in reversed(comments)
                    if 'Final reminder' in c.body
                ),
                None
            )

            if checkin_comment:
                if DRY_RUN:
                    print(f'[DRY-RUN] Would unassign {assignee} from issue #{issue.number}')
                else:
                    handle_unassign(issue, assignee)

                    create_comment(
                        issue,
                        'No response received in the last 3 days.\n\n'
                        'The assignee has been removed so others can pick up this issue.\n\n'
                        '*This comment was automatically generated.*'
                    )
