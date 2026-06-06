"""Retrieval configuration models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RetrievalConfig(BaseModel):
    """Hybrid retrieval sizing and fusion policy."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    dense_top_k: int = Field(default=30, ge=1)
    sparse_top_k: int = Field(default=30, ge=1)
    rrf_k: int = Field(default=60, ge=1)
    fusion_top_k: int = Field(default=30, ge=1)
    rerank_top_n: int = Field(default=10, ge=1)
    rerank_enabled: bool = False
    rerank_model: str = Field(default="cross-encoder/ms-marco-MiniLM-L-6-v2")

    @classmethod
    def default(cls) -> RetrievalConfig:
        """Return the default TraceRAG hybrid retrieval policy."""
        return cls()
