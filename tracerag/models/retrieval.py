"""Retrieval query and result models for hybrid search."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from tracerag.models.types import ChildChunkId, ParentChunkId, VectorPointId
from tracerag.models.vector import VectorPointPayload


class RetrievalSource(str, Enum):
    """Provenance of a retrieval candidate score."""

    DENSE = "dense"
    SPARSE = "sparse"
    FUSED = "fused"
    RERANKED = "reranked"


class RetrievalFilter(BaseModel):
    """Metadata-aware constraints applied to retrieval candidates."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    chunk_ids: frozenset[ChildChunkId] | None = None
    parent_chunk_ids: frozenset[ParentChunkId] | None = None
    embedding_models: frozenset[str] | None = None
    embedding_providers: frozenset[str] | None = None
    document_content_hashes: frozenset[str] | None = None
    require_context_prefix: bool | None = None

    def is_empty(self) -> bool:
        return (
            self.chunk_ids is None
            and self.parent_chunk_ids is None
            and self.embedding_models is None
            and self.embedding_providers is None
            and self.document_content_hashes is None
            and self.require_context_prefix is None
        )


class RetrievalQuery(BaseModel):
    """Natural-language retrieval request."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    text: str = Field(min_length=1)
    top_k: int | None = Field(default=None, ge=1)
    filters: RetrievalFilter | None = None

    @field_validator("text")
    @classmethod
    def _strip_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            msg = "query text must not be empty"
            raise ValueError(msg)
        return stripped


class SparseCorpusDocument(BaseModel):
    """Indexed document for sparse (BM25) retrieval."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    chunk_id: ChildChunkId
    text: str
    parent_chunk_id: ParentChunkId | None = None
    document_content_hash: str | None = None
    embedding_model: str | None = None
    embedding_provider: str | None = None
    uses_context_prefix: bool | None = None

    @field_validator("text")
    @classmethod
    def _text_not_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "corpus text must not be empty"
            raise ValueError(msg)
        return value


class RetrievalCandidate(BaseModel):
    """Single ranked retrieval hit."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    chunk_id: ChildChunkId
    rank: int = Field(ge=1)
    score: float
    source: RetrievalSource
    point_id: VectorPointId | None = None
    payload: VectorPointPayload | None = None
    snippet: str | None = None
    dense_score: float | None = None
    sparse_score: float | None = None
    rrf_score: float | None = None
    rerank_score: float | None = None


class RetrievalResult(BaseModel):
    """Ranked list of candidates from one retrieval stream."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    query: RetrievalQuery
    source: RetrievalSource
    candidates: tuple[RetrievalCandidate, ...] = ()

    @property
    def count(self) -> int:
        return len(self.candidates)


class HybridRetrievalResult(BaseModel):
    """Combined outcome of dense, sparse, fusion, and optional reranking."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    query: RetrievalQuery
    dense: RetrievalResult
    sparse: RetrievalResult
    fused: RetrievalResult
    reranked: RetrievalResult | None = None

    @property
    def final_candidates(self) -> tuple[RetrievalCandidate, ...]:
        if self.reranked is not None:
            return self.reranked.candidates
        return self.fused.candidates
