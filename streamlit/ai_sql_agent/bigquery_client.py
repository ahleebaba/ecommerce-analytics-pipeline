"""BigQuery execution helpers."""

from __future__ import annotations

from google.cloud import bigquery

from ai_sql_agent.config import AppConfig


def get_bigquery_client(config: AppConfig) -> bigquery.Client:
    """Create a BigQuery client using Application Default Credentials."""

    return bigquery.Client(project=config.gcp_project, location=config.bigquery_location)


def dry_run_query(sql: str, config: AppConfig) -> int:
    """Validate a query in BigQuery and return estimated bytes processed."""

    client = get_bigquery_client(config)
    job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
    query_job = client.query(sql, job_config=job_config, location=config.bigquery_location)
    return int(query_job.total_bytes_processed or 0)


def run_query(sql: str, config: AppConfig):
    """Execute a query and return a pandas DataFrame."""

    client = get_bigquery_client(config)
    query_job = client.query(sql, location=config.bigquery_location)
    return query_job.result().to_dataframe(create_bqstorage_client=False)

