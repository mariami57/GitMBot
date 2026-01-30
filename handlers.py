from bot import check_in_reply_by_assignee
from helpers import label_names, get_assignee_logins, get_assignees, create_comment, get_github, ensure_label

def handle_assign(issue, comment_author):
    assignee_logins = get_assignee_logins(issue)
    assignees = get_assignees(issue)

    if len(assignees) > 0:
        return

    if comment_author in assignee_logins:
        return


    issue.add_to_assignees(comment_author)
    issue.add_to_labels('bot:assigned')
    labels = label_names(issue)
    if 'bot:dropped' in labels:
        issue.remove_from_labels('bot:dropped')

    create_comment(issue, f'Assigned to @{comment_author}.\n\n This comment was automatically generated.*')

def handle_unassign(issue, comment_author):
    assignee_logins = get_assignee_logins(issue)
    assignees = get_assignees(issue)

    if not assignees:
        create_comment(issue, 'No one is currently assigned.')
        return

    if comment_author not in assignee_logins:
        create_comment(issue, f'You are not assigned to this issue and '
                              'you are not able to unassign it.'
                              '\n\n This comment was automatically generated.*')
        return

    issue.remove_from_assignees(comment_author)
    issue.remove_from_labels('bot:assigned', 'bot:checkin-sent', 'bot:awaiting-response')

    issue.add_to_labels('bot:dropped')
    create_comment(issue, f'@{comment_author} has unassigned themselves from this issue.\n\n'
                          '*This comment was automatically generated.*')



