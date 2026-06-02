"""Schema contracts for parser outputs representing normalized source documents."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from tracerag.models.types import (
    BlockId,
    BlockType,
    ContentHash,
    FileExtension,
    ParserName,
    SourceKind,
    normalize_extension,
    source_kind_for_extension,
)

# ---------------------------------------------------------------------------
# Structural blocks (populated by parser implementations in later phases)
# ---------------------------------------------------------------------------


class DocumentBlock(BaseModel):
    """A structural segment within a parsed document."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    block_id: BlockId
    content: str
    block_type: BlockType = BlockType.UNKNOWN
    line_start: int | None = Field(default=None, ge=1)
    line_end: int | None = Field(default=None, ge=1)
    page_number: int | None = Field(default=None, ge=1)
    heading: str | None = None

    @model_validator(mode="after")
    def _validate_line_range(self) -> DocumentBlock:
        if self.line_start is not None and self.line_end is not None and self.line_end < self.line_start:
            msg = "line_end must be greater than or equal to line_start"
            raise ValueError(msg)
        return self


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------


class DocumentMetadata(BaseModel):
    """Immutable provenance and classification metadata for a source artifact."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid", arbitrary_types_allowed=True)

    file_path: Path
    file_extension: FileExtension
    source_kind: SourceKind
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    workspace_root: Path | None = None
    file_size_bytes: int | None = Field(default=None, ge=0)
    content_hash: ContentHash | None = None
    language: str | None = None
    line_count: int | None = Field(default=None, ge=0)
    page_count: int | None = Field(default=None, ge=1)
    source_modified_at: datetime | None = None
    parser_name: ParserName | None = None

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

    @field_validator("file_extension", mode="before")
    @classmethod
    def _normalize_file_extension(cls, value: str) -> FileExtension:
        return normalize_extension(value)

    @field_validator("ingested_at", "source_modified_at", mode="after")
    @classmethod
    def _ensure_utc(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @model_validator(mode="after")
    def _align_extension_with_path(self) -> DocumentMetadata:
        path_ext = normalize_extension(self.file_path.suffix)
        if self.file_extension != path_ext:
            msg = (
                f"file_extension {self.file_extension!r} does not match "
                f"path suffix {path_ext!r} for {self.file_path!r}"
            )
            raise ValueError(msg)
        return self

    @classmethod
    def from_path(
        cls,
        path: Path | str,
        *,
        workspace_root: Path | str | None = None,
        source_kind: SourceKind | None = None,
        parser_name: ParserName | None = None,
        file_size_bytes: int | None = None,
        content_hash: ContentHash | None = None,
        language: str | None = None,
        line_count: int | None = None,
        page_count: int | None = None,
        source_modified_at: datetime | None = None,
    ) -> DocumentMetadata:
        """Build metadata from a filesystem path without parsing content."""
        file_path = Path(path).expanduser().resolve()
        extension = normalize_extension(file_path.suffix)
        resolved_workspace = (
            Path(workspace_root).expanduser().resolve() if workspace_root is not None else None
        )
        return cls(
            file_path=file_path,
            file_extension=extension,
            source_kind=source_kind or source_kind_for_extension(extension),
            workspace_root=resolved_workspace,
            parser_name=parser_name,
            file_size_bytes=file_size_bytes,
            content_hash=content_hash,
            language=language,
            line_count=line_count,
            page_count=page_count,
            source_modified_at=source_modified_at,
        )


# ---------------------------------------------------------------------------
# Parser output
# ---------------------------------------------------------------------------


class ParsedDocument(BaseModel):
    """Normalized output produced by a parser prior to chunking."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    metadata: DocumentMetadata
    content: str
    blocks: tuple[DocumentBlock, ...] = ()

    @field_validator("content")
    @classmethod
    def _content_not_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "content must not be empty or whitespace-only"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def _parser_name_present_when_blocks_exist(self) -> ParsedDocument:
        if self.blocks and self.metadata.parser_name is None:
            msg = "metadata.parser_name is required when blocks are present"
            raise ValueError(msg)
        return self
