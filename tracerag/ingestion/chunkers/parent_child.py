"""Parent-child chunking boundary defining hierarchical chunk relationship contracts."""

from __future__ import annotations

from dataclasses import dataclass

from tracerag.core.exceptions import ChunkingError
from tracerag.ingestion.chunkers.base import StructuralChunker
from tracerag.ingestion.chunkers.config import ChunkingConfig
from tracerag.ingestion.chunkers.ids import (
    chunk_namespace_for_document,
    make_child_chunk_id,
    make_parent_chunk_id,
)
from tracerag.ingestion.chunkers.splitting import split_into_child_chunks
from tracerag.ingestion.metadata import build_chunk_metadata
from tracerag.models.chunk import ChildChunk, ParentChildChunkSet, ParentChunk
from tracerag.models.document import DocumentBlock, ParsedDocument
from tracerag.models.types import ChildChunkId, ChunkLevel
from tracerag.utils.token_utils import estimate_token_count


@dataclass(frozen=True)
class _Segment:
    """Internal segment used when grouping structural blocks into parent chunks."""

    text: str
    block: DocumentBlock | None


class ParentChildChunker(StructuralChunker):
    """Generate parent synthesis chunks and linked child retrieval chunks from a parsed document."""

    def chunk_blocks(
        self,
        document: ParsedDocument,
        *,
        config: ChunkingConfig | None = None,
    ) -> ParentChildChunkSet:
        policy = config or ChunkingConfig.default()
        segments = self._segments_from_document(document)
        if not segments:
            raise ChunkingError("document produced no chunkable segments", path=str(document.metadata.file_path))

        namespace = chunk_namespace_for_document(document.metadata)
        parent_groups = self._group_segments_for_parents(segments, policy)

        parents: list[ParentChunk] = []
        children: list[ChildChunk] = []

        for parent_index, group in enumerate(parent_groups):
            parent_id = make_parent_chunk_id(namespace, parent_index)
            parent_content = "\n\n".join(segment.text.strip() for segment in group if segment.text.strip())
            if not parent_content.strip():
                continue

            child_texts = split_into_child_chunks(parent_content, policy)
            if not child_texts:
                raise ChunkingError(
                    "failed to derive child chunks from parent content",
                    path=str(document.metadata.file_path),
                )

            child_ids: list[ChildChunkId] = []
            anchor_block = next((segment.block for segment in group if segment.block is not None), None)

            for child_index, child_content in enumerate(child_texts):
                child_id = make_child_chunk_id(parent_id, child_index)
                child_ids.append(child_id)
                children.append(
                    ChildChunk(
                        chunk_id=child_id,
                        parent_chunk_id=parent_id,
                        content=child_content,
                        metadata=build_chunk_metadata(
                            document.metadata,
                            chunk_id=child_id,
                            chunk_level=ChunkLevel.CHILD,
                            chunk_index=child_index,
                            content=child_content,
                            parent_chunk_id=parent_id,
                            block=anchor_block,
                        ),
                    )
                )

            parents.append(
                ParentChunk(
                    chunk_id=parent_id,
                    content=parent_content,
                    metadata=build_chunk_metadata(
                        document.metadata,
                        chunk_id=parent_id,
                        chunk_level=ChunkLevel.PARENT,
                        chunk_index=parent_index,
                        content=parent_content,
                        block=anchor_block,
                    ),
                    child_chunk_ids=tuple(child_ids),
                )
            )

        if not parents:
            raise ChunkingError("no parent chunks were produced", path=str(document.metadata.file_path))

        return ParentChildChunkSet(
            source=document.metadata,
            parents=tuple(parents),
            children=tuple(children),
        )

    def _segments_from_document(self, document: ParsedDocument) -> list[_Segment]:
        if document.blocks:
            return [_Segment(text=block.content, block=block) for block in document.blocks]
        return [_Segment(text=document.content, block=None)]

    def _group_segments_for_parents(
        self,
        segments: list[_Segment],
        config: ChunkingConfig,
    ) -> list[list[_Segment]]:
        groups: list[list[_Segment]] = []
        current: list[_Segment] = []
        current_tokens = 0

        for segment in segments:
            segment_tokens = estimate_token_count(segment.text)
            if current and current_tokens + segment_tokens > config.parent_token_max:
                groups.append(current)
                current = []
                current_tokens = 0

            current.append(segment)
            current_tokens += segment_tokens

            if current_tokens >= config.parent_token_target:
                groups.append(current)
                current = []
                current_tokens = 0

        if current:
            groups.append(current)

        return groups
