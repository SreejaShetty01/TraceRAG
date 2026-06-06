"""Retrieval orchestration boundary for dense, sparse, fusion, and reranking stages."""

from __future__ import annotations

from tracerag.models.retrieval import (
    HybridRetrievalResult,
    RetrievalCandidate,
    RetrievalQuery,
    RetrievalResult,
    RetrievalSource,
)
from tracerag.retrieval.config import RetrievalConfig
from tracerag.retrieval.contracts import DenseRetrievalProvider, SparseRetrievalProvider
from tracerag.retrieval.fusion import fuse_retrieval_results
from tracerag.retrieval.reranker import CrossEncoderReranker


class HybridRetrievalPipeline:
    """Execute dense + sparse retrieval, RRF fusion, and optional reranking."""

    def __init__(
        self,
        dense: DenseRetrievalProvider,
        sparse: SparseRetrievalProvider,
        *,
        config: RetrievalConfig | None = None,
        reranker: CrossEncoderReranker | None = None,
    ) -> None:
        self._dense = dense
        self._sparse = sparse
        self._config = config or RetrievalConfig.default()
        self._reranker = reranker

    @property
    def config(self) -> RetrievalConfig:
        return self._config

    @property
    def dense(self) -> DenseRetrievalProvider:
        return self._dense

    @property
    def sparse(self) -> SparseRetrievalProvider:
        return self._sparse

    @property
    def reranker(self) -> CrossEncoderReranker | None:
        return self._reranker

    def retrieve(self, query: RetrievalQuery) -> HybridRetrievalResult:
        """Run hybrid retrieval for a natural-language query."""
        dense_result = self._dense.retrieve(query, config=self._config)
        sparse_result = self._sparse.retrieve(query, config=self._config)
        fused_result = fuse_retrieval_results(dense_result, sparse_result, config=self._config)

        reranked: RetrievalResult | None = None
        if self._config.rerank_enabled and self._reranker is not None:
            reranked_candidates = self._reranker.rerank(
                query,
                list(fused_result.candidates),
                config=self._config,
            )
            reranked = RetrievalResult(
                query=query,
                source=RetrievalSource.RERANKED,
                candidates=tuple(reranked_candidates),
            )

        return HybridRetrievalResult(
            query=query,
            dense=dense_result,
            sparse=sparse_result,
            fused=fused_result,
            reranked=reranked,
        )

    def retrieve_dense_only(self, query: RetrievalQuery) -> RetrievalResult:
        """Run dense retrieval independently."""
        return self._dense.retrieve(query, config=self._config)

    def retrieve_sparse_only(self, query: RetrievalQuery) -> RetrievalResult:
        """Run sparse retrieval independently."""
        return self._sparse.retrieve(query, config=self._config)
