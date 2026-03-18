"""
Odoo 19 Documentation Chunker

Heading-aware RST chunker per agents/knowledge/odoo19_docs/chunking.yaml.
Splits on h1/h2/h3 headings, maintains parent heading context (breadcrumb),
and produces deterministic chunk IDs.
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
    heading_chain: str  # e.g. "Accounting > Invoicing > Tax Configuration"
    ordinal: int
    content_hash: str
    metadata: dict = field(default_factory=dict)


# RST heading underline characters by level
RST_HEADING_CHARS = {
    "h1": "=",  # overline + underline
    "h2": "-",
    "h3": "~",
}

# Directives to strip (content removed)
STRIP_DIRECTIVES = frozenset(
    [".. image::", ".. figure::", ".. raw::", ".. only::"]
)

# Directives to preserve (content kept)
PRESERVE_DIRECTIVES = frozenset(
    [
        ".. note::",
        ".. tip::",
        ".. warning::",
        ".. important::",
        ".. seealso::",
        ".. code-block::",
    ]
)


def _content_hash(text: str, length: int = 8) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:length]


def _estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token for English text."""
    return len(text) // 4


def _is_heading_underline(line: str, char: str) -> bool:
    """Check if line is a valid RST heading underline."""
    stripped = line.rstrip()
    return len(stripped) >= 3 and all(c == char for c in stripped)


def _strip_directives(text: str) -> str:
    """Remove content of directives that should be stripped."""
    lines = text.split("\n")
    result = []
    skip_indent = None

    for line in lines:
        stripped = line.lstrip()
        if skip_indent is not None:
            # Inside a stripped directive — skip indented content
            if line == "" or (len(line) - len(stripped) > skip_indent):
                continue
            else:
                skip_indent = None

        if any(stripped.startswith(d) for d in STRIP_DIRECTIVES):
            skip_indent = len(line) - len(stripped)
            continue

        result.append(line)

    return "\n".join(result)


def _strip_toctree(text: str) -> str:
    """Remove toctree directives."""
    lines = text.split("\n")
    result = []
    skip_indent = None

    for line in lines:
        stripped = line.lstrip()
        if skip_indent is not None:
            if line == "" or (len(line) - len(stripped) > skip_indent):
                continue
            else:
                skip_indent = None

        if stripped.startswith(".. toctree::"):
            skip_indent = len(line) - len(stripped)
            continue

        result.append(line)

    return "\n".join(result)


class RSTHeadingChunker:
    """Heading-aware RST chunker."""

    def __init__(
        self,
        config_path: str = "agents/knowledge/odoo19_docs/chunking.yaml",
    ):
        with open(config_path) as f:
            config = yaml.safe_load(f)

        chunking = config["chunking"]
        self.max_tokens = chunking["max_chunk_tokens"]
        self.overlap_tokens = chunking["overlap_tokens"]
        self.min_tokens = chunking["min_chunk_tokens"]

        ctx = chunking["context_window"]
        self.include_parent_headings = ctx["include_parent_headings"]
        self.include_breadcrumb = ctx["include_breadcrumb"]
        self.max_parent_depth = ctx["max_parent_depth"]

        meta = config["metadata_per_chunk"]
        self.id_template = meta["id_template"]

        self.strip_toctree = config.get("rst_handling", {}).get(
            "strip_toctree", True
        )

    def _parse_headings(self, text: str) -> list[dict]:
        """Parse RST into sections split by headings.

        Returns list of {level, title, content, line_start}.
        """
        lines = text.split("\n")
        sections = []
        current_title = None
        current_level = None
        current_lines = []
        current_start = 0

        i = 0
        while i < len(lines):
            heading_found = False

            # Check h1: overline + title + underline (=)
            if (
                i + 2 < len(lines)
                and _is_heading_underline(lines[i], "=")
                and _is_heading_underline(lines[i + 2], "=")
                and lines[i + 1].strip()
            ):
                # Save previous section
                if current_title is not None or current_lines:
                    sections.append(
                        {
                            "level": current_level or 0,
                            "title": current_title or "",
                            "content": "\n".join(current_lines).strip(),
                            "line_start": current_start,
                        }
                    )
                current_title = lines[i + 1].strip()
                current_level = 1
                current_lines = []
                current_start = i
                i += 3
                heading_found = True

            # Check h2/h3: title + underline
            if not heading_found and i + 1 < len(lines) and lines[i].strip():
                for level, (hname, char) in enumerate(
                    [("h2", "-"), ("h3", "~")], start=2
                ):
                    if _is_heading_underline(lines[i + 1], char) and len(
                        lines[i + 1].rstrip()
                    ) >= len(lines[i].strip()):
                        # Save previous section
                        if current_title is not None or current_lines:
                            sections.append(
                                {
                                    "level": current_level or 0,
                                    "title": current_title or "",
                                    "content": "\n".join(
                                        current_lines
                                    ).strip(),
                                    "line_start": current_start,
                                }
                            )
                        current_title = lines[i].strip()
                        current_level = level
                        current_lines = []
                        current_start = i
                        i += 2
                        heading_found = True
                        break

            if not heading_found:
                current_lines.append(lines[i])
                i += 1

        # Final section
        if current_title is not None or current_lines:
            sections.append(
                {
                    "level": current_level or 0,
                    "title": current_title or "",
                    "content": "\n".join(current_lines).strip(),
                    "line_start": current_start,
                }
            )

        return sections

    def _build_heading_chain(
        self, sections: list[dict], idx: int
    ) -> str:
        """Build breadcrumb heading chain for a section."""
        current = sections[idx]
        parents = []

        for j in range(idx - 1, -1, -1):
            if sections[j]["level"] < current["level"] and (
                not parents
                or sections[j]["level"] < parents[-1]["level"]
            ):
                parents.append(sections[j])
                if len(parents) >= self.max_parent_depth:
                    break

        parents.reverse()
        chain = [s["title"] for s in parents if s["title"]]
        if current["title"]:
            chain.append(current["title"])

        return " > ".join(chain) if chain else ""

    def _split_large_section(
        self, text: str, max_tokens: int, overlap_tokens: int
    ) -> list[str]:
        """Split oversized section into token-bounded sub-chunks."""
        paragraphs = re.split(r"\n\n+", text)
        chunks = []
        current = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = _estimate_tokens(para)
            if current_tokens + para_tokens > max_tokens and current:
                chunks.append("\n\n".join(current))
                # Overlap: keep last paragraph
                overlap_text = current[-1] if current else ""
                if _estimate_tokens(overlap_text) <= overlap_tokens:
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
        """Chunk a single RST document into embedding-ready chunks."""
        # Pre-process
        text = _strip_directives(content)
        if self.strip_toctree:
            text = _strip_toctree(text)

        sections = self._parse_headings(text)
        if not sections:
            return []

        repo = metadata.get("repo", "odoo/documentation")
        branch = metadata.get("branch", "19.0")

        chunks = []
        ordinal = 0

        for idx, section in enumerate(sections):
            section_text = section["content"]
            if not section_text.strip():
                continue

            heading_chain = self._build_heading_chain(sections, idx)

            # Prepend breadcrumb context
            if self.include_breadcrumb and heading_chain:
                context_prefix = f"[{heading_chain}]\n\n"
            else:
                context_prefix = ""

            # Split if too large
            section_tokens = _estimate_tokens(section_text)
            if section_tokens > self.max_tokens:
                sub_chunks = self._split_large_section(
                    section_text, self.max_tokens, self.overlap_tokens
                )
            else:
                sub_chunks = [section_text]

            for sub in sub_chunks:
                full_content = context_prefix + sub
                if _estimate_tokens(full_content) < self.min_tokens:
                    continue

                chash = _content_hash(full_content)
                chunk_id = self.id_template.format(
                    repo=repo,
                    branch=branch,
                    path=path,
                    heading_chain=heading_chain.replace(" ", "_"),
                    ordinal=ordinal,
                    content_hash_8=chash,
                )

                chunks.append(
                    Chunk(
                        chunk_id=chunk_id,
                        content=full_content,
                        path=path,
                        heading_chain=heading_chain,
                        ordinal=ordinal,
                        content_hash=chash,
                        metadata={
                            **metadata,
                            "version": branch,
                            "product": "odoo",
                            "source_type": "documentation",
                            "lang": "en",
                        },
                    )
                )
                ordinal += 1

        return chunks
