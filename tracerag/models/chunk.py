"""Schema contracts for chunk payloads and immutable chunk metadata fields."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from tracerag.models.document import DocumentMetadata
from tracerag.models.types import (
    BlockId,
    ChildChunkId,
    ChunkId,
    ChunkLevel,
    ContentHash,
    FileExtension,
    ParentChunkId,
    ParserName,
    SourceKind,
)


class ChunkMetadata(BaseModel):
    """Immutable provenance for a parent or child chunk, derived from source document metadata."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid", arbitrary_types_allowed=True)

    # Source document provenance
    file_path: Path
    file_extension: FileExtension
    source_kind: SourceKind
    workspace_root: Path | None = None
    document_content_hash: ContentHash | None = None
    language: str | None = None
    parser_name: ParserName | None = None
    source_modified_at: datetime | None = None

    # Chunk identity and hierarchy
    chunk_id: ChunkId
    chunk_level: ChunkLevel
    chunk_index: int = Field(ge=0)
    parent_chunk_id: ParentChunkId | None = None

    # Structural linkage (parser block, when applicable)
    block_id: BlockId | None = None
    line_start: int | None = Field(default=None, ge=1)
    line_end: int | None = Field(default=None, ge=1)
    page_number: int | None = Field(default=None, ge=1)
    heading: str | None = None

    # Sizing and lifecycle
    token_count: int = Field(ge=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Populated by contextual enrichment; mirrored on ContextualChunkMetadata
    context_prefix: str | None = None

    @field_validator("file_path", "workspace_root", mode="before")
    @classmethod
    def _coerce_path(cls, value: object) -> Path | None:
        if value is None:
            return None
        if isinstance(value, Path):
            return value
        if isinstance(value, str):
            return Path(value)
        msg = "path fields must be str or Path"
        raise TypeError(msg)

    @field_validator("file_path", mode="after")
    @classmethod
    def _resolve_file_path(cls, value: Path) -> Path:
        return value.expanduser().resolve()

    @field_validator("workspace_root", mode="after")
    @classmethod
    def _resolve_workspace_root(cls, value: Path | None) -> Path | None:
        if value is None:
            return None
        return value.expanduser().resolve()

    @field_validator("created_at", "source_modified_at", mode="after")
    @classmethod
    def _ensure_utc(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @model_validator(mode="after")
    def _validate_hierarchy(self) -> ChunkMetadata:
        if self.chunk_level == ChunkLevel.CHILD and self.parent_chunk_id is None:
            msg = "parent_chunk_id is required for child chunks"
            raise ValueError(msg)
        if self.chunk_level == ChunkLevel.PARENT and self.parent_chunk_id is not None:
            msg = "parent_chunk_id must be null for parent chunks"
            raise ValueError(msg)
        if self.line_start is not None and self.line_end is not None and self.line_end < self.line_start:
            msg = "line_end must be greater than or equal to line_start"
            raise ValueError(msg)
        return self


class Chunk(BaseModel):
    """Common chunk payload for parent and child retrieval units."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    chunk_id: ChunkId
    content: str
    metadata: ChunkMetadata

    @field_validator("content")
    @classmethod
    def _content_not_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "chunk content must not be empty or whitespace-only"
            raise ValueError(msg)
        return value


class ParentChunk(Chunk):
    """Synthesis-oriented parent chunk referencing child retrieval units."""

    child_chunk_ids: tuple[ChildChunkId, ...] = ()

    @model_validator(mode="after")
    def _validate_parent_level(self) -> ParentChunk:
        if self.metadata.chunk_level != ChunkLevel.PARENT:
            msg = "ParentChunk metadata.chunk_level must be PARENT"
            raise ValueError(msg)
        if self.metadata.parent_chunk_id is not None:
            msg = "ParentChunk must not set metadata.parent_chunk_id"
            raise ValueError(msg)
        return self


class ChildChunk(Chunk):
    """Retrieval-oriented child chunk linked to a parent synthesis chunk."""

    parent_chunk_id: ParentChunkId

    @model_validator(mode="after")
    def _validate_child_level(self) -> ChildChunk:
        if self.metadata.chunk_level != ChunkLevel.CHILD:
            msg = "ChildChunk metadata.chunk_level must be CHILD"
            raise ValueError(msg)
        if self.metadata.parent_chunk_id != self.parent_chunk_id:
            msg = "ChildChunk.parent_chunk_id must match metadata.parent_chunk_id"
            raise ValueError(msg)
        if self.metadata.chunk_id != self.chunk_id:
            msg = "ChildChunk.chunk_id must match metadata.chunk_id"
            raise ValueError(msg)
        return self


class ParentChildChunkSet(BaseModel):
    """Hierarchical chunk output for one parsed document."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    source: DocumentMetadata
    parents: tuple[ParentChunk, ...]
    children: tuple[ChildChunk, ...]

    @model_validator(mode="after")
    def _validate_relationships(self) -> ParentChildChunkSet:
        parent_ids = {parent.chunk_id for parent in self.parents}
        child_ids: set[str] = set()

        for parent in self.parents:
            for child_id in parent.child_chunk_ids:
                if child_id not in {child.chunk_id for child in self.children}:
                    msg = f"parent {parent.chunk_id!r} references unknown child {child_id!r}"
                    raise ValueError(msg)

        for child in self.children:
            if child.parent_chunk_id not in parent_ids:
                msg = f"child {child.chunk_id!r} references unknown parent {child.parent_chunk_id!r}"
                raise ValueError(msg)
            if child.chunk_id in child_ids:
                msg = f"duplicate child chunk id {child.chunk_id!r}"
                raise ValueError(msg)
            child_ids.add(child.chunk_id)

        return self

    def children_for_parent(self, parent_chunk_id: ParentChunkId) -> tuple[ChildChunk, ...]:
        """Return child chunks belonging to ``parent_chunk_id``."""
        return tuple(child for child in self.children if child.parent_chunk_id == parent_chunk_id)

    def parent_for_child(self, child_chunk_id: ChildChunkId) -> ParentChunk | None:
        """Return the parent chunk for ``child_chunk_id``, if present."""
        child = next((item for item in self.children if item.chunk_id == child_chunk_id), None)
        if child is None:
            return None
        return next((item for item in self.parents if item.chunk_id == child.parent_chunk_id), None)
