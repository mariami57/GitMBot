from datetime import datetime, timedelta, timezone

from config import DRY_RUN
import helpers



def check_in_reply_by_assignee(issue, comment_author):
    labels= helpers.label_names(issue)

    if 'bot:awaiting-response' not in labels or not issue.assignees:
        return False

    return comment_author == issue.assignees[0].login


def check_in(repo):

    now = datetime.now(timezone.utc)

    for issue in repo.get_issues(state='open'):
        labels = helpers.label_names(issue)

        if not issue.assignees or 'bot:assigned' not in labels:
            continue

        assignee = issue.assignees[0].login
        age = helpers.days_since_assignment(issue, now, assignee)

        if 'bot:checkin-sent' not in labels:

            if age == 1:
                helpers.create_comment(
                    issue,
                    f'Hi @{assignee} 👋\n\n'
                    'Just checking in — are you still working on this issue?\n\n'
                    'Please reply within **1 day**, otherwise I’ll unassign you so someone else can take it.'
                    'Please confirm you are working on the issue using the command: /working \n\n'
                    '*This comment was automatically generated.*'
                )
                issue.add_to_labels('bot:checkin-sent', 'bot:awaiting-response')
            continue


        if 'bot:awaiting-response' in labels and 'bot:checkin-sent' in labels and age == 2:
            helpers.create_comment(
                issue,
                f'⚠️ Final reminder @{assignee}\n\n'
                'I haven’t heard back yet. If there’s no reply by tomorrow, '
                'I’ll unassign this issue.'
                'Please confirm you are working on the issue using the command: /working \n\n'
                '*This comment was automatically generated.*'
            )
            issue.add_to_labels('bot:warning-sent')
            continue

        if age == 3 and 'bot:awaiting-response' in labels:
            comments = list(issue.get_comments())
            checkin_comment = next(
                (
                    c for c in reversed(comments)
                    if c.user.type == 'Bot' and 'Final reminder' in c.body
                ),
                None
            )

            if checkin_comment:
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

                    helpers.create_comment(
                        issue,
                        '⏳ No response received in the last 3 days.\n\n'
                        'The assignee has been removed so others can pick up this issue.\n\n'
                        '*This comment was automatically generated.*'
                    )