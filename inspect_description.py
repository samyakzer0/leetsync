from src.leetcode_client import fetch_daily_question

problem = fetch_daily_question()

print("TITLE:", problem["title"])
print("\nRAW DESCRIPTION HTML:\n")
print(problem.get("content_html", ""))