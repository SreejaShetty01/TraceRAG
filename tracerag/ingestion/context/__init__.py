"""Contextual retrieval enrichment for parent-child chunks."""

from tracerag.ingestion.context.augmentor import BaseContextAugmentor, ParentContextAugmentor
from tracerag.ingestion.context.config import ContextEnrichmentConfig
from tracerag.ingestion.context.contracts import (
    ContextGenerationRequest,
    ContextGenerationResult,
    ContextGenerator,
)
from tracerag.ingestion.context.pipeline import ParentContextAttachmentPipeline
from tracerag.ingestion.context.prefix_builder import build_prefixed_envelope
from tracerag.ingestion.context.summarizer import DeterministicContextGenerator
from tracerag.ingestion.context.validation import validate_context_prefix

__all__ = [
    "BaseContextAugmentor",
    "ContextEnrichmentConfig",
    "ContextGenerationRequest",
    "ContextGenerationResult",
    "ContextGenerator",
    "DeterministicContextGenerator",
    "ParentContextAttachmentPipeline",
    "ParentContextAugmentor",
    "build_prefixed_envelope",
    "validate_context_prefix",
]
