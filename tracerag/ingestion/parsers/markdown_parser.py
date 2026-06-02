"""Markdown parsing boundary for heading-aware section normalization."""

from __future__ import annotations

import re
from pathlib import Path

from tracerag.ingestion.parsers.base import BaseParser
from tracerag.ingestion.parsers.common import (
    build_parsed_document,
    line_count_for,
    make_block_id,
    read_source_text,
)
from tracerag.models.document import DocumentBlock, ParsedDocument
from tracerag.models.types import BlockType, FileExtension, SourceKind

_HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)


class MarkdownParser(BaseParser):
    """Parse Markdown files into heading-aware sections."""

    @property
    def name(self) -> str:
        return "markdown"

    @property
    def supported_extensions(self) -> frozenset[FileExtension]:
        return frozenset({".md"})

    def parse(
        self,
        path: Path,
        *,
        workspace_root: Path | None = None,
    ) -> ParsedDocument:
        text = read_source_text(path)
        blocks = self._split_sections(text)
        return build_parsed_document(
            path,
            workspace_root=workspace_root,
            parser_name=self.name,
            content=text,
            blocks=blocks,
            language="markdown",
            source_kind=SourceKind.MARKDOWN,
        )

    def _split_sections(self, text: str) -> list[DocumentBlock]:
        matches = list(_HEADING_PATTERN.finditer(text))
        if not matches:
            return [
                DocumentBlock(
                    block_id=make_block_id(self.name, 0),
                    content=text.strip(),
                    block_type=BlockType.PARAGRAPH,
                    line_start=1,
                    line_end=line_count_for(text),
                )
            ]

        blocks: list[DocumentBlock] = []
        for index, match in enumerate(matches):
            start = match.start()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            section_text = text[start:end].strip()
            if not section_text:
                continue
            heading_title = match.group(2).strip()
            line_start = text[:start].count("\n") + 1
            line_end = text[:end].count("\n") + 1
            blocks.append(
                DocumentBlock(
                    block_id=make_block_id(self.name, len(blocks)),
                    content=section_text,
                    block_type=BlockType.SECTION,
                    line_start=line_start,
                    line_end=line_end,
                    heading=heading_title,
                )
            )
        return blocks
