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
