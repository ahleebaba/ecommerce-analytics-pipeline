"""
DAG 1: Ecommerce Ingestion Pipeline
Last updated: 2026-05-31 — git-sync test
Handles Airbyte sync only.

Emits dataset signal ECOMMERCE_RAW when complete
to trigger DAG 2 (transformation).

Schedule: Daily at 5am SGT
"""

from airflow import DAG, Dataset
from airflow.operators.bash import BashOperator
from datetime import timedelta
import pendulum

# ── Dataset signal ───────────────────────────────────────────────
ECOMMERCE_RAW = Dataset("bigquery://ecommerce-analytics-495218/ingest_ecommerce")

# ── Default arguments ────────────────────────────────────────────
default_args = {
    'owner': 'lee_jun_yan',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
}

# ── DAG definition ───────────────────────────────────────────────
with DAG(
    dag_id='ecommerce_ingestion',
    description='Airbyte sync for ecommerce data — emits dataset signal on completion',
    default_args=default_args,
    start_date=pendulum.datetime(2025, 1, 1, tz="Asia/Singapore"),
    schedule='0 5 * * *',,  # daily at 5am SGT
    catchup=False,
    tags=['ecommerce', 'ingestion', 'airbyte']
) as dag:

    # ── Task 1: Trigger Airbyte sync ─────────────────────────────
    # Credentials stored as Airflow Variables (Admin → Variables):
    # - airbyte_api_key
    # - airbyte_connection_id
    airbyte_sync = BashOperator(
        task_id='airbyte_sync',
        bash_command="""
            echo "Triggering Airbyte sync at $(date)..."
            RESPONSE=$(curl -s -X POST \
                "http://{{ var.value.airbyte_host }}:8000/api/v1/connections/sync" \
                -H "Authorization: Basic {{ var.value.airbyte_basic_auth }}" \
                -H "Content-Type: application/json" \
                -d '{"connectionId": "{{ var.value.airbyte_connection_id }}"}')
            echo "Airbyte response: $RESPONSE"
            echo "Airbyte sync triggered successfully"
        """,
        outlets=[ECOMMERCE_RAW],
    )

    # ── Task 2: Wait for Airbyte sync to complete ─────────────────
    wait_for_airbyte = BashOperator(
        task_id='wait_for_airbyte_completion',
        bash_command="""
            echo "Waiting for Airbyte sync to complete..."
            sleep 60
            echo "Airbyte sync complete at $(date)"
        """,
        outlets=[ECOMMERCE_RAW],  # ← signals ingest_ecommerce updated
    )

    # ── Pipeline order ────────────────────────────────────────────
    airbyte_sync >> wait_for_airbyte