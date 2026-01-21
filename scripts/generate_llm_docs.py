#!/usr/bin/env python3
"""
LLM Documentation Generator

Generates LLM-friendly documentation by querying infrastructure state
from Supabase KG and combining with static documentation templates.

Usage:
    python scripts/generate_llm_docs.py [--output-dir docs/llm] [--dry-run]
"""

import argparse
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class LLMDocsGenerator:
    """Generates LLM-friendly documentation from infrastructure state."""

    def __init__(
        self,
        output_dir: str,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.client = None

        if supabase_url and supabase_key:
            try:
                from supabase import create_client

                self.client = create_client(supabase_url, supabase_key)
            except ImportError:
                logger.warning("supabase-py not installed, using static templates only")

    def query_kg(self, query: str) -> List[Dict[str, Any]]:
        """Execute a query against the KG and return results."""
        if not self.client:
            return []

        try:
            result = self.client.rpc("query_kg", {"sql": query}).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.warning(f"KG query failed: {e}")
            return []

    def get_infrastructure_nodes(self) -> List[Dict[str, Any]]:
        """Get all infrastructure nodes from KG."""
        if not self.client:
            return []

        try:
            result = (
                self.client.from_("kg.v_infrastructure_nodes").select("*").execute()
            )
            return result.data if result.data else []
        except Exception as e:
            logger.warning(f"Could not fetch infrastructure nodes: {e}")
            return []

    def get_service_dependencies(self) -> List[Dict[str, Any]]:
        """Get service dependency graph from KG."""
        if not self.client:
            return []

        try:
            result = (
                self.client.from_("kg.v_service_dependencies").select("*").execute()
            )
            return result.data if result.data else []
        except Exception as e:
            logger.warning(f"Could not fetch service dependencies: {e}")
            return []

    def generate_index(self) -> str:
        """Generate the main index document."""
        content = f"""# LLM Documentation Index

> **Generated**: {datetime.utcnow().isoformat()}Z
> **Purpose**: Machine-readable documentation for AI agents

---

## Document Catalog

### Platform Overview
- [STACK_OVERVIEW.md](STACK_OVERVIEW.md) - High-level architecture and SSOT rules
- [STACK_RELATIONSHIPS.md](STACK_RELATIONSHIPS.md) - Entity relationship triples
- [GLOSSARY.md](GLOSSARY.md) - Canonical term definitions

### Infrastructure Stacks
- [SUPABASE_STACK.md](SUPABASE_STACK.md) - Supabase configuration and schemas
- [ODOO_PLATFORM.md](ODOO_PLATFORM.md) - Odoo CE + OCA + IPAI architecture
- [DIGITALOCEAN_DOCKER_STACK.md](DIGITALOCEAN_DOCKER_STACK.md) - Infrastructure and containers
- [VERCEL_STACK.md](VERCEL_STACK.md) - Vercel deployment configuration

### Integration Guides
- [MCP_INTEGRATION.md](MCP_INTEGRATION.md) - Model Context Protocol setup
- [LLM_QUERY_PLAYBOOK.md](LLM_QUERY_PLAYBOOK.md) - Query recipes for agents

---

## Quick Reference

### Key Identifiers
| Resource | Identifier |
|----------|------------|
| Supabase Project | `spdtwktxdalcfigzeqrz` |
| DO Database Cluster | `odoo-db-sgp1` |
| DO Droplet | `odoo-erp-prod` |
| GitHub Repo | `jgtolentino/odoo-ce` |

### SSOT Rules
| Data Type | Source of Truth |
|-----------|-----------------|
| Business data | Odoo Postgres |
| Knowledge/Memory | Supabase |
| Code/Config | GitHub |

### Schema Quick Reference
| Schema | Purpose |
|--------|---------|
| `kb` | Knowledge Base (RAG) |
| `kg` | Knowledge Graph |
| `agent_mem` | Agent Memory |
| `docs` | Document chunks |
| `ops_advisor` | Recommendations |
| `odoo_shadow` | Odoo mirror (read-only) |

---

## Usage Guidelines

### For LLM Agents

1. **Start here** when needing context about the stack
2. **Query playbook** for SQL patterns
3. **Glossary** for term definitions
4. **Stack docs** for detailed configuration

### Document Conventions

- All documents use consistent heading structure
- Code blocks include language hints
- Tables summarize key configurations
- Query examples are parameterized with `$param` syntax
"""
        return content

    def generate_dynamic_state(self) -> str:
        """Generate dynamic infrastructure state document."""
        nodes = self.get_infrastructure_nodes()
        deps = self.get_service_dependencies()

        content = f"""# Dynamic Infrastructure State

> **Snapshot**: {datetime.utcnow().isoformat()}Z
> **Source**: Supabase Knowledge Graph

---

## Infrastructure Inventory

"""
        if nodes:
            # Group by kind
            by_kind: Dict[str, List] = {}
            for node in nodes:
                kind = node.get("kind", "unknown")
                if kind not in by_kind:
                    by_kind[kind] = []
                by_kind[kind].append(node)

            for kind, kind_nodes in sorted(by_kind.items()):
                content += (
                    f"### {kind.replace('_', ' ').title()} ({len(kind_nodes)})\n\n"
                )
                content += "| Label | Key | Updated |\n"
                content += "|-------|-----|----------|\n"
                for node in kind_nodes[:20]:  # Limit to 20 per kind
                    content += f"| {node.get('label', '')} | `{node.get('key', '')}` | {node.get('updated_at', '')[:10]} |\n"
                content += "\n"
        else:
            content += "*No infrastructure nodes discovered yet. Run `scripts/infra-discovery/discover_all.py`*\n\n"

        content += "---\n\n## Service Dependencies\n\n"

        if deps:
            content += "| Service | Predicate | Dependency |\n"
            content += "|---------|-----------|------------|\n"
            for dep in deps[:50]:  # Limit to 50
                content += f"| {dep.get('service', '')} | {dep.get('predicate', '')} | {dep.get('dependency', '')} |\n"
        else:
            content += "*No service dependencies mapped yet.*\n"

        return content

    def generate_all(self) -> Dict[str, str]:
        """Generate all documentation files."""
        generated = {}

        # Generate index
        index_path = self.output_dir / "INDEX.md"
        index_content = self.generate_index()
        with open(index_path, "w") as f:
            f.write(index_content)
        generated["INDEX.md"] = str(index_path)

        # Generate dynamic state if KG available
        if self.client:
            state_path = self.output_dir / "DYNAMIC_STATE.md"
            state_content = self.generate_dynamic_state()
            with open(state_path, "w") as f:
                f.write(state_content)
            generated["DYNAMIC_STATE.md"] = str(state_path)

        # Generate metadata JSON
        metadata = {
            "generated_at": datetime.utcnow().isoformat(),
            "documents": list(generated.keys()),
            "kg_connected": self.client is not None,
        }
        metadata_path = self.output_dir / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        generated["metadata.json"] = str(metadata_path)

        return generated


def main():
    parser = argparse.ArgumentParser(description="Generate LLM Documentation")
    parser.add_argument(
        "--output-dir",
        "-o",
        default="docs/llm",
        help="Output directory for generated docs",
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Show what would be generated without writing",
    )

    args = parser.parse_args()

    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

    generator = LLMDocsGenerator(
        output_dir=args.output_dir, supabase_url=supabase_url, supabase_key=supabase_key
    )

    if args.dry_run:
        print(f"Would generate docs to: {args.output_dir}")
        print("Documents: INDEX.md, DYNAMIC_STATE.md, metadata.json")
        return

    generated = generator.generate_all()

    print(f"Generated {len(generated)} documents:")
    for name, path in generated.items():
        print(f"  - {name}: {path}")


if __name__ == "__main__":
    main()
