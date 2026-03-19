#!/usr/bin/env python3
"""Populate Azure AI Search index from knowledge base markdown files.

Reads all markdown files from agents/knowledge-base/, chunks content,
extracts YAML frontmatter, creates the index if missing, and uploads
documents in batches.

Environment variables required:
    AZURE_SEARCH_ENDPOINT  — e.g. https://srch-ipai-dev.search.windows.net/
    AZURE_SEARCH_API_KEY   — admin API key (vaulted at kv-ipai-dev)

Usage:
    export AZURE_SEARCH_ENDPOINT="https://srch-ipai-dev.search.windows.net/"
    export AZURE_SEARCH_API_KEY="$(az keyvault secret show --vault-name kv-ipai-dev --name srch-ipai-dev-api-key --query value -o tsv)"
    python scripts/ai-search/populate-index.py
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

INDEX_NAME = "ipai-knowledge-base"
SCHEMA_PATH = Path(__file__).resolve().parents[2] / "agents" / "knowledge-base" / "index-schema.json"
KB_ROOT = Path(__file__).resolve().parents[2] / "agents" / "knowledge-base"
API_VERSION = "2024-07-01"
CHUNK_SIZE = 2000  # max characters per chunk
CHUNK_OVERLAP = 200  # overlap between chunks
BATCH_SIZE = 100  # documents per upload batch

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------


def _require_env(name: str) -> str:
    """Return an environment variable or exit with a clear message."""
    value = os.environ.get(name, "").strip()
    if not value:
        log.error("Missing required environment variable: %s", name)
        sys.exit(1)
    return value


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------


class SearchClient:
    """Minimal Azure AI Search REST client using only stdlib + requests."""

    def __init__(self, endpoint: str, api_key: str) -> None:
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "api-key": self.api_key,
            }
        )

    def _url(self, path: str, extra_params: dict[str, str] | None = None) -> str:
        params = {"api-version": API_VERSION}
        if extra_params:
            params.update(extra_params)
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.endpoint}{path}?{qs}"

    # -- Index management ---------------------------------------------------

    def index_exists(self, name: str) -> bool:
        resp = self.session.get(self._url(f"/indexes/{name}"))
        return resp.status_code == 200

    def create_index(self, schema: dict[str, Any]) -> None:
        url = self._url("/indexes")
        resp = self.session.post(url, json=schema)
        if resp.status_code in (200, 201):
            log.info("Index '%s' created successfully.", schema["name"])
        else:
            log.error(
                "Failed to create index: %s %s", resp.status_code, resp.text
            )
            sys.exit(1)

    def delete_all_documents(self, name: str) -> None:
        """Not used by default — included for convenience."""
        pass

    # -- Document upload ----------------------------------------------------

    def upload_documents(self, index_name: str, documents: list[dict[str, Any]]) -> int:
        """Upload documents in batches. Returns total uploaded count."""
        url = self._url(f"/indexes/{index_name}/docs/index")
        uploaded = 0

        for i in range(0, len(documents), BATCH_SIZE):
            batch = documents[i : i + BATCH_SIZE]
            payload = {
                "value": [
                    {**doc, "@search.action": "mergeOrUpload"} for doc in batch
                ]
            }
            resp = self.session.post(url, json=payload)
            if resp.status_code in (200, 207):
                result = resp.json()
                success_count = sum(
                    1 for r in result.get("value", []) if r.get("statusCode") == 200 or r.get("statusCode") == 201
                )
                uploaded += success_count
                failed = len(batch) - success_count
                if failed > 0:
                    log.warning(
                        "Batch %d-%d: %d succeeded, %d failed.",
                        i, i + len(batch), success_count, failed,
                    )
                else:
                    log.info(
                        "Batch %d-%d: %d documents uploaded.",
                        i, i + len(batch), success_count,
                    )
            else:
                log.error(
                    "Batch upload failed: %s %s", resp.status_code, resp.text[:500]
                )
        return uploaded

    # -- Query (for validation) ---------------------------------------------

    def count_documents(self, index_name: str) -> int:
        url = self._url(f"/indexes/{index_name}/docs/$count")
        resp = self.session.get(url)
        if resp.status_code == 200:
            try:
                return int(resp.text)
            except ValueError:
                return 0
        return 0


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(
    r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL
)


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Extract YAML-like frontmatter and return (metadata, body).

    Uses simple key-value parsing to avoid requiring PyYAML.
    Supports string values, lists (JSON-style), and bare values.
    """
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}, text

    raw = match.group(1)
    body = text[match.end():]
    meta: dict[str, Any] = {}

    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()

        # Remove surrounding quotes
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]

        # Try JSON parse for lists
        if value.startswith("["):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                pass

        meta[key] = value

    return meta, body


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------


def chunk_text(text: str, max_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into chunks of max_size characters with overlap.

    Splits on paragraph boundaries (double newline) first, then on sentence
    boundaries, falling back to hard character splits.
    """
    if len(text) <= max_size:
        return [text]

    # Split into paragraphs
    paragraphs = re.split(r"\n{2,}", text)
    chunks: list[str] = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # If adding this paragraph would exceed the limit
        if len(current_chunk) + len(para) + 2 > max_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
                # Start new chunk with overlap from the end of the previous
                if overlap > 0 and len(current_chunk) > overlap:
                    current_chunk = current_chunk[-overlap:] + "\n\n" + para
                else:
                    current_chunk = para
            else:
                # Single paragraph exceeds max_size — split by sentences
                sentences = re.split(r"(?<=[.!?])\s+", para)
                sub_chunk = ""
                for sent in sentences:
                    if len(sub_chunk) + len(sent) + 1 > max_size:
                        if sub_chunk:
                            chunks.append(sub_chunk.strip())
                            if overlap > 0 and len(sub_chunk) > overlap:
                                sub_chunk = sub_chunk[-overlap:] + " " + sent
                            else:
                                sub_chunk = sent
                        else:
                            # Single sentence exceeds max_size — hard split
                            for j in range(0, len(sent), max_size - overlap):
                                chunks.append(sent[j : j + max_size])
                            sub_chunk = ""
                    else:
                        sub_chunk = sub_chunk + " " + sent if sub_chunk else sent
                if sub_chunk:
                    current_chunk = sub_chunk
        else:
            current_chunk = current_chunk + "\n\n" + para if current_chunk else para

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


# ---------------------------------------------------------------------------
# Document generation
# ---------------------------------------------------------------------------


def generate_doc_id(source_file: str, chunk_index: int) -> str:
    """Generate a stable, URL-safe document ID."""
    raw = f"{source_file}::chunk-{chunk_index}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def process_markdown_files(kb_root: Path) -> list[dict[str, Any]]:
    """Read all markdown files under kb_root and return search documents."""
    documents: list[dict[str, Any]] = []

    md_files = sorted(kb_root.rglob("*.md"))
    log.info("Found %d markdown files in %s", len(md_files), kb_root)

    for md_path in md_files:
        rel_path = md_path.relative_to(kb_root)
        log.info("Processing: %s", rel_path)

        text = md_path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(text)

        title = meta.get("title", md_path.stem.replace("-", " ").title())
        kb_scope = meta.get("kb_scope", rel_path.parts[0] if len(rel_path.parts) > 1 else "unknown")
        group_ids = meta.get("group_ids", ["group-guid-placeholder"])
        last_updated = meta.get("last_updated", "2026-03-15")

        if isinstance(group_ids, str):
            group_ids = [group_ids]

        # Ensure last_updated is in ISO 8601 format
        if "T" not in last_updated:
            last_updated = f"{last_updated}T00:00:00Z"

        chunks = chunk_text(body)
        log.info("  -> %d chunks generated", len(chunks))

        for i, chunk in enumerate(chunks):
            doc = {
                "id": generate_doc_id(str(rel_path), i),
                "title": title,
                "content": chunk,
                "kb_scope": kb_scope,
                "group_ids": group_ids,
                "source_file": str(rel_path),
                "chunk_index": i,
                "last_updated": last_updated,
            }
            documents.append(doc)

    return documents


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    log.info("=" * 60)
    log.info("Azure AI Search — Knowledge Base Population")
    log.info("=" * 60)

    endpoint = _require_env("AZURE_SEARCH_ENDPOINT")
    api_key = _require_env("AZURE_SEARCH_API_KEY")

    log.info("Endpoint: %s", endpoint)
    log.info("Index: %s", INDEX_NAME)
    log.info("KB root: %s", KB_ROOT)

    client = SearchClient(endpoint, api_key)

    # Step 1: Create index if it does not exist
    if client.index_exists(INDEX_NAME):
        log.info("Index '%s' already exists.", INDEX_NAME)
    else:
        log.info("Index '%s' does not exist. Creating...", INDEX_NAME)
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        client.create_index(schema)

    # Step 2: Process markdown files
    documents = process_markdown_files(KB_ROOT)
    log.info("Total documents to upload: %d", len(documents))

    if not documents:
        log.warning("No documents found. Exiting.")
        sys.exit(0)

    # Step 3: Upload documents
    uploaded = client.upload_documents(INDEX_NAME, documents)
    log.info("Upload complete. %d documents uploaded.", uploaded)

    # Step 4: Verify count
    count = client.count_documents(INDEX_NAME)
    log.info("Index document count: %d", count)

    log.info("=" * 60)
    log.info("Done.")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
