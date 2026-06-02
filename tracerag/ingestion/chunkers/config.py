"""Chunking configuration models for parent-child retrieval sizing."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ChunkingConfig(BaseModel):
    """Token-oriented sizing policy for parent-child chunk generation."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    child_token_target: int = Field(default=175, ge=1)
    child_token_min: int = Field(default=150, ge=1)
    child_token_max: int = Field(default=200, ge=1)
    parent_token_target: int = Field(default=900, ge=1)
    parent_token_min: int = Field(default=800, ge=1)
    parent_token_max: int = Field(default=1000, ge=1)
    overlap_tokens: int = Field(default=20, ge=0)

    @model_validator(mode="after")
    def _validate_ranges(self) -> ChunkingConfig:
        if self.child_token_min > self.child_token_target:
            msg = "child_token_min must be <= child_token_target"
            raise ValueError(msg)
        if self.child_token_target > self.child_token_max:
            msg = "child_token_target must be <= child_token_max"
            raise ValueError(msg)
        if self.parent_token_min > self.parent_token_target:
            msg = "parent_token_min must be <= parent_token_target"
            raise ValueError(msg)
        if self.parent_token_target > self.parent_token_max:
            msg = "parent_token_target must be <= parent_token_max"
            raise ValueError(msg)
        if self.overlap_tokens >= self.child_token_max:
            msg = "overlap_tokens must be less than child_token_max"
            raise ValueError(msg)
        return self

    @classmethod
    def default(cls) -> ChunkingConfig:
        """Return the default TraceRAG parent-child sizing policy."""
        return cls()
