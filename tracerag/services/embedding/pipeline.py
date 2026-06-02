"""Embedding pipeline for contextual child chunks."""

from __future__ import annotations

from datetime import datetime, timezone

from tracerag.core.exceptions import EmbeddingError
from tracerag.ingestion.context.config import ContextEnrichmentConfig
from tracerag.ingestion.context.prefix_builder import build_prefixed_envelope
from tracerag.models.context import ContextualChunk, ContextualChunkSet
from tracerag.models.embedding import (
    ChunkEmbeddingRecord,
    EmbeddingBatchResult,
    EmbeddingFailure,
    EmbeddingMetadata,
)
from tracerag.models.types import EmbeddingVector
from tracerag.services.embedding.config import EmbeddingConfig
from tracerag.services.embedding.contracts import EmbeddingProvider
from tracerag.services.embedding.ollama_provider import OllamaEmbeddingProvider
from tracerag.services.embedding.validation import validate_embedding_vector
from tracerag.utils.hash_utils import sha256_hex


class EmbeddingPipeline:
    """Transform contextualized chunks into validated embedding records."""

    def __init__(
        self,
        provider: EmbeddingProvider | None = None,
        *,
        config: EmbeddingConfig | None = None,
        context_config: ContextEnrichmentConfig | None = None,
    ) -> None:
        self._config = config or EmbeddingConfig.default()
        self._provider = provider or OllamaEmbeddingProvider(self._config)
        self._context_config = context_config or ContextEnrichmentConfig.default()

    @property
    def config(self) -> EmbeddingConfig:
        return self._config

    @property
    def provider(self) -> EmbeddingProvider:
        return self._provider

    def embed_chunk(self, chunk: ContextualChunk) -> ChunkEmbeddingRecord:
        """Embed a single contextual child chunk."""
        results = self.embed_chunks([chunk])
        if not results.records:
            failure = results.failures[0] if results.failures else None
            detail = failure.error if failure else "unknown embedding failure"
            raise EmbeddingError(f"failed to embed chunk {chunk.chunk_id!r}: {detail}")
        return results.records[0]

    def embed_chunks(self, chunks: list[ContextualChunk]) -> EmbeddingBatchResult:
        """Embed multiple contextual child chunks with batching."""
        records: list[ChunkEmbeddingRecord] = []
        failures: list[EmbeddingFailure] = []

        for batch_start in range(0, len(chunks), self._config.batch_size):
            batch = chunks[batch_start : batch_start + self._config.batch_size]
            inputs = [self._embedding_input(chunk) for chunk in batch]
            try:
                vectors = self._provider.embed_batch(inputs)
            except EmbeddingError as exc:
                for chunk in batch:
                    failures.append(
                        EmbeddingFailure(chunk_id=chunk.chunk_id, error=str(exc))
                    )
                continue

            if len(vectors) != len(batch):
                msg = f"provider returned {len(vectors)} vectors for {len(batch)} inputs"
                for chunk in batch:
                    failures.append(EmbeddingFailure(chunk_id=chunk.chunk_id, error=msg))
                continue

            for chunk, input_text, vector in zip(batch, inputs, vectors, strict=True):
                try:
                    records.append(self._build_record(chunk, input_text, vector))
                except EmbeddingError as exc:
                    failures.append(
                        EmbeddingFailure(chunk_id=chunk.chunk_id, error=str(exc))
                    )

        return EmbeddingBatchResult(records=tuple(records), failures=tuple(failures))

    def embed_contextual_set(self, chunk_set: ContextualChunkSet) -> EmbeddingBatchResult:
        """Embed all child chunks in a contextual chunk hierarchy."""
        return self.embed_chunks(list(chunk_set.children))

    def _embedding_input(self, chunk: ContextualChunk) -> str:
        if self._config.use_prefixed_envelope:
            return build_prefixed_envelope(chunk, config=self._context_config)
        if chunk.context_prefix and chunk.context_prefix.strip():
            return f"{chunk.context_prefix.strip()}\n\n{chunk.content}"
        return chunk.content

    def _build_record(
        self,
        chunk: ContextualChunk,
        input_text: str,
        vector: EmbeddingVector,
    ) -> ChunkEmbeddingRecord:
        validation = validate_embedding_vector(vector, config=self._config)
        if self._config.validate_vectors and not validation.is_valid:
            joined = "; ".join(validation.errors)
            raise EmbeddingError(
                f"embedding validation failed for chunk {chunk.chunk_id!r}: {joined}"
            )

        metadata = EmbeddingMetadata(
            chunk_id=chunk.chunk_id,
            parent_chunk_id=chunk.parent_chunk_id,
            provider=self._provider.name,
            model=self._provider.model,
            dimension=len(vector),
            embedded_at=datetime.now(timezone.utc),
            input_text_hash=sha256_hex(input_text),
            document_content_hash=chunk.metadata.document_content_hash,
            uses_context_prefix=bool(chunk.context_prefix and chunk.context_prefix.strip()),
            uses_prefixed_envelope=self._config.use_prefixed_envelope,
        )
        return ChunkEmbeddingRecord(
            chunk_id=chunk.chunk_id,
            vector=vector,
            metadata=metadata,
            validation=validation,
        )
