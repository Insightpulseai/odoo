#!/usr/bin/env python3
"""
OpenAI Academy Prompt Packs Extractor

Crawls OpenAI Academy to extract prompt engineering patterns,
templates, and best practices for integration into IPAI prompt registry.

Usage:
    python scripts/extract_openai_academy_prompt_packs.py --mode discover
    python scripts/extract_openai_academy_prompt_packs.py --mode extract
    python scripts/extract_openai_academy_prompt_packs.py --mode curate
    python scripts/extract_openai_academy_prompt_packs.py --mode gap-analysis

Requirements:
    pip install requests beautifulsoup4 lxml
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependencies. Install with: pip install requests beautifulsoup4 lxml")
    sys.exit(1)


# Configuration
BASE_URL = "https://academy.openai.com"
OUTPUT_DIR = Path("docs/prompts/openai-academy")
CACHE_DIR = Path(".cache/openai-academy")
USER_AGENT = "IPAI-PromptExtractor/1.0 (educational; github.com/jgtolentino/odoo-ce)"
REQUEST_DELAY = 1.5  # seconds between requests


class OpenAIAcademyExtractor:
    """Extracts prompt packs from OpenAI Academy."""

    def __init__(self, cookie: str | None = None, use_cache: bool = True):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })
        if cookie:
            self.session.headers["Cookie"] = cookie

        self.use_cache = use_cache
        self.cache_dir = CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.discovered_pages: list[dict[str, Any]] = []
        self.extracted_packs: list[dict[str, Any]] = []
        self.errors: list[dict[str, Any]] = []

    def _get_cache_path(self, url: str) -> Path:
        """Generate cache file path for URL."""
        parsed = urlparse(url)
        safe_name = re.sub(r"[^\w\-.]", "_", parsed.path.strip("/") or "index")
        return self.cache_dir / f"{safe_name}.html"

    def _fetch(self, url: str) -> str | None:
        """Fetch URL with caching and rate limiting."""
        cache_path = self._get_cache_path(url)

        # Check cache
        if self.use_cache and cache_path.exists():
            return cache_path.read_text(encoding="utf-8")

        # Rate limit
        time.sleep(REQUEST_DELAY)

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            content = response.text

            # Cache response
            if self.use_cache:
                cache_path.write_text(content, encoding="utf-8")

            return content

        except requests.RequestException as e:
            self.errors.append({
                "url": url,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            print(f"  ERROR: {url} - {e}")
            return None

    def discover(self) -> list[dict[str, Any]]:
        """Discover available pages and resources."""
        print(f"Discovering content from {BASE_URL}...")

        # Known entry points
        entry_points = [
            "/",
            "/courses",
            "/lessons",
            "/resources",
            "/prompt-engineering",
        ]

        for path in entry_points:
            url = urljoin(BASE_URL, path)
            print(f"  Checking: {url}")
            content = self._fetch(url)

            if content:
                soup = BeautifulSoup(content, "lxml")
                self._extract_links(soup, url)

        print(f"Discovered {len(self.discovered_pages)} pages")
        return self.discovered_pages

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> None:
        """Extract relevant links from page."""
        for link in soup.find_all("a", href=True):
            href = link["href"]
            full_url = urljoin(base_url, href)

            # Only follow internal links
            if not full_url.startswith(BASE_URL):
                continue

            # Skip already discovered
            if any(p["url"] == full_url for p in self.discovered_pages):
                continue

            # Check if likely contains prompts
            text = link.get_text(strip=True).lower()
            href_lower = href.lower()

            relevance = 0
            if any(kw in text for kw in ["prompt", "template", "example", "pattern"]):
                relevance += 2
            if any(kw in href_lower for kw in ["prompt", "lesson", "course", "guide"]):
                relevance += 1

            if relevance > 0:
                self.discovered_pages.append({
                    "url": full_url,
                    "title": link.get_text(strip=True),
                    "relevance": relevance,
                    "discovered_from": base_url
                })

    def extract(self) -> list[dict[str, Any]]:
        """Extract prompt packs from discovered pages."""
        print("Extracting prompt packs...")

        # Load discovery manifest if exists
        manifest_path = OUTPUT_DIR / "discovery_manifest.json"
        if manifest_path.exists() and not self.discovered_pages:
            with open(manifest_path) as f:
                data = json.load(f)
                self.discovered_pages = data.get("pages", [])

        # Sort by relevance
        pages = sorted(self.discovered_pages, key=lambda x: -x.get("relevance", 0))

        for i, page in enumerate(pages[:50]):  # Limit to top 50 pages
            print(f"  [{i+1}/{min(len(pages), 50)}] {page['url']}")
            content = self._fetch(page["url"])

            if content:
                prompts = self._extract_prompts(content, page["url"])
                if prompts:
                    self.extracted_packs.append({
                        "source_url": page["url"],
                        "title": page.get("title", "Unknown"),
                        "prompts": prompts,
                        "extracted_at": datetime.now(timezone.utc).isoformat()
                    })
                    print(f"    Found {len(prompts)} prompts")

        print(f"Extracted {len(self.extracted_packs)} packs with {sum(len(p['prompts']) for p in self.extracted_packs)} total prompts")
        return self.extracted_packs

    def _extract_prompts(self, content: str, url: str) -> list[dict[str, Any]]:
        """Extract prompts from page content."""
        soup = BeautifulSoup(content, "lxml")
        prompts: list[dict[str, Any]] = []

        # Look for code blocks that might contain prompts
        for code in soup.find_all(["code", "pre"]):
            text = code.get_text(strip=True)

            # Heuristic: prompts often have certain patterns
            if len(text) > 50 and any(kw in text.lower() for kw in [
                "you are", "your task", "given the", "please",
                "write a", "create a", "analyze", "summarize",
                "{{", "{{"  # template variables
            ]):
                # Try to find a title/label
                parent = code.find_parent(["div", "section", "article"])
                title = "Untitled Prompt"
                if parent:
                    heading = parent.find(["h1", "h2", "h3", "h4", "h5", "h6"])
                    if heading:
                        title = heading.get_text(strip=True)

                # Extract variables
                variables = re.findall(r"\{\{(\w+)\}\}", text)
                variables = list(set(variables))  # dedupe

                prompts.append({
                    "name": title,
                    "template": text,
                    "variables": variables,
                    "source_url": url
                })

        # Look for prompt examples in prose
        for section in soup.find_all(["div", "section"], class_=re.compile(r"prompt|example|template", re.I)):
            # Implementation for prose-embedded prompts
            pass

        return prompts

    def curate(self) -> str:
        """Curate extracted packs into library format."""
        print("Curating prompt library...")

        # Load raw extraction if exists
        raw_path = OUTPUT_DIR / "prompt_packs_raw.json"
        if raw_path.exists() and not self.extracted_packs:
            with open(raw_path) as f:
                data = json.load(f)
                self.extracted_packs = data.get("packs", [])

        # Group by category (simple heuristic)
        categories: dict[str, list] = {
            "summarization": [],
            "extraction": [],
            "generation": [],
            "analysis": [],
            "classification": [],
            "conversation": [],
            "reasoning": [],
            "code": [],
            "structured-output": [],
            "agents": [],
            "uncategorized": []
        }

        for pack in self.extracted_packs:
            for prompt in pack.get("prompts", []):
                template = prompt.get("template", "").lower()
                category = self._categorize_prompt(template)
                categories[category].append({
                    **prompt,
                    "pack_title": pack.get("title"),
                    "pack_url": pack.get("source_url")
                })

        # Generate markdown
        lines = [
            "# OpenAI Academy Prompt Library",
            "",
            f"> **Last Updated**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
            ">",
            f"> **Source**: {BASE_URL}",
            "",
            "---",
            "",
            "## Quick Stats",
            "",
            "| Metric | Count |",
            "|--------|-------|",
            f"| Total Packs | {len(self.extracted_packs)} |",
            f"| Total Prompts | {sum(len(c) for c in categories.values())} |",
            f"| Categories | {sum(1 for c in categories.values() if c)} |",
            "",
            "---",
            "",
            "## Prompt Packs by Category",
            ""
        ]

        for category, prompts in categories.items():
            if not prompts:
                continue

            lines.append(f"### {category.replace('-', ' ').title()}")
            lines.append("")

            for prompt in prompts[:10]:  # Limit per category
                lines.append(f"#### {prompt.get('name', 'Untitled')}")
                lines.append("")
                lines.append(f"**Source**: [{prompt.get('pack_title', 'Unknown')}]({prompt.get('pack_url', '#')})")
                lines.append("")

                if prompt.get("variables"):
                    lines.append(f"**Variables**: `{'`, `'.join(prompt['variables'])}`")
                    lines.append("")

                lines.append("```text")
                # Truncate long templates
                template = prompt.get("template", "")
                if len(template) > 500:
                    template = template[:500] + "..."
                lines.append(template)
                lines.append("```")
                lines.append("")

            lines.append("---")
            lines.append("")

        content = "\n".join(lines)
        print(f"Generated library with {sum(len(c) for c in categories.values())} prompts")
        return content

    def _categorize_prompt(self, template: str) -> str:
        """Categorize prompt based on content."""
        template = template.lower()

        if any(kw in template for kw in ["summarize", "summary", "condense", "tldr"]):
            return "summarization"
        if any(kw in template for kw in ["extract", "find", "identify", "parse"]):
            return "extraction"
        if any(kw in template for kw in ["generate", "create", "write", "compose"]):
            return "generation"
        if any(kw in template for kw in ["analyze", "evaluate", "assess", "review"]):
            return "analysis"
        if any(kw in template for kw in ["classify", "categorize", "label", "tag"]):
            return "classification"
        if any(kw in template for kw in ["chat", "conversation", "dialog", "respond"]):
            return "conversation"
        if any(kw in template for kw in ["reason", "think", "step by step", "chain of thought"]):
            return "reasoning"
        if any(kw in template for kw in ["code", "function", "program", "script"]):
            return "code"
        if any(kw in template for kw in ["json", "xml", "structured", "schema"]):
            return "structured-output"
        if any(kw in template for kw in ["agent", "tool", "action", "execute"]):
            return "agents"

        return "uncategorized"

    def gap_analysis(self) -> str:
        """Compare extracted prompts against IPAI requirements."""
        print("Running gap analysis...")

        # IPAI-specific requirements
        ipai_requirements = {
            "Finance/Accounting": [
                "BIR tax form generation",
                "Month-end close assistance",
                "Journal entry validation",
                "Financial report summarization",
                "Audit trail analysis"
            ],
            "Odoo ERP Integration": [
                "Module documentation generation",
                "XML-RPC query construction",
                "Workflow automation prompts",
                "Data migration assistance",
                "Field mapping suggestions"
            ],
            "Multi-tenant Operations": [
                "Tenant-aware prompt templates",
                "Cross-tenant analysis with isolation",
                "Tenant onboarding workflows",
                "Usage analytics per tenant"
            ],
            "Observability/DevOps": [
                "Log analysis prompts",
                "Incident triage assistance",
                "Runbook generation",
                "Alert correlation",
                "Performance analysis"
            ]
        }

        # Load extracted prompts
        raw_path = OUTPUT_DIR / "prompt_packs_raw.json"
        if raw_path.exists():
            with open(raw_path) as f:
                data = json.load(f)
                self.extracted_packs = data.get("packs", [])

        # Simple coverage check
        all_templates = " ".join(
            p.get("template", "").lower()
            for pack in self.extracted_packs
            for p in pack.get("prompts", [])
        )

        lines = [
            "# OpenAI Academy Prompt Pack Gap Report",
            "",
            f"> **Generated**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
            ">",
            "> **Comparison**: OpenAI Academy vs IPAI Platform Requirements",
            "",
            "---",
            "",
            "## Coverage by Domain",
            ""
        ]

        total_reqs = 0
        covered_reqs = 0

        for domain, requirements in ipai_requirements.items():
            lines.append(f"### {domain}")
            lines.append("")
            lines.append("| Requirement | Covered | Notes |")
            lines.append("|-------------|---------|-------|")

            for req in requirements:
                total_reqs += 1
                # Simple keyword matching
                keywords = req.lower().split()
                is_covered = any(kw in all_templates for kw in keywords if len(kw) > 3)

                if is_covered:
                    covered_reqs += 1
                    status = "Partial"
                else:
                    status = "Gap"

                lines.append(f"| {req} | {status} | |")

            lines.append("")

        # Summary
        coverage_pct = (covered_reqs / total_reqs * 100) if total_reqs else 0

        summary = [
            "## Executive Summary",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Total IPAI Requirements | {total_reqs} |",
            f"| Potentially Covered | {covered_reqs} |",
            f"| Gaps Identified | {total_reqs - covered_reqs} |",
            f"| Coverage Percentage | {coverage_pct:.1f}% |",
            "",
            "---",
            ""
        ]

        content = "\n".join(summary + lines[3:])  # Insert summary at top
        print(f"Gap analysis complete: {coverage_pct:.1f}% coverage")
        return content

    def save_outputs(self, mode: str) -> None:
        """Save outputs to files."""
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        if mode == "discover":
            manifest = {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "base_url": BASE_URL,
                "pages_found": len(self.discovered_pages),
                "pages": self.discovered_pages,
                "errors": self.errors
            }
            path = OUTPUT_DIR / "discovery_manifest.json"
            with open(path, "w") as f:
                json.dump(manifest, f, indent=2)
            print(f"Saved: {path}")

        elif mode == "extract":
            raw_data = {
                "metadata": {
                    "source": "openai-academy",
                    "extracted_at": datetime.now(timezone.utc).isoformat(),
                    "extractor_version": "1.0.0",
                    "status": "extracted"
                },
                "discovery": {
                    "pages_found": len(self.discovered_pages),
                    "pages_crawled": len(self.extracted_packs),
                    "pages_failed": len(self.errors),
                    "prompts_extracted": sum(len(p["prompts"]) for p in self.extracted_packs)
                },
                "packs": self.extracted_packs,
                "errors": self.errors
            }
            path = OUTPUT_DIR / "prompt_packs_raw.json"
            with open(path, "w") as f:
                json.dump(raw_data, f, indent=2)
            print(f"Saved: {path}")

        elif mode == "curate":
            content = self.curate()
            path = OUTPUT_DIR / "prompt_library.md"
            with open(path, "w") as f:
                f.write(content)
            print(f"Saved: {path}")

        elif mode == "gap-analysis":
            content = self.gap_analysis()
            path = OUTPUT_DIR / "prompt_pack_gap_report.md"
            with open(path, "w") as f:
                f.write(content)
            print(f"Saved: {path}")


def main():
    parser = argparse.ArgumentParser(description="Extract OpenAI Academy prompt packs")
    parser.add_argument(
        "--mode",
        choices=["discover", "extract", "curate", "gap-analysis", "all"],
        default="all",
        help="Extraction mode"
    )
    parser.add_argument("--cookie", help="Session cookie for authentication")
    parser.add_argument("--cookie-file", help="File containing session cookie")
    parser.add_argument("--no-cache", action="store_true", help="Disable caching")

    args = parser.parse_args()

    # Load cookie from file if provided
    cookie = args.cookie
    if args.cookie_file and os.path.exists(args.cookie_file):
        with open(args.cookie_file) as f:
            cookie = f.read().strip()

    extractor = OpenAIAcademyExtractor(
        cookie=cookie,
        use_cache=not args.no_cache
    )

    if args.mode in ("discover", "all"):
        extractor.discover()
        extractor.save_outputs("discover")

    if args.mode in ("extract", "all"):
        extractor.extract()
        extractor.save_outputs("extract")

    if args.mode in ("curate", "all"):
        extractor.save_outputs("curate")

    if args.mode in ("gap-analysis", "all"):
        extractor.save_outputs("gap-analysis")

    print("\nDone!")
    if extractor.errors:
        print(f"Encountered {len(extractor.errors)} errors (see discovery_manifest.json)")


if __name__ == "__main__":
    main()
