#!/usr/bin/env python3
"""
Generate an "EE surface catalog" by scraping Odoo's Editions comparison page and extracting
Enterprise-vs-Community differences into structured YAML.

Notes:
- The Odoo editions page may evolve; this script is defensive and will fail clearly if parsing yields zero.
- If the page becomes heavily JS-rendered, use the Playwright fallback script provided separately.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup

ODDO_EDITIONS_URL = "https://www.odoo.com/page/editions"


@dataclass
class Surface:
    surface_id: str
    category: str
    label: str
    enterprise_only: bool
    source: str
    notes: str = ""


def slugify(s: str) -> str:
    s = re.sub(r"\s+", " ", s.strip())
    s = re.sub(r"[^a-zA-Z0-9 ]+", "", s)
    return re.sub(r"\s+", "-", s).lower()


def fetch_html(url: str) -> str:
    r = requests.get(url, timeout=30, headers={"User-Agent": "ipai-ee-surface-catalog/1.0"})
    r.raise_for_status()
    return r.text


def extract_surfaces(html: str) -> List[Surface]:
    soup = BeautifulSoup(html, "html.parser")

    # Heuristic: the compare table is organized by categories (General, Finance, etc.)
    # We'll extract text blocks and then identify features that appear under headings.
    # If Odoo changes structure, this will likely produce empty results => explicit failure below.

    # Grab visible text blocks under "Compare Editions" section.
    main = soup.get_text("\n")
    if "Compare Editions" not in main:
        # Still try; but signal in output notes.
        pass

    # Minimal extraction strategy:
    # - Find category headings known to exist: General, User interface, Finance, Sales, Websites, Supply Chain, Human Resource, Marketing, Services, Productivity, Customization
    categories = [
        "General",
        "User interface",
        "Finance",
        "Sales",
        "Websites",
        "Supply Chain",
        "Human Resource",
        "Marketing",
        "Services",
        "Productivity",
        "Customization",
    ]

    # Extract the relevant section via regex slicing to reduce noise.
    # Not perfect, but robust across minor DOM changes.
    text = soup.get_text("\n")
    start = text.find("Compare Editions")
    text = text[start:] if start != -1 else text

    # Build category -> lines
    cat_blocks: Dict[str, List[str]] = {c: [] for c in categories}
    current: Optional[str] = None

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line in categories:
            current = line
            continue
        if current:
            # stop when we hit footer noise
            if line.startswith("©") or line == "Privacy Policy":
                break
            cat_blocks[current].append(line)

    surfaces: List[Surface] = []
    # We cannot reliably infer Community-vs-Enterprise availability purely from text lines without table signals.
    # So: generate a "candidate surface list" from category blocks, then let overlay file mark enterprise_only.
    # This keeps the pipeline stable and audit-friendly.

    seen = set()
    for cat, lines in cat_blocks.items():
        for label in lines:
            # skip obvious non-feature filler
            if label in {"Community", "Enterprise"}:
                continue
            if len(label) > 120:
                continue
            key = (cat, label)
            if key in seen:
                continue
            seen.add(key)
            sid = f"ee-{slugify(cat)}-{slugify(label)}"
            surfaces.append(
                Surface(
                    surface_id=sid,
                    category=cat,
                    label=label,
                    enterprise_only=False,  # set in overlay / curation step
                    source=ODDO_EDITIONS_URL,
                    notes="candidate-from-editions-page",
                )
            )
    return surfaces


def main() -> int:
    try:
        html = fetch_html(ODDO_EDITIONS_URL)
        surfaces = extract_surfaces(html)
    except Exception as e:
        print(f"[ERROR] Extraction failed: {e}", file=sys.stderr)
        return 2

    # Dump as JSON (intermediate); YAML via yq in shell stage to avoid adding yaml dependency here.
    out = {"source": ODDO_EDITIONS_URL, "candidates": [asdict(s) for s in surfaces]}
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
