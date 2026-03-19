"""
Web Documentation Loader

Fetches and extracts content from web-based documentation sources
(Microsoft Learn, Databricks docs, etc.) for KB ingestion.
Supports crawl-depth-limited spidering from base URLs.
"""

import hashlib
import logging
import re
import time
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse

import requests
import yaml

logger = logging.getLogger(__name__)

# Strip HTML to plain text / markdown
_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\n{3,}")


@dataclass
class WebDoc:
    """A single web page ready for chunking."""

    url: str
    path: str  # URL path component
    content: str  # Extracted markdown/text
    content_hash: str
    metadata: dict = field(default_factory=dict)


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _extract_text_from_html(html: str, selector_hint: str = "main") -> str:
    """Basic HTML-to-text extraction.

    For production, swap with beautifulsoup4 or trafilatura.
    This is a minimal fallback that strips tags and normalizes whitespace.
    """
    # Try to extract content within the selector hint tag
    pattern = rf"<{selector_hint}[^>]*>(.*?)</{selector_hint}>"
    match = re.search(pattern, html, re.DOTALL)
    if match:
        html = match.group(1)

    # Strip HTML tags
    text = _TAG_RE.sub("", html)

    # Decode common entities
    text = (
        text.replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
        .replace("&nbsp;", " ")
    )

    # Normalize whitespace
    text = _WHITESPACE_RE.sub("\n\n", text)
    return text.strip()


def _extract_links(html: str, base_url: str) -> list[str]:
    """Extract absolute URLs from HTML."""
    links = []
    for match in re.finditer(r'href="([^"]+)"', html):
        href = match.group(1)
        if href.startswith("#") or href.startswith("javascript:"):
            continue
        absolute = urljoin(base_url, href)
        links.append(absolute)
    return links


class WebDocsLoader:
    """Load documentation from web sources with depth-limited crawling."""

    def __init__(
        self,
        source_config_path: str,
        max_pages: int = 500,
        request_delay: float = 0.5,
    ):
        with open(source_config_path) as f:
            self.config = yaml.safe_load(f)

        self.sources = self.config["sources"]
        self.metadata_base = self.config.get("metadata", {})
        self.max_pages = max_pages
        self.request_delay = request_delay

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "IPAI-KB-Loader/1.0 (knowledge-base-ingestion)",
                "Accept": "text/html,application/xhtml+xml",
            }
        )

    def load_source(self, source: dict) -> list[WebDoc]:
        """Load all pages from a single source definition."""
        name = source["name"]
        base_urls = source["base_urls"]
        crawl_depth = source.get("crawl_depth", 1)
        content_selector = source.get("content_selector", "main")

        visited = set()
        docs = []

        # BFS crawl from each base URL
        queue = [(url, 0) for url in base_urls]

        while queue and len(docs) < self.max_pages:
            url, depth = queue.pop(0)

            # Normalize URL
            parsed = urlparse(url)
            normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if normalized in visited:
                continue
            visited.add(normalized)

            # Fetch page
            try:
                resp = self.session.get(url, timeout=30)
                resp.raise_for_status()
            except Exception as e:
                logger.warning("Failed to fetch %s: %s", url, e)
                continue

            # Extract content
            content = _extract_text_from_html(resp.text, content_selector)
            if not content or len(content) < 100:
                continue

            doc = WebDoc(
                url=url,
                path=parsed.path,
                content=content,
                content_hash=_content_hash(content),
                metadata={
                    **self.metadata_base,
                    "source": name,
                    "url": url,
                },
            )
            docs.append(doc)

            logger.info(
                "Loaded %s (%d chars, depth=%d)", parsed.path, len(content), depth
            )

            # Spider links if depth allows
            if depth < crawl_depth:
                links = _extract_links(resp.text, url)
                base_domain = parsed.netloc
                for link in links:
                    link_parsed = urlparse(link)
                    # Stay on same domain and under base path
                    if link_parsed.netloc == base_domain:
                        for base_url in base_urls:
                            base_path = urlparse(base_url).path
                            if link_parsed.path.startswith(
                                base_path.rstrip("/")
                            ):
                                queue.append((link, depth + 1))
                                break

            time.sleep(self.request_delay)

        logger.info(
            "Source '%s': loaded %d pages from %d base URLs",
            name,
            len(docs),
            len(base_urls),
        )
        return docs

    def load_all(self) -> list[WebDoc]:
        """Load all pages from all configured sources."""
        all_docs = []
        for source in self.sources:
            docs = self.load_source(source)
            all_docs.extend(docs)

        logger.info("Total: %d pages from %d sources", len(all_docs), len(self.sources))
        return all_docs
