"""Shared helpers for parser implementations."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from tracerag.core.exceptions import ParseError
from tracerag.models.document import DocumentBlock, DocumentMetadata, ParsedDocument
from tracerag.models.types import BlockId, ParserName, SourceKind
from tracerag.utils.hash_utils import sha256_hex
from tracerag.utils.text_utils import normalize_newlines


def read_source_text(path: Path, *, allow_empty: bool = False) -> str:
    """Read a source file as normalized UTF-8 text."""
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise ParseError("failed to read source file", path=str(path), cause=exc) from exc
    text = normalize_newlines(raw)
    if not allow_empty and not text.strip():
        raise ParseError("source file is empty", path=str(path))
    return text


def source_modified_at(path: Path) -> datetime | None:
    """Return filesystem modification time in UTC, if available."""
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    except OSError:
        return None


def line_count_for(text: str) -> int:
    """Return a 1-based line count for non-empty text."""
    if not text:
        return 0
    return text.count("\n") + 1


def make_block_id(parser_name: ParserName, index: int) -> BlockId:
    """Build a stable block identifier within a parsed document."""
    return f"{parser_name}:{index:04d}"


def build_document_metadata(
    path: Path,
    *,
    workspace_root: Path | None,
    parser_name: ParserName,
    content: str,
    language: str | None = None,
    source_kind: SourceKind | None = None,
) -> DocumentMetadata:
    """Construct provenance metadata for a parsed source artifact."""
    try:
        stat = path.stat()
        file_size = stat.st_size
    except OSError as exc:
        raise ParseError("failed to read file metadata", path=str(path), cause=exc) from exc

    return DocumentMetadata.from_path(
        path,
        workspace_root=workspace_root,
        parser_name=parser_name,
        source_kind=source_kind,
        file_size_bytes=file_size,
        content_hash=sha256_hex(content),
        language=language,
        line_count=line_count_for(content),
        source_modified_at=source_modified_at(path),
    )


def build_parsed_document(
    path: Path,
    *,
    workspace_root: Path | None,
    parser_name: ParserName,
    content: str,
    blocks: list[DocumentBlock],
    language: str | None = None,
    source_kind: SourceKind | None = None,
) -> ParsedDocument:
    """Assemble a ``ParsedDocument`` with metadata and optional structural blocks."""
    metadata = build_document_metadata(
        path,
        workspace_root=workspace_root,
        parser_name=parser_name,
        content=content,
        language=language,
        source_kind=source_kind,
    )
    return ParsedDocument(metadata=metadata, content=content, blocks=tuple(blocks))
