"""Context prefix assembly boundary for chunk context and content envelopes."""

from __future__ import annotations

from tracerag.ingestion.context.config import ContextEnrichmentConfig
from tracerag.models.context import ContextualChunk


def build_prefixed_envelope(
    contextual_chunk: ContextualChunk,
    *,
    config: ContextEnrichmentConfig | None = None,
) -> str:
    """Compose a labeled envelope for future embedding without mutating stored content.

    Format::

        [CONTEXT]: <context prefix>
        [CONTENT]: <original child content>
    """
    policy = config or ContextEnrichmentConfig.default()
    prefix = (contextual_chunk.context_prefix or "").strip()
    content = contextual_chunk.content

    if not prefix:
        return content

    return (
        f"[{policy.context_label}]: {prefix}\n"
        f"[{policy.content_label}]: {content}"
    )
