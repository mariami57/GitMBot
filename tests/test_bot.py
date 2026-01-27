import pytest
from unittest.mock import MagicMock
from datetime import datetime, timedelta, timezone

from bot import handle_assign, check_in_reply_by_assignee, check_in,handle_issue_comment, create_comment


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


def test_handle_assign():
    issue = fake_issue()
    comment_author = 'Alice'

    handle_assign(issue, comment_author)

    issue.add_to_assignees.assert_called_with('Alice')
    issue.add_to_labels.assert_called_with('bot:assigned')
    issue.create_comment.assert_called()

def test_check_in_reply_by_assignee_assignee_not_in_issue_assignees():
    issue = fake_issue()
    label_mock = MagicMock()
    label_mock.name = 'bot:awaiting-response'
    issue.get_labels.return_value = [label_mock]

    assert check_in_reply_by_assignee(issue, 'Bob') is False


def test_check_in_reply_by_assignee_label_not_in_issue_labels():
    issue = fake_issue()
    assignee_mock = MagicMock()
    assignee_mock.login = 'Bob'
    issue.assignees = [assignee_mock]

    assert check_in_reply_by_assignee(issue, 'Bob') is False

def test_check_in_reply_by_assignee_label_returns_true():
    issue = fake_issue()
    assignee_mock = MagicMock()
    label_mock = MagicMock()
    assignee_mock.login = 'Bob'
    label_mock.name = 'bot:awaiting-response'
    issue.assignees = [assignee_mock]
    issue.get_labels.return_value = [label_mock]

    assert check_in_reply_by_assignee(issue, 'Bob') is True


def test_check_in_send_a_reminder_to_assignee():
    issue = fake_issue()

    assignee_mock = MagicMock()
    assignee_mock.login = 'Alice'
    issue.assignees = [assignee_mock]

    label_assigned = MagicMock()
    label_assigned.name = 'bot:assigned'
    issue.get_labels.return_value = [label_assigned]

    issue.updated_at = datetime.now(timezone.utc) - timedelta(days=8)

    repo = fake_repo(issue)

    check_in(repo)

    issue.create_comment.assert_called_once()
    issue.add_to_labels.assert_any_call('bot:checkin-sent', 'bot:awaiting-response')


