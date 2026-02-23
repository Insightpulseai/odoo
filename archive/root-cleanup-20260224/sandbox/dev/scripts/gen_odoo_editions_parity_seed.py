#!/usr/bin/env python3
"""
Odoo Editions Parity Seed Generator

Extracts Odoo Enterprise vs Community Edition capabilities from the official
Editions comparison page using text-based parsing with BeautifulSoup4.

Output: spec/parity/odoo_editions_parity_seed.yaml

Features:
- Text-based extraction (resilient to markup changes)
- Heuristic EE-only detection (OCR, AI, Studio, VoIP, IoT, Barcode, Shopfloor, Scheduling)
- area → app → feature data model
- Placeholder mapping fields for manual OCA enrichment
- Deterministic deduplication while preserving order
"""

import os
import re
import sys
import yaml
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: Missing dependencies. Install with:")
    print("  pip install beautifulsoup4 requests pyyaml")
    sys.exit(1)


# Configuration
EDITIONS_URL = "https://www.odoo.com/page/editions"
OUTPUT_PATH = Path(__file__).parent.parent / "spec" / "parity" / "odoo_editions_parity_seed.yaml"
USER_AGENT = "Mozilla/5.0 (compatible; OdooParitySeedBot/1.0)"

# Heuristic keywords for EE-only detection
EE_KEYWORDS = [
    "ocr", "ai", "studio", "voip", "iot", "barcode",
    "shopfloor", "scheduling", "machine learning", "artificial intelligence"
]


def fetch_html(url: str, timeout: int = 30) -> str:
    """Fetch HTML from Odoo Editions page with user-agent header."""
    headers = {"User-Agent": USER_AGENT}
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"ERROR: Failed to fetch {url}: {e}")
        sys.exit(1)


def slugify(text: str) -> str:
    """Convert text to lowercase slug (alphanumeric + hyphens)."""
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def is_assumed_ee_only(text: str) -> bool:
    """Heuristic detection of EE-only features based on keywords."""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in EE_KEYWORDS)


def extract_visible_structure(html: str) -> List[Dict[str, Any]]:
    """
    Extract area → app → feature structure from Editions comparison table.

    The table structure is:
    - Header row: "" | "Community" | "Enterprise" (skip)
    - Section headers: 1 cell (Finance, Sales, etc.)
    - App rows: 3 cells (Accounting | checkmark | checkmark)
    - Feature rows: 3 cells (↳ Feature name | checkmark | checkmark)

    Returns list of rows with area, app, feature fields.
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Find the main comparison table
    table = soup.find('table')
    if not table:
        print("ERROR: No comparison table found on page")
        return []

    rows = []
    current_area = None
    current_app = None

    for tr in table.find_all('tr'):
        cells = tr.find_all(['th', 'td'])

        if not cells:
            continue

        # Get text from first cell
        text = cells[0].get_text(strip=True)

        if not text or len(text) < 2:
            continue

        # Skip header row (Community | Enterprise)
        if len(cells) >= 2:
            cell1 = cells[1].get_text(strip=True).lower()
            if 'community' in cell1 or 'enterprise' in cell1:
                continue

        # Section headers (1 cell only)
        if len(cells) == 1:
            current_area = text
            current_app = None
            continue

        # Feature rows (start with ↳)
        if text.startswith('↳'):
            if current_app:
                feature = text.lstrip('↳ ').strip()
                # Split combined text if it has no spaces (e.g., "↳Spreadsheet")
                if not ' ' in feature and len(feature) > 15:
                    # Likely truncated, keep as-is
                    pass
                rows.append({
                    "area": current_area or "Unknown",
                    "app": current_app,
                    "feature": feature,
                    "evidence_text": feature,
                    "assumed_ee_only": is_assumed_ee_only(feature),
                })
            continue

        # App rows (3 cells, no ↳ prefix)
        if len(cells) == 3 and not text.startswith('↳'):
            current_app = text
            # Add app-level row
            rows.append({
                "area": current_area or "Unknown",
                "app": current_app,
                "feature": None,
                "evidence_text": None,
                "assumed_ee_only": False,
            })

    return rows


def deduplicate_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deduplicate rows based on normalized (area, app, feature) tuples.
    Preserves first occurrence and maintains order.
    """
    seen = set()
    deduped = []

    for row in rows:
        # Create normalized key
        key = (
            slugify(row["area"]) if row["area"] else "",
            slugify(row["app"]) if row["app"] else "",
            slugify(row["feature"]) if row["feature"] else "",
        )

        if key not in seen:
            seen.add(key)
            deduped.append(row)

    return deduped


def build_yaml_output(rows: List[Dict[str, Any]], source_url: str) -> Dict[str, Any]:
    """Build final YAML structure with metadata."""
    # Add placeholder mapping fields
    for row in rows:
        row["source_url"] = source_url
        row["mapping"] = {
            "oca_repo": None,
            "oca_module": None,
            "ipai_module": None,
        }
        row["confidence"] = 0.0
        row["notes"] = (
            f"seed row ({'app-level' if row['feature'] is None else 'feature-level'}) "
            f"from editions page"
        )

    # Support deterministic mode for CI drift detection
    det = os.getenv("PARITY_SEED_DETERMINISTIC", "").lower() in ("1", "true", "yes")
    fetched_ts = "1970-01-01T00:00:00Z" if det else datetime.now(timezone.utc).isoformat()

    return {
        "parity_seed": {
            "source": {
                "url": source_url,
                "fetched_at": fetched_ts,
                "notes": "Seed extracted from editions comparison page; enrich with OCA mapping + evidence URLs per row.",
            },
            "schema_version": "v1",
            "rows": rows,
        }
    }


def write_yaml(data: Dict[str, Any], output_path: Path) -> None:
    """Write YAML output with atomic operation (temp file + rename)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    temp_path = output_path.with_suffix('.tmp')

    try:
        with temp_path.open('w') as f:
            yaml.dump(
                data,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
                width=120,
            )

        # Atomic rename
        temp_path.rename(output_path)
        print(f"✅ Wrote {len(data['parity_seed']['rows'])} rows to {output_path}")

    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()
        raise e


def main():
    """Main execution pipeline."""
    print(f"Fetching Odoo Editions page: {EDITIONS_URL}")
    html = fetch_html(EDITIONS_URL)

    print("Extracting area → app → feature structure...")
    rows = extract_visible_structure(html)
    print(f"Extracted {len(rows)} raw rows")

    print("Deduplicating rows...")
    rows = deduplicate_rows(rows)
    print(f"After deduplication: {len(rows)} rows")

    if len(rows) < 20:
        print(f"WARNING: Expected ≥20 rows, got {len(rows)}. Extraction may have failed.")
        sys.exit(1)

    print("Building YAML output...")
    data = build_yaml_output(rows, EDITIONS_URL)

    print(f"Writing to {OUTPUT_PATH}...")
    write_yaml(data, OUTPUT_PATH)

    print("✅ Seed generation complete")

    # Print sample rows for verification
    print("\nSample rows:")
    for i, row in enumerate(rows[:3], 1):
        print(f"  {i}. {row['area']} → {row['app']} → {row['feature'] or '(app-level)'}")


if __name__ == "__main__":
    main()
