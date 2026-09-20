import json
import time
import httpx
from loguru import logger
from app.core.config import settings

DIAGNOSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "root_cause": {"type": "string"},
        "explanation": {"type": "string"},
        "suggested_fix": {"type": "string"},
        "kubectl_commands": {"type": "array", "items": {"type": "string"}},
        "prevention_recommendation": {"type": "string"},
        "confidence": {"type": "integer"},
        "confidence_reasoning": {"type": "string"},
    },
    "required": [
        "root_cause", "explanation", "suggested_fix", "kubectl_commands",
        "prevention_recommendation", "confidence", "confidence_reasoning",
    ],
    "additionalProperties": False,
}

class LLMClient:
    def __init__(self, client: httpx.Client | None = None): self.client = client
    def complete(self, messages: list[dict[str, str]]) -> dict:
        if not settings.openrouter_api_key or not settings.openrouter_model:
            raise RuntimeError("OpenRouter is not configured. Set OPENROUTER_API_KEY and OPENROUTER_MODEL.")
        headers = {"Authorization": f"Bearer {settings.openrouter_api_key}", "Content-Type": "application/json"}
        payload = {
            "model": settings.openrouter_model,
            "messages": messages,
            "temperature": 0,
            "max_tokens": 1200,
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": "kubernetes_diagnosis", "strict": True, "schema": DIAGNOSIS_SCHEMA},
            },
            "provider": {"require_parameters": True},
        }
        last_error = ""
        for attempt in range(1, 4):
            try:
                client = self.client or httpx.Client(timeout=settings.openrouter_timeout_seconds)
                response = client.post(f"{settings.openrouter_base_url}/chat/completions", headers=headers, json=payload)
                response.raise_for_status()
                return json.loads(response.json()["choices"][0]["message"]["content"])
            except (httpx.HTTPError, KeyError, ValueError, json.JSONDecodeError) as exc:
                last_error = str(exc); logger.warning("OpenRouter attempt {} failed: {}", attempt, type(exc).__name__)
                if attempt < 3: time.sleep(0.5 * attempt)
        raise RuntimeError(f"OpenRouter request failed after retries: {last_error}")
