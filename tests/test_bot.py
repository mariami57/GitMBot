import pytest
from unittest.mock import MagicMock
from datetime import datetime, timezone


from bot import handle_issue_comment
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


def test_handle_issue_comment_assign(monkeypatch):
    issue = fake_issue()
    repo = fake_repo(issue)

    event = {
        'comment':{'body': 'assign me', 'user': {'login': 'Alice', 'type':'User'}},
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



def test_ignore_bot_comment(monkeypatch):
    event = {
        'comment':{'body': 'assign me', 'user': {'login': 'my-bot', 'type':'Bot'}},
        'issue': {'number': 1},
        'repository':{'full_name':'test/repo'}
    }

    handle_issue_comment(event)


def test_handle_issue_comment_unassign(monkeypatch):
    issue = fake_issue()
    repo = fake_repo(issue)

    event = {
        'comment': {'body': '/unassign', 'user': {'login': 'Alice', 'type': 'User'}},
        'issue': {'number': 1},
        'repository': {'full_name': 'test/repo'}
    }

    fake_gh = MagicMock()
    fake_gh.get_repo.return_value = repo
    monkeypatch.setattr('bot.get_github', lambda: fake_gh)

    assignee = MagicMock()
    assignee.login = 'Alice'
    issue.assignees = [assignee]

    assigned_label = MagicMock()
    assigned_label.name = 'bot:assigned'
    awaiting_label = MagicMock()
    awaiting_label.name = 'bot:awaiting-response'
    checkin_label = MagicMock()
    checkin_label.name = 'bot:checkin-sent'
    issue.get_labels.return_value = [awaiting_label, assigned_label, checkin_label]


    issue.get_labels.return_value = [assigned_label]

    handle_issue_comment(event)

    issue.remove_from_assignees.assert_called_with('Alice')
    issue.remove_from_labels.assert_any_call('bot:assigned')

    existing_label_names = [lbl.name for lbl in issue.get_labels()]
    if 'bot:awaiting-response' in existing_label_names and 'bot:checkin-sent' in existing_label_names:
        issue.remove_from_labels.asert_any_call('bot:awaiting-response', 'bot:checkin-sent')

    issue.add_to_labels.assert_called_with('bot:dropped')
    issue.create_comment.assert_called()
    assert (f"@{event['comment']['user']['login']} has"
    " unassigned themselves from this issue.\n\n") in issue.create_comment.call_args[0][0]

def test_handle_issue_comment_working(monkeypatch):
    issue = fake_issue()
    repo = fake_repo(issue)

    event = {
        'comment': {'body': '/working', 'user': {'login': 'Alice', 'type': 'User'}},
        'issue': {'number': 1},
        'repository': {'full_name': 'test/repo'}
    }

    fake_gh = MagicMock()
    fake_gh.get_repo.return_value = repo
    monkeypatch.setattr('bot.get_github', lambda: fake_gh)

    assignee = MagicMock()
    assignee.login = 'Alice'
    issue.assignees = [assignee]

    assigned_label = MagicMock()
    assigned_label.name = 'bot:assigned'

    checkin_label = MagicMock()
    checkin_label.name = 'bot:checkin-sent'

    awaiting_label = MagicMock()
    awaiting_label.name = 'bot:awaiting-response'

    issue.get_labels.return_value = [awaiting_label, assigned_label, checkin_label]

    handle_issue_comment(event)


    issue.remove_from_labels.assert_any_call('bot:checkin-sent')
    issue.remove_from_labels.assert_any_call('bot:awaiting-response')
    issue.create_comment.assert_called()
    assert (f"Thanks @{event['comment']['user']['login']} for "
            "confirming you are working on this issue!") in issue.create_comment.call_args[0][0]