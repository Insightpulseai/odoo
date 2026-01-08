#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deterministic Odoo module generator from capability_map.yaml.

Generates:
- Odoo module scaffolds under addons/ipai/ or addons/delta/
- Spec Kit bundles under spec/<slug>/
- Wiki pages under docs/wiki/
"""
import argparse
import hashlib
import os
import re
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader

# Naming conventions (SAP-aligned)
MODULE_RE = re.compile(r"^(ipai|ipai_delta)_[a-z0-9_]+$")
MODEL_RE = re.compile(r"^ipai\.[a-z0-9_]+\.[a-z0-9_]+$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_spec(path: Path) -> dict:
    return yaml.safe_load(path.read_text("utf-8"))


def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def write_if_changed(path: Path, content: str):
    if path.exists() and path.read_text("utf-8") == content:
        return False
    path.write_text(content, "utf-8")
    return True


def render(env: Environment, template: str, **ctx) -> str:
    return env.get_template(template).render(**ctx)


def main():
    ap = argparse.ArgumentParser(description="Generate Odoo modules from capability map")
    ap.add_argument("--spec", default="spec/ipai-odoo18-enterprise-patch/capability_map.yaml",
                    help="Path to capability_map.yaml")
    ap.add_argument("--check", action="store_true",
                    help="Check mode: fail if generator would change files")
    args = ap.parse_args()

    spec_path = Path(args.spec).resolve()
    if not spec_path.exists():
        print(f"Capability map not found: {spec_path}", file=sys.stderr)
        print("Creating empty capability map template...", file=sys.stderr)
        ensure_dir(spec_path.parent)
        spec_path.write_text(DEFAULT_CAPABILITY_MAP, "utf-8")
        print(f"Created: {spec_path}", file=sys.stderr)
        return

    spec = load_spec(spec_path)

    templates_dir = Path(__file__).parent / "templates"
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True
    )

    addons_root = Path(spec.get("addons_root", "addons")).resolve()
    spec_root = Path(spec.get("spec_root", "spec")).resolve()
    wiki_root = Path(spec.get("wiki_root", "docs/wiki")).resolve()
    odoo_series = spec.get("odoo_series", "18.0")
    ns = spec.get("namespace", "ipai")

    planned_changes = []

    for cap in spec.get("capabilities", []):
        sap_id = cap.get("sap_id", "UNKNOWN")
        sap_doc = cap.get("sap_doc", "")
        slug = cap.get("slug")
        title = cap.get("title", sap_id)
        odoo = cap.get("odoo", {})
        layer = odoo.get("layer", "ipai")
        module = odoo.get("module", "")

        # Validate slug
        if not slug or not SLUG_RE.match(slug):
            print(f"Warning: Invalid/missing slug for {sap_id}: '{slug}'", file=sys.stderr)
            continue

        # Validate module name
        if module and not MODULE_RE.match(module):
            print(f"Warning: Invalid module name: {module}", file=sys.stderr)
            continue

        # Validate models
        models = odoo.get("models", [])
        for m in models:
            if not MODEL_RE.match(m.get("name", "")):
                print(f"Warning: Invalid model name: {m.get('name')}", file=sys.stderr)

        # --- Generate Odoo module scaffold ---
        if module:
            base_dir = addons_root / ("delta" if layer == "delta" else "ipai") / module
            ensure_dir(base_dir / "models")
            ensure_dir(base_dir / "views")
            ensure_dir(base_dir / "security")
            ensure_dir(base_dir / "data")

            ctx = dict(
                module=module,
                summary=odoo.get("summary", title),
                odoo_series=odoo_series,
                sap_id=sap_id,
                sap_doc=sap_doc,
                depends=odoo.get("depends", ["base"]),
                models=models,
                menus=odoo.get("menus", []),
                views=odoo.get("views", []),
                namespace=ns,
            )

            files = {
                "__init__.py": "from . import models\n",
                "__manifest__.py": render(env, "manifest.py.j2", **ctx),
                "README.md": render(env, "readme.md.j2", **ctx),
                "models/__init__.py": "\n".join([
                    f"from . import {m['name'].split('.')[-1]}"
                    for m in models
                ]) + ("\n" if models else ""),
                "security/security.xml": render(env, "security.xml.j2", **ctx),
                "security/ir.model.access.csv": render(env, "access.csv.j2", **ctx),
                "views/views.xml": render(env, "views.xml.j2", **ctx),
            }

            # Model stubs
            for m in models:
                py_name = m["name"].split(".")[-1]
                files[f"models/{py_name}.py"] = render(env, "model.py.j2", **ctx, model=m, py_name=py_name)

            # Check or write files
            for rel, content in files.items():
                out = base_dir / rel
                if args.check:
                    if not out.exists() or out.read_text("utf-8") != content:
                        planned_changes.append(str(out))
                else:
                    ensure_dir(out.parent)
                    if write_if_changed(out, content):
                        print(f"  Updated: {out}")

        # --- Generate Spec Kit bundle ---
        spec_dir = spec_root / slug
        ensure_dir(spec_dir)

        spec_ctx = dict(
            cap=dict(sap_id=sap_id, sap_doc=sap_doc, slug=slug, title=title),
            odoo=odoo,
            odoo_series=odoo_series
        )

        spec_files = {
            "constitution.md": render(env, "spec/constitution.md.j2", **spec_ctx),
            "prd.md": render(env, "spec/prd.md.j2", **spec_ctx),
            "plan.md": render(env, "spec/plan.md.j2", **spec_ctx),
            "tasks.md": render(env, "spec/tasks.md.j2", **spec_ctx),
        }

        for rel, content in spec_files.items():
            out = spec_dir / rel
            if args.check:
                if not out.exists() or out.read_text("utf-8") != content:
                    planned_changes.append(str(out))
            else:
                if write_if_changed(out, content):
                    print(f"  Updated: {out}")

    # --- Generate Wiki pages ---
    ensure_dir(wiki_root)

    # Home page
    home = render(env, "wiki/Home.md.j2", capabilities=[
        dict(sap_id=c.get("sap_id"), slug=c.get("slug"), title=c.get("title", c.get("sap_id")))
        for c in spec.get("capabilities", [])
    ])

    home_path = wiki_root / "Home.md"
    if args.check:
        if not home_path.exists() or home_path.read_text("utf-8") != home:
            planned_changes.append(str(home_path))
    else:
        if write_if_changed(home_path, home):
            print(f"  Updated: {home_path}")

    # Per-capability pages
    for c in spec.get("capabilities", []):
        page = render(env, "wiki/capability.md.j2", cap=c)
        out = wiki_root / f"cap-{c.get('slug', 'unknown')}.md"
        if args.check:
            if not out.exists() or out.read_text("utf-8") != page:
                planned_changes.append(str(out))
        else:
            if write_if_changed(out, page):
                print(f"  Updated: {out}")

    # Diagrams index page
    diagrams_dir = Path("docs/diagrams").resolve()
    images = []
    if diagrams_dir.exists():
        for p in sorted(diagrams_dir.glob("*.png")):
            images.append({
                "title": p.stem.replace("_", " ").title(),
                "url": f"https://raw.githubusercontent.com/{os.environ.get('GITHUB_REPOSITORY', 'jgtolentino/odoo-ce')}/main/docs/diagrams/{p.name}"
            })

    diagrams_md = render(env, "wiki/Diagrams.md.j2", images=images)
    diagrams_path = wiki_root / "Diagrams.md"
    if args.check:
        if not diagrams_path.exists() or diagrams_path.read_text("utf-8") != diagrams_md:
            planned_changes.append(str(diagrams_path))
    else:
        if write_if_changed(diagrams_path, diagrams_md):
            print(f"  Updated: {diagrams_path}")

    # Check mode result
    if args.check and planned_changes:
        print("Generator drift detected. Run: ipai-gen", file=sys.stderr)
        for p in planned_changes[:50]:
            print(f"  - {p}", file=sys.stderr)
        if len(planned_changes) > 50:
            print(f"  ... and {len(planned_changes) - 50} more", file=sys.stderr)
        sys.exit(1)

    if not args.check:
        print(f"\nGeneration complete. Check {addons_root} and {spec_root}")


DEFAULT_CAPABILITY_MAP = """# IPAI Capability Map - SAP-aligned module definitions
# This file defines capabilities that map to Odoo modules, specs, and wiki pages.

namespace: ipai
odoo_series: "18.0"
addons_root: "addons"
spec_root: "spec"
wiki_root: "docs/wiki"

capabilities:
  - sap_id: "FI-CLOSE-AFC"
    slug: "fi-close-afc"
    title: "Advanced Financial Closing"
    sap_doc: "https://help.sap.com/docs/"
    odoo:
      layer: "ipai"
      module: "ipai_finance_close_manager"
      summary: "Advanced Financial Closing - close calendar, tasks, lock, audit"
      depends: ["account", "mail", "project"]
      models:
        - name: "ipai.finance.close_cycle"
          description: "Close cycle (month-end) header"
        - name: "ipai.finance.close_task"
          description: "Close tasks linked to cycle"
      menus:
        - name: "Financial Closing"
          parent: "account.menu_finance"
          action: "action_close_cycle"
      views:
        - model: "ipai.finance.close_cycle"
          type: "form"
        - model: "ipai.finance.close_cycle"
          type: "tree"
"""


if __name__ == "__main__":
    main()
