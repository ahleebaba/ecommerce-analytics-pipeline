"""Configuration helpers for the Streamlit AI SQL agent."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    """Runtime configuration loaded from environment variables."""

    gcp_project: str = "ecommerce-analytics-495218"
    bigquery_location: str = "asia-southeast1"
    default_dataset: str = "warehouse_ecommerce"
    default_table: str = "fct_orders"
    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma2:2b"
    vertex_location: str = "us-central1"
    vertex_model: str = "gemini-2.5-flash"
    max_rows: int = 500

    @property
    def fq_table(self) -> str:
        return f"`{self.gcp_project}.{self.default_dataset}.{self.default_table}`"


def load_config() -> AppConfig:
    """Load app config from environment variables with project defaults."""

    return AppConfig(
        gcp_project=os.getenv("GCP_PROJECT", AppConfig.gcp_project),
        bigquery_location=os.getenv("BIGQUERY_LOCATION", AppConfig.bigquery_location),
        default_dataset=os.getenv("BIGQUERY_DATASET", AppConfig.default_dataset),
        default_table=os.getenv("BIGQUERY_TABLE", AppConfig.default_table),
        llm_provider=os.getenv("LLM_PROVIDER", AppConfig.llm_provider).lower(),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", AppConfig.ollama_base_url).rstrip("/"),
        ollama_model=os.getenv("OLLAMA_MODEL", AppConfig.ollama_model),
        vertex_location=os.getenv("VERTEX_LOCATION", AppConfig.vertex_location),
        vertex_model=os.getenv("VERTEX_MODEL", AppConfig.vertex_model),
        max_rows=int(os.getenv("MAX_RESULT_ROWS", str(AppConfig.max_rows))),
    )
