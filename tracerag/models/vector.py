"""Vector storage domain models for persisted embedding records."""

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
    VectorPointId,
)


class VectorPointPayload(BaseModel):
    """Chunk metadata payload stored alongside a vector in the vector database."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    chunk_id: ChildChunkId
    parent_chunk_id: ParentChunkId
    provider: EmbeddingProviderName
    model: EmbeddingModelName
    dimension: int = Field(ge=1)
    embedded_at: datetime
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


class StoredVectorRecord(BaseModel):
    """Normalized vector record prepared for vector store upsert."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    point_id: VectorPointId
    chunk_id: ChildChunkId
    vector: EmbeddingVector
    payload: VectorPointPayload

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
    def _align_identifiers(self) -> StoredVectorRecord:
        if self.payload.chunk_id != self.chunk_id:
            msg = "payload.chunk_id must match StoredVectorRecord.chunk_id"
            raise ValueError(msg)
        if len(self.vector) != self.payload.dimension:
            msg = "vector length must match payload.dimension"
            raise ValueError(msg)
        return self


class VectorStorageValidationResult(BaseModel):
    """Outcome of validating records before vector store persistence."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    is_valid: bool
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _consistent_valid_flag(self) -> VectorStorageValidationResult:
        if self.is_valid and self.errors:
            msg = "is_valid cannot be true when errors are present"
            raise ValueError(msg)
        if not self.is_valid and not self.errors:
            msg = "is_valid=false requires at least one error"
            raise ValueError(msg)
        return self


class VectorSearchHit(BaseModel):
    """Single vector similarity search hit from the vector store."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    point_id: VectorPointId
    chunk_id: ChildChunkId
    score: float
    payload: VectorPointPayload


class VectorUpsertFailure(BaseModel):
    """Failed upsert for a single embedding record."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    chunk_id: ChildChunkId
    error: str


class VectorUpsertResult(BaseModel):
    """Batch upsert outcome for vector storage."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    collection_name: str
    upserted_count: int = Field(ge=0)
    failures: tuple[VectorUpsertFailure, ...] = ()

    @property
    def total(self) -> int:
        return self.upserted_count + len(self.failures)

    @property
    def failed(self) -> int:
        return len(self.failures)
