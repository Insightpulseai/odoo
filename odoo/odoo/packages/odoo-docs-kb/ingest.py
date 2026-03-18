"""
Unified Ingestion Pipeline for Org Documentation

Orchestrates discovery, chunking, embedding, and indexing for all
org documentation sources: repo docs, spec bundles, and web docs.

Reuses existing components:
- MarkdownChunker (md_chunker.py) for .md files
- RSTHeadingChunker (chunker.py) for .rst files
- AzureEmbedder (embed.py) for embeddings
- AzureSearchIndexer (index.py) for Azure AI Search

New sources:
- RepoDocsLoader (repo_loader.py) for local repo docs
- SpecBundleLoader (spec_loader.py) for spec bundles
"""

import hashlib
import json
import logging
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from .chunker import Chunk, RSTHeadingChunker
from .md_chunker import MarkdownChunker
from .repo_loader import RepoDocsLoader, RepoDoc
from .spec_loader import SpecBundleLoader, SpecDoc

logger = logging.getLogger(__name__)

# Default config
DEFAULT_CONFIG = {
    "index_name": "org-docs",
    "chunk_size_target": 1500,
    "chunk_overlap": 200,
    "min_chunk_tokens": 50,
    "manifest_path": "agents/knowledge/org_docs/.index_manifest.json",
}


class OrgDocsIngestor:
    """Unified ingestion pipeline for all org documentation sources."""

    def __init__(self, repo_root: str, config: dict | None = None):
        """
        Args:
            repo_root: Path to repo root.
            config: Configuration dict with keys:
                index_name: Target index name (default: "org-docs")
                chunk_size_target: Target chunk size in tokens
                chunk_overlap: Overlap tokens between chunks
                manifest_path: Path for manifest file
        """
        self.repo_root = Path(repo_root).resolve()
        self.config = {**DEFAULT_CONFIG, **(config or {})}

        # Initialize loaders
        self.repo_loader = RepoDocsLoader(repo_root=str(self.repo_root))
        self.spec_loader = SpecBundleLoader(repo_root=str(self.repo_root))

        # Initialize chunkers (no config file dependency for standalone use)
        self.md_chunker = MarkdownChunker(
            max_chunk_tokens=self.config["chunk_size_target"],
            overlap_tokens=self.config["chunk_overlap"],
            min_chunk_tokens=self.config["min_chunk_tokens"],
            id_template="{source}:{path}:{heading_chain}:{ordinal}:{content_hash_8}",
        )

        # Embedder and indexer are lazily initialized (require env vars)
        self._embedder = None
        self._indexer = None

        self.manifest_path = self.repo_root / self.config["manifest_path"]

    @property
    def embedder(self):
        """Lazy-init embedder (requires Azure OpenAI env vars)."""
        if self._embedder is None:
            from .embed import AzureEmbedder
            self._embedder = AzureEmbedder(batch_size=100)
        return self._embedder

    @property
    def indexer(self):
        """Lazy-init indexer (requires Azure Search env vars)."""
        if self._indexer is None:
            from .index import AzureSearchIndexer
            # Create a minimal config for the indexer
            self._indexer = _create_org_indexer(
                self.config["index_name"],
                str(self.manifest_path),
            )
        return self._indexer

    def _get_head_commit(self) -> str:
        """Get current HEAD commit SHA."""
        try:
            result = subprocess.run(
                ["git", "-C", str(self.repo_root), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "unknown"

    def _chunk_doc(self, path: str, content: str, metadata: dict) -> list[Chunk]:
        """Chunk a document using the appropriate chunker."""
        if path.endswith(".rst"):
            # RST chunker requires config file; use md_chunker as fallback
            # since most org docs are markdown
            return self.md_chunker.chunk(path, content, metadata)
        else:
            return self.md_chunker.chunk(path, content, metadata)

    def _repo_doc_to_chunks(self, doc: RepoDoc) -> list[Chunk]:
        """Convert a RepoDoc to chunks."""
        return self._chunk_doc(doc.path, doc.content, doc.metadata)

    def _spec_doc_to_chunks(self, doc: SpecDoc) -> list[Chunk]:
        """Convert a SpecDoc to chunks."""
        metadata = {
            **doc.metadata,
            "source": "spec-bundle",
            "bundle": doc.bundle_name,
            "doc_role": doc.doc_role,
        }
        return self._chunk_doc(doc.path, doc.content, metadata)

    def ingest_repo_docs(
        self,
        incremental: bool = True,
        since_commit: str | None = None,
        dry_run: bool = False,
    ) -> dict:
        """Ingest repo documentation (Markdown files).

        Args:
            incremental: If True, only process changed files.
            since_commit: Git ref for incremental mode.
            dry_run: If True, chunk but don't embed/index.

        Returns:
            Dict with stats: files_found, chunks_created, docs_indexed.
        """
        manifest = self.load_manifest()

        if incremental and since_commit is None:
            since_commit = manifest.get("repo_docs_commit")

        if incremental and since_commit:
            docs = self.repo_loader.load_changed(since_commit=since_commit)
        else:
            docs = self.repo_loader.discover()

        all_chunks = []
        for doc in docs:
            chunks = self._repo_doc_to_chunks(doc)
            all_chunks.extend(chunks)

        stats = {
            "source": "repo-docs",
            "files_found": len(docs),
            "chunks_created": len(all_chunks),
            "docs_indexed": 0,
            "incremental": incremental,
        }

        if dry_run or not all_chunks:
            logger.info(
                "Repo docs: %d files, %d chunks%s",
                len(docs), len(all_chunks),
                " (dry run)" if dry_run else " (no chunks)",
            )
            return stats

        # Embed and index
        stats["docs_indexed"] = self._embed_and_index(all_chunks)

        # Update manifest
        head = self._get_head_commit()
        manifest["repo_docs_commit"] = head
        manifest["repo_docs_last_run"] = datetime.now(timezone.utc).isoformat()
        manifest["repo_docs_file_count"] = len(docs)
        self._save_manifest(manifest)

        return stats

    def ingest_spec_bundles(
        self,
        incremental: bool = True,
        dry_run: bool = False,
    ) -> dict:
        """Ingest spec bundles.

        Args:
            incremental: If True, only process bundles with changed hashes.
            dry_run: If True, chunk but don't embed/index.

        Returns:
            Dict with stats.
        """
        manifest = self.load_manifest()
        prev_hashes = manifest.get("spec_file_hashes", {})

        all_spec_docs = self.spec_loader.load_all()

        # Filter to changed docs in incremental mode
        if incremental and prev_hashes:
            changed_docs = [
                doc for doc in all_spec_docs
                if prev_hashes.get(doc.path) != doc.file_hash
            ]
        else:
            changed_docs = all_spec_docs

        all_chunks = []
        for doc in changed_docs:
            chunks = self._spec_doc_to_chunks(doc)
            all_chunks.extend(chunks)

        stats = {
            "source": "spec-bundles",
            "files_found": len(changed_docs),
            "total_spec_files": len(all_spec_docs),
            "chunks_created": len(all_chunks),
            "docs_indexed": 0,
            "incremental": incremental,
        }

        if dry_run or not all_chunks:
            logger.info(
                "Spec bundles: %d/%d files changed, %d chunks%s",
                len(changed_docs), len(all_spec_docs), len(all_chunks),
                " (dry run)" if dry_run else " (no chunks)",
            )
            return stats

        # Embed and index
        stats["docs_indexed"] = self._embed_and_index(all_chunks)

        # Update manifest with all spec file hashes
        manifest["spec_file_hashes"] = {
            doc.path: doc.file_hash for doc in all_spec_docs
        }
        manifest["spec_bundles_last_run"] = datetime.now(timezone.utc).isoformat()
        self._save_manifest(manifest)

        return stats

    def ingest_all(
        self,
        incremental: bool = True,
        since_commit: str | None = None,
        dry_run: bool = False,
    ) -> dict:
        """Run full ingestion pipeline.

        Args:
            incremental: If True, only process changed files.
            since_commit: Git ref for incremental mode (repo docs only).
            dry_run: If True, chunk but don't embed/index.

        Returns:
            Dict with combined stats from all sources.
        """
        logger.info(
            "Starting %s ingestion (dry_run=%s)",
            "incremental" if incremental else "full",
            dry_run,
        )

        repo_stats = self.ingest_repo_docs(
            incremental=incremental,
            since_commit=since_commit,
            dry_run=dry_run,
        )
        spec_stats = self.ingest_spec_bundles(
            incremental=incremental,
            dry_run=dry_run,
        )

        combined = {
            "repo_docs": repo_stats,
            "spec_bundles": spec_stats,
            "totals": {
                "files_found": repo_stats["files_found"] + spec_stats["files_found"],
                "chunks_created": repo_stats["chunks_created"] + spec_stats["chunks_created"],
                "docs_indexed": repo_stats["docs_indexed"] + spec_stats["docs_indexed"],
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "incremental": incremental,
        }

        logger.info(
            "Ingestion complete: %d files, %d chunks, %d indexed",
            combined["totals"]["files_found"],
            combined["totals"]["chunks_created"],
            combined["totals"]["docs_indexed"],
        )

        return combined

    def _embed_and_index(self, chunks: list[Chunk]) -> int:
        """Embed chunks and upsert to index. Returns count indexed."""
        if not chunks:
            return 0

        texts = [c.content for c in chunks]
        ids = [c.chunk_id for c in chunks]

        embeddings = self.embedder.embed_texts(texts, ids)

        self.indexer.ensure_index()
        commit = self._get_head_commit()
        return self.indexer.upsert_chunks(chunks, embeddings, commit)

    def load_manifest(self) -> dict:
        """Load the ingestion manifest."""
        if self.manifest_path.exists():
            with open(self.manifest_path) as f:
                return json.load(f)
        return {}

    def _save_manifest(self, manifest: dict) -> None:
        """Save the ingestion manifest."""
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
        with open(self.manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        logger.info("Manifest saved to %s", self.manifest_path)

    def get_manifest(self) -> dict:
        """Return current index manifest with source tracking."""
        manifest = self.load_manifest()
        manifest["repo_root"] = str(self.repo_root)
        manifest["index_name"] = self.config["index_name"]
        manifest["current_commit"] = self._get_head_commit()
        return manifest


def _create_org_indexer(index_name: str, manifest_path: str):
    """Create an AzureSearchIndexer with inline config (no YAML dependency)."""
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import SearchClient
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import (
        HnswAlgorithmConfiguration,
        SearchableField,
        SearchField,
        SearchFieldDataType,
        SearchIndex,
        SimpleField,
        VectorSearch,
        VectorSearchProfile,
    )

    endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
    key = os.environ["AZURE_SEARCH_API_KEY"]
    credential = AzureKeyCredential(key)

    class _OrgIndexer:
        """Lightweight indexer for org docs (no YAML config dependency)."""

        def __init__(self):
            self.index_name = index_name
            self.dimensions = 1536
            self.manifest_path = manifest_path
            self.index_client = SearchIndexClient(
                endpoint=endpoint, credential=credential
            )
            self.search_client = SearchClient(
                endpoint=endpoint,
                index_name=index_name,
                credential=credential,
            )

        def ensure_index(self):
            fields = [
                SimpleField(name="chunk_id", type=SearchFieldDataType.String, key=True, filterable=True),
                SearchableField(name="content", type=SearchFieldDataType.String, analyzer_name="en.microsoft"),
                SearchField(
                    name="content_vector",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=self.dimensions,
                    vector_search_profile_name="org-docs-vector-profile",
                ),
                SimpleField(name="path", type=SearchFieldDataType.String, filterable=True, facetable=True),
                SearchableField(name="heading_chain", type=SearchFieldDataType.String, filterable=True),
                SimpleField(name="source", type=SearchFieldDataType.String, filterable=True),
                SimpleField(name="source_type", type=SearchFieldDataType.String, filterable=True),
                SimpleField(name="bundle", type=SearchFieldDataType.String, filterable=True),
                SimpleField(name="doc_role", type=SearchFieldDataType.String, filterable=True),
                SimpleField(name="repo", type=SearchFieldDataType.String, filterable=True),
                SimpleField(name="branch", type=SearchFieldDataType.String, filterable=True),
                SimpleField(name="ordinal", type=SearchFieldDataType.Int32, sortable=True),
                SimpleField(name="content_hash", type=SearchFieldDataType.String, filterable=True),
                SimpleField(name="indexed_at", type=SearchFieldDataType.DateTimeOffset, sortable=True),
                SimpleField(name="source_commit", type=SearchFieldDataType.String, filterable=True),
            ]

            vector_search = VectorSearch(
                algorithms=[HnswAlgorithmConfiguration(name="org-docs-hnsw")],
                profiles=[
                    VectorSearchProfile(
                        name="org-docs-vector-profile",
                        algorithm_configuration_name="org-docs-hnsw",
                    )
                ],
            )

            index = SearchIndex(name=self.index_name, fields=fields, vector_search=vector_search)
            self.index_client.create_or_update_index(index)
            logger.info("Index '%s' ensured", self.index_name)

        def upsert_chunks(self, chunks, embeddings, source_commit):
            from .embed import EmbeddingResult
            embedding_map = {e.chunk_id: e.vector for e in embeddings}
            now = datetime.now(timezone.utc).isoformat()

            documents = []
            for chunk in chunks:
                vector = embedding_map.get(chunk.chunk_id)
                if vector is None:
                    continue

                documents.append({
                    "chunk_id": chunk.chunk_id,
                    "content": chunk.content,
                    "content_vector": vector,
                    "path": chunk.path,
                    "heading_chain": chunk.heading_chain,
                    "source": chunk.metadata.get("source", "unknown"),
                    "source_type": chunk.metadata.get("source_type", "internal-docs"),
                    "bundle": chunk.metadata.get("bundle", ""),
                    "doc_role": chunk.metadata.get("doc_role", ""),
                    "repo": chunk.metadata.get("repo", "Insightpulseai/odoo"),
                    "branch": chunk.metadata.get("branch", "main"),
                    "ordinal": chunk.ordinal,
                    "content_hash": chunk.content_hash,
                    "indexed_at": now,
                    "source_commit": source_commit,
                })

            if not documents:
                return 0

            result = self.search_client.upload_documents(documents)
            succeeded = sum(1 for r in result if r.succeeded)
            logger.info("Upserted %d documents (commit: %s)", succeeded, source_commit[:8])
            return succeeded

    return _OrgIndexer()
