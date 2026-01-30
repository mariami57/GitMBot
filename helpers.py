import os

from github import Github, Auth


def get_assignee_logins(issue):
    return [a.login for a in issue.assignees]

def get_assignees(issue):
    return [a for a in issue.assignees]

def get_github():
    return Github(auth=Auth.Token(os.environ['GH_TOKEN']))

def get_repo(repo_name):
    return get_github().get_repo(repo_name)

def ensure_label(repo, name, color='ededed', description=''):
    try:
        repo.get_label(name)
    except Exception:
        repo.create_label(name=name, color=color, description=description)

def label_names(issue):
    return  [label.name for label in issue.get_labels()]

def create_comment(issue, comment_text):
    return issue.create_comment(comment_text)


def days_since_assignment(issue, now):
    return (now - issue.updated_at).days