"""Ollama client and prompt construction for SQL generation."""

from __future__ import annotations

import requests

from ai_sql_agent.config import AppConfig
from ai_sql_agent.prompts import build_prompt
from ai_sql_agent.sql_guard import normalize_sql


def generate_sql(question: str, config: AppConfig, temperature: float = 0.0) -> str:
    """Generate SQL from a natural-language question using Ollama."""

    response = requests.post(
        f"{config.ollama_base_url}/api/generate",
        json={
            "model": config.ollama_model,
            "prompt": build_prompt(question, config),
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": 512,
            },
        },
        timeout=120,
    )
    response.raise_for_status()
    payload = response.json()
    return normalize_sql(payload.get("response", ""))
