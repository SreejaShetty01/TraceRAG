"""Vector store and collection configuration models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CollectionConfig(BaseModel):
    """Qdrant collection parameters for chunk embeddings."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    name: str = Field(default="tracerag_chunks", min_length=1)
    vector_size: int = Field(default=768, ge=1)
    distance: Literal["cosine", "euclid", "dot"] = "cosine"
    on_disk_payload: bool = True
    recreate_if_exists: bool = False

    @classmethod
    def default(cls) -> CollectionConfig:
        """Return the default TraceRAG chunk collection configuration."""
        return cls()


class QdrantConfig(BaseModel):
    """Connection and collection settings for a Qdrant vector store."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    url: str = Field(default="http://localhost:6333")
    api_key: str | None = None
    prefer_grpc: bool = False
    timeout_seconds: float = Field(default=30.0, gt=0)
    upsert_batch_size: int = Field(default=64, ge=1)
    collection: CollectionConfig = Field(default_factory=CollectionConfig.default)

    @classmethod
    def default(cls) -> QdrantConfig:
        """Return the default local Qdrant configuration."""
        return cls()


class VectorStoreConfig(BaseModel):
    """Top-level vector storage configuration."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    provider: Literal["qdrant"] = "qdrant"
    qdrant: QdrantConfig = Field(default_factory=QdrantConfig.default)
    validate_before_upsert: bool = True
    bootstrap_on_upsert: bool = True

    @model_validator(mode="after")
    def _validate_provider_settings(self) -> VectorStoreConfig:
        if self.provider == "qdrant" and self.qdrant is None:
            msg = "qdrant settings are required when provider is qdrant"
            raise ValueError(msg)
        return self

    @classmethod
    def default(cls) -> VectorStoreConfig:
        """Return the default vector store configuration (Qdrant)."""
        return cls()
