"""Embedding provider interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from tracerag.models.types import EmbeddingModelName, EmbeddingProviderName, EmbeddingVector


@dataclass(frozen=True)
class EmbeddingRequest:
    """Single-text embedding request."""

    text: str


@dataclass(frozen=True)
class EmbeddingBatchRequest:
    """Batch embedding request preserving input order."""

    texts: tuple[str, ...]


class EmbeddingProvider(ABC):
    """Contract for dense vector generation from text inputs."""

    @property
    @abstractmethod
    def name(self) -> EmbeddingProviderName:
        """Stable provider identifier."""

    @property
    @abstractmethod
    def model(self) -> EmbeddingModelName:
        """Active embedding model name."""

    @abstractmethod
    def embed(self, text: str) -> EmbeddingVector:
        """Embed a single text input."""

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[EmbeddingVector]:
        """Embed multiple texts preserving order."""

    def embed_request(self, request: EmbeddingRequest) -> EmbeddingVector:
        """Embed using an ``EmbeddingRequest`` wrapper."""
        return self.embed(request.text)

    def embed_batch_request(self, request: EmbeddingBatchRequest) -> list[EmbeddingVector]:
        """Embed using an ``EmbeddingBatchRequest`` wrapper."""
        return self.embed_batch(list(request.texts))
