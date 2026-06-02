"""Chunking contracts and parent-child chunk generation."""

from tracerag.ingestion.chunkers.base import BaseChunker, StructuralChunker
from tracerag.ingestion.chunkers.config import ChunkingConfig
from tracerag.ingestion.chunkers.parent_child import ParentChildChunker
from tracerag.ingestion.chunkers.ids import (
    chunk_namespace_for_document,
    make_child_chunk_id,
    make_parent_chunk_id,
)

__all__ = [
    "BaseChunker",
    "ChunkingConfig",
    "ParentChildChunker",
    "StructuralChunker",
    "chunk_namespace_for_document",
    "make_child_chunk_id",
    "make_parent_chunk_id",
]
