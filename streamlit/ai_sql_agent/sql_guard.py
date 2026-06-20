"""Simple guardrails for LLM-generated BigQuery SQL."""

from __future__ import annotations

import re

from ai_sql_agent.config import AppConfig


FORBIDDEN_KEYWORDS = {
    "ALTER",
    "CREATE",
    "DELETE",
    "DROP",
    "GRANT",
    "INSERT",
    "MERGE",
    "REVOKE",
    "TRUNCATE",
    "UPDATE",
}


class SqlValidationError(ValueError):
    """Raised when generated SQL fails safety checks."""


def strip_markdown_fences(sql: str) -> str:
    """Remove common Markdown fences returned by chat models."""

    text = sql.strip()
    fence_match = re.fullmatch(r"```(?:sql)?\s*(.*?)\s*```", text, flags=re.IGNORECASE | re.DOTALL)
    if fence_match:
        return fence_match.group(1).strip()
    return text


def normalize_sql(sql: str) -> str:
    """Normalize SQL text while preserving readable formatting."""

    text = strip_markdown_fences(sql)
    text = text.strip()
    if text.endswith(";"):
        text = text[:-1].strip()
    return text


def validate_select_only(sql: str, config: AppConfig) -> str:
    """Validate that SQL is read-only and aimed at the configured table."""

    cleaned = normalize_sql(sql)
    if not cleaned:
        raise SqlValidationError("SQL is empty.")

    if ";" in cleaned:
        raise SqlValidationError("Only one SQL statement is allowed.")

    upper_sql = re.sub(r"\s+", " ", cleaned).upper()
    if not (upper_sql.startswith("SELECT ") or upper_sql.startswith("WITH ")):
        raise SqlValidationError("Only SELECT queries are allowed.")

    keyword_hits = {
        keyword
        for keyword in FORBIDDEN_KEYWORDS
        if re.search(rf"\b{keyword}\b", upper_sql)
    }
    if keyword_hits:
        raise SqlValidationError(
            f"Query contains forbidden keyword(s): {', '.join(sorted(keyword_hits))}."
        )

    fq_table_plain = f"{config.gcp_project}.{config.default_dataset}.{config.default_table}".upper()
    table_name = config.default_table.upper()
    if fq_table_plain not in upper_sql and table_name not in upper_sql:
        raise SqlValidationError(
            f"Query must reference {config.fq_table} or {config.default_table}."
        )

    if " LIMIT " not in f" {upper_sql} ":
        cleaned = f"{cleaned}\nLIMIT {config.max_rows}"

    return cleaned

