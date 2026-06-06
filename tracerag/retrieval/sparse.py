"""Sparse retrieval boundary for lexical candidate selection over indexed terms."""

from __future__ import annotations

from tracerag.models.retrieval import RetrievalCandidate, RetrievalQuery, RetrievalResult, RetrievalSource
from tracerag.retrieval.config import RetrievalConfig
from tracerag.retrieval.contracts import SparseRetrievalProvider
from tracerag.retrieval.filters import apply_retrieval_filters, corpus_document_matches_filter
from tracerag.retrieval.sparse_index import SparseCorpusIndex


class BM25SparseRetriever(SparseRetrievalProvider):
    """Sparse retriever backed by an in-memory BM25 corpus index."""

    def __init__(self, index: SparseCorpusIndex | None = None) -> None:
        self._index = index or SparseCorpusIndex()

    @property
    def index(self) -> SparseCorpusIndex:
        return self._index

    def retrieve(
        self,
        query: RetrievalQuery,
        *,
        config: RetrievalConfig | None = None,
    ) -> RetrievalResult:
        policy = config or RetrievalConfig.default()
        top_k = query.top_k or policy.sparse_top_k

        if self._index.size == 0:
            return RetrievalResult(query=query, source=RetrievalSource.SPARSE, candidates=())

        oversample = top_k * 3 if query.filters and not query.filters.is_empty() else top_k
        hits = self._index.search(query.text, top_k=oversample)

        candidates: list[RetrievalCandidate] = []
        for document, score in hits:
            if query.filters and not query.filters.is_empty():
                if not corpus_document_matches_filter(document, query.filters):
                    continue
            candidates.append(
                RetrievalCandidate(
                    chunk_id=document.chunk_id,
                    rank=len(candidates) + 1,
                    score=score,
                    source=RetrievalSource.SPARSE,
                    snippet=document.text[:500] if len(document.text) > 500 else document.text,
                    sparse_score=score,
                )
            )
            if len(candidates) >= top_k:
                break

        filtered = apply_retrieval_filters(candidates, query.filters)
        return RetrievalResult(
            query=query,
            source=RetrievalSource.SPARSE,
            candidates=tuple(filtered),
        )
