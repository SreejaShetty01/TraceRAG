"""Ollama service boundary for local model invocation transport interfaces."""

from __future__ import annotations

from typing import Any

import httpx

from tracerag.core.exceptions import EmbeddingError


class OllamaClient:
    """HTTP client for Ollama local inference APIs."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        *,
        timeout_seconds: float = 60.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds

    @property
    def base_url(self) -> str:
        return self._base_url

    def embed(self, model: str, input_text: str | list[str]) -> list[list[float]]:
        """Call Ollama ``/api/embed`` and return embedding vectors."""
        payload: dict[str, Any] = {"model": model, "input": input_text}
        url = f"{self._base_url}/api/embed"
        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                body = response.json()
        except httpx.HTTPError as exc:
            raise EmbeddingError(
                "Ollama embed request failed",
                cause=exc,
            ) from exc

        embeddings = body.get("embeddings")
        if not isinstance(embeddings, list):
            raise EmbeddingError("Ollama embed response missing embeddings list")

        if isinstance(input_text, str):
            if len(embeddings) != 1:
                raise EmbeddingError("expected exactly one embedding for single input")
            return [_coerce_vector(embeddings[0])]

        if len(embeddings) != len(input_text):
            raise EmbeddingError(
                f"embedding count {len(embeddings)} does not match input count {len(input_text)}"
            )
        return [_coerce_vector(item) for item in embeddings]


def _coerce_vector(value: object) -> list[float]:
    if not isinstance(value, list):
        raise EmbeddingError("embedding item is not a list")
    return [float(item) for item in value]
