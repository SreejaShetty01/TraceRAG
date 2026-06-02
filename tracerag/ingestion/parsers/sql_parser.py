"""SQL parsing boundary for statement-level segmentation and schema artifact extraction."""

from __future__ import annotations

import re
from pathlib import Path

from tracerag.ingestion.parsers.base import BaseParser
from tracerag.ingestion.parsers.common import (
    build_parsed_document,
    make_block_id,
    read_source_text,
)
from tracerag.models.document import DocumentBlock, ParsedDocument
from tracerag.models.types import BlockType, FileExtension, SourceKind

_DDL_PATTERN = re.compile(
    r"^\s*(CREATE|ALTER|DROP|TRUNCATE|RENAME)\b",
    re.IGNORECASE | re.DOTALL,
)


class SQLParser(BaseParser):
    """Parse SQL scripts into semicolon-delimited statements."""

    @property
    def name(self) -> str:
        return "sql"

    @property
    def supported_extensions(self) -> frozenset[FileExtension]:
        return frozenset({".sql"})

    def parse(
        self,
        path: Path,
        *,
        workspace_root: Path | None = None,
    ) -> ParsedDocument:
        text = read_source_text(path)
        blocks = self._split_statements(text)
        return build_parsed_document(
            path,
            workspace_root=workspace_root,
            parser_name=self.name,
            content=text,
            blocks=blocks,
            language="sql",
            source_kind=SourceKind.SQL,
        )

    def _split_statements(self, text: str) -> list[DocumentBlock]:
        statements = self._segment_statements(text)
        if not statements:
            return [
                DocumentBlock(
                    block_id=make_block_id(self.name, 0),
                    content=text.strip(),
                    block_type=BlockType.PARAGRAPH,
                    line_start=1,
                    line_end=text.count("\n") + 1,
                )
            ]

        blocks: list[DocumentBlock] = []
        offset = 0
        for statement in statements:
            start_index = text.find(statement, offset)
            if start_index < 0:
                start_index = offset
            line_start = text[:start_index].count("\n") + 1
            line_end = text[: start_index + len(statement)].count("\n") + 1
            block_type = BlockType.DDL if _DDL_PATTERN.match(statement) else BlockType.PARAGRAPH
            blocks.append(
                DocumentBlock(
                    block_id=make_block_id(self.name, len(blocks)),
                    content=statement.strip(),
                    block_type=block_type,
                    line_start=line_start,
                    line_end=line_end,
                )
            )
            offset = start_index + len(statement)
        return blocks

    def _segment_statements(self, text: str) -> list[str]:
        parts = re.split(r";\s*(?:\n|$)", text)
        return [part.strip() for part in parts if part.strip()]
