"""Shared typing definitions for TraceRAG domain models and ingestion contracts."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import TypeAlias

# ---------------------------------------------------------------------------
# Scalar aliases
# ---------------------------------------------------------------------------

FileExtension: TypeAlias = str
"""Normalized file extension including leading dot (e.g. ``".py"``)."""

ParserName: TypeAlias = str
"""Stable identifier for a registered parser implementation."""

ContentHash: TypeAlias = str
"""Hex-encoded digest of normalized document content."""

BlockId: TypeAlias = str
"""Stable identifier for a structural block within a parsed document."""

ChunkNamespace: TypeAlias = str
"""Stable namespace grouping all chunks from one source document."""

ChunkId: TypeAlias = str
"""Unique identifier for a parent or child retrieval chunk."""

ParentChunkId: TypeAlias = str
"""Identifier for a parent synthesis chunk."""

ChildChunkId: TypeAlias = str
"""Identifier for a child retrieval chunk."""

EmbeddingProviderName: TypeAlias = str
"""Identifier for an embedding provider implementation."""

EmbeddingModelName: TypeAlias = str
"""Name of an embedding model served by a provider."""

EmbeddingVector: TypeAlias = tuple[float, ...]
"""Dense embedding vector returned by an embedding provider."""

VectorPointId: TypeAlias = str
"""Stable identifier for a vector point in the vector database."""

CollectionName: TypeAlias = str
"""Name of a vector store collection."""

WorkspacePath: TypeAlias = Path
"""Root directory of an indexed workspace."""

AbsolutePath: TypeAlias = Path
"""Resolved absolute path to a source artifact."""

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class SourceKind(str, Enum):
    """High-level classification of an ingested artifact."""

    CODE = "code"
    SQL = "sql"
    CONFIG = "config"
    MARKDOWN = "markdown"
    PDF = "pdf"
    PRESENTATION = "presentation"
    IMAGE = "image"
    UNKNOWN = "unknown"


class ChunkLevel(str, Enum):
    """Retrieval tier of a generated chunk."""

    PARENT = "parent"
    CHILD = "child"


class ContextSource(str, Enum):
    """Origin of a contextual prefix attached to a child chunk."""

    NONE = "none"
    DOCUMENT = "document"
    PARENT = "parent"
    DOCUMENT_AND_PARENT = "document_and_parent"
    MANUAL = "manual"
    GENERATED = "generated"
    """Reserved for future LLM-generated summaries."""


class BlockType(str, Enum):
    """Structural role of a segment within a parsed document."""

    ROOT = "root"
    SECTION = "section"
    PARAGRAPH = "paragraph"
    CODE_UNIT = "code_unit"
    DDL = "ddl"
    TABLE = "table"
    SLIDE = "slide"
    CONFIG_KEY = "config_key"
    IMAGE_REGION = "image_region"
    UNKNOWN = "unknown"


class DiscoveryStatus(str, Enum):
    """Classification of a discovered file relative to the active ingestion phase."""

    READY = "ready"
    """Supported extension with a registered parser available for ingestion."""

    PENDING_PARSER = "pending_parser"
    """Supported for the active phase; parser implementation not yet registered."""

    DEFERRED = "deferred"
    """Recognized extension deferred to a later ingestion phase (e.g. SQL, PDF)."""

    SKIPPED = "skipped"
    """Excluded by discovery filter rules (directory, size, hidden, etc.)."""

    UNSUPPORTED = "unsupported"
    """File extension outside the TraceRAG supported vocabulary."""


# ---------------------------------------------------------------------------
# Extension vocabulary
# ---------------------------------------------------------------------------

SUPPORTED_EXTENSIONS: frozenset[FileExtension] = frozenset(
    {
        ".py",
        ".java",
        ".js",
        ".ts",
        ".sh",
        ".r",
        ".sql",
        ".json",
        ".yaml",
        ".yml",
        ".ini",
        ".pdf",
        ".pptx",
        ".md",
        ".png",
        ".jpg",
        ".jpeg",
    }
)

# Phase 2: discover and prepare for ingestion (no SQL/PDF/PPTX/image parsers yet).
DISCOVERABLE_EXTENSIONS: frozenset[FileExtension] = frozenset(
    {
        ".py",
        ".java",
        ".js",
        ".ts",
        ".sh",
        ".r",
        ".sql",
        ".json",
        ".yaml",
        ".yml",
        ".ini",
        ".md",
    }
)

DEFERRED_EXTENSIONS: frozenset[FileExtension] = frozenset(
    {
        ".pdf",
        ".pptx",
        ".png",
        ".jpg",
        ".jpeg",
    }
)

EXTENSION_TO_SOURCE_KIND: dict[FileExtension, SourceKind] = {
    ".py": SourceKind.CODE,
    ".java": SourceKind.CODE,
    ".js": SourceKind.CODE,
    ".ts": SourceKind.CODE,
    ".sh": SourceKind.CODE,
    ".r": SourceKind.CODE,
    ".sql": SourceKind.SQL,
    ".json": SourceKind.CONFIG,
    ".yaml": SourceKind.CONFIG,
    ".yml": SourceKind.CONFIG,
    ".ini": SourceKind.CONFIG,
    ".pdf": SourceKind.PDF,
    ".pptx": SourceKind.PRESENTATION,
    ".md": SourceKind.MARKDOWN,
    ".png": SourceKind.IMAGE,
    ".jpg": SourceKind.IMAGE,
    ".jpeg": SourceKind.IMAGE,
}


def normalize_extension(extension: str) -> FileExtension:
    """Return a lowercase extension with a leading dot."""
    value = extension.lower()
    if not value.startswith("."):
        value = f".{value}"
    return value


def source_kind_for_extension(extension: FileExtension) -> SourceKind:
    """Map a normalized extension to its default source kind."""
    return EXTENSION_TO_SOURCE_KIND.get(extension, SourceKind.UNKNOWN)


def is_supported_extension(extension: str) -> bool:
    """Return whether ``extension`` is in the TraceRAG supported vocabulary."""
    return normalize_extension(extension) in SUPPORTED_EXTENSIONS


def is_discoverable_extension(extension: str) -> bool:
    """Return whether ``extension`` is targeted by the active discovery phase."""
    return normalize_extension(extension) in DISCOVERABLE_EXTENSIONS


def is_deferred_extension(extension: str) -> bool:
    """Return whether ``extension`` is deferred to a later ingestion phase."""
    return normalize_extension(extension) in DEFERRED_EXTENSIONS
