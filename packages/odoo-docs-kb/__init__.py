# Odoo 18 Documentation Knowledge Base
# Ingestion, chunking, embedding, and indexing for Odoo docs RAG

from .chunker import Chunk, RSTHeadingChunker
from .loader import DocFile, OdooDocsLoader
from .md_chunker import MarkdownChunker
from .repo_loader import RepoDoc, RepoDocsLoader
from .spec_loader import SpecBundleLoader, SpecDoc
from .ingest import OrgDocsIngestor

__all__ = [
    "Chunk",
    "DocFile",
    "MarkdownChunker",
    "OdooDocsLoader",
    "OrgDocsIngestor",
    "RepoDoc",
    "RepoDocsLoader",
    "RSTHeadingChunker",
    "SpecBundleLoader",
    "SpecDoc",
]
