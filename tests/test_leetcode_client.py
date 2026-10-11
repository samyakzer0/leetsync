import unittest
from src.leetcode_client import match_focus_topics


class MatchFocusTopicsTests(unittest.TestCase):
    def test_matches_case_insensitively_and_preserves_configured_label(self):
        self.assertEqual(
            match_focus_topics(
                ["array", "BINARY SEARCH", "Hash Table"],
                {"Array", "Binary Search"},
            ),
            ["Array", "Binary Search"],
        )

    def test_no_match_returns_empty_list(self):
        self.assertEqual(
            match_focus_topics(["Tree", "Graph"], {"Array", "Greedy"}), []
        )

    def test_empty_tags_return_no_matches(self):
        self.assertEqual(match_focus_topics([], {"Array"}), [])


if __name__ == "__main__":
    unittest.main()
