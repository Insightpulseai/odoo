#!/usr/bin/env python3
"""
Infrastructure Discovery Orchestrator

Discovers infrastructure from multiple sources and stores in Supabase KG.
Sources: Vercel, Supabase, DigitalOcean, Docker, Odoo, GitHub

Usage:
    python scripts/infra-discovery/discover_all.py [--source SOURCE] [--dry-run]
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from uuid import UUID, uuid4

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from discover_vercel import discover_vercel
from discover_supabase import discover_supabase
from discover_digitalocean import discover_digitalocean
from discover_docker import discover_docker
from discover_odoo import discover_odoo
from discover_github import discover_github

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Default tenant ID for infrastructure (system tenant)
SYSTEM_TENANT_ID = os.environ.get(
    "SYSTEM_TENANT_ID", "00000000-0000-0000-0000-000000000001"
)


class InfraDiscoveryOrchestrator:
    """Orchestrates infrastructure discovery across all sources."""

    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        tenant_id: str,
        dry_run: bool = False,
    ):
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.tenant_id = tenant_id
        self.dry_run = dry_run
        self.nodes_discovered = 0
        self.edges_discovered = 0

        if not dry_run:
            try:
                from supabase import create_client

                self.client = create_client(supabase_url, supabase_key)
            except ImportError:
                logger.warning("supabase-py not installed. Running in dry-run mode.")
                self.dry_run = True
                self.client = None
        else:
            self.client = None

    def start_run(self, discovery_type: str) -> Optional[str]:
        """Start a discovery run and return run_id."""
        if self.dry_run:
            return str(uuid4())

        result = self.client.rpc(
            "kg.start_discovery_run",
            {
                "p_tenant": self.tenant_id,
                "p_discovery_type": discovery_type,
                "p_metadata": json.dumps({"started_by": "discover_all.py"}),
            },
        ).execute()

        return result.data if result.data else None

    def complete_run(self, run_id: str, error: Optional[str] = None):
        """Complete a discovery run."""
        if self.dry_run:
            return

        self.client.rpc(
            "kg.complete_discovery_run",
            {
                "p_run_id": run_id,
                "p_nodes_discovered": self.nodes_discovered,
                "p_edges_discovered": self.edges_discovered,
                "p_error_message": error,
            },
        ).execute()

    def upsert_node(
        self, kind: str, key: str, label: str, attrs: dict
    ) -> Optional[str]:
        """Upsert a node and return node_id."""
        self.nodes_discovered += 1

        if self.dry_run:
            logger.info(f"[DRY-RUN] Would upsert node: {kind}/{key} ({label})")
            return str(uuid4())

        result = self.client.rpc(
            "kg.upsert_node",
            {
                "p_tenant": self.tenant_id,
                "p_kind": kind,
                "p_key": key,
                "p_label": label,
                "p_attrs": json.dumps(attrs),
            },
        ).execute()

        return result.data if result.data else None

    def upsert_edge(
        self,
        src_node_id: str,
        predicate: str,
        dst_node_id: str,
        weight: float = 1.0,
        source_type: Optional[str] = None,
        source_ref: Optional[str] = None,
    ) -> Optional[str]:
        """Upsert an edge and return edge_id."""
        self.edges_discovered += 1

        if self.dry_run:
            logger.info(
                f"[DRY-RUN] Would upsert edge: {src_node_id} --{predicate}--> {dst_node_id}"
            )
            return str(uuid4())

        result = self.client.rpc(
            "kg.upsert_edge",
            {
                "p_tenant": self.tenant_id,
                "p_src_node_id": src_node_id,
                "p_predicate": predicate,
                "p_dst_node_id": dst_node_id,
                "p_weight": weight,
                "p_source_type": source_type,
                "p_source_ref": source_ref,
            },
        ).execute()

        return result.data if result.data else None

    def discover_all(self, sources: Optional[list] = None):
        """Run discovery for all (or specified) sources."""
        all_sources = ["vercel", "supabase", "digitalocean", "docker", "odoo", "github"]
        sources_to_run = sources if sources else all_sources

        logger.info(f"Starting infrastructure discovery for: {sources_to_run}")

        results = {}
        for source in sources_to_run:
            try:
                logger.info(f"Discovering {source}...")
                run_id = self.start_run(source)

                if source == "vercel":
                    results[source] = discover_vercel(self)
                elif source == "supabase":
                    results[source] = discover_supabase(self)
                elif source == "digitalocean":
                    results[source] = discover_digitalocean(self)
                elif source == "docker":
                    results[source] = discover_docker(self)
                elif source == "odoo":
                    results[source] = discover_odoo(self)
                elif source == "github":
                    results[source] = discover_github(self)
                else:
                    logger.warning(f"Unknown source: {source}")
                    continue

                self.complete_run(run_id)
                logger.info(f"Completed {source} discovery: {results[source]}")

            except Exception as e:
                logger.error(f"Error discovering {source}: {e}")
                if run_id:
                    self.complete_run(run_id, str(e))
                results[source] = {"error": str(e)}

        return results


def main():
    parser = argparse.ArgumentParser(
        description="Infrastructure Discovery Orchestrator"
    )
    parser.add_argument(
        "--source",
        "-s",
        action="append",
        choices=["vercel", "supabase", "digitalocean", "docker", "odoo", "github"],
        help="Specific source to discover (can be repeated)",
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Run without making changes to Supabase",
    )
    parser.add_argument("--output", "-o", help="Output results to JSON file")

    args = parser.parse_args()

    # Get Supabase credentials
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

    if not args.dry_run and (not supabase_url or not supabase_key):
        logger.error(
            "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required (or use --dry-run)"
        )
        sys.exit(1)

    # Run discovery
    orchestrator = InfraDiscoveryOrchestrator(
        supabase_url=supabase_url or "",
        supabase_key=supabase_key or "",
        tenant_id=SYSTEM_TENANT_ID,
        dry_run=args.dry_run,
    )

    results = orchestrator.discover_all(args.source)

    # Summary
    summary = {
        "timestamp": datetime.utcnow().isoformat(),
        "dry_run": args.dry_run,
        "total_nodes": orchestrator.nodes_discovered,
        "total_edges": orchestrator.edges_discovered,
        "sources": results,
    }

    print(json.dumps(summary, indent=2))

    if args.output:
        with open(args.output, "w") as f:
            json.dump(summary, f, indent=2)


if __name__ == "__main__":
    main()
