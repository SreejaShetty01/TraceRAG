"""Mapping between embedding records and vector store records."""

from __future__ import annotations

import uuid

from tracerag.models.embedding import ChunkEmbeddingRecord
from tracerag.models.types import VectorPointId
from tracerag.models.vector import StoredVectorRecord, VectorPointPayload


def point_id_for_chunk(chunk_id: str) -> VectorPointId:
    """Derive a deterministic Qdrant-compatible point id from a chunk id."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, chunk_id))


def embedding_record_to_stored_vector(record: ChunkEmbeddingRecord) -> StoredVectorRecord:
    """Map a validated embedding record to a storage-ready vector record."""
    payload = VectorPointPayload(
        chunk_id=record.metadata.chunk_id,
        parent_chunk_id=record.metadata.parent_chunk_id,
        provider=record.metadata.provider,
        model=record.metadata.model,
        dimension=record.metadata.dimension,
        embedded_at=record.metadata.embedded_at,
        input_text_hash=record.metadata.input_text_hash,
        document_content_hash=record.metadata.document_content_hash,
        uses_context_prefix=record.metadata.uses_context_prefix,
        uses_prefixed_envelope=record.metadata.uses_prefixed_envelope,
    )
    return StoredVectorRecord(
        point_id=point_id_for_chunk(record.chunk_id),
        chunk_id=record.chunk_id,
        vector=record.vector,
        payload=payload,
    )


def embedding_records_to_stored_vectors(
    records: list[ChunkEmbeddingRecord],
) -> list[StoredVectorRecord]:
    """Map multiple embedding records to storage-ready vector records."""
    return [embedding_record_to_stored_vector(record) for record in records]
