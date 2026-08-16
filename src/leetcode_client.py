import requests
from datetime import datetime
from typing import Optional, Dict, Any

LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"

DAILY_QUESTION_QUERY = """
query questionOfToday {
    activeDailyCodingChallengeQuestion {
        date
        link
        userStatus
        question {
            questionId
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
}
"""

def fetch_daily_question(timeout: int = 15) -> Optional[Dict[str, Any]]:
    """
    Fetches the active daily coding challenge from LeetCode GraphQL API.
    
    Returns:
        Dictionary containing extracted metadata and problem details, or None if unavailable.
    """
    print(f"Connecting to LeetCode API: {LEETCODE_GRAPHQL_URL}...")
    response = requests.post(
        LEETCODE_GRAPHQL_URL,
        json={"query": DAILY_QUESTION_QUERY},
        timeout=timeout,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "LeetPulse-Bot/1.0"
        }
    )
    response.raise_for_status()

    data = response.json()
    daily_challenge = data.get("data", {}).get("activeDailyCodingChallengeQuestion")

    if not daily_challenge or not daily_challenge.get("question"):
        print("⚠️ No active daily coding challenge found in response.")
        return None

    question = daily_challenge["question"]
    raw_tags = [tag["name"] for tag in question.get("topicTags", [])]

    result = {
        "date": daily_challenge.get("date", datetime.now().strftime("%Y-%m-%d")),
        "link": f"https://leetcode.com{daily_challenge.get('link', '')}",
        "question_id": question.get("questionFrontendId"),
        "title": question.get("title"),
        "slug": question.get("titleSlug"),
        "difficulty": question.get("difficulty"),
        "all_tags": raw_tags,
        "content_html": question.get("content", ""),
    }

    print(f"✅ Successfully fetched: #{result['question_id']} - {result['title']} ({result['difficulty']})")
    print(f"Tags: {', '.join(raw_tags)}")
    return result


def match_focus_topics(all_tags: list[str], target_tags: set[str]) -> list[str]:
    """
    Compares the problem tags against the user's focus topics (case-insensitive).
    """
    target_lookup = {t.lower(): t for t in target_tags}
    matched = [target_lookup[t.lower()] for t in all_tags if t.lower() in target_lookup]
    return matched
