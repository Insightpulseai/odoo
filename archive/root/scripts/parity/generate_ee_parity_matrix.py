#!/usr/bin/env python3
"""
Odoo EE→CE+OCA Parity Matrix Generator

Scrapes Odoo All Apps (apps.odoo.com) and OCA GitHub repos to generate
evidence-based EE→CE+OCA parity mappings. Outputs SQL upserts for Supabase.

Usage:
    python scripts/parity/generate_ee_parity_matrix.py --output parity_upserts.sql
    python scripts/parity/generate_ee_parity_matrix.py --odoo-version 19.0 --json
    python scripts/parity/generate_ee_parity_matrix.py --categories Accounting,Sales

Features:
- Scrapes apps.odoo.com for EE app metadata (name, category, description, URL)
- Scrapes OCA GitHub repos for available modules
- Matches EE features to CE/OCA equivalents with confidence scoring
- Generates SQL INSERT/UPDATE statements for ops.ee_parity_map table
- Includes evidence URLs and verification metadata

Created: 2026-02-12
Task: #2 - Parity matrix generator implementation
"""

import argparse
import json
import logging
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from urllib.parse import urljoin

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: Required packages missing. Install: pip install requests beautifulsoup4", file=sys.stderr)
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class EEApp:
    """Odoo EE Application metadata"""
    name: str
    slug: str
    category: str
    description: str = ""
    url: str = ""


@dataclass
class OCAModule:
    """OCA module metadata"""
    repo: str
    name: str
    url: str


@dataclass
class ParityMapping:
    """EE→CE+OCA parity mapping with evidence"""
    ee_app_name: str
    ee_app_slug: str
    ee_category: str
    ee_description: str
    ee_url: str
    parity_level: str  # full, partial, alternative, missing
    ce_modules: List[str] = field(default_factory=list)
    oca_modules: List[str] = field(default_factory=list)
    ipai_modules: List[str] = field(default_factory=list)
    evidence_urls: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    notes: str = ""
    scraped_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def make_deterministic(self):
        """Sort lists alphabetically and use fixed timestamp for deterministic output"""
        self.ce_modules = sorted(self.ce_modules)
        self.oca_modules = sorted(self.oca_modules)
        self.ipai_modules = sorted(self.ipai_modules)
        self.evidence_urls = sorted(self.evidence_urls)
        self.scraped_at = "2026-01-01T00:00:00Z"


class OdooAppsScraper:
    """Scraper for apps.odoo.com EE applications"""

    BASE_URL = "https://apps.odoo.com"

    def __init__(self, version: str = "19.0"):
        self.version = version
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def scrape_ee_apps(self, categories: Optional[List[str]] = None) -> List[EEApp]:
        """Scrape EE apps from apps.odoo.com"""
        apps = []

        # Start with apps listing page
        url = f"{self.BASE_URL}/web/modules/{self.version}/"
        logger.info(f"Scraping Odoo apps from {url}")

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find app cards (adjust selectors based on actual page structure)
            app_cards = soup.find_all('div', class_='o_app_card')

            if not app_cards:
                # Fallback: try alternative selectors
                app_cards = soup.find_all('a', href=re.compile(r'/web/modules/\d+\.\d+/'))

            for card in app_cards:
                try:
                    # Extract app metadata
                    link = card.find('a', href=True)
                    if not link:
                        continue

                    app_url = urljoin(self.BASE_URL, link['href'])
                    slug = app_url.split('/')[-2] if app_url.endswith('/') else app_url.split('/')[-1]

                    # Get app name
                    name_elem = card.find('h4') or card.find('span', class_='o_app_name')
                    name = name_elem.get_text(strip=True) if name_elem else slug

                    # Get category
                    cat_elem = card.find('span', class_='badge') or card.find('small')
                    category = cat_elem.get_text(strip=True) if cat_elem else "Uncategorized"

                    # Get description
                    desc_elem = card.find('p', class_='o_app_desc') or card.find('p')
                    description = desc_elem.get_text(strip=True) if desc_elem else ""

                    # Filter by category if specified
                    if categories and category not in categories:
                        continue

                    app = EEApp(
                        name=name,
                        slug=slug,
                        category=category,
                        description=description,
                        url=app_url
                    )
                    apps.append(app)
                    logger.debug(f"Found EE app: {name} ({category})")

                except Exception as e:
                    logger.warning(f"Failed to parse app card: {e}")
                    continue

            logger.info(f"Scraped {len(apps)} EE apps")

        except Exception as e:
            logger.error(f"Failed to scrape Odoo apps: {e}")

        return apps


class OCARepoScraper:
    """Scraper for OCA GitHub repositories"""

    OCA_REPOS = [
        "account-financial-tools",
        "account-invoicing",
        "document-management",
        "helpdesk",
        "hr",
        "manufacture",
        "project",
        "sale-workflow",
        "server-tools",
        "stock-logistics-workflow",
        "website",
    ]

    def __init__(self, version: str = "19.0"):
        self.version = version
        self.session = requests.Session()

    def scrape_oca_modules(self) -> List[OCAModule]:
        """Scrape OCA modules from GitHub repos"""
        modules = []

        for repo_name in self.OCA_REPOS:
            logger.info(f"Scraping OCA repo: {repo_name}")

            # GitHub API endpoint for repo contents
            api_url = f"https://api.github.com/repos/OCA/{repo_name}/contents"

            try:
                response = self.session.get(api_url, timeout=30)
                if response.status_code == 403:
                    logger.warning(f"Rate limited on {repo_name}, skipping")
                    continue

                response.raise_for_status()
                contents = response.json()

                # Filter directories that look like Odoo modules
                for item in contents:
                    if item['type'] == 'dir' and not item['name'].startswith('.'):
                        module_name = item['name']
                        module_url = item['html_url']

                        # Check if __manifest__.py or __openerp__.py exists
                        manifest_url = f"{api_url}/{module_name}/__manifest__.py"
                        manifest_check = self.session.head(manifest_url, timeout=10)

                        if manifest_check.status_code == 200:
                            module = OCAModule(
                                repo=repo_name,
                                name=module_name,
                                url=module_url
                            )
                            modules.append(module)
                            logger.debug(f"Found OCA module: {repo_name}/{module_name}")

            except Exception as e:
                logger.warning(f"Failed to scrape {repo_name}: {e}")
                continue

        logger.info(f"Scraped {len(modules)} OCA modules")
        return modules


class ParityMatcher:
    """Match EE apps to CE+OCA equivalents"""

    # Manual mapping of known equivalents
    KNOWN_MAPPINGS = {
        "documents": {
            "oca_modules": ["document-management/dms", "document-management/dms_field"],
            "parity_level": "full",
            "confidence": 0.95,
            "notes": "OCA DMS provides full feature parity with EE Documents"
        },
        "helpdesk": {
            "oca_modules": ["helpdesk/helpdesk_mgmt", "helpdesk/helpdesk_mgmt_sla"],
            "parity_level": "full",
            "confidence": 0.9,
            "notes": "OCA Helpdesk Management provides SLA and team features"
        },
        "project": {
            "ce_modules": ["project"],
            "oca_modules": ["project/project_timeline"],
            "parity_level": "partial",
            "confidence": 0.7,
            "notes": "CE project + OCA extensions provide core features, missing some EE analytics"
        },
    }

    def __init__(self, oca_modules: List[OCAModule]):
        self.oca_modules = oca_modules
        self.oca_index = self._build_oca_index()

    def _build_oca_index(self) -> dict:
        """Build searchable index of OCA modules"""
        index = {}
        for module in self.oca_modules:
            key = module.name.lower().replace('_', ' ')
            index[key] = module
        return index

    def match_app(self, app: EEApp) -> ParityMapping:
        """Match EE app to CE+OCA equivalents"""
        slug = app.slug.lower()

        # Check known mappings first
        if slug in self.KNOWN_MAPPINGS:
            known = self.KNOWN_MAPPINGS[slug]
            return ParityMapping(
                ee_app_name=app.name,
                ee_app_slug=app.slug,
                ee_category=app.category,
                ee_description=app.description,
                ee_url=app.url,
                parity_level=known["parity_level"],
                ce_modules=known.get("ce_modules", []),
                oca_modules=known["oca_modules"],
                evidence_urls=[m.split('/')[0] for m in known["oca_modules"]],  # Simplified
                confidence_score=known["confidence"],
                notes=known["notes"]
            )

        # Fuzzy matching for unknown apps
        search_terms = [slug, app.name.lower().replace(' ', '_')]
        matched_modules = []

        for term in search_terms:
            for key, module in self.oca_index.items():
                if term in key or key in term:
                    matched_modules.append(f"{module.repo}/{module.name}")

        # Determine parity level based on matches
        if matched_modules:
            parity_level = "partial"
            confidence = 0.5
        else:
            parity_level = "missing"
            confidence = 0.3

        return ParityMapping(
            ee_app_name=app.name,
            ee_app_slug=app.slug,
            ee_category=app.category,
            ee_description=app.description,
            ee_url=app.url,
            parity_level=parity_level,
            oca_modules=matched_modules,
            evidence_urls=[],
            confidence_score=confidence,
            notes="Fuzzy match - requires manual verification"
        )


class SQLGenerator:
    """Generate SQL upserts for ops.ee_parity_map"""

    @staticmethod
    def generate_upsert(mapping: ParityMapping) -> str:
        """Generate SQL INSERT...ON CONFLICT UPDATE statement"""

        # Format arrays for PostgreSQL
        def format_array(items: List[str]) -> str:
            if not items:
                return "ARRAY[]::text[]"
            escaped = [item.replace("'", "''") for item in items]
            return "ARRAY[" + ", ".join(f"'{item}'" for item in escaped) + "]"

        # Escape strings for SQL
        def escape_str(s: str) -> str:
            return s.replace("'", "''")

        sql = f"""
INSERT INTO ops.ee_parity_map (
  ee_app_name, ee_app_slug, ee_category, ee_description, ee_url,
  parity_level, ce_modules, oca_modules, ipai_modules,
  evidence_urls, confidence_score, notes
) VALUES (
  '{escape_str(mapping.ee_app_name)}',
  '{escape_str(mapping.ee_app_slug)}',
  '{escape_str(mapping.ee_category)}',
  '{escape_str(mapping.ee_description)}',
  '{escape_str(mapping.ee_url)}',
  '{mapping.parity_level}',
  {format_array(mapping.ce_modules)},
  {format_array(mapping.oca_modules)},
  {format_array(mapping.ipai_modules)},
  {format_array(mapping.evidence_urls)},
  {mapping.confidence_score},
  '{escape_str(mapping.notes)}'
)
ON CONFLICT (ee_app_slug) DO UPDATE SET
  ee_app_name = EXCLUDED.ee_app_name,
  ee_category = EXCLUDED.ee_category,
  ee_description = EXCLUDED.ee_description,
  ee_url = EXCLUDED.ee_url,
  parity_level = EXCLUDED.parity_level,
  ce_modules = EXCLUDED.ce_modules,
  oca_modules = EXCLUDED.oca_modules,
  ipai_modules = EXCLUDED.ipai_modules,
  evidence_urls = EXCLUDED.evidence_urls,
  confidence_score = EXCLUDED.confidence_score,
  notes = EXCLUDED.notes,
  scraped_at = now(),
  updated_at = now();
"""
        return sql.strip()


def main():
    parser = argparse.ArgumentParser(description="Generate Odoo EE→CE+OCA parity matrix")
    parser.add_argument("--odoo-version", default="19.0", help="Odoo version (default: 19.0)")
    parser.add_argument("--categories", help="Comma-separated list of categories to scrape")
    parser.add_argument("--output", default="parity_upserts.sql", help="Output SQL file")
    parser.add_argument("--json", action="store_true", help="Also output JSON file")
    parser.add_argument("--limit", type=int, help="Limit number of apps to process")
    parser.add_argument("--deterministic", action="store_true",
                       help="Generate deterministic output (fixed timestamp, sorted lists)")

    args = parser.parse_args()

    # Parse categories
    categories = [c.strip() for c in args.categories.split(',')] if args.categories else None

    logger.info("Starting EE→CE+OCA parity matrix generation")
    logger.info(f"Odoo version: {args.odoo_version}")
    if categories:
        logger.info(f"Categories: {', '.join(categories)}")

    # Step 1: Scrape EE apps
    ee_scraper = OdooAppsScraper(version=args.odoo_version)
    ee_apps = ee_scraper.scrape_ee_apps(categories=categories)

    if args.limit:
        ee_apps = ee_apps[:args.limit]

    # Step 2: Scrape OCA modules
    oca_scraper = OCARepoScraper(version=args.odoo_version)
    oca_modules = oca_scraper.scrape_oca_modules()

    # Step 3: Match EE apps to CE+OCA
    matcher = ParityMatcher(oca_modules)
    mappings = [matcher.match_app(app) for app in ee_apps]

    # Step 3.5: Apply deterministic mode if requested
    if args.deterministic:
        logger.info("Applying deterministic mode (fixed timestamp, sorted lists)")
        for mapping in mappings:
            mapping.make_deterministic()
        # Sort mappings alphabetically by ee_app_slug for deterministic ordering
        mappings = sorted(mappings, key=lambda m: m.ee_app_slug)

    # Step 4: Generate SQL
    sql_generator = SQLGenerator()
    sql_statements = [sql_generator.generate_upsert(m) for m in mappings]

    # Write SQL output
    output_path = Path(args.output)
    generated_timestamp = "2026-01-01T00:00:00Z" if args.deterministic else datetime.utcnow().isoformat()
    with output_path.open('w') as f:
        f.write("-- Odoo EE→CE+OCA Parity Matrix\n")
        f.write(f"-- Generated: {generated_timestamp}\n")
        f.write(f"-- Version: {args.odoo_version}\n")
        f.write(f"-- Total mappings: {len(mappings)}\n\n")
        f.write("BEGIN;\n\n")
        f.write("\n\n".join(sql_statements))
        f.write("\n\nCOMMIT;\n")

    logger.info(f"Generated {len(sql_statements)} SQL upsert statements")
    logger.info(f"SQL output written to: {output_path}")

    # Write JSON output if requested
    if args.json:
        json_path = output_path.with_suffix('.json')
        with json_path.open('w') as f:
            json.dump([asdict(m) for m in mappings], f, indent=2)
        logger.info(f"JSON output written to: {json_path}")

    # Print summary
    parity_summary = {}
    for m in mappings:
        parity_summary[m.parity_level] = parity_summary.get(m.parity_level, 0) + 1

    print("\n" + "="*60)
    print("PARITY MATRIX SUMMARY")
    print("="*60)
    print(f"Total EE apps processed: {len(mappings)}")
    for level, count in sorted(parity_summary.items()):
        print(f"  {level}: {count}")
    print("="*60)


if __name__ == "__main__":
    main()
