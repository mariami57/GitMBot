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


