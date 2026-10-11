
import json
import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from sqlalchemy import bindparam, create_engine, text


DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured.")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


def save_problem(problem: dict, matched_tags: list[str]) -> None:
    """Persist one problem and synchronize its tag relationships."""

    problem_date = problem["date"]
    all_tags = list(dict.fromkeys(problem.get("all_tags", [])))
    matched_tags = list(dict.fromkeys(matched_tags))

    unknown_matches = set(matched_tags) - set(all_tags)
    if unknown_matches:
        raise ValueError(
            f"Matched tags not present in all_tags: {unknown_matches}"
        )

    with engine.begin() as conn:
        # Insert or update the canonical problem record.
        conn.execute(
            text("""
                INSERT INTO problems (
                    problem_date,
                    problem_id,
                    title,
                    slug,
                    url,
                    difficulty,
                    tags,
                    description,
                    starter_code,
                    matched
                )
                VALUES (
                    :problem_date,
                    :problem_id,
                    :title,
                    :slug,
                    :url,
                    :difficulty,
                    :tags,
                    :description,
                    CAST(:starter_code AS jsonb),
                    :matched
                )
                ON CONFLICT (problem_date) DO UPDATE SET
                    problem_id = EXCLUDED.problem_id,
                    title = EXCLUDED.title,
                    slug = EXCLUDED.slug,
                    url = EXCLUDED.url,
                    difficulty = EXCLUDED.difficulty,
                    tags = EXCLUDED.tags,
                    description = EXCLUDED.description,
                    starter_code = EXCLUDED.starter_code,
                    matched = EXCLUDED.matched
            """),
            {
                "problem_date": problem_date,
                "problem_id": str(problem["question_id"]),
                "title": problem["title"],
                "slug": problem["slug"],
                "url": problem["link"],
                "difficulty": problem["difficulty"],
                "tags": all_tags,
                "description": problem.get("content_html") or "",
                "starter_code": json.dumps(
                    problem.get("starter_code") or {}
                ),
                "matched": bool(matched_tags),
            },
        )

        # Create canonical tag records and retrieve their IDs.
        tag_ids = {}

        for tag in all_tags:
            tag_id = conn.execute(
                text("""
                    INSERT INTO tags (name)
                    VALUES (:name)
                    ON CONFLICT (name) DO UPDATE
                        SET name = EXCLUDED.name
                    RETURNING id
                """),
                {"name": tag},
            ).scalar_one()

            tag_ids[tag] = tag_id

        all_tag_ids = [tag_ids[tag] for tag in all_tags]
        matched_tag_ids = [tag_ids[tag] for tag in matched_tags]

        # Remove relationships for tags no longer present.
        for table, current_ids in (
            ("problem_tags", all_tag_ids),
            ("problem_matches", matched_tag_ids),
        ):
            delete_stmt = text(f"""
                DELETE FROM {table}
                WHERE problem_date = :problem_date
                  AND tag_id NOT IN :tag_ids
            """).bindparams(bindparam("tag_ids", expanding=True))

            conn.execute(
                delete_stmt,
                {
                    "problem_date": problem_date,
                    "tag_ids": current_ids,
                },
            )

        # Insert missing problem-to-tag relationships.
        for tag in all_tags:
            conn.execute(
                text("""
                    INSERT INTO problem_tags (problem_date, tag_id)
                    VALUES (:problem_date, :tag_id)
                    ON CONFLICT DO NOTHING
                """),
                {
                    "problem_date": problem_date,
                    "tag_id": tag_ids[tag],
                },
            )

        # Record only the tags that matched the focus list.
        for tag in matched_tags:
            conn.execute(
                text("""
                    INSERT INTO problem_matches (problem_date, tag_id)
                    VALUES (:problem_date, :tag_id)
                    ON CONFLICT DO NOTHING
                """),
                {
                    "problem_date": problem_date,
                    "tag_id": tag_ids[tag],
                },
            )


def start_pipeline_run() -> int:
    """Create a pipeline execution record and return its ID."""

    with engine.begin() as conn:
        return conn.execute(
            text("""
                INSERT INTO pipeline_runs (status)
                VALUES ('running')
                RETURNING id
            """)
        ).scalar_one()


def finish_pipeline_run(
    run_id: int,
    status: str,
    records_processed: int = 0,
    error_message: str | None = None,
) -> None:
    """Record the final status of a pipeline execution."""

    if status not in {"success", "failure"}:
        raise ValueError("status must be 'success' or 'failure'")

    with engine.begin() as conn:
        result = conn.execute(
            text("""
                UPDATE pipeline_runs
                SET status = :status,
                    records_processed = :records_processed,
                    error_message = :error_message,
                    finished_at = NOW()
                WHERE id = :run_id
                  AND status = 'running'
            """),
            {
                "run_id": run_id,
                "status": status,
                "records_processed": records_processed,
                "error_message": error_message,
            },
        )

        if result.rowcount != 1:
            raise ValueError(
                f"Pipeline run {run_id} does not exist or is already finished."
            )
