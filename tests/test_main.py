import unittest
from unittest.mock import patch
from src import main as pipeline


SAMPLE_PROBLEM = {
    "date": "2026-10-11",
    "link": "https://leetcode.com/problems/example/",
    "question_id": "2778",
    "title": "Example Problem",
    "slug": "example-problem",
    "difficulty": "Easy",
    "all_tags": ["Array"],
    "content_html": "<p>Example</p>",
}


class MainPipelineTests(unittest.TestCase):
    @patch.object(pipeline, "finish_pipeline_run")
    @patch.object(pipeline, "build_and_save_markdown")
    @patch.object(pipeline, "save_problem")
    @patch.object(pipeline, "match_focus_topics", return_value=[])
    @patch.object(pipeline, "fetch_daily_question", return_value=SAMPLE_PROBLEM)
    @patch.object(pipeline, "start_pipeline_run", return_value=42)
    def test_success_path_without_match(
        self, start_run, fetch, match, save, markdown, finish
    ):
        pipeline.main()
        start_run.assert_called_once_with()
        fetch.assert_called_once_with()
        save.assert_called_once()
        markdown.assert_called_once()
        finish.assert_called_once_with(42, status="success", records_processed=1)

    @patch.object(pipeline, "finish_pipeline_run")
    @patch.object(pipeline, "fetch_daily_question", return_value=None)
    @patch.object(pipeline, "start_pipeline_run", return_value=43)
    def test_missing_problem_records_failure_and_raises(
        self, start_run, fetch, finish
    ):
        with self.assertRaises(RuntimeError):
            pipeline.main()
        finish.assert_called_once()
        args, kwargs = finish.call_args
        self.assertEqual(args[0], 43)
        self.assertEqual(kwargs["status"], "failure")
        self.assertIn("No daily LeetCode problem", kwargs["error_message"])


if __name__ == "__main__":
    unittest.main()
