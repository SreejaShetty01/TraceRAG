"""Deterministic chunk identifier generation."""

from __future__ import annotations

from tracerag.models.document import DocumentMetadata
from tracerag.models.types import ChildChunkId, ChunkNamespace, ParentChunkId
from tracerag.utils.hash_utils import sha256_hex


def chunk_namespace_for_document(metadata: DocumentMetadata) -> ChunkNamespace:
    """Build a stable namespace for all chunks originating from one document."""
    path_part = str(metadata.file_path.resolve())
    hash_part = metadata.content_hash or sha256_hex(path_part)
    return f"doc:{hash_part[:16]}:{metadata.file_path.name}"


def make_parent_chunk_id(namespace: ChunkNamespace, index: int) -> ParentChunkId:
    """Return a deterministic parent chunk identifier."""
    return f"{namespace}:p{index:04d}"


def make_child_chunk_id(parent_chunk_id: ParentChunkId, index: int) -> ChildChunkId:
    """Return a deterministic child chunk identifier bound to a parent."""
    return f"{parent_chunk_id}:c{index:04d}"
