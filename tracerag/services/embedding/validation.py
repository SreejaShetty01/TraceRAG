"""Embedding vector validation helpers."""

from __future__ import annotations

import math

from tracerag.models.embedding import EmbeddingValidationResult
from tracerag.models.types import EmbeddingVector
from tracerag.services.embedding.config import EmbeddingConfig


def validate_embedding_vector(
    vector: EmbeddingVector,
    *,
    config: EmbeddingConfig,
) -> EmbeddingValidationResult:
    """Validate a dense embedding vector against policy constraints."""
    errors: list[str] = []
    warnings: list[str] = []

    if not vector:
        errors.append("embedding vector is empty")
        return EmbeddingValidationResult(is_valid=False, errors=tuple(errors))

    if len(vector) != config.expected_dimension:
        errors.append(
            f"vector dimension {len(vector)} does not match expected {config.expected_dimension}"
        )

    if any(not math.isfinite(value) for value in vector):
        errors.append("embedding vector contains non-finite values")

    magnitude = math.sqrt(sum(value * value for value in vector))
    if magnitude == 0.0:
        warnings.append("embedding vector has zero magnitude")

    return EmbeddingValidationResult(
        is_valid=not errors,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )
