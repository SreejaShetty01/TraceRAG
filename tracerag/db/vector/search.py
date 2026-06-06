"""Vector search boundary for dense similarity retrieval query execution."""

from __future__ import annotations

from tracerag.db.vector.qdrant_provider import QdrantVectorStore
from tracerag.models.vector import VectorSearchHit
from tracerag.retrieval.qdrant_filters import build_qdrant_filter
from tracerag.models.retrieval import RetrievalFilter

__all__ = [
    "QdrantVectorStore",
    "VectorSearchHit",
    "build_qdrant_filter",
    "search_vectors",
]


def search_vectors(
    store: QdrantVectorStore,
    query_vector: list[float],
    *,
    limit: int,
    filters: RetrievalFilter | None = None,
) -> list[VectorSearchHit]:
    """Search a Qdrant collection with optional metadata filters."""
    return store.search(
        query_vector,
        limit=limit,
        query_filter=build_qdrant_filter(filters),
    )
