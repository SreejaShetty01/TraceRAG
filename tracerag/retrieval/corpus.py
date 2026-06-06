"""Helpers for building sparse retrieval corpora from contextual chunks."""

from __future__ import annotations

from tracerag.ingestion.context.config import ContextEnrichmentConfig
from tracerag.ingestion.context.prefix_builder import build_prefixed_envelope
from tracerag.models.context import ContextualChunk
from tracerag.models.embedding import ChunkEmbeddingRecord
from tracerag.models.retrieval import SparseCorpusDocument


def contextual_chunk_to_corpus_document(
    chunk: ContextualChunk,
    *,
    use_prefixed_envelope: bool = True,
    context_config: ContextEnrichmentConfig | None = None,
) -> SparseCorpusDocument:
    """Map a contextual chunk to a BM25-indexable corpus document."""
    if use_prefixed_envelope:
        text = build_prefixed_envelope(chunk, config=context_config)
    elif chunk.context_prefix and chunk.context_prefix.strip():
        text = f"{chunk.context_prefix.strip()}\n\n{chunk.content}"
    else:
        text = chunk.content

    return SparseCorpusDocument(
        chunk_id=chunk.chunk_id,
        text=text,
        parent_chunk_id=chunk.parent_chunk_id,
        document_content_hash=chunk.metadata.document_content_hash,
        embedding_model=None,
        embedding_provider=None,
        uses_context_prefix=bool(chunk.context_prefix and chunk.context_prefix.strip()),
    )


def embedding_record_to_corpus_document(
    record: ChunkEmbeddingRecord,
    *,
    text: str,
) -> SparseCorpusDocument:
    """Map an embedding record plus searchable text to a corpus document."""
    return SparseCorpusDocument(
        chunk_id=record.chunk_id,
        text=text,
        parent_chunk_id=record.metadata.parent_chunk_id,
        document_content_hash=record.metadata.document_content_hash,
        embedding_model=record.metadata.model,
        embedding_provider=record.metadata.provider,
        uses_context_prefix=record.metadata.uses_context_prefix,
    )


def build_corpus_from_contextual_chunks(
    chunks: list[ContextualChunk],
    *,
    use_prefixed_envelope: bool = True,
    context_config: ContextEnrichmentConfig | None = None,
) -> list[SparseCorpusDocument]:
    """Build sparse corpus documents from contextual child chunks."""
    return [
        contextual_chunk_to_corpus_document(
            chunk,
            use_prefixed_envelope=use_prefixed_envelope,
            context_config=context_config,
        )
        for chunk in chunks
    ]
