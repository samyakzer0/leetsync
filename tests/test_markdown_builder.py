import tempfile
import unittest
from pathlib import Path
from src.markdown_builder import build_and_save_markdown


class MarkdownBuilderTests(unittest.TestCase):
    def setUp(self):
        self.problem = {
            "date": "2026-10-11",
            "link": "https://leetcode.com/problems/example/",
            "question_id": "2778",
            "title": "Example Problem",
            "slug": "example-problem",
            "difficulty": "Easy",
            "all_tags": ["Array", "Enumeration"],
            "matched_tags": ["Array"],
            "content_html": "<p>Return <strong>true</strong> for this example.</p>",
        }

    def test_builds_markdown_file_with_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(build_and_save_markdown(self.problem, tmp))
            self.assertTrue(path.is_file())
            self.assertEqual(path.name, "2026-10-11_example-problem.md")
            content = path.read_text(encoding="utf-8")
            self.assertIn("Example Problem", content)
            self.assertIn("Easy", content)
            self.assertIn("Array", content)
            self.assertIn("Return", content)

    def test_no_focus_badge_when_no_topics_match(self):
     with tempfile.TemporaryDirectory() as tmp:
        path = Path(
            build_and_save_markdown(self.problem, [], tmp)
        )
        content = path.read_text(encoding="utf-8")
        self.assertNotIn("Focus Match", content)


if __name__ == "__main__":
    unittest.main()
