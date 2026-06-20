"""Google Vertex AI Gemini client for hosted SQL generation."""

from __future__ import annotations

import requests
import google.auth
from google.auth.transport.requests import Request

from ai_sql_agent.config import AppConfig
from ai_sql_agent.prompts import SYSTEM_INSTRUCTIONS, build_user_prompt
from ai_sql_agent.sql_guard import normalize_sql


class VertexConfigError(ValueError):
    """Raised when Vertex AI authentication or config is incomplete."""


def _get_access_token() -> str:
    """Return an access token from Google Application Default Credentials."""

    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    credentials.refresh(Request())
    if not credentials.token:
        raise VertexConfigError("Could not refresh Google Application Default Credentials.")
    return credentials.token


def _extract_text(payload: dict) -> str:
    """Extract generated text from a Vertex AI generateContent response."""

    chunks = []
    for candidate in payload.get("candidates", []):
        content = candidate.get("content", {})
        for part in content.get("parts", []):
            if part.get("text"):
                chunks.append(str(part["text"]))
    return "\n".join(chunks)


def generate_sql(question: str, config: AppConfig, temperature: float = 0.0) -> str:
    """Generate SQL with Gemini on Vertex AI."""

    token = _get_access_token()
    url = (
        f"https://{config.vertex_location}-aiplatform.googleapis.com/v1/"
        f"projects/{config.gcp_project}/locations/{config.vertex_location}/"
        f"publishers/google/models/{config.vertex_model}:generateContent"
    )
    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={
            "systemInstruction": {
                "parts": [{"text": SYSTEM_INSTRUCTIONS}],
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": build_user_prompt(question, config)}],
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": 512,
            },
        },
        timeout=120,
    )
    response.raise_for_status()
    return normalize_sql(_extract_text(response.json()))
