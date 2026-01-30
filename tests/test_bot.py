import pytest
from unittest.mock import MagicMock
from datetime import datetime, timedelta, timezone

import helpers
from bot import handle_assign, check_in_reply_by_assignee, check_in,handle_issue_comment
from helpers import get_github, get_repo, create_comment

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


def test_handle_issue_comment_assign(monkeypatch):
    issue = fake_issue()
    repo = fake_repo(issue)

    event = {
        'comment':{'body': 'assign me', 'user': {'login': 'Alice'}},
        'issue': {'number': 1},
        'repository':{'full_name':'test/repo'}
    }


    fake_gh = MagicMock()
    fake_gh.get_repo.return_value = repo
    monkeypatch.setattr('bot.get_github', lambda: fake_gh)


    handle_issue_comment(event)

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


def test_check_in_send_a_reminder_to_assignee(monkeypatch):
    issue = fake_issue()

    assignee_mock = MagicMock()
    assignee_mock.login = 'Alice'
    issue.assignees = [assignee_mock]

    label_assigned = MagicMock()
    label_assigned.name = 'bot:assigned'
    issue.get_labels.return_value = [label_assigned]


    repo = fake_repo(issue)

    monkeypatch.setattr(helpers, 'days_since_assignment', lambda issue, now: 7)

    check_in(repo)

    issue.create_comment.assert_called()
    issue.add_to_labels.assert_any_call('bot:checkin-sent', 'bot:awaiting-response')


def test_check_in_unassign_assignee(monkeypatch):
    issue = fake_issue()

    assignee_mock = MagicMock()
    assignee_mock.login = 'Alice'
    issue.assignees = [assignee_mock]

    label_assigned = MagicMock()
    label_assigned.name = 'bot:assigned'
    label_checkin = MagicMock()
    label_checkin.name = 'bot:awaiting-response'
    label_sent = MagicMock()
    label_sent.name = 'bot:checkin-sent'

    issue.get_labels.return_value = [label_assigned, label_checkin, label_sent]

    bot_comment = MagicMock()
    bot_comment.user.type = 'Bot'
    bot_comment.body = 'Final reminder'
    bot_comment.created_at = datetime.now(timezone.utc) - timedelta(days=1)
    issue.get_comments.return_value = [bot_comment]

    repo = fake_repo(issue)

    monkeypatch.setattr(helpers, 'days_since_assignment', lambda issue, now: 10)

    check_in(repo)

    issue.remove_from_assignees.assert_called_with('Alice')
    issue.remove_from_labels.assert_called()
    issue.add_to_labels.assert_called_with('bot:dropped')
    issue.create_comment.assert_called()


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


