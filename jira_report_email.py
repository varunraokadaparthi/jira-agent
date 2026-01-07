#!/usr/bin/env python3
"""
JIRA Report Email Sender

Sends HTML-formatted JIRA reports via email to configured recipients.
"""

import argparse
import os
import re
import smtplib
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path


def validate_environment():
    """Validate that all required environment variables are set."""
    required_vars = [
        "SMTP_PASSWORD",
        "SMTP_PORT",
        "SMTP_REQUIRE_TLS",
        "SMTP_SERVER",
        "SMTP_USERNAME",
        "SMTP_FROM",
    ]

    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        print("Error: Missing required environment variables:", file=sys.stderr)
        for var in missing_vars:
            print(f"  - {var}", file=sys.stderr)
        print("\nRequired environment variables:", file=sys.stderr)
        print("  SMTP_SERVER    - SMTP server hostname", file=sys.stderr)
        print("  SMTP_PORT      - SMTP server port", file=sys.stderr)
        print("  SMTP_USERNAME  - SMTP authentication username", file=sys.stderr)
        print("  SMTP_PASSWORD  - SMTP authentication password", file=sys.stderr)
        print("  SMTP_FROM      - Email sender address", file=sys.stderr)
        print("  SMTP_REQUIRE_TLS - Use STARTTLS (true/false)", file=sys.stderr)
        sys.exit(1)


def extract_date_from_filename(filename):
    """
    Extract date from filename in format YYYY-MM-DD.
    Falls back to current date if not found.
    """
    match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if match:
        return match.group(1)
    return datetime.now().strftime('%Y-%m-%d')


def format_date_for_subject(date_str):
    """Format date string for email subject (e.g., 'Jan 06, 2026')."""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%b %d, %Y')
    except ValueError:
        return date_str


def read_html_file(html_file):
    """Read HTML content from file."""
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: HTML file not found: {html_file}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading HTML file: {e}", file=sys.stderr)
        sys.exit(1)


def send_report_email(html_file, report_date, recipients_list):
    """Send the JIRA report email."""
    # Email configuration from environment
    smtp_server = os.environ['SMTP_SERVER']
    smtp_port = int(os.environ['SMTP_PORT'])
    smtp_username = os.environ['SMTP_USERNAME']
    smtp_password = os.environ['SMTP_PASSWORD']
    smtp_from = os.environ['SMTP_FROM']
    smtp_require_tls = os.environ['SMTP_REQUIRE_TLS'].lower() in ('true', '1', 'yes')

    # Format date for subject
    formatted_date = format_date_for_subject(report_date)

    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'JIRA Progress Report - {formatted_date}'
    msg['From'] = smtp_from
    msg['To'] = ', '.join(recipients_list)

    # Read HTML content
    html_content = read_html_file(html_file)

    # Attach HTML content
    html_part = MIMEText(html_content, 'html')
    msg.attach(html_part)

    # Send email
    try:
        print(f"Connecting to SMTP server: {smtp_server}:{smtp_port}")

        if smtp_require_tls:
            # Use STARTTLS
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
        else:
            # Direct SSL/TLS connection
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(smtp_username, smtp_password)
                server.send_message(msg)

        print(f"Successfully sent email to: {', '.join(recipients_list)}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("Error: SMTP authentication failed. Check username and password.", file=sys.stderr)
        return False
    except smtplib.SMTPException as e:
        print(f"Error: SMTP error occurred: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error: Failed to send email: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Send HTML-formatted JIRA reports via email",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment variables required:
  SMTP_SERVER       SMTP server hostname
  SMTP_PORT         SMTP server port
  SMTP_USERNAME     SMTP authentication username
  SMTP_PASSWORD     SMTP authentication password
  SMTP_FROM         Email sender address
  SMTP_REQUIRE_TLS  Use STARTTLS (true/false)

Examples:
  %(prog)s jira-report-2026-01-06.html
  %(prog)s --date 2026-01-10 --recipients user1@example.com,user2@example.com report.html
        """,
    )
    parser.add_argument(
        "html_file",
        help="Path to HTML file to send",
    )
    parser.add_argument(
        "--date",
        help="Report date (YYYY-MM-DD). If not specified, extracted from filename or uses current date.",
    )
    parser.add_argument(
        "--recipients",
        help="Comma-separated list of email recipients. If not specified, uses SMTP_RECIPIENTS env var.",
    )

    args = parser.parse_args()

    # Validate environment variables
    validate_environment()

    # Verify HTML file exists
    if not Path(args.html_file).is_file():
        print(f"Error: HTML file not found: {args.html_file}", file=sys.stderr)
        sys.exit(1)

    # Determine report date
    if args.date:
        report_date = args.date
        # Validate date format
        try:
            datetime.strptime(report_date, '%Y-%m-%d')
        except ValueError:
            print(f"Error: Invalid date format: {report_date}", file=sys.stderr)
            print("Expected format: YYYY-MM-DD", file=sys.stderr)
            sys.exit(1)
    else:
        report_date = extract_date_from_filename(args.html_file)

    # Determine recipients
    if args.recipients:
        recipients = [email.strip() for email in args.recipients.split(',')]
    else:
        recipients_env = os.environ.get('SMTP_RECIPIENTS')
        if not recipients_env:
            print("Error: No recipients specified. Use --recipients or set SMTP_RECIPIENTS env var.", file=sys.stderr)
            sys.exit(1)
        recipients = [email.strip() for email in recipients_env.split(',')]

    print(f"Sending report for date: {report_date}")
    print(f"Recipients: {', '.join(recipients)}")

    # Send email
    success = send_report_email(args.html_file, report_date, recipients)

    if success:
        print("Email sent successfully!")
        sys.exit(0)
    else:
        print("Failed to send email.", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
