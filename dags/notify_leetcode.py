
from datetime import datetime, timedelta

from airflow.decorators import dag, task
from src.main import main as run_daily_pipeline


@dag(
    dag_id="notify_leetcode",
    description="Orchestrate the LeetMeKnow daily pipeline",
    schedule="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args={
        "owner": "samyak",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
    tags=["leetcode", "data-engineering"],
)
def notify_leetcode():

    @task()
    def execute_pipeline():
        run_daily_pipeline()

    execute_pipeline()


notify_leetcode()
