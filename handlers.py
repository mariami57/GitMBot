from datetime import datetime, timezone
from helpers import label_names, get_assignee_logins, get_assignees, create_comment, get_bot_label_state


def handle_assign(issue, comment_author):
    assignee_logins = get_assignee_logins(issue)
    assignees = get_assignees(issue)
    state = get_bot_label_state(issue)

    if len(assignees) > 0:
        return

    if comment_author in assignee_logins:
        return


    issue.add_to_assignees(comment_author)

    issue.add_to_labels('bot:assigned')

    if state['dropped']:
        issue.remove_from_labels('bot:dropped')

    now = datetime.now(timezone.utc).isoformat()
    create_comment(issue, f'Assigned to @{comment_author} at {now}.\n\n '
                          '*This comment was automatically generated.*')

def handle_unassign(issue, comment_author):
    assignee_logins = get_assignee_logins(issue)
    assignees = get_assignees(issue)
    state = get_bot_label_state(issue)

    if not assignees:
        create_comment(issue, 'No one is currently assigned.'
                              '\n\n *This comment was automatically generated.*')
        return

    if comment_author not in assignee_logins:
        create_comment(issue, f'You are not assigned to this issue and '
                              'you are not able to unassign it.'
                              '\n\n *This comment was automatically generated.*')
        return

    if state['awaiting_response'] and state['checkin_sent']:
        issue.remove_from_labels('bot:checkin-sent')
        issue.remove_from_labels('bot:awaiting-response')

    if state['warning_sent']:
        issue.remove_from_labels('bot:warning-sent')

    issue.add_to_labels('bot:dropped')
    issue.remove_from_assignees(comment_author)
    issue.remove_from_labels('bot:assigned')


    comments = list(issue.get_comments())
    last_comment = comments[-1]
    unassign_comment = last_comment if '/unassign' in last_comment.body else None

    if unassign_comment is not None:
        create_comment(issue, f'@{comment_author} has unassigned themselves from this issue.\n\n'
                          '*This comment was automatically generated.*')




def handle_working_confirmation(issue, comment_author):
    assignees = get_assignees(issue)
    assignee_logins = get_assignee_logins(issue)
    labels = label_names(issue)
    state = get_bot_label_state(issue)

    if not assignees:
        create_comment(issue, 'No one is currently assigned. Please comment the following command to get assigned: assign me '
                              '\n\n *This comment was automatically generated.*')
        return

    if comment_author not in assignee_logins:
        create_comment(issue, f'You are not assigned to this issue. '
                              '\n\n *This comment was automatically generated.*')
        return

    if not state['checkin_sent'] or not state['awaiting_response']:
        return

    issue.remove_from_labels('bot:checkin-sent')
    issue.remove_from_labels('bot:awaiting-response')

    if state['warning_sent']:
        issue.remove_from_labels('bot:warning-sent')

    create_comment(issue,  f'Thanks @{comment_author} for confirming you are working on this issue! ✅\n\n'
        '*This comment was automatically generated.*')









