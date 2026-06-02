"""Embedding domain models for contextual chunk vectorization."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from tracerag.models.types import (
    ChildChunkId,
    ContentHash,
    EmbeddingModelName,
    EmbeddingProviderName,
    EmbeddingVector,
    ParentChunkId,
)


class EmbeddingMetadata(BaseModel):
    """Provenance for a vector generated from a contextual child chunk."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    chunk_id: ChildChunkId
    parent_chunk_id: ParentChunkId
    provider: EmbeddingProviderName
    model: EmbeddingModelName
    dimension: int = Field(ge=1)
    embedded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    input_text_hash: ContentHash
    document_content_hash: ContentHash | None = None
    uses_context_prefix: bool = False
    uses_prefixed_envelope: bool = True

    @field_validator("embedded_at", mode="after")
    @classmethod
    def _ensure_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


class EmbeddingValidationResult(BaseModel):
    """Outcome of validating an embedding vector and its metadata."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    is_valid: bool
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _consistent_valid_flag(self) -> EmbeddingValidationResult:
        if self.is_valid and self.errors:
            msg = "is_valid cannot be true when errors are present"
            raise ValueError(msg)
        if not self.is_valid and not self.errors:
            msg = "is_valid=false requires at least one error"
            raise ValueError(msg)
        return self


class ChunkEmbeddingRecord(BaseModel):
    """Storage-ready embedding record for one contextual child chunk."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    chunk_id: ChildChunkId
    vector: EmbeddingVector
    metadata: EmbeddingMetadata
    validation: EmbeddingValidationResult

    @field_validator("vector", mode="before")
    @classmethod
    def _coerce_vector(cls, value: object) -> EmbeddingVector:
        if isinstance(value, tuple):
            return value
        if isinstance(value, list):
            return tuple(float(item) for item in value)
        msg = "vector must be a sequence of floats"
        raise TypeError(msg)

    @model_validator(mode="after")
    def _align_metadata(self) -> ChunkEmbeddingRecord:
        if self.metadata.chunk_id != self.chunk_id:
            msg = "metadata.chunk_id must match ChunkEmbeddingRecord.chunk_id"
            raise ValueError(msg)
        if len(self.vector) != self.metadata.dimension:
            msg = "vector length must match metadata.dimension"
            raise ValueError(msg)
        if not self.validation.is_valid:
            msg = "ChunkEmbeddingRecord requires a passing validation result"
            raise ValueError(msg)
        return self


class EmbeddingFailure(BaseModel):
    """Failed embedding attempt for a single chunk."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    chunk_id: ChildChunkId
    error: str


class EmbeddingBatchResult(BaseModel):
    """Batch embedding outcome for multiple contextual child chunks."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    records: tuple[ChunkEmbeddingRecord, ...] = ()
    failures: tuple[EmbeddingFailure, ...] = ()

    @property
    def total(self) -> int:
        return len(self.records) + len(self.failures)

    @property
    def succeeded(self) -> int:
        return len(self.records)

    @property
    def failed(self) -> int:
        return len(self.failures)
