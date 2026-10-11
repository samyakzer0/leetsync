
import os
import re
import html
from html.parser import HTMLParser
from typing import Dict, Any, List


class DescriptionParser(HTMLParser):
    """Convert LeetCode problem-description HTML into readable Markdown."""

    BLOCK_TAGS = {
        "p", "div", "section", "article", "ul", "ol",
        "li", "h1", "h2", "h3", "h4", "blockquote"
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.pre_depth = 0
        self.skip_depth = 0
        self.skip_tags = {"script", "style"}

    def handle_starttag(self, tag, attrs):
        if tag in self.skip_tags:
            self.skip_depth += 1
            return

        if self.skip_depth:
            return

        if tag == "pre":
            self.pre_depth += 1
            if self.pre_depth == 1:
                self.parts.append("\n\n```\n")
        elif tag in {"strong", "b"}:
            self.parts.append("**")
        elif tag in {"em", "i"}:
            self.parts.append("*")
        elif tag == "code":
            self.parts.append("`")
        elif tag == "br":
            self.parts.append("\n")
        elif tag == "li":
            self.parts.append("\n- ")
        elif tag in self.BLOCK_TAGS:
            self.parts.append("\n\n")

    def handle_endtag(self, tag):
        if tag in self.skip_tags:
            self.skip_depth = max(0, self.skip_depth - 1)
            return

        if self.skip_depth:
            return

        if tag == "pre":
            if self.pre_depth:
                self.pre_depth -= 1
                if self.pre_depth == 0:
                    self.parts.append("\n```\n\n")
        elif tag in {"strong", "b"}:
            self.parts.append("**")
        elif tag in {"em", "i"}:
            self.parts.append("*")
        elif tag == "code":
            self.parts.append("`")
        elif tag in self.BLOCK_TAGS:
            self.parts.append("\n\n")

    def handle_data(self, data):
        if self.skip_depth:
            return

        if self.pre_depth:
            self.parts.append(data)
        else:
            self.parts.append(data)

    def get_markdown(self):
        text = "".join(self.parts)
        text = html.unescape(text)
        text = re.sub(r"[ \t]+\n", "\n", text)
        text = re.sub(r"\n[ \t]*\n(?:[ \t]*\n)+", "\n\n", text)
        return text.strip()



def clean_html_to_markdown(raw_html: str) -> str:
    """Convert LeetCode HTML descriptions into readable Markdown."""
    if not raw_html:
        return "No description provided."

    from html.parser import HTMLParser
    from html import unescape

    class Parser(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.parts = []
            self.in_pre = False
            self.skip = 0

        def handle_starttag(self, tag, attrs):
            if tag in {"script", "style"}:
                self.skip += 1
                return
            if self.skip:
                return

            if tag == "pre":
                self.in_pre = True
                self.parts.append("\n\n")
            elif tag in {"p", "ul", "ol"}:
                self.parts.append("\n\n")
            elif tag == "li":
                self.parts.append("\n- ")
            elif tag in {"strong", "b"}:
                classes = dict(attrs).get("class", "")
                if "example" in classes:
                    self.parts.append("\n\n**")
                else:
                    self.parts.append("**")
            elif tag in {"em", "i"}:
                self.parts.append("*")
            elif tag == "code":
                self.parts.append("`")
            elif tag == "br":
                self.parts.append("\n")

        def handle_endtag(self, tag):
            if tag in {"script", "style"}:
                self.skip = max(0, self.skip - 1)
                return
            if self.skip:
                return

            if tag == "pre":
                self.in_pre = False
                self.parts.append("\n\n")
            elif tag in {"p", "ul", "ol", "li"}:
                self.parts.append("\n")
            elif tag in {"strong", "b"}:
                self.parts.append("**")
            elif tag in {"em", "i"}:
                self.parts.append("*")
            elif tag == "code":
                self.parts.append("`")

        def handle_data(self, data):
            if not self.skip:
                self.parts.append(data)

    parser = Parser()
    parser.feed(unescape(raw_html))
    parser.close()

    text = "".join(parser.parts)
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n[ \t]*\n(?:[ \t]*\n)+", "\n\n", text)

    # Repair malformed emphasis tags in the source HTML.
    text = text.replace("*nums`", "nums`")
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()



def build_and_save_markdown(
    problem: Dict[str, Any],
    matched_tags: List[str],
    output_dir: str = "daily_challenges",
) -> str:
    """Build and save a Markdown file for the daily challenge."""
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
        focus_badge = (
            f"> 🎯 **Focus Match:** `{matched_str}` — "
            "*Target topic for your daily practice!*\n\n"
        )

    cleaned_description = clean_html_to_markdown(
        problem.get("content_html", "")
    )

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

    with open(file_path, "w", encoding="utf-8", newline="\n") as file:
        file.write(content)

    print(f"📝 Saved daily challenge markdown to: {file_path}")
    return file_path
