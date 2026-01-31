## 🤖 GitHub Issue Assignment Bot

A lightweight GitHub Actions bot written in Python that helps manage issue assignments automatically based on comments and inactivity.

This bot can:

- Assign issues when a user comments ``assign me``

- Periodically check in with assignees

- Automatically unassign inactive assignees after reminders or unassign them if they comment ``/unassign``

- Keep issue state visible using labels

Built with GitHub Actions, Python, and PyGithub.

## ✨ Features
### 📝 Comment-based commands

- ``assign me``
Assigns the commenting user to the issue (if unassigned).

- ``/unassign``
Allows the current assignee to unassign themselves.

- ``/working``
Allows the assignee to confirm they are still working on the issue, so that they will not be unassigned.

### ⏰ Scheduled check-ins

Runs daily via GitHub Actions cron:

- Day 7: Sends a friendly check-in comment

- Day 9: Sends a final reminder

- Day 10: Automatically unassigns if no response

### 🏷 Labels used by the bot

The bot manages issue state using labels:

- ``bot:assigned``

- ``bot:checkin-sent``

- ``bot:awaiting-response``

- ``bot:warning-sent``

- ``bot:dropped``

Labels are automatically created if they don’t exist.


## 🧠 How it works

The bot reacts to two GitHub events:

### 1️⃣ issue_comment

Triggered when someone comments on an issue:

- Parses the comment text

- Matches known commands

- Executes the corresponding handler

### 2️⃣ schedule

Triggered once per day:

- Iterates over open issues

- Checks how long the issue has been assigned

- Sends reminders or unassigns as needed

## 📁 Project structure
<pre>
.
├── bot.py              # Main entry point
├── checkins.py         # Checkin functions
├── config.py           # config settings
├── handlers.py         # Handlers of assign/unassign logic  
├── helpers.py          # GitHub + time helper functions
├── .github/
│   └── workflows/
│       └── bot.yml     # GitHub Actions workflow
├── tests/
│   └── test_bot.py     # Unit tests (pytest)
└── README.md
</pre>

## ⚙️ Setup
### 1️⃣ Create a GitHub token

Create a fine-grained or classic token with:

- ``issues: write``

- ``contents: read``

Add it to your repo secrets as:
<pre>
GH_TOKEN
</pre>  

### 2️⃣ Add the GitHub Actions workflow

``.github/workflows/bot.yml``

## 🧪 Running tests locally

Install dependencies:

<pre>
pip install pytest PyGithub
</pre>  

Run tests:

<pre>
pytest
</pre>  

The test suite uses MagicMock and monkeypatch to avoid real GitHub API calls.


## 🤝 Contributing

Pull requests and ideas are welcome!

## 📜 License

MIT 


