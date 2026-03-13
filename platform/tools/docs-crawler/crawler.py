#!/usr/bin/env python3
"""
Kapa-style docs crawler for Odoo CE + OCA 18.0
Multi-source ingestion with versioning, structure-aware chunking, hybrid retrieval
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
from collections import deque
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse, urldefrag

import requests
import yaml
from bs4 import BeautifulSoup


UA = "odoo-docs-crawler/1.0 (+https://insightpulseai.com)"
SKIP_EXT = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".pdf",
            ".zip", ".gz", ".tar", ".tgz", ".mp4", ".mov", ".avi", ".webm")


@dataclass
class Document:
    source_type: str
    source_url: str
    canonical_url: str
    title: str
    content: str
    metadata: dict
    doc_version: str
    commit_sha: Optional[str]
    visibility: str
    content_checksum: str


@dataclass
class Chunk:
    content: str
    chunk_index: int
    section_path: Optional[str]
    metadata: dict
    language: str = 'en'
    embedding_model: str = 'text-embedding-3-small'


class SourceConnector:
    """Base class for source connectors"""

    def __init__(self, config: dict):
        self.config = config
        self.name = config['name']
        self.doc_version = config['doc_version']
        self.visibility = config['visibility']

    def crawl(self) -> List[Document]:
        raise NotImplementedError


class SitemapConnector(SourceConnector):
    """Crawl documentation from sitemap.xml"""

    def __init__(self, config: dict):
        super().__init__(config)
        self.canonical_url_prefix = config['canonical_url_prefix']
        self.sitemap_urls = config['sitemap_urls']
        self.include_patterns = config.get('include_patterns', [])
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": UA})

    def norm_url(self, u: str) -> str:
        u, _frag = urldefrag(u)
        return u.rstrip("/")

    def looks_like_doc(self, url: str) -> bool:
        p = urlparse(url)
        if not p.scheme.startswith("http"):
            return False
        if any(p.path.lower().endswith(ext) for ext in SKIP_EXT):
            return False

        # Check include patterns
        if self.include_patterns:
            return any(re.match(pattern.replace('**', '.*'), url)
                      for pattern in self.include_patterns)
        return True

    def extract_section_path(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract hierarchical section path from headings"""
        headings = []
        for tag in ['h1', 'h2', 'h3']:
            h = soup.find(tag)
            if h:
                text = h.get_text(" ", strip=True)
                headings.append(text)
        return " > ".join(headings) if headings else None

    def fetch_page(self, url: str) -> Optional[Document]:
        """Fetch and parse a single documentation page"""
        try:
            r = self.session.get(url, timeout=20)
            if r.status_code != 200:
                return None

            soup = BeautifulSoup(r.text, "html.parser")

            # Extract title
            title = (soup.title.get_text(" ", strip=True)
                    if soup.title else url.split('/')[-1])

            # Extract main content (remove nav, footer, scripts)
            for tag in soup.find_all(['nav', 'footer', 'script', 'style', 'aside']):
                tag.decompose()

            main = soup.find('main') or soup.find('article') or soup.body
            content = main.get_text("\n", strip=True) if main else ""

            # Extract section path
            section_path = self.extract_section_path(soup)

            # Compute checksum
            checksum = hashlib.sha256(content.encode('utf-8')).hexdigest()

            return Document(
                source_type=self.name,
                source_url=url,
                canonical_url=url,
                title=title[:300],
                content=content,
                metadata={
                    'section_path': section_path,
                    'word_count': len(content.split())
                },
                doc_version=self.doc_version,
                commit_sha=None,
                visibility=self.visibility,
                content_checksum=checksum
            )

        except Exception as e:
            print(f"[warn] Failed to fetch {url}: {e}")
            return None

    def crawl(self) -> List[Document]:
        """Crawl all URLs from sitemap"""
        print(f"[{self.name}] Crawling sitemap sources...")

        urls_to_fetch = set()

        # Parse sitemaps
        for sitemap_url in self.sitemap_urls:
            try:
                r = self.session.get(sitemap_url, timeout=20)
                soup = BeautifulSoup(r.text, 'xml')

                for loc in soup.find_all('loc'):
                    url = self.norm_url(loc.get_text(strip=True))
                    if self.looks_like_doc(url):
                        urls_to_fetch.add(url)

            except Exception as e:
                print(f"[warn] Failed to parse sitemap {sitemap_url}: {e}")

        print(f"[{self.name}] Found {len(urls_to_fetch)} URLs to fetch")

        # Fetch all pages
        documents = []
        for i, url in enumerate(sorted(urls_to_fetch), 1):
            if i % 10 == 0:
                print(f"[{self.name}] Progress: {i}/{len(urls_to_fetch)}")

            doc = self.fetch_page(url)
            if doc:
                documents.append(doc)

            time.sleep(0.2)  # Rate limiting

        print(f"[{self.name}] Fetched {len(documents)} documents")
        return documents


class GitHubRepoConnector(SourceConnector):
    """Crawl documentation from GitHub repository"""

    def __init__(self, config: dict):
        super().__init__(config)
        self.repo = config['repo']
        self.branch = config['branch']
        self.include_globs = config.get('include_globs', [])
        self.github_token = os.environ.get('GITHUB_TOKEN')
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": UA,
            "Accept": "application/vnd.github.v3+json"
        })
        if self.github_token:
            self.session.headers.update({
                "Authorization": f"token {self.github_token}"
            })

    def get_tree(self) -> Tuple[List[dict], str]:
        """Get file tree and latest commit SHA"""
        url = f"https://api.github.com/repos/{self.repo}/git/trees/{self.branch}"
        params = {"recursive": "1"}

        try:
            r = self.session.get(url, params=params, timeout=20)
            r.raise_for_status()
            data = r.json()

            # Get latest commit SHA
            commits_url = f"https://api.github.com/repos/{self.repo}/commits/{self.branch}"
            r2 = self.session.get(commits_url, timeout=20)
            r2.raise_for_status()
            commit_sha = r2.json()['sha']

            return data['tree'], commit_sha

        except Exception as e:
            print(f"[error] Failed to get tree for {self.repo}: {e}")
            return [], None

    def matches_glob(self, path: str) -> bool:
        """Check if path matches any include glob"""
        if not self.include_globs:
            return True

        for glob in self.include_globs:
            pattern = glob.replace('**/', '').replace('**', '.*').replace('*', '[^/]*')
            if re.match(pattern, path):
                return True
        return False

    def fetch_file(self, path: str, commit_sha: str) -> Optional[Document]:
        """Fetch a single file from GitHub"""
        url = f"https://api.github.com/repos/{self.repo}/contents/{path}"
        params = {"ref": commit_sha}

        try:
            r = self.session.get(url, params=params, timeout=20)
            r.raise_for_status()
            data = r.json()

            if data.get('encoding') == 'base64':
                import base64
                content = base64.b64decode(data['content']).decode('utf-8')
            else:
                content = data.get('content', '')

            # Extract section path from headings (Markdown/RST)
            section_path = self.extract_section_path_text(content, path)

            # Compute checksum
            checksum = hashlib.sha256(content.encode('utf-8')).hexdigest()

            canonical_url = f"https://github.com/{self.repo}/blob/{commit_sha}/{path}"

            # Extract module name if __manifest__.py
            module_name = None
            if path.endswith('__manifest__.py'):
                module_name = Path(path).parent.name

            return Document(
                source_type=self.name,
                source_url=canonical_url,
                canonical_url=canonical_url,
                title=Path(path).name,
                content=content,
                metadata={
                    'path': path,
                    'section_path': section_path,
                    'module_name': module_name,
                    'file_type': Path(path).suffix,
                    'word_count': len(content.split())
                },
                doc_version=self.doc_version,
                commit_sha=commit_sha,
                visibility=self.visibility,
                content_checksum=checksum
            )

        except Exception as e:
            print(f"[warn] Failed to fetch {path}: {e}")
            return None

    def extract_section_path_text(self, content: str, path: str) -> Optional[str]:
        """Extract section path from Markdown/RST headings"""
        if path.endswith('.md'):
            # Markdown headings
            headings = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        elif path.endswith('.rst'):
            # RST headings (simplified)
            headings = re.findall(r'^(.+)\n[=\-~]+$', content, re.MULTILINE)
        else:
            return None

        return " > ".join(headings[:3]) if headings else None

    def crawl(self) -> List[Document]:
        """Crawl all matching files from GitHub repo"""
        print(f"[{self.name}] Crawling {self.repo} @ {self.branch}")

        tree, commit_sha = self.get_tree()
        if not tree:
            print(f"[error] No tree found for {self.repo}")
            return []

        # Filter files by globs
        paths = [item['path'] for item in tree
                if item['type'] == 'blob' and self.matches_glob(item['path'])]

        print(f"[{self.name}] Found {len(paths)} matching files (commit: {commit_sha[:7]})")

        # Fetch all files
        documents = []
        for i, path in enumerate(paths, 1):
            if i % 10 == 0:
                print(f"[{self.name}] Progress: {i}/{len(paths)}")

            doc = self.fetch_file(path, commit_sha)
            if doc:
                documents.append(doc)

            time.sleep(0.5)  # GitHub rate limiting

        print(f"[{self.name}] Fetched {len(documents)} documents")
        return documents


class Chunker:
    """Structure-aware chunking with context preservation"""

    def __init__(self, config: dict):
        self.max_tokens = config.get('max_tokens', 750)
        self.overlap_tokens = config.get('overlap_tokens', 120)
        self.split_by_headings = config.get('split_by_headings', True)
        self.preserve_code_blocks = config.get('preserve_code_blocks', True)
        self.section_delimiter = config.get('section_delimiter', '###')

    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation (1 token ≈ 4 chars)"""
        return len(text) // 4

    def split_by_sections(self, content: str) -> List[Tuple[str, Optional[str]]]:
        """Split content by section headings"""
        if not self.split_by_headings:
            return [(content, None)]

        # Split by Markdown/RST-style headings
        sections = []
        current_section = []
        current_heading = None

        for line in content.split('\n'):
            # Detect heading
            if re.match(r'^#+\s+', line) or re.match(r'^[=\-~]{3,}$', line):
                if current_section:
                    sections.append(('\n'.join(current_section), current_heading))
                    current_section = []
                current_heading = line.strip('# =\-~')

            current_section.append(line)

        if current_section:
            sections.append(('\n'.join(current_section), current_heading))

        return sections if sections else [(content, None)]

    def chunk_document(self, doc: Document) -> List[Chunk]:
        """Chunk document with structure preservation"""
        sections = self.split_by_sections(doc.content)
        chunks = []
        chunk_index = 0

        for section_text, section_heading in sections:
            # Split section into chunks if too large
            section_tokens = self.estimate_tokens(section_text)

            if section_tokens <= self.max_tokens:
                # Section fits in one chunk
                chunks.append(Chunk(
                    content=section_text,
                    chunk_index=chunk_index,
                    section_path=section_heading or doc.metadata.get('section_path'),
                    metadata={
                        'source_type': doc.source_type,
                        'doc_version': doc.doc_version,
                        'commit_sha': doc.commit_sha,
                        'module_name': doc.metadata.get('module_name')
                    }
                ))
                chunk_index += 1
            else:
                # Split section with overlap
                words = section_text.split()
                words_per_chunk = self.max_tokens * 4  # Rough estimate
                overlap_words = self.overlap_tokens * 4

                for i in range(0, len(words), words_per_chunk - overlap_words):
                    chunk_words = words[i:i + words_per_chunk]
                    chunk_text = ' '.join(chunk_words)

                    chunks.append(Chunk(
                        content=chunk_text,
                        chunk_index=chunk_index,
                        section_path=section_heading or doc.metadata.get('section_path'),
                        metadata={
                            'source_type': doc.source_type,
                            'doc_version': doc.doc_version,
                            'commit_sha': doc.commit_sha,
                            'module_name': doc.metadata.get('module_name')
                        }
                    ))
                    chunk_index += 1

        return chunks


def load_config(config_path: Path) -> dict:
    """Load crawler configuration from YAML"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def create_connector(config: dict) -> SourceConnector:
    """Factory for creating source connectors"""
    source_type = config['type']

    if source_type == 'sitemap':
        return SitemapConnector(config)
    elif source_type == 'github_repo':
        return GitHubRepoConnector(config)
    else:
        raise ValueError(f"Unknown source type: {source_type}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="tools/docs-crawler/config.yaml",
                   help="Path to crawler config YAML")
    ap.add_argument("--out", default="out/docs-crawler",
                   help="Output directory")
    ap.add_argument("--sources", nargs="+",
                   help="Filter to specific source names")
    args = ap.parse_args()

    # Load config
    config = load_config(Path(args.config))
    print(f"[config] Loaded {len(config['sources'])} source(s)")

    # Filter sources if specified
    sources = config['sources']
    if args.sources:
        sources = [s for s in sources if s['name'] in args.sources]
        print(f"[config] Filtered to {len(sources)} source(s): {args.sources}")

    # Create output directory
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Crawl each source
    all_documents = []
    all_chunks = []
    chunker = Chunker(config['chunking'])

    for source_config in sources:
        connector = create_connector(source_config)
        documents = connector.crawl()

        # Chunk documents
        for doc in documents:
            chunks = chunker.chunk_document(doc)
            all_chunks.extend(chunks)

        all_documents.extend(documents)

    # Write outputs
    docs_file = out_dir / "documents.json"
    chunks_file = out_dir / "chunks.json"

    with open(docs_file, 'w') as f:
        json.dump([asdict(d) for d in all_documents], f, indent=2)

    with open(chunks_file, 'w') as f:
        json.dump([asdict(c) for c in all_chunks], f, indent=2)

    print(f"\n[ok] Crawled {len(all_documents)} documents, {len(all_chunks)} chunks")
    print(f"     Documents: {docs_file}")
    print(f"     Chunks: {chunks_file}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
