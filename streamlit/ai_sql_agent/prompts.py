"""Prompt construction shared by LLM providers."""

from __future__ import annotations

from ai_sql_agent.config import AppConfig
from ai_sql_agent.schema import build_schema_context


SYSTEM_INSTRUCTIONS = """You are a BigQuery SQL analyst for an ecommerce analytics portfolio project.
Return only one BigQuery Standard SQL query. Do not include Markdown, explanations, comments, or multiple statements.
The query must be read-only and answer the user's question using the provided schema.
Use fully-qualified table names with backticks.
Keep the query concise and include a sensible LIMIT for detail-level outputs.
"""


def build_prompt(question: str, config: AppConfig) -> str:
    """Build a grounded text-to-SQL prompt."""

    return f"""{SYSTEM_INSTRUCTIONS}

{build_schema_context(config)}

User question:
{question}

SQL:"""


def build_user_prompt(question: str, config: AppConfig) -> str:
    """Build the user portion for chat/response APIs with separate system instructions."""

    return f"""{build_schema_context(config)}

User question:
{question}

SQL:"""
