"""Context generation contracts for contextual retrieval enrichment."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from tracerag.ingestion.context.config import ContextEnrichmentConfig
from tracerag.models.chunk import ChildChunk, ParentChunk
from tracerag.models.context import ContextValidationResult
from tracerag.models.document import DocumentMetadata


@dataclass(frozen=True)
class ContextGenerationRequest:
    """Input payload for generating a contextual prefix for one child chunk."""

    child: ChildChunk
    parent: ParentChunk | None
    document: DocumentMetadata
    config: ContextEnrichmentConfig


@dataclass(frozen=True)
class ContextGenerationResult:
    """Output of contextual prefix generation for one child chunk."""

    context_prefix: str | None
    context_source: str
    document_context_excerpt: str | None
    parent_context_excerpt: str | None
    validation: ContextValidationResult


class ContextGenerator(ABC):
    """Contract for producing contextual prefixes without mutating chunk content."""

    @abstractmethod
    def generate(self, request: ContextGenerationRequest) -> ContextGenerationResult:
        """Generate a contextual prefix for the supplied child chunk."""
