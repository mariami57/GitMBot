from helpers import label_names, get_assignee_logins, get_assignees, create_comment

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

    create_comment(issue, f'Assigned to @{comment_author}.\n\n '
                          '*This comment was automatically generated.*')

def handle_unassign(issue, comment_author):
    assignee_logins = get_assignee_logins(issue)
    assignees = get_assignees(issue)

    if not assignees:
        create_comment(issue, 'No one is currently assigned.'
                              '\n\n *This comment was automatically generated.*')
        return

    if comment_author not in assignee_logins:
        create_comment(issue, f'You are not assigned to this issue and '
                              'you are not able to unassign it.'
                              '\n\n *This comment was automatically generated.*')
        return

    issue.remove_from_assignees(comment_author)
    issue.remove_from_labels('bot:assigned')

    if 'bot:awaiting-response' in label_names(issue) and 'bot:checkin-sent' in label_names(issue):
        issue.remove_from_labels('bot:checkin-sent', 'bot:awaiting-response')

    issue.add_to_labels('bot:dropped')


    create_comment(issue, f'@{comment_author} has unassigned themselves from this issue.\n\n'
                          '*This comment was automatically generated.*')




def handle_working_confirmation(issue, comment_author):
    assignees = get_assignees(issue)
    assignee_logins = get_assignee_logins(issue)
    labels = label_names(issue)

    if not assignees:
        create_comment(issue, 'No one is currently assigned. Please comment the following command to get assigned: assign me '
                              '\n\n *This comment was automatically generated.*')
        return

    if comment_author not in assignee_logins:
        create_comment(issue, f'You are not assigned to this issue. '
                              '\n\n *This comment was automatically generated.*')
        return

    if not 'bot:checkin-sent' in labels or not 'bot:awaiting-response' in labels:
        return

    issue.remove_from_labels('bot:checkin-sent')
    issue.remove_from_labels('bot:awaiting-response')
    create_comment(issue,  f'Thanks @{comment_author} for confirming you are working on this issue! ✅\n\n'
        '*This comment was automatically generated.*')









