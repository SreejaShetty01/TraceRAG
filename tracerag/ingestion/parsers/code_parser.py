"""Code parsing boundary for language-aware structural extraction from source files."""

from __future__ import annotations

import ast
from pathlib import Path

from tracerag.core.exceptions import ParseError
from tracerag.ingestion.parsers.base import BaseParser
from tracerag.ingestion.parsers.common import (
    build_parsed_document,
    make_block_id,
    read_source_text,
)
from tracerag.models.document import DocumentBlock, ParsedDocument
from tracerag.models.types import BlockType, FileExtension, SourceKind


class PythonParser(BaseParser):
    """Parse Python source files into function and class structural blocks."""

    @property
    def name(self) -> str:
        return "python"

    @property
    def supported_extensions(self) -> frozenset[FileExtension]:
        return frozenset({".py"})

    def parse(
        self,
        path: Path,
        *,
        workspace_root: Path | None = None,
    ) -> ParsedDocument:
        source = read_source_text(path, allow_empty=True)
        if not source.strip():
            source = "#\n"
        try:
            module = ast.parse(source, filename=str(path))
        except SyntaxError as exc:
            raise ParseError("invalid Python syntax", path=str(path), cause=exc) from exc

        blocks = self._extract_blocks(source, module)
        return build_parsed_document(
            path,
            workspace_root=workspace_root,
            parser_name=self.name,
            content=source,
            blocks=blocks,
            language="python",
            source_kind=SourceKind.CODE,
        )

    def _extract_blocks(self, source: str, module: ast.Module) -> list[DocumentBlock]:
        blocks: list[DocumentBlock] = []
        for node in module.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            segment = ast.get_source_segment(source, node)
            if not segment or not segment.strip():
                continue
            end_line = node.end_lineno or node.lineno
            blocks.append(
                DocumentBlock(
                    block_id=make_block_id(self.name, len(blocks)),
                    content=segment.strip(),
                    block_type=BlockType.CODE_UNIT,
                    line_start=node.lineno,
                    line_end=end_line,
                    heading=node.name,
                )
            )
        if blocks:
            return blocks

        return [
            DocumentBlock(
                block_id=make_block_id(self.name, 0),
                content=source.strip(),
                block_type=BlockType.CODE_UNIT,
                line_start=1,
                line_end=source.count("\n") + 1,
            )
        ]
