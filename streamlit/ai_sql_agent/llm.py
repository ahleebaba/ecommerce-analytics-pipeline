"""LLM provider router."""

from __future__ import annotations

from ai_sql_agent.config import AppConfig
from ai_sql_agent import google_vertex_client, ollama_client


def provider_label(config: AppConfig) -> str:
    """Return a human-readable provider/model label."""

    if config.llm_provider == "openai":
        return f"Vertex AI / {config.vertex_model}"
    if config.llm_provider == "google":
        return f"Vertex AI / {config.vertex_model}"
    return f"Ollama / {config.ollama_model}"


def generate_sql(question: str, config: AppConfig, temperature: float = 0.0) -> str:
    """Generate SQL using the configured LLM provider."""

    if config.llm_provider == "ollama":
        return ollama_client.generate_sql(question, config, temperature=temperature)
    if config.llm_provider in {"google", "vertex"}:
        return google_vertex_client.generate_sql(question, config, temperature=temperature)
    raise ValueError("LLM_PROVIDER must be either 'ollama' or 'google'.")
