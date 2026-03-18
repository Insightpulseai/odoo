"""
Markdown Heading-Aware Chunker

Splits Markdown documents on h1/h2/h3 headings with breadcrumb context.
Used for Azure and Databricks documentation KBs.
"""

import hashlib
import re
from dataclasses import dataclass, field

import yaml


@dataclass
class Chunk:
    """A single chunk ready for embedding."""

    chunk_id: str
    content: str
    path: str
    heading_chain: str
    ordinal: int
    content_hash: str
    metadata: dict = field(default_factory=dict)


def _content_hash(text: str, length: int = 8) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:length]


def _estimate_tokens(text: str) -> int:
    return len(text) // 4


# Markdown heading pattern: # heading, ## heading, ### heading
_MD_HEADING_RE = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)


class MarkdownChunker:
    """Heading-aware Markdown chunker."""

    def __init__(
        self,
        config_path: str | None = None,
        max_chunk_tokens: int = 512,
        overlap_tokens: int = 64,
        min_chunk_tokens: int = 50,
        max_parent_depth: int = 3,
        id_template: str = "{source}:{path}:{heading_chain}:{ordinal}:{content_hash_8}",
    ):
        if config_path:
            with open(config_path) as f:
                config = yaml.safe_load(f)
            chunking = config["chunking"]
            self.max_tokens = chunking["max_chunk_tokens"]
            self.overlap_tokens = chunking["overlap_tokens"]
            self.min_tokens = chunking["min_chunk_tokens"]
            self.max_parent_depth = chunking["context_window"]["max_parent_depth"]
            self.id_template = config["metadata_per_chunk"]["id_template"]
        else:
            self.max_tokens = max_chunk_tokens
            self.overlap_tokens = overlap_tokens
            self.min_tokens = min_chunk_tokens
            self.max_parent_depth = max_parent_depth
            self.id_template = id_template

    def _strip_frontmatter(self, text: str) -> str:
        """Remove YAML frontmatter from Markdown."""
        if text.startswith("---"):
            end = text.find("---", 3)
            if end != -1:
                return text[end + 3:].strip()
        return text

    def _strip_elements(self, text: str, patterns: list[str] | None = None) -> str:
        """Remove specified patterns from text."""
        if not patterns:
            return text
        for pattern in patterns:
            text = text.replace(pattern, "")
        return text

    def _parse_sections(self, text: str) -> list[dict]:
        """Parse Markdown into sections split by headings."""
        lines = text.split("\n")
        sections = []
        current_title = ""
        current_level = 0
        current_lines = []

        for line in lines:
            match = _MD_HEADING_RE.match(line)
            if match:
                # Save previous section
                if current_lines or current_title:
                    sections.append({
                        "level": current_level,
                        "title": current_title,
                        "content": "\n".join(current_lines).strip(),
                    })
                current_level = len(match.group(1))
                current_title = match.group(2).strip()
                current_lines = []
            else:
                current_lines.append(line)

        # Final section
        if current_lines or current_title:
            sections.append({
                "level": current_level,
                "title": current_title,
                "content": "\n".join(current_lines).strip(),
            })

        return sections

    def _build_heading_chain(self, sections: list[dict], idx: int) -> str:
        """Build breadcrumb heading chain."""
        current = sections[idx]
        parents = []

        for j in range(idx - 1, -1, -1):
            if sections[j]["level"] < current["level"] and (
                not parents or sections[j]["level"] < parents[-1]["level"]
            ):
                parents.append(sections[j])
                if len(parents) >= self.max_parent_depth:
                    break

        parents.reverse()
        chain = [s["title"] for s in parents if s["title"]]
        if current["title"]:
            chain.append(current["title"])

        return " > ".join(chain) if chain else ""

    def _split_large_section(self, text: str) -> list[str]:
        """Split oversized section into sub-chunks."""
        paragraphs = re.split(r"\n\n+", text)
        chunks = []
        current = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = _estimate_tokens(para)
            if current_tokens + para_tokens > self.max_tokens and current:
                chunks.append("\n\n".join(current))
                overlap_text = current[-1] if current else ""
                if _estimate_tokens(overlap_text) <= self.overlap_tokens:
                    current = [overlap_text]
                    current_tokens = _estimate_tokens(overlap_text)
                else:
                    current = []
                    current_tokens = 0
            current.append(para)
            current_tokens += para_tokens

        if current:
            chunks.append("\n\n".join(current))
        return chunks

    def chunk(self, path: str, content: str, metadata: dict) -> list[Chunk]:
        """Chunk a Markdown document into embedding-ready chunks."""
        text = self._strip_frontmatter(content)

        sections = self._parse_sections(text)
        if not sections:
            return []

        source = metadata.get("source", "unknown")
        chunks = []
        ordinal = 0

        for idx, section in enumerate(sections):
            section_text = section["content"]
            if not section_text.strip():
                continue

            heading_chain = self._build_heading_chain(sections, idx)
            context_prefix = f"[{heading_chain}]\n\n" if heading_chain else ""

            # Split if too large
            if _estimate_tokens(section_text) > self.max_tokens:
                sub_chunks = self._split_large_section(section_text)
            else:
                sub_chunks = [section_text]

            for sub in sub_chunks:
                full_content = context_prefix + sub
                if _estimate_tokens(full_content) < self.min_tokens:
                    continue

                chash = _content_hash(full_content)

                # Build chunk ID from template
                chunk_id = self.id_template.format(
                    source=source,
                    service=metadata.get("service", ""),
                    domain=metadata.get("domain", ""),
                    path=path,
                    heading_chain=heading_chain.replace(" ", "_"),
                    ordinal=ordinal,
                    content_hash_8=chash,
                )

                chunks.append(Chunk(
                    chunk_id=chunk_id,
                    content=full_content,
                    path=path,
                    heading_chain=heading_chain,
                    ordinal=ordinal,
                    content_hash=chash,
                    metadata=metadata,
                ))
                ordinal += 1

        return chunks
