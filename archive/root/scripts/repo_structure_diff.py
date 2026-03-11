#!/usr/bin/env python3
"""
repo_structure_diff.py — Compare directory structures of Insightpulseai/odoo
vs upstream odoo/odoo and produce categorized reports.

Outputs:
  reports/repo_structure_diff.json   — machine-readable diff
  docs/architecture/REPO_STRUCTURE_DIFF.md — human-readable summary

Idempotent: safe to re-run; overwrites previous outputs deterministically.
"""

import json
import os
import pathlib
import sys
from collections import defaultdict
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
REPORT_JSON = REPO_ROOT / "reports" / "repo_structure_diff.json"
REPORT_MD = REPO_ROOT / "docs" / "architecture" / "REPO_STRUCTURE_DIFF.md"

UPSTREAM_OWNER = "odoo"
UPSTREAM_REPO = "odoo"
UPSTREAM_BRANCH = "19.0"

OUR_OWNER = "Insightpulseai"
OUR_REPO = "odoo"

# Categorize top-level dirs into buckets
BUCKET_DEFINITIONS = {
    # L0: Odoo core runtime
    "runtime-core": {
        "description": "Odoo CE core framework and server",
        "paths": {
            "odoo", "odoo-bin", "setup.py", "setup.cfg", "setup",
            "requirements.txt", "debian",
        },
    },
    # L1: Addons (modules loaded into Odoo)
    "runtime-addons": {
        "description": "Odoo addons (CE, OCA, IPAI modules)",
        "paths": {"addons"},
    },
    # L2: IPAI glue modules (subset of addons, tracked separately)
    "ipai-modules": {
        "description": "InsightPulseAI thin glue modules (inside addons/ipai*)",
        "paths": set(),  # detected dynamically inside addons/
    },
    # L3: Non-module bridges / platform services
    "bridges-services": {
        "description": "Non-module integration bridges and platform services",
        "paths": {
            "ocr_service", "ocr-adapter", "automations", "n8n",
            "services", "integrations", "api", "apps", "web",
            "platform-kit", "platform", "ipai-platform",
        },
    },
    # Infrastructure / IaC
    "infra": {
        "description": "Infrastructure, deployment, Docker, CI",
        "paths": {
            "infra", "docker", "docker-compose.yml", "docker-compose.dev.yml",
            "Dockerfile", "Makefile", ".devcontainer", ".github", "ci",
            "vercel", "vercel.json",
        },
    },
    # Documentation
    "docs": {
        "description": "Documentation, specs, architecture docs",
        "paths": {
            "docs", "doc", "claudedocs", "handbook", "kb",
            "CLAUDE.md", "README.md", "CONTRIBUTING.md", "CHANGELOG.md",
            "SECURITY.md", "llms.txt", "llms-full.txt",
        },
    },
    # Tooling / Scripts
    "tooling": {
        "description": "Scripts, dev tooling, build configs",
        "paths": {
            "scripts", "tools", "bin", "dev", "sandbox", "scratch",
            "pyproject.toml", "package.json", "pnpm-lock.yaml",
            "pnpm-workspace.yaml", "turbo.json", "mkdocs.yml",
            "odoo.code-workspace", "figma.config.json",
            "devserver.config.json", "figma-make-dev.yaml",
        },
    },
    # Agent / AI systems
    "agent-ai": {
        "description": "AI agent systems, skills, MCP, spec-kit",
        "paths": {
            "agents", "agent-library", "agent-library-pack",
            "contains-studio-agents", "mcp", "skills", "skillpack",
            "spec", "specs", ".claude", "memory",
            "superclaude_bridge.yaml", "aiux_ship_manifest.yml",
        },
    },
    # Data / DB tooling
    "data-db": {
        "description": "Database tooling, seeds, schemas, migrations",
        "paths": {
            "db", "dbt", "data", "seeds", "seed_export", "schemas",
            "supabase", "odoo-schema-mirror", "odoo_local", "odoo19",
        },
    },
    # Misc / uncategorized
    "misc": {
        "description": "Miscellaneous project files",
        "paths": set(),  # catch-all
    },
}


def get_local_tree(root: pathlib.Path, max_depth: int = 2) -> list[str]:
    """Walk the local repo and collect paths up to max_depth."""
    paths = []
    root_str = str(root)
    for dirpath, dirnames, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root_str)
        depth = 0 if rel == "." else rel.count(os.sep) + 1
        if depth >= max_depth:
            dirnames.clear()
            continue
        # Skip hidden dirs at depth 0+ (except special ones)
        dirnames[:] = sorted(
            d for d in dirnames
            if not d.startswith(".")
            or d in {".claude", ".devcontainer", ".github", ".specify", ".supabase"}
        )
        for d in dirnames:
            p = os.path.join(rel, d) if rel != "." else d
            paths.append(p + "/")
        if depth == 0:
            for f in sorted(filenames):
                if not f.startswith(".") or f in {".gitignore", ".gitmodules"}:
                    paths.append(f)
    return sorted(set(paths))


def get_upstream_tree_via_git_api(
    owner: str, repo: str, branch: str, max_depth: int = 2
) -> list[str]:
    """Fetch entire repo tree via Git Trees API (single request, no rate-limit issues)."""
    import urllib.request
    import urllib.error

    # Use recursive tree API — returns all paths in one call
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github.v3+json"})
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", f"token {token}")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"  [ERROR] GitHub Trees API {e.code}: {e.reason}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"  [ERROR] GitHub Trees API: {e}", file=sys.stderr)
        return []

    if data.get("truncated"):
        print("  [WARN] Tree was truncated by GitHub (repo is very large)", file=sys.stderr)

    paths = []
    for item in data.get("tree", []):
        path = item["path"]
        mode = item["type"]  # "blob" or "tree"
        depth = path.count("/") + 1

        # Only include paths up to max_depth
        if depth > max_depth:
            continue

        if mode == "tree":
            paths.append(path + "/")
        elif mode == "blob":
            # Only include top-level files (depth == 1 means no "/" in path)
            if "/" not in path:
                paths.append(path)

    return sorted(set(paths))


def categorize_path(path: str) -> str:
    """Assign a top-level path to a bucket."""
    top = path.rstrip("/").split("/")[0]
    for bucket, defn in BUCKET_DEFINITIONS.items():
        if bucket == "misc":
            continue
        if top in defn["paths"]:
            return bucket
    return "misc"


def build_report(our_paths: list[str], upstream_paths: list[str]) -> dict:
    """Build the structured diff report."""
    our_top = {p.rstrip("/").split("/")[0] for p in our_paths}
    upstream_top = {p.rstrip("/").split("/")[0] for p in upstream_paths}

    only_ours = sorted(our_top - upstream_top)
    only_upstream = sorted(upstream_top - our_top)
    shared = sorted(our_top & upstream_top)

    # Categorize our paths
    our_buckets: dict[str, list[str]] = defaultdict(list)
    for p in our_paths:
        bucket = categorize_path(p)
        our_buckets[bucket].append(p)

    upstream_buckets: dict[str, list[str]] = defaultdict(list)
    for p in upstream_paths:
        bucket = categorize_path(p)
        upstream_buckets[bucket].append(p)

    # Addons sub-analysis (our repo)
    our_addons = [p for p in our_paths if p.startswith("addons/")]
    addons_oca = sorted(p for p in our_addons if "/oca/" in p or p.startswith("addons/oca"))
    addons_ipai = sorted(p for p in our_addons if "ipai" in p.lower())
    addons_other = sorted(set(our_addons) - set(addons_oca) - set(addons_ipai))

    report = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "upstream": {
            "owner": UPSTREAM_OWNER,
            "repo": UPSTREAM_REPO,
            "branch": UPSTREAM_BRANCH,
            "top_level_count": len(upstream_top),
            "total_paths": len(upstream_paths),
            "top_level_items": sorted(upstream_top),
        },
        "ours": {
            "owner": OUR_OWNER,
            "repo": OUR_REPO,
            "top_level_count": len(our_top),
            "total_paths": len(our_paths),
            "top_level_items": sorted(our_top),
        },
        "diff": {
            "shared": shared,
            "only_upstream": only_upstream,
            "only_ours": only_ours,
        },
        "buckets": {
            bucket: {
                "description": BUCKET_DEFINITIONS[bucket]["description"],
                "our_paths": sorted(our_buckets.get(bucket, [])),
                "upstream_paths": sorted(upstream_buckets.get(bucket, [])),
                "our_count": len(our_buckets.get(bucket, [])),
                "upstream_count": len(upstream_buckets.get(bucket, [])),
            }
            for bucket in BUCKET_DEFINITIONS
        },
        "addons_analysis": {
            "total": len(our_addons),
            "oca": addons_oca,
            "ipai": addons_ipai,
            "other": addons_other,
        },
    }
    return report


def generate_markdown(report: dict) -> str:
    """Generate the Markdown summary from the report."""
    ts = report["generated_at"]
    upstream = report["upstream"]
    ours = report["ours"]
    diff = report["diff"]

    lines = [
        "# Repo Structure Diff: `Insightpulseai/odoo` vs `odoo/odoo`",
        "",
        f"> Auto-generated by `scripts/repo_structure_diff.py` on {ts}",
        "> Re-run the script to update. Do not edit manually.",
        "",
        "---",
        "",
        "## Overview",
        "",
        f"| Metric | `odoo/odoo` ({upstream['branch']}) | `Insightpulseai/odoo` |",
        "|--------|------|------|",
        f"| Top-level items | {upstream['top_level_count']} | {ours['top_level_count']} |",
        f"| Total paths (depth 2) | {upstream['total_paths']} | {ours['total_paths']} |",
        "",
        "---",
        "",
        "## Top-Level Comparison",
        "",
        "### Shared (present in both repos)",
        "",
    ]
    for item in diff["shared"]:
        lines.append(f"- `{item}`")
    lines.append("")

    lines.append("### Only in upstream `odoo/odoo`")
    lines.append("")
    if diff["only_upstream"]:
        for item in diff["only_upstream"]:
            lines.append(f"- `{item}`")
    else:
        lines.append("_(none)_")
    lines.append("")

    lines.append("### Only in `Insightpulseai/odoo`")
    lines.append("")
    if diff["only_ours"]:
        for item in diff["only_ours"]:
            lines.append(f"- `{item}`")
    else:
        lines.append("_(none)_")
    lines.append("")

    lines.extend([
        "---",
        "",
        "## Bucket Classification",
        "",
        "Every top-level path is assigned to a bucket. This clarifies what is",
        "**Odoo runtime** vs **platform services** vs **tooling**.",
        "",
        "| Bucket | Description | Ours | Upstream |",
        "|--------|-------------|------|----------|",
    ])
    for bucket, data in report["buckets"].items():
        lines.append(
            f"| `{bucket}` | {data['description']} | {data['our_count']} | {data['upstream_count']} |"
        )
    lines.append("")

    # Detailed bucket contents
    lines.extend(["### Bucket Details", ""])
    for bucket, data in report["buckets"].items():
        if not data["our_paths"] and not data["upstream_paths"]:
            continue
        lines.append(f"#### `{bucket}` — {data['description']}")
        lines.append("")
        if data["our_paths"]:
            lines.append("**Insightpulseai/odoo:**")
            for p in data["our_paths"][:30]:  # cap for readability
                lines.append(f"- `{p}`")
            if len(data["our_paths"]) > 30:
                lines.append(f"- _...and {len(data['our_paths']) - 30} more_")
            lines.append("")
        if data["upstream_paths"]:
            lines.append("**odoo/odoo:**")
            for p in data["upstream_paths"][:30]:
                lines.append(f"- `{p}`")
            if len(data["upstream_paths"]) > 30:
                lines.append(f"- _...and {len(data['upstream_paths']) - 30} more_")
            lines.append("")

    # Addons analysis
    addons = report["addons_analysis"]
    lines.extend([
        "---",
        "",
        "## Addons Analysis (Insightpulseai/odoo)",
        "",
        f"Total addons paths (depth 2): **{addons['total']}**",
        "",
        f"- OCA modules: {len(addons['oca'])}",
        f"- IPAI modules: {len(addons['ipai'])}",
        f"- Other (CE / misc): {len(addons['other'])}",
        "",
    ])
    if addons["ipai"]:
        lines.append("### IPAI Modules")
        lines.append("")
        for p in sorted(addons["ipai"]):
            lines.append(f"- `{p}`")
        lines.append("")

    # Recommendation
    lines.extend([
        "---",
        "",
        "## Recommended Canonical Layout",
        "",
        "Based on the CE + OCA parity rule, the repo should enforce clear",
        "boundaries between runtime and non-runtime content:",
        "",
        "```",
        "Logical Layer Model",
        "====================",
        "",
        "L0  Odoo 19 CE (core server)",
        "    odoo/           framework + core",
        "    addons/          official community addons",
        "    odoo-bin          server entrypoint",
        "",
        "L1  OCA: EE-module replacements (still Odoo modules)",
        "    addons/oca/...   mounted on addons_path",
        "",
        "L2  IPAI minimal glue (ONLY true Odoo modules)",
        "    addons/ipai/...  thin localization/bridges-as-modules",
        "",
        "L3  Non-module bridges (NOT Odoo modules)",
        "    services/        OCR, n8n workers, pipelines",
        "    integrations/    connectors, control-plane hooks",
        "    api/             external API services",
        "```",
        "",
        "### Runtime vs Non-Runtime Boundary",
        "",
        "| Category | Belongs in addons_path | Examples |",
        "|----------|----------------------|----------|",
        "| **Runtime (L0-L2)** | Yes | `odoo/`, `addons/`, OCA modules, `ipai_*` modules |",
        "| **Bridges (L3)** | No | `ocr_service/`, `automations/`, `n8n/`, `api/` |",
        "| **Infra** | No | `infra/`, `docker/`, `.devcontainer/`, CI configs |",
        "| **Tooling** | No | `scripts/`, `tools/`, build configs |",
        "| **Agent/AI** | No | `agents/`, `mcp/`, `skills/`, `spec/` |",
        "| **Docs** | No | `docs/`, `handbook/`, `kb/` |",
        "",
        "### Key Principle",
        "",
        "> Only L0-L2 content should appear on `addons_path`.",
        "> Everything else is platform infrastructure and must not pollute the Odoo runtime.",
        "",
        "---",
        "",
        f"*Report generated: {ts}*",
        "",
    ])

    return "\n".join(lines)


def main():
    print("=== Repo Structure Diff ===")
    print()

    # 1. Collect our local tree
    print("[1/4] Scanning local repo (Insightpulseai/odoo)...")
    our_paths = get_local_tree(REPO_ROOT, max_depth=2)
    # Also scan addons at depth 2 (relative to addons/)
    addons_dir = REPO_ROOT / "addons"
    if addons_dir.is_dir():
        addons_sub = get_local_tree(addons_dir, max_depth=2)
        our_paths.extend(f"addons/{p}" for p in addons_sub if not any(
            existing.startswith(f"addons/{p.split('/')[0]}")
            for existing in our_paths
        ))
        our_paths = sorted(set(our_paths))

    print(f"  Found {len(our_paths)} paths")

    # 2. Fetch upstream tree via Git Trees API (single request)
    print(f"[2/4] Fetching upstream tree (odoo/odoo @ {UPSTREAM_BRANCH})...")
    upstream_paths = get_upstream_tree_via_git_api(
        UPSTREAM_OWNER, UPSTREAM_REPO, UPSTREAM_BRANCH, max_depth=2
    )
    print(f"  Found {len(upstream_paths)} paths")

    # 3. Build report
    print("[3/4] Building report...")
    report = build_report(our_paths, upstream_paths)

    # 4. Write outputs
    print("[4/4] Writing outputs...")

    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_JSON, "w") as f:
        json.dump(report, f, indent=2, sort_keys=False)
    print(f"  JSON: {REPORT_JSON.relative_to(REPO_ROOT)}")

    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    md = generate_markdown(report)
    with open(REPORT_MD, "w") as f:
        f.write(md)
    print(f"  Markdown: {REPORT_MD.relative_to(REPO_ROOT)}")

    print()
    print("Done. Outputs are deterministic and safe to re-run.")


if __name__ == "__main__":
    main()
