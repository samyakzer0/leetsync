# LeetMeKnow — Daily LeetCode Data Pipeline

LeetMeKnow ingests LeetCode's daily challenge through GraphQL, matches its tags against configurable focus topics, persists structured data in PostgreSQL, generates a Markdown archive, and sends a priority email when a topic matches. It runs locally with Python or under Apache Airflow in Docker.

## Architecture

```mermaid
flowchart TD
    S[LeetCode GraphQL API] --> I[Fetch daily challenge]
    I --> V[Validate and normalize metadata]
    V --> M[Match tags against configured focus topics]
    M --> DB[(PostgreSQL)]
    DB --> P[problems]
    DB --> T[tags]
    DB --> PT[problem_tags]
    DB --> PM[problem_matches]
    M --> MD[Generate Markdown archive]
    M --> C{Focus topic matched?}
    C -- Yes --> E[Priority email]
    C -- No --> SK[Skip email]
    L[Local Python CLI] --> I
    A[Airflow scheduled DAG] --> I
    A --> R[(pipeline_runs)]
```

## Engineering concepts demonstrated

- GraphQL API ingestion with HTTP timeout and response handling.
- Tag matching and transformation using configurable focus topics.
- Relational modelling for problems, tags, matches, and pipeline run history.
- Idempotent upserts keyed by problem date and conflict-safe relationship inserts.
- Airflow scheduling and task retries.
- Dockerized execution with PostgreSQL.
- Markdown archive generation and conditional SMTP notification.

## Data model

| Table | Purpose |
|---|---|
| `problems` | One daily challenge record, metadata, description, tags, and match flag |
| `tags` | Unique tag dictionary |
| `problem_tags` | Relationship between problems and all tags |
| `problem_matches` | Relationship between problems and matched focus tags |
| `pipeline_runs` | Start/end time, status, processed-record count, and failure details |

`problems.problem_date` is the natural key for a daily challenge. Composite keys in relationship tables prevent duplicate links.

## Repository layout

```text
.
├── dags/notify_leetcode.py
├── daily_challenges/       # generated Markdown output
├── docs/
├── sql/
├── src/
│   ├── config.py
│   ├── leetcode_client.py
│   ├── main.py
│   ├── markdown_builder.py
│   ├── notifier.py
│   └── storage.py
├── tests/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Configuration

Create `.env` locally and never commit it. Example shape (use your own credentials):

```dotenv
POSTGRES_DB=leetmeknow
POSTGRES_USER=leetmeknow
POSTGRES_PASSWORD=replace_with_local_password
DATABASE_URL=postgresql+psycopg2://leetmeknow:replace_with_local_password@localhost:5433/leetmeknow
SMTP_USER=
SMTP_PASSWORD=
NOTIFICATION_EMAIL=
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
OUTPUT_DIR=daily_challenges
```

Local Python connects through `localhost:5433`. Inside Docker, Airflow should use the Compose hostname `postgres` and container port `5432`.

## Run locally

After dependencies are installed and the schema is applied:

```powershell
python -m src.main
```

This calls the real LeetCode API and may send an email if a focus topic matches.

## Run with Docker and Airflow

```powershell
docker compose config --quiet
docker compose up -d --build airflow-standalone
docker compose ps
docker exec leetpulse-airflow airflow dags list
docker exec leetpulse-airflow airflow dags list-import-errors
```

Open `http://localhost:8080` for the Airflow UI. A full DAG test executes the real pipeline and may send an email:

```powershell
docker exec leetpulse-airflow airflow dags test notify_leetcode 2026-10-12
```

## Unit tests

The included unit tests use Python's standard `unittest` framework and mock the pipeline's external dependencies:

```powershell
python -m unittest discover -s tests -v
```

A separate development-database integration test should verify repeat-save idempotency. Never run destructive schema or volume reset commands against your working database.

## Operational checks

```powershell
docker compose ps
docker compose logs --tail 100 airflow-standalone
docker exec leetpulse-airflow airflow dags list-import-errors
```

Review recent `pipeline_runs` rows to verify status and inspect failure messages.

## Known limitations and follow-up work

- SMTP and database writes are separate side effects. A retry after an ambiguous SMTP failure can send a duplicate notification; track notification status independently before claiming exactly-once delivery.
- Unit tests do not replace database integration tests or an actual Airflow execution.
- No performance numbers are claimed here; record metrics only after measuring actual runs.
