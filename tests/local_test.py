# tests/local_test_assignment.py
import sys
from pathlib import Path
from datetime import datetime, timezone

from checkins import check_in

# Add project root to sys.path so we can import helpers
sys.path.append(str(Path(__file__).resolve().parent.parent))

from helpers import get_repo, days_since_assignment, get_assignment_date, create_comment, label_names

# --------- CONFIG ----------
repo = get_repo("mariami57/GitMBot")
ISSUE_NUMBER = 5
assignee = "mariami57"
issue = repo.get_issue(5)
now = datetime.now(timezone.utc)
# ---------------------------
#
# comments = list(issue.get_comments())  # fetch all comments
#
# print(f"All comments for issue #{ISSUE_NUMBER}:\n")
# for c in comments:
#     print(f"Author: {c.user.login} ({c.user.type})")
#     print(f"Created at: {c.created_at}")
#     print("Body:")
#     print(c.body)
#     print("-" * 40)

# assigned_at = get_assignment_date(issue, assignee)
# print("Assigned at:", assigned_at)
#
# age = days_since_assignment(issue, now, assignee)
# print("Age in days:", age)


# Backup original functions
create_comment_original = create_comment
add_to_labels_original = None


# 2️⃣ Get all label names
labels = label_names(issue)

# 3️⃣ Print them
print(f"Labels for issue #{issue.number}: {labels}")



check_in(repo)