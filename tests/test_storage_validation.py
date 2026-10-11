import unittest
from unittest.mock import patch
from src import storage


class StorageValidationTests(unittest.TestCase):
    def test_rejects_match_not_in_problem_tags_before_database_write(self):
        problem = {
            "date": "2026-10-11",
            "question_id": "2778",
            "title": "Example",
            "slug": "example",
            "link": "https://leetcode.com/problems/example/",
            "difficulty": "Easy",
            "all_tags": ["Array"],
            "content_html": "<p>Example</p>",
        }
        with patch.object(storage, "engine") as engine:
            with self.assertRaises(ValueError):
                storage.save_problem(problem, ["Graph"])
            engine.begin.assert_not_called()


if __name__ == "__main__":
    unittest.main()
