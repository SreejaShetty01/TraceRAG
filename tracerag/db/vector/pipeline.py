"""Vector upsert pipeline for validated embedding records."""

from __future__ import annotations

from tracerag.core.exceptions import VectorStorageError
from tracerag.db.vector.bootstrap import bootstrap_collection
from tracerag.db.vector.config import VectorStoreConfig
from tracerag.db.vector.contracts import VectorStore
from tracerag.db.vector.mapper import embedding_records_to_stored_vectors
from tracerag.db.vector.validation import (
    validate_batch_consistency,
    validate_stored_vector_record,
)
from tracerag.models.embedding import ChunkEmbeddingRecord, EmbeddingBatchResult
from tracerag.models.vector import VectorUpsertResult


class VectorUpsertPipeline:
    """Persist validated embedding records into the configured vector store."""

    def __init__(
        self,
        store: VectorStore | None = None,
        *,
        config: VectorStoreConfig | None = None,
    ) -> None:
        self._config = config or VectorStoreConfig.default()
        self._store = store
        if self._store is None:
            from tracerag.db.vector.bootstrap import create_vector_store

            self._store = create_vector_store(self._config)

    @property
    def config(self) -> VectorStoreConfig:
        return self._config

    @property
    def store(self) -> VectorStore:
        return self._store

    def upsert_records(self, records: list[ChunkEmbeddingRecord]) -> VectorUpsertResult:
        """Validate and upsert embedding records."""
        if self._config.bootstrap_on_upsert:
            bootstrap_collection(self._store, config=self._config)

        collection = self._config.qdrant.collection
        if self._config.validate_before_upsert:
            batch_validation = validate_batch_consistency(records, collection=collection)
            if not batch_validation.is_valid:
                joined = "; ".join(batch_validation.errors)
                raise VectorStorageError(f"batch validation failed: {joined}")

        stored_records = embedding_records_to_stored_vectors(records)
        if self._config.validate_before_upsert:
            for stored in stored_records:
                item_validation = validate_stored_vector_record(stored, collection=collection)
                if not item_validation.is_valid:
                    joined = "; ".join(item_validation.errors)
                    raise VectorStorageError(
                        f"stored record validation failed for {stored.chunk_id!r}: {joined}"
                    )

        return self._store.upsert(stored_records)

    def upsert_batch_result(self, batch: EmbeddingBatchResult) -> VectorUpsertResult:
        """Upsert records from an embedding batch result."""
        return self.upsert_records(list(batch.records))
