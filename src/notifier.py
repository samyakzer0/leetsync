import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List

def send_priority_email(
    problem: Dict[str, Any],
    matched_tags: List[str],
    smtp_user: str,
    smtp_password: str,
    recipient: str,
    smtp_server: str = "smtp.gmail.com",
    smtp_port: int = 587
) -> bool:
    """Dispatches a styled HTML priority email alert."""
    if not smtp_user or not smtp_password or not recipient:
        print("⚠️ SMTP credentials not provided. Skipping real email dispatch.")
        return False

    q_id = problem["question_id"]
    title = problem["title"]
    diff = problem["difficulty"]
    link = problem["link"]
    date_str = problem["date"]
    matched_str = ", ".join(matched_tags)

    subject = f"🎯 [Priority Match] Today's LeetCode Question is Meant For You! (#{q_id}. {title})"

    text_body = f"""Hey Sam! 🎯

Today's LeetCode Daily Challenge matches your focus practice topics!

• Problem: #{q_id} - {title} ({diff})
• Matched Topics: {matched_str}
• Link: {link}

Keep your streak going and solve it today!
"""

    diff_color = "#27ae60" if diff == "Easy" else "#f39c12" if diff == "Medium" else "#e74c3c"

    html_body = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; border: 1px solid #e1e4e8; border-radius: 8px; background-color: #ffffff;">
        <h2 style="color: #24292e; margin-top: 0;">🎯 Today's Daily Challenge is Meant For You!</h2>
        <p style="font-size: 15px; color: #586069;">Hey Sam, today's LeetCode POTD matches your target practice topics:</p>
        
        <div style="background-color: #f6f8fa; padding: 16px; border-left: 4px solid #0366d6; border-radius: 4px; margin: 16px 0;">
            <h3 style="margin: 0 0 8px 0; color: #24292e;">#{q_id}. {title}</h3>
            <p style="margin: 4px 0;"><strong>Difficulty:</strong> <span style="color: {diff_color}; font-weight: 600;">{diff}</span></p>
            <p style="margin: 4px 0;"><strong>Matched Focus Topics:</strong> <code style="background: #e1ecf4; color: #0366d6; padding: 3px 6px; border-radius: 3px; font-weight: 600;">{matched_str}</code></p>
            <p style="margin: 4px 0;"><strong>Date:</strong> {date_str}</p>
        </div>

        <div style="margin-top: 24px;">
            <a href="{link}" style="background-color: #f08c00; color: #ffffff; padding: 12px 20px; text-decoration: none; border-radius: 6px; font-weight: 600; display: inline-block;">Solve on LeetCode →</a>
        </div>

        <hr style="border: none; border-top: 1px solid #eaecef; margin-top: 28px;" />
        <p style="font-size: 12px; color: #6a737d;">Automated notification sent by LeetPulse Daily Bot</p>
    </div>
    """

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"LeetCode Daily Alert <{smtp_user}>"
        msg["To"] = recipient
        msg["Subject"] = subject

        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        print(f"Connecting to SMTP server {smtp_server}:{smtp_port}...")
        with smtplib.SMTP(smtp_server, smtp_port, timeout=20) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        print(f"✅ Real email successfully sent to {recipient}!")
        return True
    except Exception as e:
        print(f"❌ Failed to dispatch email: {e}")
        return False


def send_discord_webhook(
    problem: Dict[str, Any],
    matched_tags: List[str],
    webhook_url: str
) -> bool:
    """Dispatches a rich embed card to a Discord webhook."""
    if not webhook_url:
        return False

    q_id = problem["question_id"]
    title = problem["title"]
    diff = problem["difficulty"]
    link = problem["link"]
    matched_str = ", ".join(matched_tags) if matched_tags else "General Daily"

    color_map = {"Easy": 0x00B8A3, "Medium": 0xFFC01E, "Hard": 0xFF375F}
    embed_color = color_map.get(diff, 0x3498DB)

    payload = {
        "content": "🎯 **LeetCode Daily Challenge Alert:** Problem matches focus topics!" if matched_tags else "📚 **LeetCode Daily Challenge Available**",
        "embeds": [
            {
                "title": f"#{q_id} - {title} ({diff})",
                "url": link,
                "color": embed_color,
                "fields": [
                    {"name": "🎯 Focus Topics", "value": matched_str, "inline": False},
                    {"name": "Difficulty", "value": diff, "inline": True},
                    {"name": "Date", "value": problem["date"], "inline": True}
                ],
                "footer": {"text": "LeetPulse Automation Bot"}
            }
        ]
    }

    try:
        res = requests.post(webhook_url, json=payload, timeout=10)
        if res.status_code in [200, 204]:
            print("✅ Discord alert posted successfully!")
            return True
    except Exception as e:
        print(f"⚠️ Discord webhook failed: {e}")
    return False
