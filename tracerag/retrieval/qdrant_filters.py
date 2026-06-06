"""Qdrant filter construction for metadata-aware dense retrieval."""

from __future__ import annotations

from tracerag.models.retrieval import RetrievalFilter


def build_qdrant_filter(filters: RetrievalFilter | None):  # noqa: ANN201
    """Build a Qdrant ``Filter`` from retrieval filters, or ``None`` if empty."""
    if filters is None or filters.is_empty():
        return None

    try:
        from qdrant_client.models import FieldCondition, Filter, MatchAny, MatchValue
    except ImportError:
        return None

    must: list[FieldCondition] = []

    if filters.chunk_ids is not None:
        must.append(FieldCondition(key="chunk_id", match=MatchAny(any=list(filters.chunk_ids))))
    if filters.parent_chunk_ids is not None:
        must.append(
            FieldCondition(key="parent_chunk_id", match=MatchAny(any=list(filters.parent_chunk_ids)))
        )
    if filters.embedding_models is not None:
        must.append(FieldCondition(key="model", match=MatchAny(any=list(filters.embedding_models))))
    if filters.embedding_providers is not None:
        must.append(
            FieldCondition(key="provider", match=MatchAny(any=list(filters.embedding_providers)))
        )
    if filters.document_content_hashes is not None:
        must.append(
            FieldCondition(
                key="document_content_hash",
                match=MatchAny(any=list(filters.document_content_hashes)),
            )
        )
    if filters.require_context_prefix is not None:
        must.append(
            FieldCondition(
                key="uses_context_prefix",
                match=MatchValue(value=filters.require_context_prefix),
            )
        )

    if not must:
        return None
    return Filter(must=must)
