"""
DAG 2: Ecommerce Transformation Pipeline
Triggered automatically when ECOMMERCE_RAW dataset is updated by DAG 1.

Tasks:
1. enrich_product_tags — LLM enrichment (Ollama) for new products
2. dbt_run — runs all 7 dbt models in correct dependency order
3. dbt_test — runs data quality tests
4. log_completion — logs pipeline completion

No fixed schedule — purely event driven via Dataset-Aware Scheduling.
"""

from airflow import DAG, Dataset
from airflow.operators.bash import BashOperator
from datetime import timedelta
import pendulum

# ── Dataset dependency ───────────────────────────────────────────
# Triggers when DAG 1 signals ingest_ecommerce is updated
ECOMMERCE_RAW = Dataset("bigquery://ecommerce-analytics-495218/ingest_ecommerce")

# ── Paths ────────────────────────────────────────────────────────
PROJECT_PATH = "/mnt/c/Users/Lee Jun Yan/OneDrive/Documents/ecommerce-analytics-pipeline/ecommerce_pipeline"

# ── Default arguments ────────────────────────────────────────────
default_args = {
    'owner': 'lee_jun_yan',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
}

# Define documentation text as a variable string
dag_docs = """
DAG 2: Ecommerce Transformation Pipeline
Triggered automatically when ECOMMERCE_RAW dataset is updated by DAG 1.

Tasks:
1. enrich_product_tags — LLM enrichment (Ollama) for new products
2. dbt_run — runs all 7 dbt models in correct dependency order
3. dbt_test — runs data quality tests
4. log_completion — logs pipeline completion

No fixed schedule — purely event driven via Dataset-Aware Scheduling.
"""
# ── DAG definition ───────────────────────────────────────────────
with DAG(
    dag_id='ecommerce_transformation',
    description='LLM enrichment + dbt transformation — triggered by ecommerce_ingestion DAG',
    default_args=default_args,
    start_date=pendulum.datetime(2025, 1, 1, tz="Asia/Singapore"),
    schedule=[ECOMMERCE_RAW],  # ← triggers when DAG 1 emits ECOMMERCE_RAW signal
    catchup=False,
    doc_md=dag_docs,
    tags=['ecommerce', 'transformation', 'dataset_scheduling' , 'dbt', 'llm']
) as dag:

    # ── Task 1: Enrich product tags with Ollama LLM ───────────────
    # Only processes NEW products not yet in stg_product_tag_enriched
    # Uses FULL OUTER JOIN logic to detect new records
    enrich_tags = BashOperator(
        task_id='enrich_product_tags',
        bash_command=f"""
            echo "Running LLM tag enrichment at $(date)..."
            cd "{PROJECT_PATH}" && \
            python ingestion/enrich_product_tags.py
            echo "Tag enrichment complete at $(date)"
        """,
    )

    # ── Task 2: Run dbt models ────────────────────────────────────
    # Runs all 7 models in correct dependency order:
    # stg_products, stg_users, stg_carts, stg_orders, stg_categories
    # → int_orders_enriched
    # → fct_orders
    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command=f"""
            echo "Running dbt models at $(date)..."
            cd "{PROJECT_PATH}" && \
            dbt run
            echo "dbt run complete at $(date)"
        """,
    )

    # ── Task 3: Run dbt tests ─────────────────────────────────────
    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command=f"""
            echo "Running dbt tests at $(date)..."
            cd "{PROJECT_PATH}" && \
            dbt test
            echo "dbt test complete at $(date)"
        """,
    )

    # ── Task 4: Log pipeline completion ──────────────────────────
    log_completion = BashOperator(
        task_id='log_completion',
        bash_command="""
            echo "=========================================="
            echo "Pipeline completed successfully!"
            echo "Timestamp: $(date)"
            echo "Layers updated:"
            echo "  ingest_ecommerce       (raw)"
            echo "  post_ingest_ecommerce  (staging + enriched)"
            echo "  hub_ecommerce          (intermediate)"
            echo "  warehouse_ecommerce    (marts)"
            echo "=========================================="
        """,
    )

    # ── Pipeline order ────────────────────────────────────────────
    enrich_tags >> dbt_run >> dbt_test >> log_completion