"""Retrieval provider interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod

from tracerag.models.retrieval import RetrievalQuery, RetrievalResult
from tracerag.retrieval.config import RetrievalConfig


class DenseRetrievalProvider(ABC):
    """Contract for embedding-based nearest-neighbor retrieval."""

    @abstractmethod
    def retrieve(
        self,
        query: RetrievalQuery,
        *,
        config: RetrievalConfig | None = None,
    ) -> RetrievalResult:
        """Return dense vector similarity candidates."""


class SparseRetrievalProvider(ABC):
    """Contract for lexical (BM25) retrieval."""

    @abstractmethod
    def retrieve(
        self,
        query: RetrievalQuery,
        *,
        config: RetrievalConfig | None = None,
    ) -> RetrievalResult:
        """Return sparse lexical candidates."""
