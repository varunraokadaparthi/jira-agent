# JIRA Agent - Claude Commands

A collection of Claude commands for automating JIRA workflows, including progress report generation and PR summary comments.

## Commands

| Command | Description |
|---------|-------------|
| `jira-report` | Generate HTML progress reports from JIRA data |
| `jira-pr-comment` | Add PR summary comments to JIRA issues |

---

## Prerequisites

### 1. Install JIRA CLI

Install the `jira` CLI tool (jira-cli):

```bash
# macOS
brew install ankitpokhrel/jira-cli/jira-cli

# Linux (using go)
go install github.com/ankitpokhrel/jira-cli/cmd/jira@latest

# Or download from releases
# https://github.com/ankitpokhrel/jira-cli/releases
```

### 2. Configure JIRA CLI

Initialize the JIRA CLI with your credentials:

```bash
jira init
```

You'll be prompted for:
- **Installation type**: `Cloud` or `Local`
- **Server URL**: Your JIRA instance URL (e.g., `https://issues.redhat.com`)
- **Login method**: `api-token` (recommended)
- **API Token**: Generate from your JIRA account settings

#### Generate JIRA API Token

1. Go to your JIRA instance → Profile → Personal Access Tokens
2. Click **Create token**
3. Give it a name and set expiration
4. Copy the token and use it during `jira init`

#### Verify Setup

```bash
# Check authentication
jira me

# List projects you have access to
jira project list

# Test issue listing
jira issue list -p YOUR_PROJECT --limit 5
```

### 3. Install GitHub CLI (for jira-pr-comment)

```bash
# macOS
brew install gh

# Linux
sudo apt install gh  # Debian/Ubuntu
sudo dnf install gh  # Fedora
```

Authenticate with GitHub:

```bash
gh auth login
```

---

## jira-report Command

Generate comprehensive HTML progress reports from JIRA data for a project and time period.

### Usage

```bash
# Current sprint
@jira-report SDCICD

# Specific date range
@jira-report SDCICD Dec 1 to Dec 31

# Quarter
@jira-report SDCICD Q4 2024
```

### Output

The command generates an HTML report saved to `output/jira-report-YYYY-MM-DD.html` with:

- **Executive Summary**: 2-3 sentence overview with completion metrics
- **Key Achievements**: Grouped by category (Features, Bug Fixes, Platform Work)
- **Metrics**: Delivery performance, work distribution percentages
- **Insights & Trends**: Analysis of patterns and velocity

---

## Sending Reports via Email (Gmail)

The `jira_report_email.py` script sends generated HTML reports via email using SMTP.

### Setup Gmail App Password

Gmail requires an **App Password** when using SMTP with 2-Factor Authentication enabled.

#### Step 1: Enable 2-Factor Authentication

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Under "Signing in to Google", click **2-Step Verification**
3. Follow the prompts to enable 2FA

#### Step 2: Generate App Password

1. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
2. Select app: **Mail**
3. Select device: **Other (Custom name)** → Enter "JIRA Report"
4. Click **Generate**
5. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

> **Note**: App Passwords are only available when 2-Step Verification is enabled.

#### Step 3: Configure Environment Variables

Set these environment variables before running the email script:

```bash
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USERNAME="your-email@gmail.com"
export SMTP_PASSWORD="abcd efgh ijkl mnop"  # Your App Password
export SMTP_FROM="your-email@gmail.com"
export SMTP_REQUIRE_TLS="true"
export SMTP_RECIPIENTS="recipient1@example.com,recipient2@example.com"
```

Or add to your `~/.bashrc` or `~/.zshrc`:

```bash
# JIRA Report Email Configuration
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USERNAME="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"
export SMTP_FROM="your-email@gmail.com"
export SMTP_REQUIRE_TLS="true"
```

### Send Report Email

```bash
# Basic usage
python jira_report_email.py output/jira-report-2026-01-06.html

# With explicit recipients
python jira_report_email.py --recipients user@example.com report.html

# With explicit date
python jira_report_email.py --date 2026-01-10 report.html
```

### Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `SMTP_SERVER` | SMTP server hostname | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | `587` (TLS) or `465` (SSL) |
| `SMTP_USERNAME` | Email account username | `your-email@gmail.com` |
| `SMTP_PASSWORD` | App Password (not regular password) | `abcd efgh ijkl mnop` |
| `SMTP_FROM` | Sender email address | `your-email@gmail.com` |
| `SMTP_REQUIRE_TLS` | Use STARTTLS encryption | `true` |
| `SMTP_RECIPIENTS` | Default recipients (comma-separated) | `a@example.com,b@example.com` |

## jira-pr-comment Command

Add summary comments to JIRA issues describing work done in associated pull requests.

### Usage

```bash
@jira-pr-comment SDCICD-1723
```

### How It Works

1. **Finds PRs**: Searches across all GitHub repos for PRs mentioning the issue key
2. **Analyzes Content**: Uses PR description/commits if meaningful, otherwise analyzes the diff
3. **Generates Comment**: Creates a formatted summary in JIRA markdown
4. **Waits for Approval**: Shows the comment and waits for your confirmation
5. **Posts to JIRA**: Adds the approved comment to the issue

### Example Output

```
h2. PR Summary

h3. Pull Requests

*[PR #3074|https://github.com/openshift/osde2e/pull/3074] - SDCICD-1723: separate Framework-Level and Test-Level Log Analysis* (open)
* Changes: +6 -2 lines across 1 file
* Separates framework-level and test-level log analysis triggers

h3. Files Modified

* pkg/e2e/e2e.go - Log analysis separation logic

---
_Generated: 2026-01-10_
```

---

## Project Structure

```
jira-agent/
├── .claude/
│   ├── commands/
│   │   ├── jira-report.md        # Progress report command
│   │   └── jira-pr-comment.md    # PR comment command
│   └── settings.local.json       # Claude permissions
├── jira_report_email.py          # Email sending script (Gmail SMTP)
└── README.md                     # This file
```