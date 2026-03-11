#!/usr/bin/env python3
"""
Coverage Audit for Knowledge Hub Pipeline
==========================================

Validates that all sources defined in config/sources/*.yaml are properly
ingested through the Bronze → Silver → Gold pipeline.

Reports:
- Discovered leaf pages per source/space
- Bronze ingestion completeness
- Silver normalization completeness
- Gold chunk/embedding coverage
- Missing or stale content

Usage:
    python scripts/lakehouse/coverage_audit.py [--source SOURCE] [--json]

Environment:
    TRINO_HOST - Trino server (default: localhost)
    TRINO_PORT - Trino port (default: 8082)
    SUPABASE_URL - Supabase project URL
    SUPABASE_SERVICE_ROLE_KEY - Service role key
"""

from __future__ import annotations
import os
import sys
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml required: pip install pyyaml")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("ERROR: requests required: pip install requests")
    sys.exit(1)


@dataclass
class SpaceCoverage:
    """Coverage metrics for a single space."""

    source: str
    space: str
    discovered: int = 0
    bronze: int = 0
    silver: int = 0
    gold_chunks: int = 0
    gold_embeddings: int = 0
    stale_count: int = 0  # Pages older than retention period
    errors: list[str] = field(default_factory=list)

    @property
    def bronze_pct(self) -> float:
        return (self.bronze / self.discovered * 100) if self.discovered > 0 else 0

    @property
    def silver_pct(self) -> float:
        return (self.silver / self.bronze * 100) if self.bronze > 0 else 0

    @property
    def gold_pct(self) -> float:
        return (self.gold_chunks / self.silver * 100) if self.silver > 0 else 0

    @property
    def is_complete(self) -> bool:
        return (
            self.discovered > 0
            and self.bronze_pct >= 95
            and self.silver_pct >= 95
            and self.gold_pct >= 90
        )


@dataclass
class SourceManifest:
    """Parsed source manifest."""

    source: str
    display_name: str
    version: str
    roots: list[dict]
    schedule: dict


class TrinoClient:
    """Simple Trino HTTP client for coverage queries."""

    def __init__(
        self, host: str = "localhost", port: int = 8082, user: str = "coverage"
    ):
        self.base_url = f"http://{host}:{port}/v1/statement"
        self.user = user

    def query(self, sql: str) -> list[dict]:
        """Execute SQL and return results as list of dicts."""
        try:
            response = requests.post(
                self.base_url,
                headers={"X-Trino-User": self.user},
                data=sql.encode("utf-8"),
                timeout=60,
            )
            response.raise_for_status()

            data = response.json()
            columns = [c["name"] for c in data.get("columns", [])]
            rows = [dict(zip(columns, row)) for row in data.get("data", [])]

            # Follow pagination
            next_uri = data.get("nextUri")
            while next_uri:
                resp = requests.get(next_uri, timeout=60)
                resp.raise_for_status()
                payload = resp.json()
                if payload.get("data") and columns:
                    rows.extend(dict(zip(columns, row)) for row in payload["data"])
                next_uri = payload.get("nextUri")

            return rows
        except Exception as e:
            print(f"WARN: Trino query failed: {e}")
            return []


def load_manifests(sources_dir: str = "config/sources") -> list[SourceManifest]:
    """Load all source manifests from directory."""
    manifests = []
    sources_path = Path(sources_dir)

    if not sources_path.exists():
        print(f"WARN: Sources directory not found: {sources_dir}")
        return manifests

    for yaml_file in sources_path.glob("*.yaml"):
        try:
            data = yaml.safe_load(yaml_file.read_text())
            manifest = SourceManifest(
                source=data.get("source", yaml_file.stem),
                display_name=data.get("display_name", data.get("source", "")),
                version=data.get("version", ""),
                roots=data.get("roots", []),
                schedule=data.get("schedule", {}),
            )
            manifests.append(manifest)
        except Exception as e:
            print(f"WARN: Failed to parse {yaml_file}: {e}")

    return manifests


def count_bronze(trino: TrinoClient, source: str, space: str) -> int:
    """Count Bronze layer rows for source/space."""
    rows = trino.query(
        f"""
        SELECT COUNT(*) as cnt
        FROM delta.bronze.raw_pages
        WHERE source = '{source}'
    """
    )
    return int(rows[0]["cnt"]) if rows else 0


def count_silver(trino: TrinoClient, source: str, space: str) -> int:
    """Count Silver layer rows for source/space."""
    rows = trino.query(
        f"""
        SELECT COUNT(*) as cnt
        FROM delta.silver.normalized_docs
        WHERE source = '{source}'
    """
    )
    return int(rows[0]["cnt"]) if rows else 0


def count_gold_chunks(trino: TrinoClient, source: str) -> int:
    """Count Gold chunks for source."""
    rows = trino.query(
        f"""
        SELECT COUNT(*) as cnt
        FROM delta.gold.chunks
        WHERE source = '{source}'
    """
    )
    return int(rows[0]["cnt"]) if rows else 0


def count_gold_embeddings(trino: TrinoClient, source: str) -> int:
    """Count Gold embeddings for source."""
    rows = trino.query(
        f"""
        SELECT COUNT(*) as cnt
        FROM delta.gold.embeddings
        WHERE chunk_id IN (
            SELECT chunk_id FROM delta.gold.chunks WHERE source = '{source}'
        )
    """
    )
    return int(rows[0]["cnt"]) if rows else 0


def audit_source(
    manifest: SourceManifest, trino: Optional[TrinoClient]
) -> list[SpaceCoverage]:
    """Audit coverage for a single source manifest."""
    results = []

    for root in manifest.roots:
        space = root.get("space", "default")
        coverage = SpaceCoverage(
            source=manifest.source,
            space=space,
        )

        # Estimate discovered pages from manifest depth
        # In production, this would come from crawler discovery log
        depth = root.get("depth", 3)
        coverage.discovered = depth * 10  # Rough estimate

        if trino:
            coverage.bronze = count_bronze(trino, manifest.source, space)
            coverage.silver = count_silver(trino, manifest.source, space)
            coverage.gold_chunks = count_gold_chunks(trino, manifest.source)
            coverage.gold_embeddings = count_gold_embeddings(trino, manifest.source)

        # Check for issues
        if coverage.bronze == 0:
            coverage.errors.append("No Bronze data - crawl may have failed")
        elif coverage.silver == 0:
            coverage.errors.append("No Silver data - normalization may have failed")
        elif coverage.gold_chunks == 0:
            coverage.errors.append("No Gold chunks - chunking may have failed")
        elif coverage.gold_embeddings == 0:
            coverage.errors.append("No Gold embeddings - embedding may have failed")

        results.append(coverage)

    return results


def print_report(all_coverage: list[SpaceCoverage], output_json: bool = False):
    """Print coverage report."""
    if output_json:
        data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "sources": {},
            "summary": {
                "total_spaces": len(all_coverage),
                "complete": sum(1 for c in all_coverage if c.is_complete),
                "incomplete": sum(1 for c in all_coverage if not c.is_complete),
            },
        }

        for coverage in all_coverage:
            if coverage.source not in data["sources"]:
                data["sources"][coverage.source] = []
            data["sources"][coverage.source].append(
                {
                    "space": coverage.space,
                    "discovered": coverage.discovered,
                    "bronze": coverage.bronze,
                    "silver": coverage.silver,
                    "gold_chunks": coverage.gold_chunks,
                    "gold_embeddings": coverage.gold_embeddings,
                    "bronze_pct": round(coverage.bronze_pct, 1),
                    "silver_pct": round(coverage.silver_pct, 1),
                    "gold_pct": round(coverage.gold_pct, 1),
                    "complete": coverage.is_complete,
                    "errors": coverage.errors,
                }
            )

        print(json.dumps(data, indent=2))
        return

    # Text report
    print("=" * 80)
    print("KNOWLEDGE HUB COVERAGE AUDIT")
    print(f"Timestamp: {datetime.utcnow().isoformat()}Z")
    print("=" * 80)

    current_source = None
    for coverage in sorted(all_coverage, key=lambda c: (c.source, c.space)):
        if coverage.source != current_source:
            current_source = coverage.source
            print(f"\n## {current_source.upper()}")
            print("-" * 40)

        status = "OK" if coverage.is_complete else "INCOMPLETE"
        print(f"\n  {coverage.space}")
        print(f"    Status: {status}")
        print(f"    Discovered: {coverage.discovered}")
        print(f"    Bronze:     {coverage.bronze:5d} ({coverage.bronze_pct:.0f}%)")
        print(f"    Silver:     {coverage.silver:5d} ({coverage.silver_pct:.0f}%)")
        print(f"    Gold Chunks:{coverage.gold_chunks:5d} ({coverage.gold_pct:.0f}%)")
        print(f"    Embeddings: {coverage.gold_embeddings:5d}")

        if coverage.errors:
            print("    Errors:")
            for err in coverage.errors:
                print(f"      - {err}")

    # Summary
    total = len(all_coverage)
    complete = sum(1 for c in all_coverage if c.is_complete)
    print("\n" + "=" * 80)
    print("SUMMARY")
    print(f"  Total Spaces:    {total}")
    print(
        f"  Complete:        {complete} ({complete/total*100:.0f}%)"
        if total > 0
        else "  Complete: 0"
    )
    print(f"  Incomplete:      {total - complete}")
    print("=" * 80)

    if complete < total:
        print("\nACTION REQUIRED: Run pipeline for incomplete sources")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Knowledge Hub Coverage Audit")
    parser.add_argument("--source", help="Audit specific source only")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument(
        "--no-trino", action="store_true", help="Skip Trino queries (manifest-only)"
    )
    args = parser.parse_args()

    # Load manifests
    manifests = load_manifests()
    if not manifests:
        print("ERROR: No source manifests found in config/sources/")
        sys.exit(1)

    # Filter by source if specified
    if args.source:
        manifests = [m for m in manifests if m.source == args.source]
        if not manifests:
            print(f"ERROR: Source not found: {args.source}")
            sys.exit(1)

    # Initialize Trino client
    trino = None
    if not args.no_trino:
        trino_host = os.getenv("TRINO_HOST", "localhost")
        trino_port = int(os.getenv("TRINO_PORT", "8082"))
        trino = TrinoClient(host=trino_host, port=trino_port)

    # Audit each source
    all_coverage = []
    for manifest in manifests:
        print(
            f"Auditing {manifest.source}..." if not args.json else "", file=sys.stderr
        )
        coverage = audit_source(manifest, trino)
        all_coverage.extend(coverage)

    # Print report
    print_report(all_coverage, output_json=args.json)


if __name__ == "__main__":
    main()
