"""Ollama API client for local LLM inference with cloud fallback."""

from __future__ import annotations

import json
from typing import Any

import httpx
import structlog

from app.core.config import settings

logger = structlog.get_logger()


class OllamaClient:
    """Async client for Ollama API with OpenRouter fallback."""

    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self._fallback_url = "https://openrouter.ai/api/v1/chat/completions"

    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        format: dict | None = None,
    ) -> dict[str, Any]:
        """Generate a response via Ollama /api/generate."""
        model = model or settings.OLLAMA_MODEL
        payload: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
        if format:
            payload["format"] = format

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(f"{self.base_url}/api/generate", json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    text = data.get("response", "")
                    # Strip markdown fences if present
                    if text.startswith("```"):
                        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
                        if text.endswith("```"):
                            text = text[:-3]
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError:
                        return {"text": text}
                logger.warning("ollama.generate_failed", status=resp.status_code)
        except Exception as exc:
            logger.warning("ollama.unavailable", error=str(exc))

        # Fallback to OpenRouter
        if settings.OPENROUTER_API_KEY:
            return await self._fallback_generate(prompt, model)

        return {"error": "Ollama unavailable and no fallback configured"}

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings via Ollama /api/embeddings."""
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                results = []
                for text in texts:
                    resp = await client.post(
                        f"{self.base_url}/api/embeddings",
                        json={"model": "mxbai-embed-large", "input": text},
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        results.append(data["embeddings"][0])
                    else:
                        results.append([0.0] * 1024)
                return results
        except Exception as exc:
            logger.warning("ollama.embed_failed", error=str(exc))
            return [[0.0] * 1024 for _ in texts]

    async def health_check(self) -> bool:
        """Check if Ollama is running."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> list[str]:
        """List available Ollama models."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                if resp.status_code == 200:
                    data = resp.json()
                    return [m["name"] for m in data.get("models", [])]
        except Exception:
            pass
        return []

    async def _fallback_generate(self, prompt: str, model: str) -> dict[str, Any]:
        """Fallback to OpenRouter when Ollama is unavailable."""
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    self._fallback_url,
                    headers={"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"},
                    json={
                        "model": "google/gemma-3-9b-it:free",
                        "messages": [{"role": "user", "content": prompt}],
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    text = data["choices"][0]["message"]["content"]
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError:
                        return {"text": text}
        except Exception as exc:
            logger.error("openrouter.fallback_failed", error=str(exc))
        return {"error": "Both Ollama and OpenRouter unavailable"}
