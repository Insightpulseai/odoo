#!/usr/bin/env python3
"""
Generate Repository Index and Knowledge Graph Seed
Scans repository and creates docs/INDEX.md + docs/knowledge/graph_seed.json
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


def scan_spec_bundles(spec_dir: Path) -> List[Dict[str, Any]]:
    """Scan spec/ directory for spec bundles"""
    bundles = []
    if not spec_dir.exists():
        return bundles

    for d in sorted(spec_dir.iterdir()):
        if d.is_dir() and (d / "constitution.md").exists():
            bundle = {
                "id": f"spec:{d.name}",
                "name": d.name,
                "path": str(d.relative_to(spec_dir.parent)),
                "files": [],
            }

            # Check required files
            for file_name in [
                "constitution.md",
                "prd.md",
                "plan.md",
                "tasks.md",
            ]:
                file_path = d / file_name
                bundle["files"].append(
                    {
                        "name": file_name,
                        "exists": file_path.exists(),
                        "size": file_path.stat().st_size if file_path.exists() else 0,
                    }
                )

            bundles.append(bundle)

    return bundles


def scan_apps(apps_dir: Path) -> List[Dict[str, Any]]:
    """Scan apps/ directory for applications"""
    apps = []
    if not apps_dir.exists():
        return apps

    for d in sorted(apps_dir.iterdir()):
        if d.is_dir() and (d / "package.json").exists():
            package_json = json.loads((d / "package.json").read_text(encoding="utf-8"))
            apps.append(
                {
                    "id": f"app:{d.name}",
                    "name": d.name,
                    "path": str(d.relative_to(apps_dir.parent)),
                    "version": package_json.get("version", "unknown"),
                    "description": package_json.get("description", ""),
                }
            )

    return apps


def scan_odoo_modules(addons_dir: Path) -> List[Dict[str, Any]]:
    """Scan addons/ directory for Odoo modules"""
    modules = []
    if not addons_dir.exists():
        return modules

    # Scan ipai/ namespace
    ipai_dir = addons_dir / "ipai"
    if ipai_dir.exists():
        for d in sorted(ipai_dir.iterdir()):
            if d.is_dir() and (d / "__manifest__.py").exists():
                modules.append(
                    {
                        "id": f"module:ipai.{d.name}",
                        "name": d.name,
                        "namespace": "ipai",
                        "path": str(d.relative_to(addons_dir.parent)),
                    }
                )

    return modules


def scan_workflows(workflows_dir: Path) -> List[Dict[str, Any]]:
    """Scan .github/workflows/ for CI/CD workflows"""
    workflows = []
    if not workflows_dir.exists():
        return workflows

    for f in sorted(workflows_dir.glob("*.yml")):
        workflows.append(
            {
                "id": f"workflow:{f.stem}",
                "name": f.stem,
                "path": str(f.relative_to(workflows_dir.parent.parent)),
            }
        )

    return workflows


def scan_scripts(scripts_dir: Path) -> List[Dict[str, Any]]:
    """Scan scripts/ directory for automation scripts"""
    scripts = []
    if not scripts_dir.exists():
        return scripts

    for f in sorted(scripts_dir.glob("*.sh")):
        scripts.append(
            {
                "id": f"script:{f.stem}",
                "name": f.name,
                "path": str(f.relative_to(scripts_dir.parent)),
                "executable": f.stat().st_mode & 0o111 != 0,
            }
        )

    for f in sorted(scripts_dir.glob("*.py")):
        scripts.append(
            {
                "id": f"script:{f.stem}",
                "name": f.name,
                "path": str(f.relative_to(scripts_dir.parent)),
                "executable": f.stat().st_mode & 0o111 != 0,
            }
        )

    return scripts


def generate_knowledge_graph_seed(
    spec_bundles: List[Dict],
    apps: List[Dict],
    modules: List[Dict],
    workflows: List[Dict],
    scripts: List[Dict],
) -> Dict[str, Any]:
    """Generate knowledge graph seed data"""
    nodes = []
    edges = []

    # Add repo node
    nodes.append(
        {
            "id": "repo:jgtolentino/odoo-ce",
            "kind": "Repo",
            "name": "odoo-ce",
            "ref": {"github_url": "https://github.com/jgtolentino/odoo-ce"},
            "props": {"language": "Python", "framework": "Odoo 18 CE"},
        }
    )

    # Add spec bundle nodes and edges
    for bundle in spec_bundles:
        nodes.append(
            {
                "id": bundle["id"],
                "kind": "SpecBundle",
                "name": bundle["name"],
                "ref": {"path": bundle["path"]},
                "props": {"files": [f["name"] for f in bundle["files"]]},
            }
        )
        edges.append(
            {
                "src": "repo:jgtolentino/odoo-ce",
                "rel": "HAS_SPEC",
                "dst": bundle["id"],
                "props": {},
            }
        )

    # Add app nodes and edges
    for app in apps:
        nodes.append(
            {
                "id": app["id"],
                "kind": "App",
                "name": app["name"],
                "ref": {"path": app["path"]},
                "props": {
                    "version": app["version"],
                    "description": app["description"],
                },
            }
        )
        edges.append(
            {
                "src": "repo:jgtolentino/odoo-ce",
                "rel": "CONTAINS",
                "dst": app["id"],
                "props": {},
            }
        )

    # Add module nodes and edges
    for module in modules:
        nodes.append(
            {
                "id": module["id"],
                "kind": "Module",
                "name": module["name"],
                "ref": {"path": module["path"]},
                "props": {"namespace": module["namespace"]},
            }
        )
        edges.append(
            {
                "src": "repo:jgtolentino/odoo-ce",
                "rel": "CONTAINS",
                "dst": module["id"],
                "props": {},
            }
        )

    # Add workflow nodes and edges
    for workflow in workflows:
        nodes.append(
            {
                "id": workflow["id"],
                "kind": "Workflow",
                "name": workflow["name"],
                "ref": {"path": workflow["path"]},
                "props": {},
            }
        )
        edges.append(
            {
                "src": "repo:jgtolentino/odoo-ce",
                "rel": "HAS_WORKFLOW",
                "dst": workflow["id"],
                "props": {},
            }
        )

    # Add script nodes and edges
    for script in scripts:
        nodes.append(
            {
                "id": script["id"],
                "kind": "Script",
                "name": script["name"],
                "ref": {"path": script["path"]},
                "props": {"executable": script["executable"]},
            }
        )
        edges.append(
            {
                "src": "repo:jgtolentino/odoo-ce",
                "rel": "HAS_SCRIPT",
                "dst": script["id"],
                "props": {},
            }
        )

    return {
        "version": "1.0.0",
        "generated_at": datetime.now().isoformat(),
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "spec_bundles": len(spec_bundles),
            "apps": len(apps),
            "modules": len(modules),
            "workflows": len(workflows),
            "scripts": len(scripts),
        },
    }


def generate_markdown_index(
    spec_bundles: List[Dict],
    apps: List[Dict],
    modules: List[Dict],
    workflows: List[Dict],
    scripts: List[Dict],
) -> str:
    """Generate markdown index document"""
    lines = [
        "# Repository Index",
        "",
        f"Generated: {datetime.now().isoformat()}",
        "",
        "## Overview",
        "",
        f"- **Spec Bundles**: {len(spec_bundles)}",
        f"- **Applications**: {len(apps)}",
        f"- **Odoo Modules**: {len(modules)}",
        f"- **CI/CD Workflows**: {len(workflows)}",
        f"- **Scripts**: {len(scripts)}",
        "",
        "---",
        "",
    ]

    # Spec Bundles section
    if spec_bundles:
        lines.extend(
            [
                "## Spec Bundles",
                "",
                "Feature specifications following Spec Kit structure.",
                "",
                "| Name | Path | Status |",
                "| ---- | ---- | ------ |",
            ]
        )
        for bundle in spec_bundles:
            all_exist = all(f["exists"] for f in bundle["files"])
            status = "✓ Complete" if all_exist else "⚠ Incomplete"
            lines.append(f"| {bundle['name']} | `{bundle['path']}` | {status} |")
        lines.extend(["", "---", ""])

    # Applications section
    if apps:
        lines.extend(
            [
                "## Applications",
                "",
                "Node.js/TypeScript applications in the monorepo.",
                "",
                "| Name | Version | Description |",
                "| ---- | ------- | ----------- |",
            ]
        )
        for app in apps:
            desc = (
                app["description"][:50] + "..."
                if len(app["description"]) > 50
                else app["description"]
            )
            lines.append(f"| {app['name']} | {app['version']} | {desc} |")
        lines.extend(["", "---", ""])

    # Odoo Modules section
    if modules:
        lines.extend(
            [
                "## Odoo Modules",
                "",
                "Custom Odoo 18 CE modules (IPAI namespace).",
                "",
                "| Name | Namespace | Path |",
                "| ---- | --------- | ---- |",
            ]
        )
        for module in modules:
            lines.append(
                f"| {module['name']} | {module['namespace']} | `{module['path']}` |"
            )
        lines.extend(["", "---", ""])

    # Workflows section
    if workflows:
        lines.extend(
            [
                "## CI/CD Workflows",
                "",
                "GitHub Actions workflows for automation.",
                "",
                "| Name | Path |",
                "| ---- | ---- |",
            ]
        )
        for workflow in workflows:
            lines.append(f"| {workflow['name']} | `{workflow['path']}` |")
        lines.extend(["", "---", ""])

    # Scripts section
    if scripts:
        lines.extend(
            [
                "## Automation Scripts",
                "",
                "Shell and Python scripts for operations.",
                "",
                "| Name | Executable | Path |",
                "| ---- | ---------- | ---- |",
            ]
        )
        for script in scripts[:50]:  # Limit to first 50
            exec_status = "✓" if script["executable"] else "✗"
            lines.append(f"| {script['name']} | {exec_status} | `{script['path']}` |")
        if len(scripts) > 50:
            lines.append(f"| ... | ... | *({len(scripts) - 50} more)* |")
        lines.extend(["", "---", ""])

    lines.extend(
        [
            "## Cross-References",
            "",
            "See `docs/knowledge/graph_seed.json` for complete knowledge graph with relationships.",
            "",
        ]
    )

    return "\n".join(lines)


def main():
    """Main indexing routine"""
    repo_root = Path(__file__).parent.parent

    print("Scanning repository...")

    # Scan all components
    spec_bundles = scan_spec_bundles(repo_root / "spec")
    apps = scan_apps(repo_root / "apps")
    modules = scan_odoo_modules(repo_root / "addons")
    workflows = scan_workflows(repo_root / ".github" / "workflows")
    scripts = scan_scripts(repo_root / "scripts")

    print(f"  Found {len(spec_bundles)} spec bundles")
    print(f"  Found {len(apps)} applications")
    print(f"  Found {len(modules)} Odoo modules")
    print(f"  Found {len(workflows)} CI/CD workflows")
    print(f"  Found {len(scripts)} scripts")

    # Generate knowledge graph seed
    kg_seed = generate_knowledge_graph_seed(
        spec_bundles, apps, modules, workflows, scripts
    )

    # Generate markdown index
    index_md = generate_markdown_index(spec_bundles, apps, modules, workflows, scripts)

    # Write outputs
    docs_dir = repo_root / "docs"
    kg_dir = docs_dir / "knowledge"
    kg_dir.mkdir(parents=True, exist_ok=True)

    index_path = docs_dir / "INDEX.md"
    kg_path = kg_dir / "graph_seed.json"

    index_path.write_text(index_md, encoding="utf-8")
    kg_path.write_text(
        json.dumps(kg_seed, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print()
    print(f"✓ Generated {index_path}")
    print(f"✓ Generated {kg_path}")
    print()
    print("Summary:")
    print(f"  - Total nodes: {kg_seed['stats']['total_nodes']}")
    print(f"  - Total edges: {kg_seed['stats']['total_edges']}")


if __name__ == "__main__":
    main()
