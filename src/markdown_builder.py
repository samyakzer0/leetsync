import os
import re
import html
from typing import Dict, Any, List

def clean_html_to_markdown(raw_html: str) -> str:
    """Converts LeetCode HTML problem descriptions into clean, readable text."""
    if not raw_html:
        return "No description provided."

    text = html.unescape(raw_html)
    text = re.sub(r'</?(strong|b)>', '**', text)
    text = re.sub(r'</?(em|i)>', '*', text)
    text = re.sub(r'</?code>', '`', text)
    text = re.sub(r'<pre>', '\n```\n', text)
    text = re.sub(r'</pre>', '\n```\n', text)
    text = re.sub(r'<li>', '- ', text)
    text = re.sub(r'</li>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    return text.strip()


def build_and_save_markdown(
    problem: Dict[str, Any],
    matched_tags: List[str],
    output_dir: str = "daily_challenges"
) -> str:
    """
    Constructs a formatted markdown file for the daily challenge and saves it locally.
    
    Returns:
        Absolute or relative path to the created markdown file.
    """
    os.makedirs(output_dir, exist_ok=True)

    date_str = problem["date"]
    slug = problem["slug"]
    q_id = problem["question_id"]
    title = problem["title"]
    diff = problem["difficulty"]
    link = problem["link"]
    all_tags_str = ", ".join(problem["all_tags"])

    focus_badge = ""
    if matched_tags:
        matched_str = ", ".join(matched_tags)
        focus_badge = f"> 🎯 **Focus Match:** `{matched_str}` — *Target topic for your daily practice!*\n\n"

    cleaned_description = clean_html_to_markdown(problem.get("content_html", ""))

    content = f"""# [{q_id}. {title}]({link})

{focus_badge}**Date:** {date_str}  
**Difficulty:** {diff}  
**Tags:** `{all_tags_str}`

---

## Problem Description

{cleaned_description}

---

## My Notes & Solution
```cpp
// Write your C++ solution here
```
"""

    file_path = os.path.join(output_dir, f"{date_str}_{slug}.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"📝 Saved daily challenge markdown to: {file_path}")
    return file_path
