from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator


with DAG(
    dag_id="brazil_energy_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="@monthly",
    catchup=False,
    tags=["energy", "data-engineering"],
) as dag:

    ingest = BashOperator(
        task_id="ingest_anp_data",
        bash_command="cd /opt/airflow && python -m src.ingestion.anp_oil_production",
    )

    bronze = BashOperator(
        task_id="build_bronze",
        bash_command="cd /opt/airflow && python -m src.transformations.anp_oil_bronze",
    )

    silver = BashOperator(
        task_id="build_silver",
        bash_command="cd /opt/airflow && python -m src.transformations.anp_oil_silver",
    )

    gold = BashOperator(
        task_id="build_gold",
        bash_command="cd /opt/airflow && python -m src.transformations.anp_oil_gold",
    )

    load_postgres = BashOperator(
    task_id="load_postgres",
    bash_command=(
        "cd /opt/airflow && "
        "python -m src.loaders.postgres_loader"
    ),
)

    ingest >> bronze >> silver >> gold >> load_postgres