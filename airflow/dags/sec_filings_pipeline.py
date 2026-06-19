from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "vinicius",
    "retries": 1,
}

with DAG(
    dag_id="sec_filings_pipeline",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    catchup=False,
    schedule="@daily",
) as dag:

    ingest = BashOperator(
        task_id="ingest_sec_data",
        bash_command="""
        cd /opt/project &&
        python -m main
        """
    )

    bronze = BashOperator(
        task_id="build_bronze",
        bash_command="""
        cd /opt/project &&
        python -m bronze.build_bronze
        """
    )

    silver = BashOperator(
        task_id="build_silver",
        bash_command="""
        cd /opt/project &&
        python -m silver.build_silver
        """
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="""
        cd /opt/project &&
        dbt run \
          --project-dir dbt \
          --profiles-dir dbt
        """
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="""
        cd /opt/project &&
        dbt test \
          --project-dir dbt \
          --profiles-dir dbt
        """
    )

    ingest >> bronze >> silver >> dbt_run >> dbt_test