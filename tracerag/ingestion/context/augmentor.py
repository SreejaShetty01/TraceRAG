"""Context augmentation interfaces for parent-child chunk hierarchies."""

from __future__ import annotations

from abc import ABC, abstractmethod

from tracerag.core.exceptions import ContextAugmentationError
from tracerag.ingestion.context.config import ContextEnrichmentConfig
from tracerag.ingestion.context.contracts import ContextGenerationRequest, ContextGenerator
from tracerag.ingestion.context.summarizer import DeterministicContextGenerator
from tracerag.models.chunk import ParentChildChunkSet
from tracerag.models.context import ContextualChunk, ContextualChunkSet
from tracerag.models.types import ContextSource


class BaseContextAugmentor(ABC):
    """Contract for augmenting parent-child chunk sets with contextual prefixes."""

    @abstractmethod
    def augment(
        self,
        chunk_set: ParentChildChunkSet,
        *,
        config: ContextEnrichmentConfig | None = None,
    ) -> ContextualChunkSet:
        """Attach contextual prefixes to child chunks in ``chunk_set``."""


class ParentContextAugmentor(BaseContextAugmentor):
    """Augment child chunks using document and parent scope context."""

    def __init__(self, generator: ContextGenerator | None = None) -> None:
        self._generator = generator or DeterministicContextGenerator()

    @property
    def generator(self) -> ContextGenerator:
        return self._generator

    def augment(
        self,
        chunk_set: ParentChildChunkSet,
        *,
        config: ContextEnrichmentConfig | None = None,
    ) -> ContextualChunkSet:
        policy = config or ContextEnrichmentConfig.default()
        contextual_children: list[ContextualChunk] = []

        for child in chunk_set.children:
            parent = chunk_set.parent_for_child(child.chunk_id)
            result = self._generator.generate(
                ContextGenerationRequest(
                    child=child,
                    parent=parent,
                    document=chunk_set.source,
                    config=policy,
                )
            )
            if not result.validation.is_valid:
                joined = "; ".join(result.validation.errors)
                raise ContextAugmentationError(
                    f"context validation failed for child {child.chunk_id!r}: {joined}",
                    path=str(chunk_set.source.file_path),
                )

            contextual_children.append(
                ContextualChunk.from_child(
                    child,
                    context_prefix=result.context_prefix,
                    context_source=ContextSource(result.context_source),
                    document_context_excerpt=result.document_context_excerpt,
                    parent_context_excerpt=result.parent_context_excerpt,
                )
            )

        return ContextualChunkSet(
            source=chunk_set.source,
            parents=chunk_set.parents,
            children=tuple(contextual_children),
        )
