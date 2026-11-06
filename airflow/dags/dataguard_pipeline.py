
from datetime import datetime, timezone
from pathlib import Path
import subprocess

from airflow.sdk import dag, task


PROJECT_ROOT = Path("/opt/dataguard")
DBT_PROJECT = PROJECT_ROOT / "dataguard_analytics"


def run_command(command, working_directory):
    """Execute a pipeline command and fail the task if it fails."""

    subprocess.run(
        command,
        cwd=str(working_directory),
        check=True
    )


@dag(
    dag_id="dataguard_end_to_end_pipeline",
    description="End-to-end transaction quality and analytics pipeline",
    start_date=datetime(2026, 11, 6, tzinfo=timezone.utc),
    schedule=None,
    catchup=False,
    tags=["dataguard", "data-engineering", "dbt"],
)
def dataguard_pipeline():

    @task
    def generate_transactions():
        run_command(
            ["python", "src/producer/transaction_producer.py"],
            PROJECT_ROOT
        )

    @task
    def validate_transactions():
        run_command(
            ["python", "src/validation/data_quality_engine.py"],
            PROJECT_ROOT
        )

    @task
    def load_duckdb():
        run_command(
            ["python", "src/processing/load_to_duckdb.py"],
            PROJECT_ROOT
        )

    @task
    def dbt_run():
        run_command(
            ["dbt", "run", "--project-dir", str(DBT_PROJECT)],
            PROJECT_ROOT
        )

    @task
    def dbt_test():
        run_command(
            ["dbt", "test", "--project-dir", str(DBT_PROJECT)],
            PROJECT_ROOT
        )

    producer = generate_transactions()
    quality = validate_transactions()
    loader = load_duckdb()
    transformations = dbt_run()
    tests = dbt_test()

    producer >> quality >> loader >> transformations >> tests


dataguard_pipeline()
