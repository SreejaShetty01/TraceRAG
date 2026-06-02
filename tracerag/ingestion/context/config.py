"""Configuration for contextual enrichment of child retrieval chunks."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ContextEnrichmentConfig(BaseModel):
    """Policy for attaching deterministic contextual prefixes to child chunks."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    enabled: bool = True
    attach_document_context: bool = True
    attach_parent_context: bool = True
    require_context_prefix: bool = False
    max_prefix_tokens: int = Field(default=120, ge=1)
    parent_excerpt_chars: int = Field(default=240, ge=32)
    context_label: str = Field(default="CONTEXT", min_length=1)
    content_label: str = Field(default="CONTENT", min_length=1)

    @model_validator(mode="after")
    def _validate_attachment_flags(self) -> ContextEnrichmentConfig:
        if self.enabled and self.require_context_prefix:
            if not (self.attach_document_context or self.attach_parent_context):
                msg = "require_context_prefix needs at least one attachment source enabled"
                raise ValueError(msg)
        return self

    @classmethod
    def default(cls) -> ContextEnrichmentConfig:
        """Return the default contextual enrichment policy."""
        return cls()
