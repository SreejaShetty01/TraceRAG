"""Metadata construction boundary for deterministic chunk provenance and traceability fields."""

from __future__ import annotations

from tracerag.models.chunk import ChunkMetadata
from tracerag.models.document import DocumentBlock, DocumentMetadata
from tracerag.models.types import ChildChunkId, ChunkId, ChunkLevel, ParentChunkId
from tracerag.utils.token_utils import estimate_token_count


def build_chunk_metadata(
    document: DocumentMetadata,
    *,
    chunk_id: ChunkId,
    chunk_level: ChunkLevel,
    chunk_index: int,
    content: str,
    parent_chunk_id: ParentChunkId | None = None,
    block: DocumentBlock | None = None,
    context_prefix: str | None = None,
) -> ChunkMetadata:
    """Derive immutable chunk metadata from document provenance and optional block linkage."""
    return ChunkMetadata(
        file_path=document.file_path,
        file_extension=document.file_extension,
        source_kind=document.source_kind,
        workspace_root=document.workspace_root,
        document_content_hash=document.content_hash,
        language=document.language,
        parser_name=document.parser_name,
        source_modified_at=document.source_modified_at,
        chunk_id=chunk_id,
        chunk_level=chunk_level,
        chunk_index=chunk_index,
        parent_chunk_id=parent_chunk_id,
        block_id=block.block_id if block is not None else None,
        line_start=block.line_start if block is not None else None,
        line_end=block.line_end if block is not None else None,
        page_number=block.page_number if block is not None else None,
        heading=block.heading if block is not None else None,
        token_count=estimate_token_count(content),
        context_prefix=context_prefix,
    )
