"""Parent-context attachment pipeline for contextual retrieval preparation."""

from __future__ import annotations

from tracerag.ingestion.context.augmentor import BaseContextAugmentor, ParentContextAugmentor
from tracerag.ingestion.context.config import ContextEnrichmentConfig
from tracerag.ingestion.context.contracts import ContextGenerator
from tracerag.models.chunk import ParentChildChunkSet
from tracerag.models.context import ContextualChunkSet


class ParentContextAttachmentPipeline:
    """Orchestrate contextual prefix attachment across a parent-child chunk hierarchy."""

    def __init__(
        self,
        *,
        augmentor: BaseContextAugmentor | None = None,
        config: ContextEnrichmentConfig | None = None,
    ) -> None:
        self._augmentor = augmentor or ParentContextAugmentor()
        self._config = config or ContextEnrichmentConfig.default()

    @property
    def config(self) -> ContextEnrichmentConfig:
        return self._config

    @property
    def augmentor(self) -> BaseContextAugmentor:
        return self._augmentor

    def run(self, chunk_set: ParentChildChunkSet) -> ContextualChunkSet:
        """Attach contextual prefixes to all child chunks in ``chunk_set``."""
        return self._augmentor.augment(chunk_set, config=self._config)

    def with_generator(self, generator: ContextGenerator) -> ParentContextAttachmentPipeline:
        """Return a pipeline instance using a custom context generator."""
        return ParentContextAttachmentPipeline(
            augmentor=ParentContextAugmentor(generator=generator),
            config=self._config,
        )
