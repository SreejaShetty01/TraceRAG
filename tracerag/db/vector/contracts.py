"""Vector store contracts for embedding persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod

from tracerag.db.vector.config import CollectionConfig
from tracerag.models.embedding import ChunkEmbeddingRecord
from tracerag.models.vector import StoredVectorRecord, VectorUpsertResult


class VectorStore(ABC):
    """Contract for persisting validated embedding records."""

    @property
    @abstractmethod
    def collection_name(self) -> str:
        """Active collection name."""

    @abstractmethod
    def collection_exists(self, collection_name: str | None = None) -> bool:
        """Return whether the target collection exists."""

    @abstractmethod
    def bootstrap_collection(self, config: CollectionConfig | None = None) -> None:
        """Ensure the target collection exists with the expected schema."""

    @abstractmethod
    def upsert(self, records: list[StoredVectorRecord]) -> VectorUpsertResult:
        """Upsert prepared vector records into storage."""

    def upsert_embedding_records(
        self,
        records: list[ChunkEmbeddingRecord],
    ) -> VectorUpsertResult:
        """Convert embedding records to stored vectors and upsert them."""
        from tracerag.db.vector.mapper import embedding_records_to_stored_vectors

        stored = embedding_records_to_stored_vectors(records)
        return self.upsert(stored)
