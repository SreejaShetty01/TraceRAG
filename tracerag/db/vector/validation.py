"""Vector storage validation and batch consistency checks."""

from __future__ import annotations

from tracerag.db.vector.config import CollectionConfig
from tracerag.models.embedding import ChunkEmbeddingRecord
from tracerag.models.vector import StoredVectorRecord, VectorStorageValidationResult


def validate_embedding_record_for_storage(
    record: ChunkEmbeddingRecord,
    *,
    collection: CollectionConfig,
) -> VectorStorageValidationResult:
    """Validate one embedding record against collection constraints."""
    errors: list[str] = []
    warnings: list[str] = []

    if not record.validation.is_valid:
        errors.append("embedding record failed upstream validation")

    if len(record.vector) != collection.vector_size:
        errors.append(
            f"vector dimension {len(record.vector)} does not match collection size "
            f"{collection.vector_size}"
        )

    if record.metadata.dimension != collection.vector_size:
        errors.append("metadata.dimension does not match collection vector_size")

    return VectorStorageValidationResult(
        is_valid=not errors,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


def validate_stored_vector_record(
    record: StoredVectorRecord,
    *,
    collection: CollectionConfig,
) -> VectorStorageValidationResult:
    """Validate a prepared stored vector record."""
    errors: list[str] = []
    warnings: list[str] = []

    if len(record.vector) != collection.vector_size:
        errors.append(
            f"vector dimension {len(record.vector)} does not match collection size "
            f"{collection.vector_size}"
        )

    if record.payload.dimension != collection.vector_size:
        errors.append("payload.dimension does not match collection vector_size")

    return VectorStorageValidationResult(
        is_valid=not errors,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


def validate_batch_consistency(
    records: list[ChunkEmbeddingRecord],
    *,
    collection: CollectionConfig,
) -> VectorStorageValidationResult:
    """Validate an embedding batch for storage consistency."""
    errors: list[str] = []
    warnings: list[str] = []

    if not records:
        errors.append("batch contains no embedding records")
        return VectorStorageValidationResult(is_valid=False, errors=tuple(errors))

    chunk_ids: set[str] = set()
    models: set[str] = set()
    dimensions: set[int] = set()

    for record in records:
        item_validation = validate_embedding_record_for_storage(record, collection=collection)
        if not item_validation.is_valid:
            errors.extend(item_validation.errors)
        warnings.extend(item_validation.warnings)

        if record.chunk_id in chunk_ids:
            errors.append(f"duplicate chunk_id in batch: {record.chunk_id!r}")
        chunk_ids.add(record.chunk_id)
        models.add(record.metadata.model)
        dimensions.add(len(record.vector))

    if len(models) > 1:
        warnings.append(f"batch mixes embedding models: {sorted(models)}")

    if len(dimensions) > 1:
        errors.append(f"batch mixes vector dimensions: {sorted(dimensions)}")

    return VectorStorageValidationResult(
        is_valid=not errors,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )
