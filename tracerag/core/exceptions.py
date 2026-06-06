"""Custom exception taxonomy used to separate failures across subsystem boundaries."""

from __future__ import annotations


class TraceRAGError(Exception):
    """Base exception for all TraceRAG domain errors."""


# ---------------------------------------------------------------------------
# Ingestion
# ---------------------------------------------------------------------------


class IngestionError(TraceRAGError):
    """Base exception for ingestion pipeline failures."""


class ChunkingError(IngestionError):
    """Raised when chunk generation fails."""

    def __init__(self, message: str, *, path: str | None = None, cause: BaseException | None = None) -> None:
        self.path = path
        if path is not None:
            message = f"{message} (path={path!r})"
        super().__init__(message)
        if cause is not None:
            self.__cause__ = cause


class ContextAugmentationError(IngestionError):
    """Raised when contextual prefix attachment or validation fails."""

    def __init__(self, message: str, *, path: str | None = None, cause: BaseException | None = None) -> None:
        self.path = path
        if path is not None:
            message = f"{message} (path={path!r})"
        super().__init__(message)
        if cause is not None:
            self.__cause__ = cause


class EmbeddingError(IngestionError):
    """Raised when embedding generation or validation fails."""

    def __init__(self, message: str, *, path: str | None = None, cause: BaseException | None = None) -> None:
        self.path = path
        if path is not None:
            message = f"{message} (path={path!r})"
        super().__init__(message)
        if cause is not None:
            self.__cause__ = cause


class VectorStorageError(IngestionError):
    """Raised when vector store operations fail."""

    def __init__(self, message: str, *, path: str | None = None, cause: BaseException | None = None) -> None:
        self.path = path
        if path is not None:
            message = f"{message} (path={path!r})"
        super().__init__(message)
        if cause is not None:
            self.__cause__ = cause


class RetrievalError(IngestionError):
    """Raised when hybrid retrieval operations fail."""

    def __init__(self, message: str, *, cause: BaseException | None = None) -> None:
        super().__init__(message)
        if cause is not None:
            self.__cause__ = cause


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


class DiscoveryError(IngestionError):
    """Base exception for workspace discovery failures."""


class WorkspaceNotFoundError(DiscoveryError):
    """Raised when the workspace path does not exist."""

    def __init__(self, path: str) -> None:
        self.path = path
        super().__init__(f"Workspace path does not exist: {path!r}")


class WorkspaceNotADirectoryError(DiscoveryError):
    """Raised when the workspace path is not a directory."""

    def __init__(self, path: str) -> None:
        self.path = path
        super().__init__(f"Workspace path is not a directory: {path!r}")


class WorkspacePermissionError(DiscoveryError):
    """Raised when the workspace or a subtree cannot be read."""

    def __init__(self, path: str, *, cause: BaseException | None = None) -> None:
        self.path = path
        super().__init__(f"Permission denied accessing workspace path: {path!r}")
        if cause is not None:
            self.__cause__ = cause


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------


class ParserError(IngestionError):
    """Base exception for parser-layer failures."""


class ParserNotFoundError(ParserError):
    """Raised when no parser is registered for a file extension."""

    def __init__(self, extension: str, path: str | None = None) -> None:
        self.extension = extension
        self.path = path
        message = f"No parser registered for extension {extension!r}"
        if path is not None:
            message = f"{message} (path={path!r})"
        super().__init__(message)


class ParserRegistrationError(ParserError):
    """Raised when parser registration violates registry constraints."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class UnsupportedFileTypeError(ParserError):
    """Raised when a path uses an extension outside the supported vocabulary."""

    def __init__(self, extension: str, path: str | None = None) -> None:
        self.extension = extension
        self.path = path
        message = f"Unsupported file type {extension!r}"
        if path is not None:
            message = f"{message} (path={path!r})"
        super().__init__(message)


class ParseError(ParserError):
    """Raised when a parser fails to normalize a source artifact."""

    def __init__(self, message: str, *, path: str | None = None, cause: BaseException | None = None) -> None:
        self.path = path
        self.cause = cause
        if path is not None:
            message = f"{message} (path={path!r})"
        super().__init__(message)
        if cause is not None:
            self.__cause__ = cause
