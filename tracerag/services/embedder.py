"""Embedding service boundary for text-to-vector generation interfaces."""

from __future__ import annotations

from tracerag.services.embedding.config import EmbeddingConfig
from tracerag.services.embedding.contracts import EmbeddingProvider
from tracerag.services.embedding.ollama_provider import OllamaEmbeddingProvider
from tracerag.services.embedding.pipeline import EmbeddingPipeline


def create_embedding_provider(config: EmbeddingConfig | None = None) -> EmbeddingProvider:
    """Create the default embedding provider (Ollama)."""
    policy = config or EmbeddingConfig.default()
    if policy.provider == "ollama":
        return OllamaEmbeddingProvider(policy)
    msg = f"unsupported embedding provider: {policy.provider!r}"
    raise ValueError(msg)


def create_embedding_pipeline(
    config: EmbeddingConfig | None = None,
    *,
    provider: EmbeddingProvider | None = None,
) -> EmbeddingPipeline:
    """Create an embedding pipeline with the default Ollama provider."""
    policy = config or EmbeddingConfig.default()
    resolved_provider = provider or create_embedding_provider(policy)
    return EmbeddingPipeline(resolved_provider, config=policy)
