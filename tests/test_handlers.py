from datetime import datetime, timezone
from unittest.mock import MagicMock

from handlers import handle_assign, handle_working_confirmation


def fake_issue():
    issue = MagicMock()
    issue.number = 1
    issue.assignees = []
    issue.updated_at = datetime.now(timezone.utc)
    issue.get_labels.return_value = []
    issue.get_comments.return_value = []
    return issue

def fake_repo(issue):
    repo = MagicMock()
    repo.get_issue.return_value = issue
    repo.get_issues.return_value = [issue]
    return repo


def test_handle_assign_successfully_assign():
    issue = fake_issue()
    comment_author = 'Alice'

    handle_assign(issue, comment_author)

    issue.add_to_assignees.assert_called_with('Alice')
    issue.add_to_labels.assert_called_with('bot:assigned')
    issue.create_comment.assert_called()

def test_handle_assign_try_to_assign_already_assigned():
    issue = fake_issue()
    assignee1 = MagicMock()
    assignee1.login = 'Alice'
    issue.assignees = [assignee1]

    assignee2 = MagicMock()
    assignee2.login = 'Bob'

    handle_assign(issue, 'Bob')
    issue.add_to_assignees.assert_not_called()
    issue.add_to_labels.assert_not_called()
    issue.create_comment.assert_not_called()

def test_handle_assign_try_to_assign_the_same_assignee():
    issue = fake_issue()
    assignee1 = MagicMock()
    assignee1.login = 'Alice'
    issue.assignees = [assignee1]


    handle_assign(issue, 'Alice')

    issue.add_to_assignees.assert_not_called()


def test_assign_after_bot_dropped():
    issue = fake_issue()
    comment_author = 'Alice'

    label_dropped = MagicMock()
    label_dropped.name = 'bot:dropped'

    issue.get_labels.return_value = [label_dropped]

    handle_assign(issue, comment_author)

    issue.add_to_labels.assert_called_with('bot:assigned')
    issue.remove_from_labels.assert_called_with('bot:dropped')
    issue.add_to_assignees.assert_called_with('Alice')
    issue.create_comment.assert_called()


def test_working_confirmation_bot_removes_awaiting_response_and_checkin_labels():
    issue = fake_issue()
    comment_author = 'Alice'

    assignee = MagicMock()
    assignee.login = comment_author
    issue.assignees = [assignee]

    label_awaiting_response = MagicMock()
    label_checkin_sent = MagicMock()
    label_awaiting_response.name = 'bot:awaiting-response'
    label_checkin_sent.name = 'bot:checkin-sent'
    issue.get_labels.return_value = [label_awaiting_response, label_checkin_sent]

    handle_working_confirmation(issue, comment_author)

    issue.remove_from_labels.assert_called_with('bot:checkin-sent', 'bot:awaiting-response')
    issue.create_comment.assert_called()
