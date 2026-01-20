#!/usr/bin/env python3
"""
Odoo Infrastructure Discovery
Queries Odoo database for installed modules, models, and views
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict
import subprocess


def query_odoo_modules() -> List[Dict]:
    """Query Odoo database for installed modules"""
    dsn = os.environ.get("ODOO_DB_DSN") or os.environ.get("POSTGRES_URL")

    if not dsn:
        print("ERROR: Missing Odoo database credentials")
        print("Required environment variables:")
        print("  - ODOO_DB_DSN or POSTGRES_URL")
        sys.exit(1)

    # Query ir_module_module for installed modules
    sql = """
        SELECT
            name,
            state,
            latest_version,
            author,
            summary,
            website,
            category_id
        FROM ir_module_module
        WHERE state IN ('installed', 'to upgrade', 'to install')
        ORDER BY name;
    """

    try:
        result = subprocess.run(
            ["psql", dsn, "-t", "-c", sql],
            capture_output=True,
            text=True,
            check=True
        )

        modules = []
        for line in result.stdout.strip().split('\n'):
            if not line.strip() or line.strip() == '(0 rows)':
                continue

            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 4:
                modules.append({
                    "name": parts[0],
                    "state": parts[1],
                    "version": parts[2] if len(parts) > 2 else None,
                    "author": parts[3] if len(parts) > 3 else None,
                    "summary": parts[4] if len(parts) > 4 else None,
                    "website": parts[5] if len(parts) > 5 else None
                })

        return modules

    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to query Odoo database: {e}")
        print(f"stderr: {e.stderr}")
        sys.exit(1)


def query_odoo_models() -> List[Dict]:
    """Query Odoo database for models"""
    dsn = os.environ.get("ODOO_DB_DSN") or os.environ.get("POSTGRES_URL")

    sql = """
        SELECT
            model,
            name,
            info,
            state
        FROM ir_model
        WHERE transient = false
        ORDER BY model;
    """

    try:
        result = subprocess.run(
            ["psql", dsn, "-t", "-c", sql],
            capture_output=True,
            text=True,
            check=True
        )

        models = []
        for line in result.stdout.strip().split('\n'):
            if not line.strip() or line.strip() == '(0 rows)':
                continue

            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 2:
                models.append({
                    "model": parts[0],
                    "name": parts[1],
                    "info": parts[2] if len(parts) > 2 else None,
                    "state": parts[3] if len(parts) > 3 else "base"
                })

        return models

    except subprocess.CalledProcessError as e:
        print(f"WARNING: Could not query models: {e}")
        return []


def discover_modules(modules: List[Dict]) -> tuple[List[Dict], List[Dict]]:
    """Convert modules to nodes and edges"""
    nodes = []
    edges = []

    # Create Odoo instance node
    odoo_id = "odoo:instance:production"
    nodes.append({
        "id": odoo_id,
        "source": "odoo",
        "kind": "instance",
        "key": "production",
        "name": "Odoo Production (CE 18.0)",
        "props": {
            "version": "18.0",
            "edition": "CE",
            "database": "production"
        }
    })

    # Create module nodes
    for module in modules:
        module_name = module["name"]
        module_id = f"odoo:module:{module_name}"

        nodes.append({
            "id": module_id,
            "source": "odoo",
            "kind": "module",
            "key": module_name,
            "name": module_name,
            "props": {
                "state": module["state"],
                "version": module.get("version"),
                "author": module.get("author"),
                "summary": module.get("summary"),
                "website": module.get("website")
            }
        })

        # Edge: instance HAS_MODULE module
        edges.append({
            "id": f"{odoo_id}→{module_id}",
            "source": "odoo",
            "from_id": odoo_id,
            "to_id": module_id,
            "type": "HAS_MODULE",
            "props": {
                "state": module["state"]
            }
        })

    return nodes, edges


def discover_models(models: List[Dict], modules: List[Dict]) -> tuple[List[Dict], List[Dict]]:
    """Convert models to nodes and edges"""
    nodes = []
    edges = []

    # Map model names to likely modules (best effort)
    module_map = {}
    for module in modules:
        module_map[module["name"]] = f"odoo:module:{module['name']}"

    for model in models:
        model_name = model["model"]
        model_id = f"odoo:model:{model_name}"

        nodes.append({
            "id": model_id,
            "source": "odoo",
            "kind": "model",
            "key": model_name,
            "name": model["name"],
            "props": {
                "model": model_name,
                "technical_name": model_name,
                "info": model.get("info"),
                "state": model.get("state", "base")
            }
        })

        # Try to link model to module (heuristic: model prefix matches module name)
        # e.g., "account.move" → "account" module
        model_prefix = model_name.split('.')[0]
        parent_module_id = module_map.get(model_prefix)

        if parent_module_id:
            # Edge: module DEFINES_MODEL model
            edges.append({
                "id": f"{parent_module_id}→{model_id}",
                "source": "odoo",
                "from_id": parent_module_id,
                "to_id": model_id,
                "type": "DEFINES_MODEL",
                "props": {}
            })
        else:
            # Fallback: link to base module
            base_module_id = "odoo:module:base"
            if base_module_id in [e["from_id"] for e in edges]:  # Only if base exists
                edges.append({
                    "id": f"{base_module_id}→{model_id}",
                    "source": "odoo",
                    "from_id": base_module_id,
                    "to_id": model_id,
                    "type": "DEFINES_MODEL",
                    "props": {
                        "inferred": True
                    }
                })

    return nodes, edges


def main():
    """Main discovery routine"""
    print("=" * 60)
    print("Odoo Infrastructure Discovery")
    print("=" * 60)
    print()

    all_nodes = []
    all_edges = []

    # Query modules
    print("Querying installed modules...")
    modules = query_odoo_modules()
    print(f"  Found {len(modules)} installed modules")
    print()

    # Discover module nodes and edges
    print("Converting modules to graph...")
    module_nodes, module_edges = discover_modules(modules)
    all_nodes.extend(module_nodes)
    all_edges.extend(module_edges)
    print(f"  Created {len(module_nodes)} nodes, {len(module_edges)} edges")
    print()

    # Query models
    print("Querying Odoo models...")
    models = query_odoo_models()
    print(f"  Found {len(models)} models")
    print()

    # Discover model nodes and edges
    if models:
        print("Converting models to graph...")
        model_nodes, model_edges = discover_models(models, modules)
        all_nodes.extend(model_nodes)
        all_edges.extend(model_edges)
        print(f"  Created {len(model_nodes)} nodes, {len(model_edges)} edges")
        print()

    # Write output files
    repo_root = Path(__file__).parent.parent
    output_dir = repo_root / "infra" / "infra_graph" / "sources"
    output_dir.mkdir(parents=True, exist_ok=True)

    nodes_path = output_dir / "odoo_nodes.json"
    edges_path = output_dir / "odoo_edges.json"

    with open(nodes_path, 'w') as f:
        json.dump(all_nodes, f, indent=2)

    with open(edges_path, 'w') as f:
        json.dump(all_edges, f, indent=2)

    print("=" * 60)
    print("✅ Odoo discovery complete")
    print("=" * 60)
    print(f"Nodes discovered: {len(all_nodes)}")
    print(f"  Instances: 1")
    print(f"  Modules: {len([n for n in all_nodes if n['kind'] == 'module'])}")
    print(f"  Models: {len([n for n in all_nodes if n['kind'] == 'model'])}")
    print(f"Edges discovered: {len(all_edges)}")
    print()
    print(f"Output files:")
    print(f"  {nodes_path}")
    print(f"  {edges_path}")
    print()
    print("Next step: Run scripts/build_infra_graph.py to merge into unified graph")
    print()


if __name__ == "__main__":
    main()
