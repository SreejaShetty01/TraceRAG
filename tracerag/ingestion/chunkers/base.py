"""Abstract chunking contracts for converting normalized documents into retrieval units."""

from __future__ import annotations

from abc import ABC, abstractmethod

from tracerag.ingestion.chunkers.config import ChunkingConfig
from tracerag.models.chunk import ParentChildChunkSet
from tracerag.models.document import ParsedDocument


class BaseChunker(ABC):
    """Contract for chunkers that emit hierarchical parent-child chunk sets."""

    @abstractmethod
    def chunk(
        self,
        document: ParsedDocument,
        *,
        config: ChunkingConfig | None = None,
    ) -> ParentChildChunkSet:
        """Transform a parsed document into parent-child chunks."""


class StructuralChunker(BaseChunker):
    """Chunker that respects parser-emitted ``DocumentBlock`` boundaries when grouping content."""

    @abstractmethod
    def chunk_blocks(
        self,
        document: ParsedDocument,
        *,
        config: ChunkingConfig | None = None,
    ) -> ParentChildChunkSet:
        """Chunk a document using structural block boundaries as parent groupings."""

    def chunk(
        self,
        document: ParsedDocument,
        *,
        config: ChunkingConfig | None = None,
    ) -> ParentChildChunkSet:
        return self.chunk_blocks(document, config=config)
