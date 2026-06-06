"""Reranking boundary for relevance refinement over preselected retrieval candidates."""

from __future__ import annotations

from abc import ABC, abstractmethod

from tracerag.models.retrieval import RetrievalCandidate, RetrievalQuery
from tracerag.retrieval.config import RetrievalConfig


class CrossEncoderReranker(ABC):
    """Contract for cross-encoder reranking over fused retrieval candidates.

    Implementations score query-passage pairs and return a reordered candidate list.
    No default implementation is provided in this phase.
    """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Reranker model identifier."""

    @abstractmethod
    def rerank(
        self,
        query: RetrievalQuery,
        candidates: list[RetrievalCandidate],
        *,
        config: RetrievalConfig | None = None,
    ) -> list[RetrievalCandidate]:
        """Return candidates reordered by cross-encoder relevance scores."""
