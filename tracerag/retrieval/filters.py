"""Metadata-aware retrieval filters."""

from __future__ import annotations

from tracerag.models.retrieval import (
    RetrievalCandidate,
    RetrievalFilter,
    SparseCorpusDocument,
)
from tracerag.models.vector import VectorPointPayload


def payload_matches_filter(payload: VectorPointPayload, filters: RetrievalFilter) -> bool:
    """Return whether a vector payload satisfies ``filters``."""
    if filters.chunk_ids is not None and payload.chunk_id not in filters.chunk_ids:
        return False
    if filters.parent_chunk_ids is not None and payload.parent_chunk_id not in filters.parent_chunk_ids:
        return False
    if filters.embedding_models is not None and payload.model not in filters.embedding_models:
        return False
    if filters.embedding_providers is not None and payload.provider not in filters.embedding_providers:
        return False
    if (
        filters.document_content_hashes is not None
        and payload.document_content_hash not in filters.document_content_hashes
    ):
        return False
    if filters.require_context_prefix is not None:
        if payload.uses_context_prefix != filters.require_context_prefix:
            return False
    return True


def candidate_matches_filter(candidate: RetrievalCandidate, filters: RetrievalFilter) -> bool:
    """Return whether a retrieval candidate satisfies ``filters``."""
    if filters.chunk_ids is not None and candidate.chunk_id not in filters.chunk_ids:
        return False

    if candidate.payload is not None:
        return payload_matches_filter(candidate.payload, filters)

    if filters.parent_chunk_ids is not None and candidate.payload is None:
        return False

    return True


def corpus_document_matches_filter(
    document: SparseCorpusDocument,
    filters: RetrievalFilter,
) -> bool:
    """Return whether a sparse corpus document satisfies ``filters``."""
    if filters.chunk_ids is not None and document.chunk_id not in filters.chunk_ids:
        return False
    if filters.parent_chunk_ids is not None:
        if document.parent_chunk_id is None or document.parent_chunk_id not in filters.parent_chunk_ids:
            return False
    if filters.embedding_models is not None:
        if document.embedding_model is None or document.embedding_model not in filters.embedding_models:
            return False
    if filters.embedding_providers is not None:
        if document.embedding_provider is None or document.embedding_provider not in filters.embedding_providers:
            return False
    if filters.document_content_hashes is not None:
        if (
            document.document_content_hash is None
            or document.document_content_hash not in filters.document_content_hashes
        ):
            return False
    if filters.require_context_prefix is not None:
        if document.uses_context_prefix != filters.require_context_prefix:
            return False
    return True


def apply_retrieval_filters(
    candidates: list[RetrievalCandidate],
    filters: RetrievalFilter | None,
) -> list[RetrievalCandidate]:
    """Filter candidates and reassign contiguous ranks."""
    if filters is None or filters.is_empty():
        return candidates

    filtered = [item for item in candidates if candidate_matches_filter(item, filters)]
    reranked: list[RetrievalCandidate] = []
    for index, item in enumerate(filtered, start=1):
        reranked.append(item.model_copy(update={"rank": index}))
    return reranked
