import os
import requests
import html
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
# pyrefly: ignore [missing-import]
from airflow.decorators import dag, task

# User focus topics
USER_TARGET = {
    "Dynamic Programming",
    "Graph",
    "Two Pointers",
    "Binary Search",
    "Sliding Window",
    "Array",
    "Greedy",
    "Tree",
    "Backtracking",
}

# Airflow default DAG arguments
default_args = {
    'owner': 'samyak',
    'retries': 5,
    'retry_delay': timedelta(minutes=5),
}

# Environment Variables & Credentials (reads from environment)
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "").replace(" ", "")
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")


def send_real_email(recipient: str, subject: str, html_content: str, text_content: str) -> bool:
    """Dispatches a real email via Gmail SMTP."""
    print(f"Connecting to SMTP server {SMTP_SERVER}:{SMTP_PORT}...")
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"LeetCode Daily Alert <{SMTP_USER}>"
        msg["To"] = recipient
        msg["Subject"] = subject

        msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=20) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        print(f"✅ Real email successfully sent to {recipient}!")
        return True
    except Exception as e:
        print(f"❌ Failed to dispatch SMTP email: {e}")
        return False


def save_markdown_archive(problem: dict, matched_tags: list) -> str:
    """Creates formatted problem markdown archive in daily_challenges/."""
    save_dir = "/mnt/d/DEGIT/leetcode-pulse/daily_challenges" if os.path.exists("/mnt/d/DEGIT/leetcode-pulse") else "daily_challenges"
    os.makedirs(save_dir, exist_ok=True)

    date_str = problem['date']
    slug = problem['slug']
    q_id = problem['question_id']
    title = problem['title']
    diff = problem['difficulty']
    link = problem['link']
    tags_str = ", ".join(problem['all_tags'])

    focus_badge = ""
    if matched_tags:
        matched_str = ", ".join(matched_tags)
        focus_badge = f"> 🎯 **Focus Match:** `{matched_str}` — *Target topic for your daily practice!*\n\n"

    raw_html = problem.get("content_html", "")
    clean_desc = html.unescape(raw_html)
    import re
    clean_desc = re.sub(r'<[^>]+>', '', clean_desc)
    clean_desc = re.sub(r'\n\s*\n\s*\n', '\n\n', clean_desc).strip()

    md_content = f"""# [{q_id}. {title}]({link})

{focus_badge}**Date:** {date_str}  
**Difficulty:** {diff}  
**Tags:** `{tags_str}`

---

## Problem Description

{clean_desc}

---

## My Notes & Solution
```cpp
// Write your C++ solution here
```
"""
    file_path = os.path.join(save_dir, f"{date_str}_{slug}.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"📝 Markdown saved to: {file_path}")
    return file_path


@dag(
    dag_id='notify_leetcode',
    default_args=default_args,
    description='Automated LeetCode daily problem tracker with smart focus-topic alerting',
    schedule='@daily',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['leetcode', 'notification', 'daily-tracker']
)
def notify_leetcode():

    @task()
    def fetch_leetcode_problems() -> dict | None:
        url = "https://leetcode.com/graphql"
        query = """query questionOfToday {
            activeDailyCodingChallengeQuestion {
                date
                link
                question {
                    questionFrontendId
                    title
                    titleSlug
                    difficulty
                    topicTags {
                        name
                    }
                    content
                }
            }
        }"""

        print(f"Fetching daily challenge from {url}...")
        response = requests.post(url, json={'query': query}, timeout=15)
        response.raise_for_status()
        payload = response.json()
        daily_question = payload.get('data', {}).get('activeDailyCodingChallengeQuestion')

        if not daily_question or not daily_question.get('question'):
            print("No active daily coding challenge found.")
            return None

        question = daily_question['question']
        raw_tags = [tag['name'] for tag in question.get('topicTags', [])]

        # Case-insensitive topic matching
        target_lookup = {t.lower(): t for t in USER_TARGET}
        matched_tags = [target_lookup[t.lower()] for t in raw_tags if t.lower() in target_lookup]

        result = {
            'date': daily_question['date'],
            'link': f"https://leetcode.com{daily_question['link']}",
            'question_id': question['questionFrontendId'],
            'title': question['title'],
            'slug': question['titleSlug'],
            'difficulty': question['difficulty'],
            'all_tags': raw_tags,
            'matched_tags': matched_tags,
            'is_target_match': len(matched_tags) > 0,
            'content_html': question.get('content', '')
        }

        print(f"✅ Fetched problem: #{result['question_id']} - {result['title']} ({result['difficulty']})")
        print(f"Target Matched: {result['is_target_match']} -> {matched_tags}")
        return result

    @task.branch()
    def notify_user(problem: dict | None) -> str:
        """Evaluates topic match and branches accordingly."""
        if not problem:
            return "no_notification"

        # Archive Markdown file for both branches
        save_markdown_archive(problem, problem.get('matched_tags', []))

        if problem.get('is_target_match'):
            print(f"🎯 Target match found! Routing to 'notification_sent' for: {problem['title']}")
            return "notification_sent"
        else:
            print("ℹ️ No target match. Routing to 'no_notification'.")
            return "no_notification"

    @task()
    def notification_sent(problem: dict):
        q_id = problem['question_id']
        title = problem['title']
        diff = problem['difficulty']
        link = problem['link']
        date_str = problem['date']
        matched = ", ".join(problem['matched_tags'])

        recipient = NOTIFICATION_EMAIL
        subject = f"🎯 [Priority Match] Today's LeetCode Question is Meant For You! (#{q_id}. {title})"

        text_body = f"""Hey Sam! 🎯

Today's LeetCode Daily Challenge matches your focus practice topics!

• Problem: #{q_id} - {title} ({diff})
• Matched Topics: {matched}
• Link: {link}

Keep your streak going and solve it today!
"""

        diff_color = "#27ae60" if diff == "Easy" else "#f39c12" if diff == "Medium" else "#e74c3c"

        html_body = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; border: 1px solid #e1e4e8; border-radius: 8px; background-color: #ffffff;">
            <h2 style="color: #24292e; margin-top: 0;">🎯 Today's Daily Challenge is Meant For You!</h2>
            <p style="font-size: 15px; color: #586069;">Hey Sam, today's LeetCode POTD matches your target topics:</p>
            
            <div style="background-color: #f6f8fa; padding: 16px; border-left: 4px solid #0366d6; border-radius: 4px; margin: 16px 0;">
                <h3 style="margin: 0 0 8px 0; color: #24292e;">#{q_id}. {title}</h3>
                <p style="margin: 4px 0;"><strong>Difficulty:</strong> <span style="color: {diff_color}; font-weight: 600;">{diff}</span></p>
                <p style="margin: 4px 0;"><strong>Matched Focus Topics:</strong> <code style="background: #e1ecf4; color: #0366d6; padding: 3px 6px; border-radius: 3px; font-weight: 600;">{matched}</code></p>
                <p style="margin: 4px 0;"><strong>Date:</strong> {date_str}</p>
            </div>

            <div style="margin-top: 24px;">
                <a href="{link}" style="background-color: #f08c00; color: #ffffff; padding: 12px 20px; text-decoration: none; border-radius: 6px; font-weight: 600; display: inline-block;">Solve on LeetCode →</a>
            </div>

            <hr style="border: none; border-top: 1px solid #eaecef; margin-top: 28px;" />
            <p style="font-size: 12px; color: #6a737d;">Automated alert sent by Apache Airflow (DAG: <code>notify_leetcode</code>)</p>
        </div>
        """

        send_real_email(recipient, subject, html_body, text_body)
        print(f"Notification task completed for #{q_id} - {title}.")

    @task()
    def no_notification():
        print("Daily challenge does not match target topics. Markdown saved; email skipped.")

    # Wiring
    problem = fetch_leetcode_problems()
    branch = notify_user(problem)

    send_notification = notification_sent(problem)
    no_notification_task = no_notification()

    branch >> [send_notification, no_notification_task]


# Instantiate DAG
notify_leetcode()
