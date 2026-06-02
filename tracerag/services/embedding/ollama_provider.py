"""Ollama embedding provider implementation."""

from __future__ import annotations

from tracerag.models.types import EmbeddingModelName, EmbeddingProviderName, EmbeddingVector
from tracerag.services.embedding.config import EmbeddingConfig
from tracerag.services.embedding.contracts import EmbeddingProvider
from tracerag.services.ollama import OllamaClient


class OllamaEmbeddingProvider(EmbeddingProvider):
    """Embedding provider backed by a local Ollama ``/api/embed`` endpoint."""

    def __init__(
        self,
        config: EmbeddingConfig | None = None,
        *,
        client: OllamaClient | None = None,
    ) -> None:
        self._config = config or EmbeddingConfig.default()
        self._client = client or OllamaClient(
            self._config.base_url,
            timeout_seconds=self._config.timeout_seconds,
        )

    @property
    def name(self) -> EmbeddingProviderName:
        return "ollama"

    @property
    def model(self) -> EmbeddingModelName:
        return self._config.model

    @property
    def config(self) -> EmbeddingConfig:
        return self._config

    def embed(self, text: str) -> EmbeddingVector:
        vectors = self.embed_batch([text])
        return vectors[0]

    def embed_batch(self, texts: list[str]) -> list[EmbeddingVector]:
        if not texts:
            return []
        raw_vectors = self._client.embed(self._config.model, texts)
        return [tuple(vector) for vector in raw_vectors]
