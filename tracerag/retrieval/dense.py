"""Dense retrieval boundary for embedding-based nearest-neighbor candidate selection."""

from __future__ import annotations

from tracerag.core.exceptions import RetrievalError
from tracerag.db.vector.qdrant_provider import QdrantVectorStore
from tracerag.models.retrieval import RetrievalCandidate, RetrievalQuery, RetrievalResult, RetrievalSource
from tracerag.retrieval.config import RetrievalConfig
from tracerag.retrieval.contracts import DenseRetrievalProvider
from tracerag.retrieval.filters import apply_retrieval_filters
from tracerag.retrieval.qdrant_filters import build_qdrant_filter
from tracerag.services.embedding.contracts import EmbeddingProvider


class QdrantDenseRetriever(DenseRetrievalProvider):
    """Dense retriever using query embeddings and Qdrant vector search."""

    def __init__(
        self,
        store: QdrantVectorStore,
        embedder: EmbeddingProvider,
    ) -> None:
        self._store = store
        self._embedder = embedder

    @property
    def store(self) -> QdrantVectorStore:
        return self._store

    @property
    def embedder(self) -> EmbeddingProvider:
        return self._embedder

    def retrieve(
        self,
        query: RetrievalQuery,
        *,
        config: RetrievalConfig | None = None,
    ) -> RetrievalResult:
        policy = config or RetrievalConfig.default()
        top_k = query.top_k or policy.dense_top_k

        try:
            query_vector = list(self._embedder.embed(query.text))
        except Exception as exc:
            raise RetrievalError("failed to embed retrieval query", cause=exc) from exc

        qdrant_filter = build_qdrant_filter(query.filters)
        try:
            hits = self._store.search(query_vector, limit=top_k, query_filter=qdrant_filter)
        except Exception as exc:
            raise RetrievalError("dense vector search failed", cause=exc) from exc

        candidates: list[RetrievalCandidate] = []
        for rank, hit in enumerate(hits, start=1):
            candidates.append(
                RetrievalCandidate(
                    chunk_id=hit.chunk_id,
                    rank=rank,
                    score=hit.score,
                    source=RetrievalSource.DENSE,
                    point_id=hit.point_id,
                    payload=hit.payload,
                    dense_score=hit.score,
                )
            )

        filtered = apply_retrieval_filters(candidates, query.filters)
        return RetrievalResult(
            query=query,
            source=RetrievalSource.DENSE,
            candidates=tuple(filtered),
        )
