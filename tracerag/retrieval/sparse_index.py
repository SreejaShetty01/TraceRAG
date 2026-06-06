"""Sparse corpus index for BM25 retrieval."""

from __future__ import annotations

from tracerag.models.retrieval import SparseCorpusDocument
from tracerag.retrieval.bm25 import BM25Index


class SparseCorpusIndex:
    """Chunk-id-addressable BM25 corpus built from contextual retrieval text."""

    def __init__(self) -> None:
        self._bm25 = BM25Index()
        self._documents: list[SparseCorpusDocument] = []
        self._chunk_index: dict[str, int] = {}

    @property
    def size(self) -> int:
        return len(self._documents)

    def add(self, document: SparseCorpusDocument) -> None:
        """Index one corpus document."""
        if document.chunk_id in self._chunk_index:
            msg = f"chunk_id already indexed: {document.chunk_id!r}"
            raise ValueError(msg)
        doc_index = self._bm25.add_document(document.text)
        self._documents.append(document)
        self._chunk_index[document.chunk_id] = doc_index

    def add_many(self, documents: list[SparseCorpusDocument]) -> None:
        for document in documents:
            self.add(document)

    def clear(self) -> None:
        self._bm25.clear()
        self._documents.clear()
        self._chunk_index.clear()

    def get(self, chunk_id: str) -> SparseCorpusDocument | None:
        index = self._chunk_index.get(chunk_id)
        if index is None:
            return None
        return self._documents[index]

    def search(self, query: str, *, top_k: int) -> list[tuple[SparseCorpusDocument, float]]:
        """Return top-k documents with BM25 scores."""
        scores = self._bm25.score_query(query)
        if not scores:
            return []

        ranked = sorted(
            enumerate(scores),
            key=lambda item: item[1],
            reverse=True,
        )
        results: list[tuple[SparseCorpusDocument, float]] = []
        for doc_index, score in ranked:
            if score <= 0.0:
                continue
            if len(results) >= top_k:
                break
            results.append((self._documents[doc_index], score))
        return results
