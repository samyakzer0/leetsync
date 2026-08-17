import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

USER_TARGET_TAGS = {
    "Dynamic Programming",
    "Graph",
    "Two Pointers",
    "Binary Search",
    "Sliding Window",
    "Array",
}

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "daily_challenges")

SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "").replace(" ", "")
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
