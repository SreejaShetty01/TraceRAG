"""JSON parsing boundary preserving top-level key structure."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tracerag.core.exceptions import ParseError
from tracerag.ingestion.parsers.base import BaseParser
from tracerag.ingestion.parsers.common import (
    build_parsed_document,
    line_count_for,
    make_block_id,
    read_source_text,
)
from tracerag.models.document import DocumentBlock, ParsedDocument
from tracerag.models.types import BlockType, FileExtension, SourceKind


class JSONParser(BaseParser):
    """Parse JSON configuration files into key-scoped structural blocks."""

    @property
    def name(self) -> str:
        return "json"

    @property
    def supported_extensions(self) -> frozenset[FileExtension]:
        return frozenset({".json"})

    def parse(
        self,
        path: Path,
        *,
        workspace_root: Path | None = None,
    ) -> ParsedDocument:
        raw = read_source_text(path)
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ParseError("invalid JSON document", path=str(path), cause=exc) from exc

        content = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)
        blocks = self._blocks_from_payload(payload)
        return build_parsed_document(
            path,
            workspace_root=workspace_root,
            parser_name=self.name,
            content=content,
            blocks=blocks,
            language="json",
            source_kind=SourceKind.CONFIG,
        )

    def _blocks_from_payload(self, payload: Any) -> list[DocumentBlock]:
        if isinstance(payload, dict):
            blocks: list[DocumentBlock] = []
            for key in sorted(payload.keys()):
                value = payload[key]
                block_content = json.dumps({key: value}, indent=2, sort_keys=True, ensure_ascii=False)
                blocks.append(
                    DocumentBlock(
                        block_id=make_block_id(self.name, len(blocks)),
                        content=block_content,
                        block_type=BlockType.CONFIG_KEY,
                        heading=str(key),
                    )
                )
            return blocks

        return [
            DocumentBlock(
                block_id=make_block_id(self.name, 0),
                content=json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False),
                block_type=BlockType.ROOT,
                line_start=1,
                line_end=line_count_for(json.dumps(payload)),
            )
        ]
