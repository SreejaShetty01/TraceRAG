#Requires -Version 5.1
<#
.SYNOPSIS
    TraceRAG — Full Repository Scaffold
    Run from the PARENT directory where you want tracerag/ created.
    Example: cd C:\Projects && .\scaffold_tracerag.ps1

.NOTES
    Creates all directories, __init__.py files, placeholder module stubs,
    config files, scripts, docker files, tests, and evals.
    No implementation logic generated — scaffold only.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ─── Root ─────────────────────────────────────────────────────────────────────
$ROOT = Join-Path $PWD "tracerag"

if (Test-Path $ROOT) {
    Write-Host "[WARN] '$ROOT' already exists. Files will be created/overwritten inside it." -ForegroundColor Yellow
} else {
    New-Item -ItemType Directory -Path $ROOT | Out-Null
    Write-Host "[OK]  Created root: $ROOT" -ForegroundColor Green
}

# ─── Helper functions ─────────────────────────────────────────────────────────
function New-Dir {
    param([string]$RelPath)
    $full = Join-Path $ROOT $RelPath
    if (-not (Test-Path $full)) {
        New-Item -ItemType Directory -Path $full -Force | Out-Null
    }
}

function New-File {
    param([string]$RelPath, [string]$Content = "")
    $full = Join-Path $ROOT $RelPath
    $dir  = Split-Path $full -Parent
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    # Only write if file does not exist — preserves any manually added content
    if (-not (Test-Path $full)) {
        Set-Content -Path $full -Value $Content -Encoding UTF8
    }
}

function New-Stub {
    # Python module stub — single docstring, no logic
    param([string]$RelPath, [string]$Doc)
    New-File -RelPath $RelPath -Content "# $Doc`n"
}

function New-Init {
    param([string]$RelPath)
    New-File -RelPath (Join-Path $RelPath "__init__.py") -Content ""
}

Write-Host "`n[1/8] Creating directories..." -ForegroundColor Cyan

# ─── 1. Directories ───────────────────────────────────────────────────────────
$dirs = @(
    "config",
    "docker\postgres",
    "docker\neo4j",
    "docker\ollama",
    "docs",
    "logs",
    "scripts",
    "evals\datasets",
    "evals\runners",
    "evals\metrics",
    "evals\reports",
    "tests\fixtures\workspaces\python_project",
    "tests\fixtures\workspaces\mixed_repo",
    "tests\unit\ingestion",
    "tests\unit\retrieval",
    "tests\unit\graph",
    "tests\unit\orchestration",
    "tests\unit\impact",
    "tests\integration",
    "tracerag\core",
    "tracerag\models",
    "tracerag\ingestion\parsers",
    "tracerag\ingestion\chunkers",
    "tracerag\ingestion\context",
    "tracerag\retrieval",
    "tracerag\graph",
    "tracerag\orchestration",
    "tracerag\memory",
    "tracerag\impact",
    "tracerag\api\routers",
    "tracerag\api\middleware",
    "tracerag\db\vector",
    "tracerag\db\graph",
    "tracerag\db\migrations",
    "tracerag\services",
    "tracerag\utils"
)

foreach ($d in $dirs) { New-Dir $d }
Write-Host "    $($dirs.Count) directories ready." -ForegroundColor Gray

# ─── 2. __init__.py placements ────────────────────────────────────────────────
Write-Host "`n[2/8] Placing __init__.py files..." -ForegroundColor Cyan

$packages = @(
    "evals",
    "evals\datasets",
    "evals\runners",
    "evals\metrics",
    "evals\reports",
    "tests",
    "tests\fixtures",
    "tests\fixtures\workspaces",
    "tests\fixtures\workspaces\python_project",
    "tests\fixtures\workspaces\mixed_repo",
    "tests\unit",
    "tests\unit\ingestion",
    "tests\unit\retrieval",
    "tests\unit\graph",
    "tests\unit\orchestration",
    "tests\unit\impact",
    "tests\integration",
    "tracerag",
    "tracerag\core",
    "tracerag\models",
    "tracerag\ingestion",
    "tracerag\ingestion\parsers",
    "tracerag\ingestion\chunkers",
    "tracerag\ingestion\context",
    "tracerag\retrieval",
    "tracerag\graph",
    "tracerag\orchestration",
    "tracerag\memory",
    "tracerag\impact",
    "tracerag\api",
    "tracerag\api\routers",
    "tracerag\api\middleware",
    "tracerag\db",
    "tracerag\db\vector",
    "tracerag\db\graph",
    "tracerag\db\migrations",
    "tracerag\services",
    "tracerag\utils"
)

foreach ($pkg in $packages) { New-Init $pkg }
Write-Host "    $($packages.Count) __init__.py files placed." -ForegroundColor Gray

# ─── 3. Config files ──────────────────────────────────────────────────────────
Write-Host "`n[3/8] Writing config files..." -ForegroundColor Cyan

New-File "config\default.yaml" @"
# TraceRAG Default Configuration
# Override with environment-specific files or env vars (prefixed TRACERAG_)

app:
  name: tracerag
  version: "1.0.0"
  log_level: INFO

ollama:
  base_url: "http://localhost:11434"
  contextualizer_model: "gemma2:2b"       # Fast prefix generation
  reasoning_model: "llama3.1:8b"          # Multi-hop synthesis

embedding:
  model: "nomic-embed-text"               # Via Ollama
  dimension: 768

retrieval:
  dense_top_k: 30
  sparse_top_k: 30
  rrf_k: 60                               # RRF fusion constant
  rerank_top_n: 10                        # Candidates passed to cross-encoder
  rerank_model: "cross-encoder/ms-marco-MiniLM-L-6-v2"

chunking:
  child_tokens: 175                       # Retrieval unit
  parent_tokens: 900                      # Synthesis unit
  overlap_tokens: 20

graph:
  max_hop_depth: 2
  max_node_limit: 500                     # Bloat guard
  neo4j_uri: "bolt://localhost:7687"
  neo4j_user: "neo4j"
  neo4j_password: ""                      # Set via env: TRACERAG_GRAPH__NEO4J_PASSWORD

vector_db:
  provider: "postgres"                    # "postgres" | "qdrant"
  postgres_dsn: "postgresql://localhost:5432/tracerag"
  qdrant_url: "http://localhost:6333"

ingestion:
  supported_extensions:
    - .py
    - .java
    - .js
    - .ts
    - .sh
    - .r
    - .sql
    - .json
    - .yaml
    - .ini
    - .pdf
    - .pptx
    - .md
    - .png
    - .jpg
  skip_dirs:
    - .git
    - __pycache__
    - node_modules
    - .venv

impact:
  read_only: true                         # System never writes to source files
"@

New-File "config\logging.yaml" @"
version: 1
disable_existing_loggers: false

formatters:
  json:
    class: pythonjsonlogger.jsonlogger.JsonFormatter
    format: "%(asctime)s %(name)s %(levelname)s %(message)s"
  simple:
    format: "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

handlers:
  console:
    class: logging.StreamHandler
    formatter: simple
    stream: ext://sys.stdout
  file:
    class: logging.handlers.RotatingFileHandler
    formatter: json
    filename: logs/tracerag.log
    maxBytes: 10485760
    backupCount: 5

root:
  level: INFO
  handlers: [console, file]

loggers:
  tracerag.ingestion:
    level: DEBUG
  tracerag.retrieval:
    level: DEBUG
  tracerag.graph:
    level: DEBUG
  tracerag.orchestration:
    level: INFO
"@

New-File ".env.example" @"
# Copy to .env and fill values. Never commit .env.

TRACERAG_APP__LOG_LEVEL=INFO

# Ollama
TRACERAG_OLLAMA__BASE_URL=http://localhost:11434
TRACERAG_OLLAMA__REASONING_MODEL=llama3.1:8b
TRACERAG_OLLAMA__CONTEXTUALIZER_MODEL=gemma2:2b

# Vector DB
TRACERAG_VECTOR_DB__PROVIDER=postgres
TRACERAG_VECTOR_DB__POSTGRES_DSN=postgresql://tracerag:password@localhost:5432/tracerag

# Graph DB
TRACERAG_GRAPH__NEO4J_URI=bolt://localhost:7687
TRACERAG_GRAPH__NEO4J_USER=neo4j
TRACERAG_GRAPH__NEO4J_PASSWORD=your_password_here
"@

New-File "docker\postgres\init.sql" @"
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
"@

New-File "docker\neo4j\neo4j.conf" @"
# TraceRAG Neo4j Config
dbms.memory.heap.initial_size=512m
dbms.memory.heap.max_size=1G
dbms.memory.pagecache.size=512m
"@

New-File "docker-compose.yml" @"
version: "3.9"

services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      - postgres
      - neo4j
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: tracerag
      POSTGRES_USER: tracerag
      POSTGRES_PASSWORD: `${POSTGRES_PASSWORD:-tracerag_dev}
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped

  neo4j:
    image: neo4j:5.20-community
    environment:
      NEO4J_AUTH: neo4j/`${NEO4J_PASSWORD:-tracerag_dev}
      NEO4J_PLUGINS: '["apoc"]'
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4jdata:/data
      - ./docker/neo4j/neo4j.conf:/conf/neo4j.conf
    restart: unless-stopped

volumes:
  pgdata:
  neo4jdata:
"@

New-File "Dockerfile" @"
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]"

COPY . .

EXPOSE 8000

CMD ["uvicorn", "tracerag.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
"@

Write-Host "    Config, Docker, and root files written." -ForegroundColor Gray

# ─── 4. pyproject.toml ────────────────────────────────────────────────────────
New-File "pyproject.toml" @"
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "tracerag"
version = "1.0.0"
description = "Local-first repository intelligence and dependency tracing engine"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.111",
    "uvicorn[standard]>=0.29",
    "pydantic>=2.7",
    "pydantic-settings>=2.3",
    "langgraph>=0.1",
    "langchain>=0.2",
    "langchain-community>=0.2",
    "sentence-transformers>=3.0",
    "rank-bm25>=0.2",
    "psycopg[binary]>=3.1",
    "pgvector>=0.3",
    "qdrant-client>=1.9",
    "neo4j>=5.20",
    "pypdf>=4.2",
    "python-pptx>=0.6",
    "Pillow>=10.3",
    "python-dotenv>=1.0",
    "pyyaml>=6.0",
    "httpx>=0.27",
    "tiktoken>=0.7",
    "python-json-logger>=2.0",
    "rich>=13.7",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.2",
    "pytest-asyncio>=0.23",
    "pytest-cov>=5.0",
    "httpx>=0.27",
    "ruff>=0.4",
    "mypy>=1.10",
    "pre-commit>=3.7",
]
evals = [
    "ragas>=0.1",
    "pandas>=2.2",
    "matplotlib>=3.9",
]

[project.scripts]
tracerag-ingest = "tracerag.ingestion.pipeline:cli_entry"
tracerag-serve  = "tracerag.api.main:cli_entry"

[tool.ruff]
line-length = 100
target-version = "py311"
select = ["E", "F", "I", "UP", "B"]

[tool.mypy]
python_version = "3.11"
strict = true
ignore_missing_imports = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "--cov=tracerag --cov-report=term-missing"

[tool.coverage.run]
omit = ["tests/*", "evals/*", "scripts/*"]
"@

# ─── 5. .gitignore ────────────────────────────────────────────────────────────
New-File ".gitignore" @"
__pycache__/
*.pyc
*.pyo
.eggs/
dist/
build/
*.egg-info/
.venv/
venv/
.env
logs/*.log
.pytest_cache/
.coverage
htmlcov/
evals/reports/*.json
evals/reports/*.csv
.vscode/
.idea/
.DS_Store
"@

# ─── 6. Scripts (PowerShell equivalents) ─────────────────────────────────────
Write-Host "`n[4/8] Writing scripts..." -ForegroundColor Cyan

New-File "scripts\ingest.ps1" @"
# Usage: .\scripts\ingest.ps1 -WorkspacePath C:\path\to\repo
param(
    [Parameter(Mandatory)][string]`$WorkspacePath
)
python -m tracerag.ingestion.pipeline --workspace `$WorkspacePath
"@

New-File "scripts\serve.ps1" @"
# Usage: .\scripts\serve.ps1 [-Reload]
param([switch]`$Reload)
`$args = @("tracerag.api.main:app", "--host", "0.0.0.0", "--port", "8000")
if (`$Reload) { `$args += "--reload" }
uvicorn @args
"@

New-File "scripts\pull_models.ps1" @"
# Pull required Ollama models before first run
`$models = @("gemma2:2b", "llama3.1:8b", "nomic-embed-text")
foreach (`$model in `$models) {
    Write-Host "Pulling `$model..."
    ollama pull `$model
}
Write-Host "All models ready."
"@

New-File "scripts\reset_db.ps1" @"
# WARNING: Drops all indexed data. Dev/test reset only.
Write-Warning "This will drop all vector index and graph data."
`$confirm = Read-Host "Type YES to continue"
if (`$confirm -eq "YES") {
    python -m tracerag.db.vector.indexer --reset
    python -m tracerag.db.graph.client --reset
    Write-Host "DB reset complete."
}
"@

New-File "scripts\run_evals.ps1" @"
# Usage: .\scripts\run_evals.ps1 -Dataset single_hop_retrieval
param(
    [Parameter(Mandatory)][string]`$Dataset
)
python -m evals.runners.run --dataset `$Dataset
"@

Write-Host "    Scripts written." -ForegroundColor Gray

# ─── 7. Application module stubs ──────────────────────────────────────────────
Write-Host "`n[5/8] Writing application module stubs..." -ForegroundColor Cyan

# core/
New-Stub "tracerag\core\settings.py"    "Pydantic-settings model. Reads config/default.yaml + TRACERAG_ env vars."
New-Stub "tracerag\core\constants.py"   "Tier labels, node type strings, metadata field names. No logic."
New-Stub "tracerag\core\exceptions.py"  "Custom exception hierarchy for ingestion, retrieval, graph, and API layers."
New-Stub "tracerag\core\logging.py"     "Logger factory. Loads config/logging.yaml on first import."

# models/
New-Stub "tracerag\models\chunk.py"         "Chunk + ChunkMetadata Pydantic models."
New-Stub "tracerag\models\document.py"      "ParsedDocument model output from parsers."
New-Stub "tracerag\models\query.py"         "QueryRequest model + QueryTier enum (DIRECT / SINGLE_HOP / MULTI_HOP)."
New-Stub "tracerag\models\response.py"      "QueryResponse + CitationBlock models."
New-Stub "tracerag\models\graph_node.py"    "GraphNode, GraphEdge, DependencySubgraph models."
New-Stub "tracerag\models\impact_report.py" "ImpactReport, AffectedFile, AffectedDoc models."
New-Stub "tracerag\models\session.py"       "SessionState + TurnHistory models."

# ingestion/
New-Stub "tracerag\ingestion\pipeline.py"  "Ingestion orchestrator: walk -> parse -> chunk -> prefix -> write. CLI entry point."
New-Stub "tracerag\ingestion\walker.py"    "Recursive workspace dir scanner. Filters by supported_extensions, skips skip_dirs."
New-Stub "tracerag\ingestion\metadata.py"  "Builds immutable ChunkMetadata: file_path, line_start, line_end, page_number, created_at."

# parsers/
New-Stub "tracerag\ingestion\parsers\base.py"            "BaseParser ABC. All parsers implement parse(path) -> ParsedDocument."
New-Stub "tracerag\ingestion\parsers\registry.py"        "Extension-to-parser mapping. Returns correct parser for a given file path."
New-Stub "tracerag\ingestion\parsers\code_parser.py"     "Handles .py .js .ts .java .sh .r — indentation and scope aware."
New-Stub "tracerag\ingestion\parsers\sql_parser.py"      "Handles .sql — isolates DDL blocks (CREATE TABLE, ALTER, etc.)."
New-Stub "tracerag\ingestion\parsers\pdf_parser.py"      "Handles .pdf via pypdf. Isolates tables as discrete blocks."
New-Stub "tracerag\ingestion\parsers\pptx_parser.py"     "Handles .pptx via python-pptx. Falls back to image_parser for visual slides."
New-Stub "tracerag\ingestion\parsers\markdown_parser.py" "Handles .md — heading-aware section splits."
New-Stub "tracerag\ingestion\parsers\config_parser.py"   "Handles .json .yaml .ini — preserves key hierarchy."
New-Stub "tracerag\ingestion\parsers\image_parser.py"    "Handles .png .jpg — vision model OCR fallback via Ollama."

# chunkers/
New-Stub "tracerag\ingestion\chunkers\base.py"         "BaseChunker ABC. All chunkers implement chunk(doc) -> List[Chunk]."
New-Stub "tracerag\ingestion\chunkers\parent_child.py" "Splits into child (150_to_200_tokens) + parent (800_to_1000_tokens) pairs. Core chunking logic."
New-Stub "tracerag\ingestion\chunkers\code_chunker.py" "Code-aware chunking — respects function and class boundaries."
New-Stub "tracerag\ingestion\chunkers\doc_chunker.py"  "Document-aware chunking — respects paragraph and section boundaries."

# context/
New-Stub "tracerag\ingestion\context\summarizer.py"    "Calls Ollama contextualizer model. Returns 1-sentence file/module summary."
New-Stub "tracerag\ingestion\context\prefix_builder.py" "Assembles prefixed chunk string: [CONTEXT]: ... + [CONTENT]: ..."

# retrieval/
New-Stub "tracerag\retrieval\pipeline.py" "Tier 2 entry point: dense -> sparse -> RRF fusion -> cross-encoder rerank."
New-Stub "tracerag\retrieval\dense.py"    "Vector similarity search via pgvector or Qdrant."
New-Stub "tracerag\retrieval\sparse.py"   "BM25 keyword search against keyword index."
New-Stub "tracerag\retrieval\fusion.py"   "RRF merge. Default k=60. Input: two ranked lists. Output: single fused list."
New-Stub "tracerag\retrieval\reranker.py" "HuggingFace cross-encoder. Scores top-30 candidates. Returns top-10."

# graph/
New-Stub "tracerag\graph\schema.py"       "Node and relationship type constants for Neo4j (SQL_COLUMN, PYTHON_FILE, etc.)."
New-Stub "tracerag\graph\extractor.py"    "Extracts repository entity names from query text via NER or regex."
New-Stub "tracerag\graph\builder.py"      "Writes graph nodes and edges to Neo4j on demand during Tier 3 queries."
New-Stub "tracerag\graph\query.py"        "Parameterised Cypher queries: neighborhood expansion (1-2 hops)."
New-Stub "tracerag\graph\neo4j_client.py" "Neo4j driver wrapper. Manages connection lifecycle and session pooling."

# orchestration/
New-Stub "tracerag\orchestration\router.py"     "3-tier query classifier. Assigns DIRECT / SINGLE_HOP / MULTI_HOP per query."
New-Stub "tracerag\orchestration\state.py"      "LangGraph AgentState TypedDict definition."
New-Stub "tracerag\orchestration\graph_flow.py" "LangGraph StateGraph: node wiring, edge conditions, fallback paths."
New-Stub "tracerag\orchestration\agent.py"      "Tier 3 agent loop. Selects and calls tools until answer assembled."
New-Stub "tracerag\orchestration\tools.py"      "Tool node implementations: hybrid_search / graph_expand / fetch_parent_chunk / synthesize."

# memory/
New-Stub "tracerag\memory\session.py"   "In-memory SessionState store. Scoped per conversation, not persisted."
New-Stub "tracerag\memory\rewriter.py"  "Rewrites vague follow-up queries into explicit retrieval prompts via LLM."

# impact/
New-Stub "tracerag\impact\analyzer.py" "Detects structural change scenarios from Tier 3 query context."
New-Stub "tracerag\impact\tracer.py"   "Graph traversal: upstream code dependents + downstream documentation references."
New-Stub "tracerag\impact\reporter.py" "Builds ImpactReport model. Renders terminal report via rich. Read-only."

# api/
New-Stub "tracerag\api\main.py"         "FastAPI app factory. Mounts routers, registers middleware, manages DB lifespan."
New-Stub "tracerag\api\dependencies.py" "FastAPI DI providers: settings, DB clients, session injection."
New-Stub "tracerag\api\routers\ingest.py" "POST /ingest — triggers ingestion pipeline on workspace path."
New-Stub "tracerag\api\routers\query.py"  "POST /query  — single-turn query entry point. Routes to orchestration layer."
New-Stub "tracerag\api\routers\impact.py" "POST /impact — returns structured ImpactReport for change scenario queries."
New-Stub "tracerag\api\routers\health.py" "GET  /health — liveness and readiness checks."
New-Stub "tracerag\api\middleware\logging.py" "Structured request/response logging middleware."
New-Stub "tracerag\api\middleware\timing.py"  "Injects X-Process-Time header per request."

# db/
New-Stub "tracerag\db\base.py"              "Shared DB connection lifecycle helpers."
New-Stub "tracerag\db\vector\client.py"     "Postgres+pgvector or Qdrant client wrapper. Provider selected from settings."
New-Stub "tracerag\db\vector\indexer.py"    "Chunk write and vector upsert operations."
New-Stub "tracerag\db\vector\search.py"     "Dense vector search queries."
New-Stub "tracerag\db\graph\client.py"      "Neo4j session wrapper."
New-Stub "tracerag\db\graph\queries.py"     "Parameterised Cypher query library."

New-File "tracerag\db\migrations\001_init_chunks.sql" @"
-- TraceRAG: chunks table with pgvector index
-- Run via psql or migration script
CREATE TABLE IF NOT EXISTS chunks (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id   UUID,
    file_path   TEXT NOT NULL,
    line_start  INT,
    line_end    INT,
    page_number INT,
    content     TEXT NOT NULL,
    context     TEXT,
    embedding   vector(768),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS chunks_embedding_idx
    ON chunks USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
"@

New-File "tracerag\db\migrations\002_init_metadata.sql" @"
-- TraceRAG: metadata constraints
ALTER TABLE chunks
    ADD CONSTRAINT chunks_file_path_not_empty CHECK (file_path <> '');

CREATE INDEX IF NOT EXISTS chunks_file_path_idx ON chunks (file_path);
CREATE INDEX IF NOT EXISTS chunks_parent_id_idx ON chunks (parent_id);
"@

# services/
New-Stub "tracerag\services\ollama.py"   "HTTP client for Ollama API at localhost:11434. Used by embedder and llm."
New-Stub "tracerag\services\embedder.py" "Embedding generation interface over ollama.py."
New-Stub "tracerag\services\llm.py"      "LLM generation interface. Routes to contextualizer or reasoning model per task."

# utils/
New-Stub "tracerag\utils\file_utils.py"  "Extension detection, path normalisation, workspace path validation."
New-Stub "tracerag\utils\token_utils.py" "tiktoken token counting helpers for chunk size enforcement."
New-Stub "tracerag\utils\hash_utils.py"  "SHA256 content hash for deduplication and change detection."
New-Stub "tracerag\utils\text_utils.py"  "Text cleaning, whitespace normalisation, context prefix assembly helpers."

Write-Host "    Application stubs written." -ForegroundColor Gray

# ─── 8. Tests ─────────────────────────────────────────────────────────────────
Write-Host "`n[6/8] Writing test stubs..." -ForegroundColor Cyan

New-File "tests\conftest.py" @"
"""
Shared pytest fixtures for TraceRAG test suite.
Available to all test modules automatically.

Fixtures to implement:
  - mock_ollama_client     : httpx mock for localhost:11434
  - in_memory_vector_store : mock vector DB returning deterministic results
  - sample_chunk           : minimal Chunk with valid metadata
  - sample_document        : minimal ParsedDocument
  - neo4j_stub             : mock Neo4j driver
  - python_workspace_path  : path to tests/fixtures/workspaces/python_project
  - mixed_workspace_path   : path to tests/fixtures/workspaces/mixed_repo
"""
import pytest
"@

# Unit test stubs
$unitTests = @(
    "tests\unit\ingestion\test_pipeline.py",
    "tests\unit\ingestion\test_parsers.py",
    "tests\unit\ingestion\test_chunkers.py",
    "tests\unit\ingestion\test_context_prefix.py",
    "tests\unit\retrieval\test_dense.py",
    "tests\unit\retrieval\test_sparse.py",
    "tests\unit\retrieval\test_fusion.py",
    "tests\unit\retrieval\test_reranker.py",
    "tests\unit\graph\test_extractor.py",
    "tests\unit\graph\test_builder.py",
    "tests\unit\graph\test_query.py",
    "tests\unit\orchestration\test_router.py",
    "tests\unit\orchestration\test_agent.py",
    "tests\unit\impact\test_analyzer.py",
    "tests\unit\impact\test_reporter.py"
)
foreach ($t in $unitTests) {
    New-File $t "# Unit tests -- implement per spec`nimport pytest`n"
}

New-File "tests\integration\test_ingest_and_query.py" @"
"""
Integration: full ingestion -> retrieval pipeline on fixture workspace.
Validates:
  - Chunk metadata fields populated correctly
  - Child chunks have context prefix
  - RRF output is ordered list of chunks
  - Reranker reduces to top-N
"""
import pytest
"@

New-File "tests\integration\test_tier3_graph_flow.py" @"
"""
Integration: Tier 3 router -> graph extraction -> LangGraph agent loop.
Validates:
  - Router correctly classifies multi-hop query as Tier 3
  - Graph extractor identifies entities from query
  - LangGraph agent completes loop and returns ImpactReport structure
"""
import pytest
"@

# Fixture workspace placeholders
New-File "tests\fixtures\workspaces\python_project\README.md" @"
# Python Project Fixture Workspace

Populate with representative files for ingestion tests:
  - auth.py         (Python code with function referencing user_status_id)
  - schema.sql      (SQL DDL with users table)
  - config.yaml     (App config with environment keys)
  - README.md       (Markdown docs)
"@

New-File "tests\fixtures\workspaces\mixed_repo\README.md" @"
# Mixed Repository Fixture Workspace

Multi-format workspace for integration and impact analysis tests:
  - auth.py         (.py with SQL column references)
  - schema.sql      (.sql DDL source of truth)
  - onboarding.pptx (.pptx with User Status Flow diagram)
  - README.md       (.md referencing user_status_id)
"@

Write-Host "    Test stubs written." -ForegroundColor Gray

# ─── 9. Evals ────────────────────────────────────────────────────────────────
Write-Host "`n[7/8] Writing eval stubs..." -ForegroundColor Cyan

New-File "evals\datasets\README.md" @"
# Evaluation Datasets

JSONL format. One query object per line:

  {
    "query": "What files reference users.user_status_id?",
    "expected_files": ["auth.py", "session.py"],
    "expected_tier": 3,
    "type": "impact_analysis"
  }

type values:
  - "direct"            Tier 1: no retrieval expected
  - "single_hop"        Tier 2: single-file lookup
  - "multi_hop"         Tier 3: cross-file dependency trace
  - "impact_analysis"   Tier 3: structural change scenario

Dataset files:
  - single_hop_retrieval.jsonl
  - multi_hop_dependency.jsonl
  - impact_analysis.jsonl
  - context_prefix_quality.jsonl
"@

New-File "evals\runners\run.py" @"
# Evaluation runner entry point.
# Usage: python -m evals.runners.run --dataset single_hop_retrieval
"@

New-File "evals\metrics\retrieval_metrics.py" @"
# Retrieval evaluation metrics.
# Implement: hit_rate_at_k, mrr, precision_at_k, recall_at_k
"@

New-File "evals\metrics\impact_metrics.py" @"
# Impact analysis evaluation metrics.
# Implement: dependency_recall, false_positive_rate, report_completeness_score
"@

New-File "evals\metrics\citation_metrics.py" @"
# Citation correctness metrics.
# Implement: metadata_match_rate, hallucination_rate
"@

New-File "logs\.gitkeep" ""
New-File "docs\architecture.md" @"
# TraceRAG Architecture

Refer to the engineering specification for full module descriptions.

Configuration: config/default.yaml
Settings model: tracerag/core/settings.py
"@

Write-Host "    Eval stubs written." -ForegroundColor Gray

# ─── 10. Verify ───────────────────────────────────────────────────────────────
Write-Host "`n[8/8] Verifying scaffold..." -ForegroundColor Cyan

$fileCount = (Get-ChildItem -Path $ROOT -Recurse -File).Count
$dirCount  = (Get-ChildItem -Path $ROOT -Recurse -Directory).Count

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║         TraceRAG scaffold complete                   ║" -ForegroundColor Green
Write-Host "╠══════════════════════════════════════════════════════╣" -ForegroundColor Green
Write-Host "║  Root     : $ROOT" -ForegroundColor Green
Write-Host "║  Dirs     : $dirCount" -ForegroundColor Green
Write-Host "║  Files    : $fileCount" -ForegroundColor Green
Write-Host "╠══════════════════════════════════════════════════════╣" -ForegroundColor Green
Write-Host "║  Next steps:                                         ║" -ForegroundColor Cyan
Write-Host "║  1. cd tracerag                                      ║" -ForegroundColor Cyan
Write-Host "║  2. Copy .env.example to .env and fill passwords     ║" -ForegroundColor Cyan
Write-Host "║  3. pip install -e .[dev,evals]                      ║" -ForegroundColor Cyan
Write-Host "║  4. .\scripts\pull_models.ps1  (Ollama models)       ║" -ForegroundColor Cyan
Write-Host "║  5. docker compose up -d postgres neo4j              ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Green