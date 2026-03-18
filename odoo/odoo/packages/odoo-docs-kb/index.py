"""
Odoo 19 Documentation Indexer

Azure AI Search index manager per agents/knowledge/odoo19_docs/indexing.yaml.
Supports full and incremental indexing with upsert/delete operations.
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import yaml
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
)

from .chunker import Chunk
from .embed import EmbeddingResult

logger = logging.getLogger(__name__)


class AzureSearchIndexer:
    """Manage Azure AI Search index for Odoo 19 docs."""

    def __init__(
        self,
        config_path: str = "agents/knowledge/odoo19_docs/indexing.yaml",
    ):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        idx = self.config["index"]
        self.index_name = idx["index_name"]
        self.dimensions = idx["embedding"]["dimensions"]

        endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
        key = os.environ["AZURE_SEARCH_API_KEY"]
        credential = AzureKeyCredential(key)

        self.index_client = SearchIndexClient(
            endpoint=endpoint, credential=credential
        )
        self.search_client = SearchClient(
            endpoint=endpoint,
            index_name=self.index_name,
            credential=credential,
        )

        self.manifest_path = self.config.get("incremental", {}).get(
            "tracking", {}
        ).get("manifest_path", "agents/knowledge/odoo19_docs/.index_manifest.json")

    def ensure_index(self) -> None:
        """Create or update the search index schema."""
        fields = [
            SimpleField(
                name="chunk_id",
                type=SearchFieldDataType.String,
                key=True,
                filterable=True,
            ),
            SearchableField(
                name="content",
                type=SearchFieldDataType.String,
                analyzer_name="en.microsoft",
            ),
            SearchField(
                name="content_vector",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=self.dimensions,
                vector_search_profile_name="odoo19-vector-profile",
            ),
            SimpleField(
                name="path",
                type=SearchFieldDataType.String,
                filterable=True,
                facetable=True,
            ),
            SearchableField(
                name="heading_chain",
                type=SearchFieldDataType.String,
                filterable=True,
            ),
            SimpleField(
                name="version",
                type=SearchFieldDataType.String,
                filterable=True,
            ),
            SimpleField(
                name="product",
                type=SearchFieldDataType.String,
                filterable=True,
            ),
            SimpleField(
                name="source_type",
                type=SearchFieldDataType.String,
                filterable=True,
            ),
            SimpleField(
                name="repo",
                type=SearchFieldDataType.String,
                filterable=True,
            ),
            SimpleField(
                name="branch",
                type=SearchFieldDataType.String,
                filterable=True,
            ),
            SimpleField(
                name="ordinal",
                type=SearchFieldDataType.Int32,
                sortable=True,
            ),
            SimpleField(
                name="content_hash",
                type=SearchFieldDataType.String,
                filterable=True,
            ),
            SimpleField(
                name="indexed_at",
                type=SearchFieldDataType.DateTimeOffset,
                sortable=True,
            ),
            SimpleField(
                name="source_commit",
                type=SearchFieldDataType.String,
                filterable=True,
            ),
        ]

        vector_search = VectorSearch(
            algorithms=[
                HnswAlgorithmConfiguration(name="odoo19-hnsw"),
            ],
            profiles=[
                VectorSearchProfile(
                    name="odoo19-vector-profile",
                    algorithm_configuration_name="odoo19-hnsw",
                ),
            ],
        )

        index = SearchIndex(
            name=self.index_name,
            fields=fields,
            vector_search=vector_search,
        )

        self.index_client.create_or_update_index(index)
        logger.info("Index '%s' ensured", self.index_name)

    def upsert_chunks(
        self,
        chunks: list[Chunk],
        embeddings: list[EmbeddingResult],
        source_commit: str,
    ) -> int:
        """Upsert chunks with their embeddings into the index.

        Returns number of documents upserted.
        """
        embedding_map = {e.chunk_id: e.vector for e in embeddings}
        now = datetime.now(timezone.utc).isoformat()

        documents = []
        for chunk in chunks:
            vector = embedding_map.get(chunk.chunk_id)
            if vector is None:
                logger.warning(
                    "No embedding for chunk %s, skipping", chunk.chunk_id
                )
                continue

            documents.append(
                {
                    "chunk_id": chunk.chunk_id,
                    "content": chunk.content,
                    "content_vector": vector,
                    "path": chunk.path,
                    "heading_chain": chunk.heading_chain,
                    "version": chunk.metadata.get("version", "19.0"),
                    "product": chunk.metadata.get("product", "odoo"),
                    "source_type": chunk.metadata.get(
                        "source_type", "documentation"
                    ),
                    "repo": chunk.metadata.get("repo", "odoo/documentation"),
                    "branch": chunk.metadata.get("branch", "19.0"),
                    "ordinal": chunk.ordinal,
                    "content_hash": chunk.content_hash,
                    "indexed_at": now,
                    "source_commit": source_commit,
                }
            )

        if not documents:
            return 0

        # Batch upload (Azure SDK handles batching internally)
        result = self.search_client.upload_documents(documents)
        succeeded = sum(1 for r in result if r.succeeded)
        failed = len(result) - succeeded

        if failed:
            logger.warning("%d documents failed to index", failed)

        logger.info(
            "Upserted %d documents (commit: %s)", succeeded, source_commit[:8]
        )
        return succeeded

    def delete_by_path_prefix(self, path_prefix: str) -> int:
        """Delete all chunks matching a path prefix.

        Returns number of documents deleted.
        """
        # Search for matching documents
        results = self.search_client.search(
            search_text="*",
            filter=f"path ge '{path_prefix}' and path lt '{path_prefix}~'",
            select=["chunk_id"],
            top=1000,
        )

        chunk_ids = [r["chunk_id"] for r in results]
        if not chunk_ids:
            return 0

        documents = [{"chunk_id": cid} for cid in chunk_ids]
        result = self.search_client.delete_documents(documents)
        deleted = sum(1 for r in result if r.succeeded)

        logger.info(
            "Deleted %d documents with path prefix '%s'",
            deleted,
            path_prefix,
        )
        return deleted

    def load_manifest(self) -> dict:
        """Load the index manifest (tracks last indexed commit + file hashes)."""
        path = Path(self.manifest_path)
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return {"last_indexed_commit": None, "file_hashes": {}}

    def save_manifest(
        self, commit: str, file_hashes: dict[str, str]
    ) -> None:
        """Save updated manifest after indexing."""
        path = Path(self.manifest_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        manifest = {
            "last_indexed_commit": commit,
            "file_hashes": file_hashes,
            "indexed_at": datetime.now(timezone.utc).isoformat(),
        }

        with open(path, "w") as f:
            json.dump(manifest, f, indent=2)

        logger.info("Manifest saved: commit=%s, files=%d", commit[:8], len(file_hashes))

    def get_index_stats(self) -> dict:
        """Get basic index statistics."""
        try:
            index = self.index_client.get_index(self.index_name)
            stats = self.index_client.get_index_statistics(self.index_name)
            return {
                "name": index.name,
                "document_count": stats.document_count,
                "storage_size": stats.storage_size,
            }
        except Exception as e:
            logger.error("Failed to get index stats: %s", e)
            return {"error": str(e)}
