"""Vector indexing boundary for chunk persistence and embedding upsert operations."""

from __future__ import annotations

from tracerag.db.vector.config import VectorStoreConfig
from tracerag.db.vector.pipeline import VectorUpsertPipeline
from tracerag.models.embedding import ChunkEmbeddingRecord, EmbeddingBatchResult
from tracerag.models.vector import VectorUpsertResult


def create_upsert_pipeline(config: VectorStoreConfig | None = None) -> VectorUpsertPipeline:
    """Create a vector upsert pipeline with the default Qdrant store."""
    return VectorUpsertPipeline(config=config)


def upsert_embedding_records(
    records: list[ChunkEmbeddingRecord],
    *,
    config: VectorStoreConfig | None = None,
) -> VectorUpsertResult:
    """Validate and upsert embedding records into vector storage."""
    return create_upsert_pipeline(config).upsert_records(records)


def upsert_embedding_batch(
    batch: EmbeddingBatchResult,
    *,
    config: VectorStoreConfig | None = None,
) -> VectorUpsertResult:
    """Validate and upsert records from an embedding batch result."""
    return create_upsert_pipeline(config).upsert_batch_result(batch)
