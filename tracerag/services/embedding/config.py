"""Embedding configuration models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class EmbeddingConfig(BaseModel):
    """Configuration for contextual chunk embedding via Ollama."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    provider: Literal["ollama"] = "ollama"
    model: str = Field(default="nomic-embed-text", min_length=1)
    expected_dimension: int = Field(default=768, ge=1)
    base_url: str = Field(default="http://localhost:11434")
    timeout_seconds: float = Field(default=60.0, gt=0)
    batch_size: int = Field(default=16, ge=1)
    use_prefixed_envelope: bool = True
    validate_vectors: bool = True

    @classmethod
    def default(cls) -> EmbeddingConfig:
        """Return the default Ollama embedding configuration for TraceRAG."""
        return cls()

    @classmethod
    def nomic_embed_text(cls, *, base_url: str = "http://localhost:11434") -> EmbeddingConfig:
        """Preset for the ``nomic-embed-text`` model served by Ollama."""
        return cls(model="nomic-embed-text", expected_dimension=768, base_url=base_url)
