#!/usr/bin/env python3
"""
build_kb_graph.py — GraphRAG KB layer populator for Insightpulseai/odoo

Reads the local sc-index (.cache/tags + addons/ipai manifests) and upserts
nodes + edges into Supabase public.kb_nodes / public.kb_edges.

Node types emitted:  OdooModule | File | Model | Controller
Edge types emitted:  DEFINED_IN | DEPENDS_ON | INHERITS_FROM

Usage:
  python scripts/build_kb_graph.py [--dry-run] [--addons-path addons/ipai]
                                    [--manifest-out reports/graphrag_manifest.json]

Environment (inherits from .env or shell):
  POSTGRES_URL_NON_POOLING  — direct (non-pooled) Supabase connection
  POSTGRES_PASSWORD + POSTGRES_HOST etc. — fallback individual params

Contract: docs/architecture/GRAPHRAG_CONTRACT.md
"""

import argparse
import ast
import hashlib
import json
import os
import re
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).parent.parent.resolve()
CACHE_TAGS = REPO_ROOT / ".cache" / "tags"

CONTRACT_VERSION = "1.0.0"
INDEXER_VERSION  = "1.1.0"

ADDON_KIND_MAP = {
    "addons/ipai": "ipai",
    "addons/oca":  "oca",
    "addons/odoo": "core",
}

EDIT_POLICY_MAP = {
    "ipai":      "editable",
    "oca":       "overlay_only",
    "core":      "no_touch",
    "vendor":    "no_touch",
    "generated": "editable",
}


# ── DB helpers ────────────────────────────────────────────────────────────────

def get_conn():
    try:
        import psycopg2
    except ImportError:
        sys.exit("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary")

    url = os.environ.get("POSTGRES_URL_NON_POOLING") or os.environ.get("POSTGRES_URL")
    if url:
        return psycopg2.connect(url)

    host = os.environ.get("POSTGRES_HOST", "")
    pw   = os.environ.get("POSTGRES_PASSWORD", "")
    user = os.environ.get("POSTGRES_USER", "postgres")
    db   = os.environ.get("POSTGRES_DATABASE", "postgres")
    if host and pw:
        return psycopg2.connect(host=host, port=5432, dbname=db, user=user,
                                password=pw, sslmode="require")

    sys.exit("ERROR: No DB credentials found. Set POSTGRES_URL_NON_POOLING or POSTGRES_HOST+PASSWORD.")


def upsert_node(cur, type_, name, path=None, module=None,
                addon_kind=None, edit_policy="editable", git_sha=None,
                attrs=None, dry_run=False):
    """Upsert a kb_node, return its UUID."""
    attrs_json = json.dumps(attrs or {})
    if dry_run:
        print(f"  [DRY] NODE {type_}:{name} ({addon_kind}/{edit_policy})")
        return None
    cur.execute("""
        INSERT INTO public.kb_nodes
            (type, name, path, module, addon_kind, edit_policy, git_sha, attrs)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb)
        ON CONFLICT ON CONSTRAINT kb_nodes_type_path_name_uniq
        DO UPDATE SET
            module      = EXCLUDED.module,
            addon_kind  = EXCLUDED.addon_kind,
            edit_policy = EXCLUDED.edit_policy,
            git_sha     = EXCLUDED.git_sha,
            attrs       = EXCLUDED.attrs,
            updated_at  = now()
        RETURNING id
    """, (type_, name, path, module, addon_kind, edit_policy, git_sha, attrs_json))
    row = cur.fetchone()
    return row[0] if row else None


def upsert_edge(cur, src_id, dst_id, edge_type, git_sha=None, dry_run=False):
    """Upsert a kb_edge."""
    if dry_run or src_id is None or dst_id is None:
        if dry_run:
            print(f"  [DRY] EDGE {edge_type}: {src_id} → {dst_id}")
        return
    cur.execute("""
        INSERT INTO public.kb_edges (src_id, dst_id, type, git_sha)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT ON CONSTRAINT kb_edges_src_dst_type_uniq DO NOTHING
    """, (str(src_id), str(dst_id), edge_type, git_sha))


# ── Git helpers ────────────────────────────────────────────────────────────────

def get_git_sha() -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, cwd=REPO_ROOT
        )
        return result.stdout.strip() or None
    except Exception:
        return None


# ── Checksum helpers ───────────────────────────────────────────────────────────

def compute_input_checksum(addons_path: Path) -> str:
    """SHA-256 of the sorted list of .py file paths (repo-relative).

    This checksum changes whenever Python files are added/removed/renamed.
    It does NOT change for in-file edits (intentional: the graph is path-based).
    Stable across OS because paths are sorted and normalized to forward-slashes.
    """
    paths = sorted(
        str(p.relative_to(REPO_ROOT)).replace("\\", "/")
        for p in addons_path.rglob("*.py")
    )
    digest = hashlib.sha256("\n".join(paths).encode()).hexdigest()
    return digest


# ── Manifest helpers ───────────────────────────────────────────────────────────

def write_manifest(
    manifest_out: Path,
    git_sha: Optional[str],
    addons_path: Path,
    input_checksum: str,
    nodes_written: int,
    edges_written: int,
    dry_run: bool,
) -> None:
    """Write a JSON manifest describing this indexer run."""
    manifest = {
        "contract_version": CONTRACT_VERSION,
        "indexer_version": INDEXER_VERSION,
        "git_sha": git_sha or "(unknown)",
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "addons_path": str(addons_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "input_checksum": input_checksum,
        "dry_run": dry_run,
        "stats": {
            "nodes_written": nodes_written,
            "edges_written": edges_written,
        },
    }
    manifest_out.parent.mkdir(parents=True, exist_ok=True)
    manifest_out.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"\nManifest written → {manifest_out.relative_to(REPO_ROOT)}")


# ── Module discovery ───────────────────────────────────────────────────────────

def addon_kind_for_path(path: Path) -> str:
    rel = path.relative_to(REPO_ROOT)
    for prefix, kind in ADDON_KIND_MAP.items():
        if str(rel).startswith(prefix):
            return kind
    return "vendor"


def discover_modules(addons_path: Path):
    """Yield (module_dir, manifest_dict) for every OCA-style __manifest__.py.

    Stable ordering: sorted by manifest path string so output is deterministic
    across OS and filesystem enumeration order.
    """
    for manifest in sorted(addons_path.rglob("__manifest__.py"), key=str):
        module_dir = manifest.parent
        try:
            src = manifest.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(src, filename=str(manifest))
            # __manifest__.py is a module-level expression (a dict literal)
            for node in ast.walk(tree):
                if isinstance(node, ast.Expr) and isinstance(node.value, ast.Dict):
                    data = ast.literal_eval(node.value)
                    if isinstance(data, dict):
                        yield module_dir, data
                        break
        except Exception:
            yield module_dir, {}


# ── Python file scanning ───────────────────────────────────────────────────────

MODEL_RE    = re.compile(r'class\s+(\w+)\s*\(.*models\.(?:Model|TransientModel|AbstractModel|BaseModel)')
INHERIT_RE  = re.compile(r"_inherit\s*=\s*['\"]([^'\"]+)['\"]")
INHERITS_RE = re.compile(r"_inherits\s*=\s*\{['\"]([^'\"]+)['\"]")


def scan_python_file(fpath: Path):
    """Return list of (class_name, inherited_model_name_or_None) from a .py file."""
    results = []
    try:
        src = fpath.read_text(encoding="utf-8", errors="replace")
        for match in MODEL_RE.finditer(src):
            class_name = match.group(1)
            # Look for _inherit near this class (within next 20 lines)
            pos = match.start()
            snippet = src[pos:pos + 1000]
            inherit = INHERIT_RE.search(snippet)
            inherits = INHERITS_RE.search(snippet)
            inherited = (inherit or inherits)
            results.append((class_name, inherited.group(1) if inherited else None))
    except Exception:
        pass
    return results


# ── Main ──────────────────────────────────────────────────────────────────────

def build(addons_path: Path, dry_run: bool, manifest_out: Path):
    git_sha = get_git_sha()
    input_checksum = compute_input_checksum(addons_path)

    print(f"Git SHA:          {git_sha or '(unknown)'}")
    print(f"Contract version: {CONTRACT_VERSION}")
    print(f"Indexer version:  {INDEXER_VERSION}")
    print(f"Addons path:      {addons_path}")
    print(f"Input checksum:   {input_checksum}")
    print(f"Dry run:          {dry_run}")
    print()

    if not dry_run:
        conn = get_conn()
        cur  = conn.cursor()
    else:
        conn = cur = None

    nodes_written = 0
    edges_written = 0

    # ── Pass 1: OdooModule nodes from __manifest__.py ─────────────────────────
    print("=== Pass 1: OdooModule nodes ===")
    module_node_ids: dict[str, object] = {}  # module_name → node uuid

    for module_dir, manifest in discover_modules(addons_path):
        module_name = module_dir.name
        kind        = addon_kind_for_path(module_dir)
        policy      = EDIT_POLICY_MAP.get(kind, "editable")
        rel_path    = str(module_dir.relative_to(REPO_ROOT)).replace("\\", "/")

        attrs = {
            "version":    manifest.get("version", ""),
            "author":     manifest.get("author", ""),
            "category":   manifest.get("category", ""),
            "depends":    manifest.get("depends", []),
        }

        node_id = upsert_node(
            cur, "OdooModule", module_name,
            path=rel_path, module=module_name,
            addon_kind=kind, edit_policy=policy,
            git_sha=git_sha, attrs=attrs,
            dry_run=dry_run
        )
        module_node_ids[module_name] = node_id
        nodes_written += 1
        print(f"  MODULE {module_name} [{kind}/{policy}]")

    # ── Pass 2: File nodes + Model nodes from Python files ────────────────────
    print(f"\n=== Pass 2: File + Model nodes ({addons_path}) ===")
    file_node_ids: dict[str, object] = {}   # rel_path → node uuid
    model_node_ids: dict[str, object] = {}  # class_name → node uuid

    # Stable sort: key=str normalises to forward-slash on POSIX, consistent ordering
    for py_file in sorted(addons_path.rglob("*.py"), key=str):
        rel = str(py_file.relative_to(REPO_ROOT)).replace("\\", "/")
        kind   = addon_kind_for_path(py_file)
        policy = EDIT_POLICY_MAP.get(kind, "editable")

        # Infer module from path  (addons/ipai/<module_name>/...)
        parts = py_file.relative_to(addons_path).parts
        module_name = parts[0] if parts else ""

        file_id = upsert_node(
            cur, "File", py_file.name,
            path=rel, module=module_name,
            addon_kind=kind, edit_policy=policy,
            git_sha=git_sha,
            dry_run=dry_run
        )
        file_node_ids[rel] = file_id
        nodes_written += 1

        # Link File → OdooModule via DEFINED_IN
        module_id = module_node_ids.get(module_name)
        upsert_edge(cur, module_id, file_id, "DEFINED_IN", git_sha=git_sha, dry_run=dry_run)
        if module_id and file_id:
            edges_written += 1

        # Model nodes inside this file
        for class_name, inherited_model in scan_python_file(py_file):
            model_id = upsert_node(
                cur, "Model", class_name,
                path=rel, module=module_name,
                addon_kind=kind, edit_policy=policy,
                git_sha=git_sha,
                dry_run=dry_run
            )
            model_node_ids[class_name] = model_id
            nodes_written += 1

            # Model DEFINED_IN File
            upsert_edge(cur, model_id, file_id, "DEFINED_IN", git_sha=git_sha, dry_run=dry_run)
            if model_id and file_id:
                edges_written += 1

    # ── Pass 3: DEPENDS_ON edges between modules ──────────────────────────────
    print("\n=== Pass 3: DEPENDS_ON edges between modules ===")
    for module_dir, manifest in discover_modules(addons_path):
        module_name = module_dir.name
        src_id      = module_node_ids.get(module_name)
        for dep in manifest.get("depends", []):
            dst_id = module_node_ids.get(dep)
            if dst_id:
                upsert_edge(cur, src_id, dst_id, "DEPENDS_ON", git_sha=git_sha, dry_run=dry_run)
                edges_written += 1

    # ── Pass 4: INHERITS_FROM edges between models ────────────────────────────
    print("\n=== Pass 4: INHERITS_FROM edges between models ===")
    for py_file in sorted(addons_path.rglob("*.py"), key=str):
        for class_name, inherited_model in scan_python_file(py_file):
            if inherited_model:
                src_id = model_node_ids.get(class_name)
                dst_id = model_node_ids.get(inherited_model)
                if src_id and dst_id:
                    upsert_edge(cur, src_id, dst_id, "INHERITS_FROM", git_sha=git_sha, dry_run=dry_run)
                    edges_written += 1

    # ── Commit ────────────────────────────────────────────────────────────────
    if not dry_run and conn:
        conn.commit()
        cur.close()
        conn.close()

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Done.")
    print(f"  Nodes: {nodes_written}")
    print(f"  Edges: {edges_written}")

    # ── Manifest ──────────────────────────────────────────────────────────────
    write_manifest(
        manifest_out=manifest_out,
        git_sha=git_sha,
        addons_path=addons_path,
        input_checksum=input_checksum,
        nodes_written=nodes_written,
        edges_written=edges_written,
        dry_run=dry_run,
    )


def main():
    parser = argparse.ArgumentParser(description="Build GraphRAG KB graph from Odoo addons")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be written, do not modify DB")
    parser.add_argument("--addons-path", default="addons/ipai",
                        help="Path to addons directory (default: addons/ipai)")
    parser.add_argument("--manifest-out", default="reports/graphrag_manifest.json",
                        help="Path to write manifest JSON (default: reports/graphrag_manifest.json)")
    args = parser.parse_args()

    addons_path  = REPO_ROOT / args.addons_path
    manifest_out = REPO_ROOT / args.manifest_out

    if not addons_path.exists():
        sys.exit(f"ERROR: addons path not found: {addons_path}")

    build(addons_path, dry_run=args.dry_run, manifest_out=manifest_out)


if __name__ == "__main__":
    main()
