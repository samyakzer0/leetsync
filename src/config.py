import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Predefined focus/target practice topics
USER_TARGET_TAGS = {
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

# Output directory for daily markdown archives
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "daily_challenges")

# Email (SMTP) Configuration
SMTP_USER = os.getenv("SMTP_USER", "space.message.app@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "ghqlmfyehdisvthp").replace(" ", "")
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL", "theweb3book@gmail.com")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

# Discord Webhook Configuration (Optional)
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
