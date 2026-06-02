"""Context summarization boundary for compact retrieval-oriented prefaces."""

from __future__ import annotations

from tracerag.ingestion.context.config import ContextEnrichmentConfig
from tracerag.ingestion.context.contracts import (
    ContextGenerationRequest,
    ContextGenerationResult,
    ContextGenerator,
)
from tracerag.ingestion.context.validation import validate_context_prefix
from tracerag.models.chunk import ParentChunk
from tracerag.models.context import ContextValidationResult
from tracerag.models.document import DocumentMetadata
from tracerag.models.types import ContextSource
from tracerag.utils.file_utils import relative_to_workspace


class DeterministicContextGenerator(ContextGenerator):
    """Build contextual prefixes from document and parent metadata without LLM calls."""

    def generate(self, request: ContextGenerationRequest) -> ContextGenerationResult:
        if not request.config.enabled:
            validation = ContextValidationResult(is_valid=True)
            return ContextGenerationResult(
                context_prefix=None,
                context_source=ContextSource.NONE.value,
                document_context_excerpt=None,
                parent_context_excerpt=None,
                validation=validation,
            )

        document_excerpt = (
            self._document_context(request.document) if request.config.attach_document_context else None
        )
        parent_excerpt = (
            self._parent_context(request.parent, request.config)
            if request.config.attach_parent_context and request.parent is not None
            else None
        )

        segments = [segment for segment in (document_excerpt, parent_excerpt) if segment]
        context_prefix = "\n".join(segments) if segments else None
        context_source = self._resolve_source(document_excerpt, parent_excerpt)

        validation = validate_context_prefix(
            context_prefix,
            child_content=request.child.content,
            config=request.config,
        )

        return ContextGenerationResult(
            context_prefix=context_prefix,
            context_source=context_source.value,
            document_context_excerpt=document_excerpt,
            parent_context_excerpt=parent_excerpt,
            validation=validation,
        )

    def _document_context(self, document: DocumentMetadata) -> str:
        path_label = self._format_path_label(document)
        parts = [f"Source file: {path_label}", f"Kind: {document.source_kind.value}"]
        if document.language:
            parts.append(f"Language: {document.language}")
        if document.parser_name:
            parts.append(f"Parser: {document.parser_name}")
        return "; ".join(parts)

    def _parent_context(self, parent: ParentChunk, config: ContextEnrichmentConfig) -> str:
        excerpt = parent.content.strip()
        if len(excerpt) > config.parent_excerpt_chars:
            excerpt = f"{excerpt[: config.parent_excerpt_chars].rstrip()}..."
        if parent.metadata.heading:
            return f'Section "{parent.metadata.heading}": {excerpt}'
        return f"Parent scope: {excerpt}"

    def _format_path_label(self, document: DocumentMetadata) -> str:
        if document.workspace_root is not None:
            try:
                return str(relative_to_workspace(document.file_path, document.workspace_root))
            except ValueError:
                pass
        return document.file_path.name

    def _resolve_source(
        self,
        document_excerpt: str | None,
        parent_excerpt: str | None,
    ) -> ContextSource:
        if document_excerpt and parent_excerpt:
            return ContextSource.DOCUMENT_AND_PARENT
        if document_excerpt:
            return ContextSource.DOCUMENT
        if parent_excerpt:
            return ContextSource.PARENT
        return ContextSource.NONE
