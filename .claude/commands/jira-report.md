---
description: Generate a natural language progress report from JIRA data for a project and time period
argument-hint: [PROJECT] [TIME_PERIOD]
allowed-tools: Bash(jira *:*)
---

Generate a comprehensive progress report from JIRA for the specified project and time period.

## Parse the Request

Extract project key from `$1` (required) and time period from remaining arguments `$2 $3 $4...`

**Defaults:**
- If no time period specified → use current active sprint
- If no active sprint found → use last 14 days

**Examples of $ARGUMENTS:**
- `SDCICD` → Current active sprint
- `SDCICD current sprint` → Current active sprint
- `SDCICD Dec 1 to Dec 31` → Date range
- `SDCICD Q4 2024` → Quarter

## Collect JIRA Data

Use JIRA CLI with `--raw` flag for JSON output.

**Get sprint context:**
```bash
jira sprint list -p $1 --state active --raw
```

**Query issues:**
```bash
# Created in period
jira issue list -p $1 --created-after YYYY-MM-DD --created-before YYYY-MM-DD --raw

# Resolved in period
jira issue list -p $1 -q "project=$1 AND resolved >= 'YYYY-MM-DD' AND resolved <= 'YYYY-MM-DD'" --raw

# In-progress work
jira issue list -p $1 -q "project=$1 AND status IN ('In Progress', 'Review') AND updated >= 'YYYY-MM-DD'" --raw
```

## Analyze & Categorize

**Group by type:**
- Stories/Tasks → Feature Delivery
- Bugs → Quality Improvements
- Infrastructure → Platform work
- Documentation → Operational Tasks

**Calculate:**
- Completion rate (resolved vs created)
- Issue counts by status
- Work distribution percentages
- Patterns and trends

## Generate Report (HTML)

**Output Format:** Generate HTML output suitable for email

**File:** Save output to `output/jira-report-YYYY-MM-DD.html`

**HTML Structure:**

Use clean, simple HTML with inline CSS for email compatibility:
- Use Arial font for all text
- Include proper heading hierarchy (h1 for title, h2 for sections, h3 for subsections)
- Make JIRA issue links clickable with `<a href="">` tags
- Use professional color palette with blues (#2c5aa0, #5b9bd5, #e8f0f8)
- Use subtle styling (light backgrounds for sections, proper spacing)
- Executive Summary section should be in a highlighted blue box at the top

**Content Structure:**

```
Title: [PROJECT] Progress Report
Period: [TIME_PERIOD]

Executive Summary Section (highlighted box):
- 2-3 sentence overview with completion % and key highlights
- Use light blue background (#e8f0f8) with left border accent (#2c5aa0)

Section 1: Key Achievements
- Group by category (Feature Delivery, Quality Improvements, Platform Work, etc.)
- List specific achievements with metrics and clickable JIRA links
- Format: "Achievement description (ISSUE-123)"

Section 2: Metrics
Delivery Performance:
- Issues Resolved: X completed
- Issues Created: Y new
- Active Development: Z in progress

Work Distribution:
- Category 1: N% (X issues)
- Category 2: N% (Y issues)

Section 3: Insights & Trends
- Analysis paragraph about patterns, velocity, focus areas
- Highlight trends and observations

Footer:
- Report Generated: [Date]
```

**HTML Template Example:**
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
        h1 { color: #2c5aa0; border-bottom: 3px solid #2c5aa0; padding-bottom: 10px; }
        h2 { color: #2c5aa0; margin-top: 30px; border-bottom: 2px solid #5b9bd5; padding-bottom: 5px; }
        h3 { color: #5b9bd5; margin-top: 20px; }
        .summary { background-color: #e8f0f8; border-left: 4px solid #2c5aa0; padding: 15px; margin: 20px 0; }
        .metrics { background-color: #f5f5f5; padding: 15px; margin: 20px 0; border-radius: 5px; }
        ul { list-style-type: none; padding-left: 0; }
        li { margin: 8px 0; padding-left: 20px; position: relative; }
        li:before { content: "▸"; position: absolute; left: 0; color: #2c5aa0; }
        a { color: #2c5aa0; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #ccc; color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <!-- Content goes here -->
</body>
</html>
```

**Writing Guidelines:**
- Use specific metrics ("45% improvement" not "significant")
- Include clickable JIRA issue links (e.g., `<a href="https://jira.example.com/browse/PROJ-123">PROJ-123</a>`)
- Keep executive summary under 3 sentences
- Positive framing with honest assessment
- Highlight completed AND in-progress work
- Ensure all CSS is inline for maximum email client compatibility

## Error Handling

- **Invalid project**: List available projects with `jira project list`
- **No sprint**: Fall back to 14 days, inform user
- **Empty results**: Explain criteria, suggest alternatives
- **Auth issues**: Suggest `jira init`
