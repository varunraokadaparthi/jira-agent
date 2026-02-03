---
description: Add PR summary comment to a JIRA issue
argument-hint: [ISSUE_KEY]
allowed-tools: Bash(jira *:*), Bash(gh *:*)
---

Add a summary comment to a JIRA issue describing the work done in associated pull requests.

## Step 1: Find PRs

Search for PRs that mention the issue key across all accessible GitHub repositories:

```bash
# Search across ALL repos for PRs mentioning the issue key
gh search prs "$ISSUE_KEY" --json repository,number,title,url,state
```

This finds PRs where the issue key appears in the title, body, or branch name - regardless of which repository they're in.

## Step 2: Generate Comment

For each PR found, get details using the repo from search results:

```bash
# Get PR details (OWNER/REPO from search results' repository.nameWithOwner)
gh pr view PR_NUMBER --repo OWNER/REPO --json title,body,state,mergedAt,additions,deletions,files,commits
```

**Use PR description and commit messages if they're meaningful.** If the description is empty or generic (e.g., "WIP", "fix", "update"), analyze the PR diff instead:

```bash
gh pr diff PR_NUMBER --repo OWNER/REPO
```

Generate a JIRA comment summarizing:
- PR title and link
- Status (merged/open/closed)
- Key changes made
- Files modified

**Comment Format (JIRA markdown):**

```
h2. PR Summary

h3. Pull Requests

*[PR #123|https://github.com/org/repo/pull/123] - Feature title* (merged)
* Changes: +150 -30 lines across 5 files
* Summary of what was done

h3. Key Changes

* Change 1
* Change 2
* Change 3

h3. Files Modified

* path/to/file.py - Description
* path/to/other.js - Description

---
_Generated: YYYY-MM-DD_
```

## Step 3: Review and Post

Display the generated comment and ask for approval:

```
Here's the comment I'll add to {ISSUE_KEY}:

[generated comment]

Post this comment? (yes/no)
```

**Wait for user approval.** Do not post until confirmed.

Once approved, use heredoc to handle multi-line comments:

```bash
cat <<'EOF' | jira issue comment add $ISSUE_KEY
$COMMENT_TEXT
EOF
```

## Error Handling

- **Issue not found**: Verify issue key is correct
- **No PRs found**: Check if PRs are linked in the issue or mention the issue key
- **GitHub auth error**: Run `gh auth login`
- **JIRA auth error**: Run `jira init`
