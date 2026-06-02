"""Validation helpers for contextual prefix attachment."""

from __future__ import annotations

from tracerag.ingestion.context.config import ContextEnrichmentConfig
from tracerag.models.context import ContextValidationResult
from tracerag.utils.token_utils import estimate_token_count


def validate_context_prefix(
    context_prefix: str | None,
    *,
    child_content: str,
    config: ContextEnrichmentConfig,
) -> ContextValidationResult:
    """Validate a contextual prefix against enrichment policy."""
    errors: list[str] = []
    warnings: list[str] = []

    if config.require_context_prefix and not (context_prefix and context_prefix.strip()):
        errors.append("context prefix is required but missing")

    if context_prefix is None or not context_prefix.strip():
        return ContextValidationResult(is_valid=not errors, errors=tuple(errors), warnings=tuple(warnings))

    normalized = context_prefix.strip()
    if normalized == child_content.strip():
        errors.append("context prefix must not duplicate child content")

    if child_content.strip() and child_content.strip() in normalized:
        warnings.append("context prefix contains child content substring")

    token_count = estimate_token_count(normalized)
    if token_count > config.max_prefix_tokens:
        errors.append(
            f"context prefix exceeds max_prefix_tokens ({token_count} > {config.max_prefix_tokens})"
        )

    return ContextValidationResult(
        is_valid=not errors,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )
