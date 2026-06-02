"""Contextual retrieval models extending parent-child chunks for prefix-augmented indexing."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from tracerag.models.chunk import ChildChunk, ChunkMetadata, ParentChunk
from tracerag.models.document import DocumentMetadata
from tracerag.models.types import ChildChunkId, ContextSource, ParentChunkId


class ContextualChunkMetadata(ChunkMetadata):
    """Chunk metadata extended with contextual enrichment provenance."""

    context_source: ContextSource = ContextSource.NONE
    context_attached_at: datetime | None = None
    document_context_excerpt: str | None = None
    parent_context_excerpt: str | None = None

    @field_validator("context_attached_at", mode="after")
    @classmethod
    def _ensure_utc(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


class ContextValidationResult(BaseModel):
    """Outcome of validating a contextual prefix before attachment or indexing."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    is_valid: bool
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _errors_inconsistent_with_valid_flag(self) -> ContextValidationResult:
        if self.is_valid and self.errors:
            msg = "is_valid cannot be true when errors are present"
            raise ValueError(msg)
        if not self.is_valid and not self.errors:
            msg = "is_valid=false requires at least one error"
            raise ValueError(msg)
        return self


class ContextualChunk(BaseModel):
    """Child retrieval chunk with original content preserved and context stored separately."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    chunk_id: ChildChunkId
    parent_chunk_id: ParentChunkId
    content: str
    context_prefix: str | None = None
    metadata: ContextualChunkMetadata

    @field_validator("content")
    @classmethod
    def _content_not_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "chunk content must not be empty or whitespace-only"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def _align_metadata(self) -> ContextualChunk:
        if self.metadata.chunk_id != self.chunk_id:
            msg = "metadata.chunk_id must match ContextualChunk.chunk_id"
            raise ValueError(msg)
        if self.metadata.parent_chunk_id != self.parent_chunk_id:
            msg = "metadata.parent_chunk_id must match ContextualChunk.parent_chunk_id"
            raise ValueError(msg)
        if self.metadata.context_prefix != self.context_prefix:
            msg = "metadata.context_prefix must match ContextualChunk.context_prefix"
            raise ValueError(msg)
        return self

    @classmethod
    def from_child(
        cls,
        child: ChildChunk,
        *,
        context_prefix: str | None,
        context_source: ContextSource,
        document_context_excerpt: str | None = None,
        parent_context_excerpt: str | None = None,
        context_attached_at: datetime | None = None,
    ) -> ContextualChunk:
        """Build a contextual chunk from a child chunk without modifying ``child.content``."""
        attached_at = context_attached_at or datetime.now(timezone.utc)
        base_fields = child.metadata.model_dump(
            exclude={"context_prefix", "context_source", "context_attached_at"}
        )
        metadata = ContextualChunkMetadata(
            **base_fields,
            context_prefix=context_prefix,
            context_source=context_source,
            context_attached_at=attached_at if context_prefix else None,
            document_context_excerpt=document_context_excerpt,
            parent_context_excerpt=parent_context_excerpt,
        )
        return cls(
            chunk_id=child.chunk_id,
            parent_chunk_id=child.parent_chunk_id,
            content=child.content,
            context_prefix=context_prefix,
            metadata=metadata,
        )


class ContextualChunkSet(BaseModel):
    """Parent-child chunk hierarchy with contextual prefixes attached to child units."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    source: DocumentMetadata
    parents: tuple[ParentChunk, ...]
    children: tuple[ContextualChunk, ...]

    @model_validator(mode="after")
    def _validate_parent_child_links(self) -> ContextualChunkSet:
        parent_ids = {parent.chunk_id for parent in self.parents}
        for child in self.children:
            if child.parent_chunk_id not in parent_ids:
                msg = (
                    f"contextual child {child.chunk_id!r} references unknown parent "
                    f"{child.parent_chunk_id!r}"
                )
                raise ValueError(msg)
        return self

    def contextual_children_for_parent(
        self,
        parent_chunk_id: ParentChunkId,
    ) -> tuple[ContextualChunk, ...]:
        """Return contextual children for ``parent_chunk_id``."""
        return tuple(child for child in self.children if child.parent_chunk_id == parent_chunk_id)
