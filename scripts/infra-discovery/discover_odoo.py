#!/usr/bin/env python3
"""
Odoo Infrastructure Discovery

Discovers Odoo modules, models, and dependencies.
Works via XML-RPC API or by parsing module manifests.
"""

import json
import logging
import os
import xmlrpc.client
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def parse_manifest(manifest_path: Path) -> Optional[Dict[str, Any]]:
    """Parse an Odoo module manifest file."""
    try:
        with open(manifest_path, "r") as f:
            content = f.read()
            # Safely evaluate the manifest dict
            return eval(content, {"__builtins__": {}})
    except Exception as e:
        logger.warning(f"Could not parse {manifest_path}: {e}")
        return None


def discover_modules_from_filesystem(addons_paths: List[str]) -> List[Dict[str, Any]]:
    """Discover modules by scanning filesystem."""
    modules = []

    for addons_path in addons_paths:
        addons_dir = Path(addons_path)
        if not addons_dir.exists():
            continue

        for module_dir in addons_dir.iterdir():
            if not module_dir.is_dir():
                continue

            manifest_path = module_dir / "__manifest__.py"
            if not manifest_path.exists():
                continue

            manifest = parse_manifest(manifest_path)
            if manifest:
                modules.append(
                    {
                        "name": module_dir.name,
                        "path": str(module_dir),
                        "version": manifest.get("version", "1.0"),
                        "summary": manifest.get(
                            "summary", manifest.get("description", "")[:100]
                        ),
                        "author": manifest.get("author", "Unknown"),
                        "depends": manifest.get("depends", []),
                        "category": manifest.get("category", "Uncategorized"),
                        "installable": manifest.get("installable", True),
                        "application": manifest.get("application", False),
                        "auto_install": manifest.get("auto_install", False),
                    }
                )

    return modules


def discover_modules_from_api(
    url: str, db: str, username: str, password: str
) -> List[Dict[str, Any]]:
    """Discover modules via Odoo XML-RPC API."""
    modules = []

    try:
        common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
        uid = common.authenticate(db, username, password, {})

        if not uid:
            logger.error("Odoo authentication failed")
            return modules

        models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

        # Get all modules
        module_ids = models.execute_kw(
            db, uid, password, "ir.module.module", "search", [[]]
        )

        module_data = models.execute_kw(
            db,
            uid,
            password,
            "ir.module.module",
            "read",
            [module_ids],
            {
                "fields": [
                    "name",
                    "state",
                    "latest_version",
                    "summary",
                    "author",
                    "category_id",
                    "application",
                    "auto_install",
                ]
            },
        )

        for mod in module_data:
            modules.append(
                {
                    "name": mod["name"],
                    "state": mod["state"],
                    "version": mod.get("latest_version", ""),
                    "summary": mod.get("summary", ""),
                    "author": mod.get("author", ""),
                    "category": (
                        mod.get("category_id", [None, "Uncategorized"])[1]
                        if mod.get("category_id")
                        else "Uncategorized"
                    ),
                    "application": mod.get("application", False),
                    "auto_install": mod.get("auto_install", False),
                }
            )

        # Get module dependencies
        dep_ids = models.execute_kw(
            db, uid, password, "ir.module.module.dependency", "search", [[]]
        )

        dep_data = models.execute_kw(
            db,
            uid,
            password,
            "ir.module.module.dependency",
            "read",
            [dep_ids],
            {"fields": ["module_id", "name", "depend_id"]},
        )

        # Map dependencies to modules
        for dep in dep_data:
            if dep.get("module_id"):
                module_name = next(
                    (m["name"] for m in modules if m["name"] == dep["module_id"][1]),
                    None,
                )
                if module_name:
                    for mod in modules:
                        if mod["name"] == module_name:
                            if "depends" not in mod:
                                mod["depends"] = []
                            mod["depends"].append(dep["name"])

    except Exception as e:
        logger.error(f"Odoo API error: {e}")

    return modules


def discover_odoo(orchestrator) -> Dict[str, Any]:
    """
    Discover Odoo infrastructure and store in KG.

    Returns summary of discovered resources.
    """
    # Configuration
    odoo_url = os.environ.get("ODOO_URL", "http://localhost:8069")
    odoo_db = os.environ.get("ODOO_DB", "odoo_core")
    odoo_user = os.environ.get("ODOO_USER")
    odoo_password = os.environ.get("ODOO_PASSWORD")

    # Default addons paths
    addons_paths = os.environ.get("ODOO_ADDONS_PATHS", "addons/ipai,addons/oca").split(
        ","
    )

    discovered = {"modules": 0, "dependencies": 0, "models": 0}

    # First try filesystem discovery (always available)
    modules_fs = discover_modules_from_filesystem(addons_paths)

    # Then try API discovery if credentials available
    modules_api = []
    if odoo_user and odoo_password:
        modules_api = discover_modules_from_api(
            odoo_url, odoo_db, odoo_user, odoo_password
        )

    # Merge results (API takes precedence for state info)
    modules_by_name = {}
    for mod in modules_fs:
        modules_by_name[mod["name"]] = mod

    for mod in modules_api:
        if mod["name"] in modules_by_name:
            modules_by_name[mod["name"]].update(mod)
        else:
            modules_by_name[mod["name"]] = mod

    modules = list(modules_by_name.values())

    # Create module nodes
    module_nodes = {}

    for mod in modules:
        # Determine module type based on name prefix
        module_type = "custom"
        if mod["name"].startswith("ipai_"):
            module_type = "ipai"
        elif mod["name"].startswith("l10n_"):
            module_type = "localization"
        elif mod.get("path") and "/oca/" in mod.get("path", "").lower():
            module_type = "oca"
        elif not mod.get("path"):
            module_type = "core"

        node_id = orchestrator.upsert_node(
            kind="odoo_module",
            key=f"odoo:module:{mod['name']}",
            label=mod["name"],
            attrs={
                "version": mod.get("version", ""),
                "summary": mod.get("summary", ""),
                "author": mod.get("author", ""),
                "category": mod.get("category", ""),
                "state": mod.get("state", "unknown"),
                "module_type": module_type,
                "application": mod.get("application", False),
                "auto_install": mod.get("auto_install", False),
                "path": mod.get("path"),
            },
        )
        module_nodes[mod["name"]] = node_id
        discovered["modules"] += 1

    # Create dependency edges
    for mod in modules:
        src_node_id = module_nodes.get(mod["name"])
        if not src_node_id:
            continue

        for dep_name in mod.get("depends", []):
            dst_node_id = module_nodes.get(dep_name)

            if dst_node_id:
                orchestrator.upsert_edge(
                    src_node_id=src_node_id,
                    predicate="DEPENDS_ON",
                    dst_node_id=dst_node_id,
                    source_type="odoo",
                    source_ref=f"odoo:module:{mod['name']}:manifest",
                )
                discovered["dependencies"] += 1
            else:
                # Create placeholder node for external dependency
                ext_node_id = orchestrator.upsert_node(
                    kind="odoo_module",
                    key=f"odoo:module:{dep_name}",
                    label=dep_name,
                    attrs={"state": "external", "module_type": "external"},
                )
                module_nodes[dep_name] = ext_node_id

                orchestrator.upsert_edge(
                    src_node_id=src_node_id,
                    predicate="DEPENDS_ON",
                    dst_node_id=ext_node_id,
                    source_type="odoo",
                    source_ref=f"odoo:module:{mod['name']}:manifest",
                )
                discovered["dependencies"] += 1

    # Create Odoo service node and link to database
    odoo_service_node = orchestrator.upsert_node(
        kind="service",
        key="service:odoo-core",
        label="Odoo Core",
        attrs={"url": odoo_url, "database": odoo_db, "service_type": "erp"},
    )

    # Link modules to service
    for mod_name, node_id in module_nodes.items():
        orchestrator.upsert_edge(
            src_node_id=node_id,
            predicate="DEPLOYED_TO",
            dst_node_id=odoo_service_node,
            source_type="odoo",
            source_ref=f"odoo:module:{mod_name}",
        )

    return discovered


if __name__ == "__main__":
    # Standalone test
    class MockOrchestrator:
        def upsert_node(self, kind, key, label, attrs):
            print(f"Node: {kind}/{key} ({label})")
            return key

        def upsert_edge(self, src_node_id, predicate, dst_node_id, **kwargs):
            print(f"Edge: {src_node_id} --{predicate}--> {dst_node_id}")
            return f"{src_node_id}:{predicate}:{dst_node_id}"

    result = discover_odoo(MockOrchestrator())
    print(f"Result: {result}")
