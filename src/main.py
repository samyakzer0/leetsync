import sys
from src.config import (
    USER_TARGET_TAGS,
    OUTPUT_DIR,
    SMTP_USER,
    SMTP_PASSWORD,
    NOTIFICATION_EMAIL,
    SMTP_SERVER,
    SMTP_PORT,
)
from src.leetcode_client import fetch_daily_question, match_focus_topics
from src.markdown_builder import build_and_save_markdown
from src.notifier import send_priority_email

def main():
    print("🚀 LeetPulse: Starting Daily POTD Tracker...")

    problem = fetch_daily_question()
    if not problem:
        print("❌ Could not retrieve daily challenge. Exiting.")
        sys.exit(1)

    matched_tags = match_focus_topics(problem["all_tags"], USER_TARGET_TAGS)
    if matched_tags:
        print(f"Target Topic Match: {matched_tags}")
    else:
        print("No target topic match for today's challenge.")

    
    saved_path = build_and_save_markdown(problem, matched_tags, OUTPUT_DIR)
    print(f"Markdown generated at: {saved_path}")

 
    if matched_tags:
        print("📧 Dispatching priority email notification...")
        send_priority_email(
            problem=problem,
            matched_tags=matched_tags,
            smtp_user=SMTP_USER,
            smtp_password=SMTP_PASSWORD,
            recipient=NOTIFICATION_EMAIL,
            smtp_server=SMTP_SERVER,
            smtp_port=SMTP_PORT
        )

        
    else:
        print("Skipping email notification (not in focus practice list).")


if __name__ == "__main__":
    main()
