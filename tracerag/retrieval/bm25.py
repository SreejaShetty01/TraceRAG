"""Okapi BM25 lexical scoring implementation."""

from __future__ import annotations

import math
import re
from collections import Counter

_TOKEN_PATTERN = re.compile(r"[a-z0-9_]+")


def tokenize(text: str) -> list[str]:
    """Lowercase alphanumeric tokenization suitable for code and prose."""
    return _TOKEN_PATTERN.findall(text.lower())


class BM25Index:
    """In-memory Okapi BM25 index over a tokenized corpus."""

    def __init__(
        self,
        *,
        k1: float = 1.5,
        b: float = 0.75,
    ) -> None:
        self._k1 = k1
        self._b = b
        self._documents: list[list[str]] = []
        self._doc_freqs: Counter[str] = Counter()
        self._avg_doc_len = 0.0

    @property
    def document_count(self) -> int:
        return len(self._documents)

    def add_document(self, text: str) -> int:
        """Add a document and return its index."""
        tokens = tokenize(text)
        self._documents.append(tokens)
        unique = set(tokens)
        self._doc_freqs.update(unique)
        total_len = sum(len(doc) for doc in self._documents)
        self._avg_doc_len = total_len / len(self._documents) if self._documents else 0.0
        return len(self._documents) - 1

    def clear(self) -> None:
        self._documents.clear()
        self._doc_freqs.clear()
        self._avg_doc_len = 0.0

    def score_query(self, query: str) -> list[float]:
        """Return BM25 scores for all indexed documents."""
        if not self._documents:
            return []

        query_terms = tokenize(query)
        if not query_terms:
            return [0.0] * len(self._documents)

        n_docs = len(self._documents)
        scores = [0.0] * n_docs

        for term in query_terms:
            df = self._doc_freqs.get(term, 0)
            if df == 0:
                continue
            idf = math.log(1.0 + (n_docs - df + 0.5) / (df + 0.5))
            for doc_index, doc_tokens in enumerate(self._documents):
                term_freq = doc_tokens.count(term)
                if term_freq == 0:
                    continue
                doc_len = len(doc_tokens)
                denom = term_freq + self._k1 * (
                    1.0 - self._b + self._b * (doc_len / self._avg_doc_len if self._avg_doc_len else 0.0)
                )
                scores[doc_index] += idf * (term_freq * (self._k1 + 1.0)) / denom

        return scores
