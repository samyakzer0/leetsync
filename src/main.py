
from src.config import (
    USER_TARGET_TAGS,
    OUTPUT_DIR,
    SMTP_USER,
    SMTP_PASSWORD,
    NOTIFICATION_EMAIL,
    SMTP_SERVER,
    SMTP_PORT,
)
from src.leetcode_client import fetch_daily_question, match_focus_topics
from src.markdown_builder import build_and_save_markdown
from src.notifier import send_priority_email
from src.storage import (
    save_problem,
    start_pipeline_run,
    finish_pipeline_run,
)


def main():
    run_id = start_pipeline_run()

    try:
        print("LeetMeKnow: Starting daily problem pipeline...")

        problem = fetch_daily_question()

        if not problem:
            raise RuntimeError("No daily LeetCode problem was returned.")

        matched_tags = match_focus_topics(
            problem["all_tags"],
            set(USER_TARGET_TAGS),
        )
        problem["matched_tags"] = matched_tags

        # Persist the problem and its tag relationships.
        save_problem(problem, matched_tags)
        print(f"Saved problem #{problem['question_id']} to PostgreSQL.")

        # Preserve the existing Markdown output.
        build_and_save_markdown(problem, OUTPUT_DIR)

        # Notify only when focus topics match.
        if matched_tags:
            send_priority_email(
                problem=problem,
                matched_tags=matched_tags,
                smtp_user=SMTP_USER,
                smtp_password=SMTP_PASSWORD,
                recipient=NOTIFICATION_EMAIL,
                smtp_server=SMTP_SERVER,
                smtp_port=SMTP_PORT,
            )
        else:
            print("No focus-topic match; email skipped.")

        finish_pipeline_run(
            run_id,
            status="success",
            records_processed=1,
        )
        print(f"Pipeline run {run_id} completed successfully.")

    except Exception as exc:
        try:
            finish_pipeline_run(
                run_id,
                status="failure",
                error_message=str(exc)[:4000],
            )
        except Exception as tracking_error:
            print(f"Could not record pipeline failure: {tracking_error}")

        raise


if __name__ == "__main__":
    main()
