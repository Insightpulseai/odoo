#!/usr/bin/env python3
"""
sweep_repo.py — Repo-wide n8n automation surface discovery and backlog generator.

Usage:
    python scripts/automations/sweep_repo.py [--env {dev,stage,prod}] \
        [--out out/automation_sweep] [--apply] [--verbose]

Exit codes:
    0  = clean (no issues found)
    1  = issues found (stale refs, stray workflows, opportunities)
    2  = apply-phase failures
"""
import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CANONICAL_WORKFLOW_DIR = REPO_ROOT / "automations" / "n8n"
STRAY_WORKFLOW_DIR = REPO_ROOT / "n8n" / "workflows"

SCAN_EXTENSIONS = {".json", ".sh", ".py", ".yml", ".yaml", ".md"}
EXCLUDE_DIRS = {
    ".git", "node_modules", "__pycache__", ".cache", ".gemini",
    "dist", ".next", "build", "vendor",
}

N8N_SHAPE_KEYS = {"name", "nodes", "connections"}

DEPRECATED_DOMAINS = [
    "insightpulseai.net",
    "ipa.insightpulseai.net",
    "n8n.insightpulseai.net",
    "erp.insightpulseai.net",
    "chat.insightpulseai.net",
]

OLD_PATH_PATTERNS = [
    r"/n8n/workflows/",          # old n8n root (moved to automations/n8n)
    r"jgtolentino/odoo-ce",      # old repo name
    r"odoo-ce",                  # old repo name
    r"/opt/ipai/odoo-ce",        # old droplet path
    r"Insightpulseai/odoo-ce",   # old repo ref
]

OPPORTUNITY_PATTERNS = [
    # multi-step fetch→transform→notify
    (r"curl.*\|.*jq", "fetch→transform pipeline: n8n candidate"),
    (r"psql.*&&.*curl", "DB query + HTTP call: event-driven n8n candidate"),
    (r"sleep\s+[0-9]", "polling sleep: scheduled n8n workflow candidate"),
    (r"cron\b|schedule", "cron/schedule reference: n8n scheduler candidate"),
    (r"smtp|sendmail|mail\b", "email notification: n8n email node candidate"),
    (r"slack.*webhook|webhook.*slack", "Slack webhook: n8n Slack node candidate"),
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def is_n8n_workflow(data: Any) -> bool:
    if not isinstance(data, dict):
        return False
    return N8N_SHAPE_KEYS.issubset(data.keys())


def log(msg: str, verbose: bool = False, force: bool = False) -> None:
    if verbose or force:
        print(msg, file=sys.stderr)


def walk_repo(root: Path, verbose: bool) -> list[Path]:
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fname in filenames:
            p = Path(dirpath) / fname
            if p.suffix in SCAN_EXTENSIONS:
                files.append(p)
    log(f"  Scanned {len(files)} files", verbose)
    return files


# ---------------------------------------------------------------------------
# Phase 1: Inventory
# ---------------------------------------------------------------------------


def discover_workflows(files: list[Path], verbose: bool) -> dict:
    """Find all n8n workflow JSONs and classify them."""
    canonical: list[dict] = []
    stray: list[dict] = []
    hashes: dict[str, list[str]] = {}  # hash → list of paths

    json_files = [f for f in files if f.suffix == ".json"]
    log(f"  Checking {len(json_files)} JSON files for n8n shape...", verbose)

    for fpath in json_files:
        try:
            data = json.loads(fpath.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue
        if not is_n8n_workflow(data):
            continue

        h = sha256(fpath)
        rel = str(fpath.relative_to(REPO_ROOT))
        entry = {
            "path": rel,
            "name": data.get("name", "<unnamed>"),
            "id": data.get("id", None),
            "hash": h,
            "node_count": len(data.get("nodes", [])),
        }

        hashes.setdefault(h, []).append(rel)

        if CANONICAL_WORKFLOW_DIR in fpath.parents:
            entry["classification"] = "canonical"
            canonical.append(entry)
        else:
            entry["classification"] = "stray"
            stray.append(entry)

    # Mark duplicates (same hash across multiple paths)
    for wf in canonical + stray:
        if len(hashes.get(wf["hash"], [])) > 1:
            wf["classification"] = "duplicate"

    return {
        "canonical": canonical,
        "stray": stray,
        "hash_map": {h: paths for h, paths in hashes.items() if len(paths) > 1},
    }


def discover_references(files: list[Path], verbose: bool) -> list[dict]:
    """Find all files that reference n8n paths/APIs."""
    refs = []
    n8n_patterns = [
        r"n8n\.insightpulseai",
        r"/api/v1/workflows",
        r"N8N_API_KEY",
        r"N8N_BASE_URL",
        r"n8n-gitops",
        r"automations/n8n",
        r"deploy.n8n",
        r"import.n8n",
    ]
    combined = re.compile("|".join(n8n_patterns), re.IGNORECASE)

    for fpath in files:
        if fpath.suffix == ".json":
            continue  # skip JSON — covered by workflow scan
        try:
            text = fpath.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        if combined.search(text):
            refs.append({
                "path": str(fpath.relative_to(REPO_ROOT)),
                "ext": fpath.suffix,
            })

    log(f"  Found {len(refs)} files referencing n8n", verbose)
    return refs


def detect_stale_refs(files: list[Path], verbose: bool) -> list[dict]:
    """Detect deprecated domain and old path references."""
    stale = []
    depr_pattern = re.compile(
        "|".join(re.escape(d) for d in DEPRECATED_DOMAINS), re.IGNORECASE
    )
    old_pattern = re.compile("|".join(OLD_PATH_PATTERNS), re.IGNORECASE)

    for fpath in files:
        try:
            text = fpath.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        issues = []
        if depr_pattern.search(text):
            issues.append("deprecated_domain")
        if old_pattern.search(text):
            issues.append("old_path")
        if issues:
            stale.append({
                "path": str(fpath.relative_to(REPO_ROOT)),
                "issues": issues,
            })

    log(f"  Found {len(stale)} files with stale refs", verbose)
    return stale


# ---------------------------------------------------------------------------
# Phase 3: Staleness & Opportunities
# ---------------------------------------------------------------------------


def detect_opportunities(files: list[Path], verbose: bool) -> list[dict]:
    """Heuristic opportunity detection for n8n automation candidates."""
    opportunities = []

    script_files = [f for f in files if f.suffix in {".sh", ".py"}]
    combined = [(re.compile(pat, re.IGNORECASE), desc) for pat, desc in OPPORTUNITY_PATTERNS]

    for fpath in script_files:
        try:
            text = fpath.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        matches = []
        for pattern, desc in combined:
            if pattern.search(text):
                matches.append(desc)
        if matches:
            opportunities.append({
                "path": str(fpath.relative_to(REPO_ROOT)),
                "type": "script_candidate",
                "signals": matches,
                "roi": _score_roi(matches),
                "risk": "Low",
                "effort_days": 1,
                "priority": _priority(matches),
                "recommendation": f"Convert to n8n workflow: {matches[0]}",
            })

    log(f"  Found {len(opportunities)} automation opportunities", verbose)
    return opportunities


def _score_roi(signals: list[str]) -> str:
    high_signals = {"email", "slack", "webhook", "cron", "schedule"}
    if any(any(hs in s.lower() for hs in high_signals) for s in signals):
        return "High"
    return "Medium"


def _priority(signals: list[str]) -> str:
    if len(signals) >= 3:
        return "P0"
    if len(signals) >= 2:
        return "P1"
    return "P2"


# ---------------------------------------------------------------------------
# Artifact generation
# ---------------------------------------------------------------------------


def build_inventory(workflows: dict, refs: list, stale: list, opps: list) -> dict:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(REPO_ROOT),
        "workflows": {
            "canonical": workflows["canonical"],
            "stray": workflows["stray"],
            "duplicates": workflows["hash_map"],
            "total_canonical": len(workflows["canonical"]),
            "total_stray": len(workflows["stray"]),
            "total_duplicates": len(workflows["hash_map"]),
        },
        "references": refs,
        "stale_references": stale,
        "opportunities": opps,
        "summary": {
            "total_workflows": len(workflows["canonical"]) + len(workflows["stray"]),
            "stale_files": len(stale),
            "opportunities": len(opps),
            "issues_found": len(stale) + len(workflows["stray"]) > 0,
        },
    }


def write_report(inventory: dict, out_dir: Path) -> None:
    wf = inventory["workflows"]
    stale = inventory["stale_references"]
    opps = inventory["opportunities"]

    lines = [
        "# Automation Sweep Report",
        f"\n**Generated**: {inventory['generated_at']}",
        f"**Repo**: {inventory['repo_root']}",
        "\n---\n",
        "## Summary\n",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Canonical workflows | {wf['total_canonical']} |",
        f"| Stray workflows | {wf['total_stray']} |",
        f"| Duplicate workflow hashes | {wf['total_duplicates']} |",
        f"| Files with stale references | {len(stale)} |",
        f"| Automation opportunities | {len(opps)} |",
        "\n---\n",
        "## Canonical Workflows\n",
    ]

    for wf_entry in wf["canonical"]:
        lines.append(f"- `{wf_entry['path']}` — **{wf_entry['name']}** ({wf_entry['node_count']} nodes)")

    if wf["stray"]:
        lines.append("\n## Stray Workflows (Outside `automations/n8n/`)\n")
        for wf_entry in wf["stray"]:
            lines.append(f"- ⚠️ `{wf_entry['path']}` — **{wf_entry['name']}** [{wf_entry['classification']}]")

    if stale:
        lines.append("\n## Stale References\n")
        for s in stale:
            issues_str = ", ".join(s["issues"])
            lines.append(f"- 🔴 `{s['path']}` — {issues_str}")

    if opps:
        lines.append("\n## Automation Opportunities\n")
        for opp in sorted(opps, key=lambda x: x["priority"]):
            lines.append(f"- [{opp['priority']}] `{opp['path']}` — {opp['recommendation']} (ROI: {opp['roi']}, Risk: {opp['risk']}, Effort: {opp['effort_days']}d)")

    (out_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")


def write_backlog(opps: list, stale: list, wf_stray: list, out_dir: Path) -> None:
    lines = [
        "# Automation Backlog",
        "\nRanked by priority (P0 → P2). Tags: [ROI:H/M/L] [Risk:H/M/L] [Effort:Nd]",
        "\n---\n",
        "## P0 — Immediate Value, Low Risk\n",
    ]

    p0 = [o for o in opps if o["priority"] == "P0"]
    p1 = [o for o in opps if o["priority"] == "P1"]
    p2 = [o for o in opps if o["priority"] == "P2"]

    # Add stale ref fixes as P0 if they reference critical paths
    if wf_stray:
        lines.append("### Move Stray Workflows to Canonical Location\n")
        for wf_entry in wf_stray:
            lines.append(
                f"- **Move**: `{wf_entry['path']}` → `automations/n8n/workflows/{Path(wf_entry['path']).name}`\n"
                f"  - **Owner**: DevOps  **ROI**: High  **Risk**: Low  **Effort**: 0.5d\n"
                f"  - **Next action**: Run `sweep_repo.py --apply` to auto-move\n"
            )

    for opp in p0:
        _write_opp(lines, opp)

    lines.append("\n## P1 — High Value, Moderate Effort\n")
    for opp in p1:
        _write_opp(lines, opp)

    lines.append("\n## P2 — Nice to Have\n")
    for opp in p2:
        _write_opp(lines, opp)

    if stale:
        lines.append("\n## Stale Reference Cleanup\n")
        for s in stale:
            lines.append(
                f"- **Fix**: `{s['path']}` ({', '.join(s['issues'])})\n"
                f"  - **Owner**: DevOps  **ROI**: Medium  **Risk**: Low  **Effort**: 0.25d\n"
                f"  - **Next action**: Update references to canonical paths and domains\n"
            )

    (out_dir / "backlog.md").write_text("\n".join(lines), encoding="utf-8")


def _write_opp(lines: list, opp: dict) -> None:
    lines.append(
        f"- **`{opp['path']}`**\n"
        f"  - {opp['recommendation']}\n"
        f"  - Signals: {', '.join(opp['signals'])}\n"
        f"  - **Owner**: DevOps  **ROI**: {opp['roi']}  **Risk**: {opp['risk']}  **Effort**: {opp['effort_days']}d\n"
        f"  - **Next action**: Extract logic → create n8n workflow in `automations/n8n/workflows/`\n"
    )


def write_patches(wf_stray: list, out_dir: Path) -> None:
    patches_dir = out_dir / "patches"
    patches_dir.mkdir(exist_ok=True)

    for wf_entry in wf_stray:
        src = REPO_ROOT / wf_entry["path"]
        dest = REPO_ROOT / "automations" / "n8n" / "workflows" / src.name
        diff_content = (
            f"--- a/{wf_entry['path']}\n"
            f"+++ b/automations/n8n/workflows/{src.name}\n"
            f"@@ Move stray workflow to canonical location @@\n"
            f"# git mv '{wf_entry['path']}' 'automations/n8n/workflows/{src.name}'\n"
        )
        patch_name = src.stem.replace(" ", "_") + ".diff"
        (patches_dir / patch_name).write_text(diff_content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Repo-wide automation sweep")
    parser.add_argument("--env", choices=["dev", "stage", "prod"], default="stage")
    parser.add_argument("--out", default="out/automation_sweep")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--fail-on",
        choices=["P0", "P1", "P2"],
        default=None,
        help="Exit non-zero if any backlog findings at this severity or higher exist",
    )
    args = parser.parse_args()

    out_dir = REPO_ROOT / args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    v = args.verbose
    log("=== Automation Sweep (dry-run)" if not args.apply else "=== Automation Sweep (APPLY)", force=True)
    log(f"  Env: {args.env}  |  Out: {out_dir}", force=True)
    log(f"  Repo: {REPO_ROOT}", v)

    # Phase 1: Inventory
    log("\n[Phase 1] Scanning repo...", force=True)
    all_files = walk_repo(REPO_ROOT, v)
    workflows = discover_workflows(all_files, v)
    refs = discover_references(all_files, v)
    stale = detect_stale_refs(all_files, v)

    # Phase 3: Opportunities
    log("\n[Phase 3] Detecting opportunities...", force=True)
    opps = detect_opportunities(all_files, v)

    # Build inventory
    inventory = build_inventory(workflows, refs, stale, opps)

    # Write artifacts
    log("\n[Output] Writing artifacts...", force=True)
    inv_path = out_dir / "inventory.json"
    inv_path.write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    log(f"  → {inv_path}", force=True)

    write_report(inventory, out_dir)
    log(f"  → {out_dir / 'report.md'}", force=True)

    write_backlog(opps, stale, workflows["stray"], out_dir)
    log(f"  → {out_dir / 'backlog.md'}", force=True)

    write_patches(workflows["stray"], out_dir)
    log(f"  → {out_dir / 'patches/'}", force=True)

    # Phase 4: Apply (optional)
    if args.apply:
        log("\n[Phase 4] Apply: calling deploy_n8n_all.py...", force=True)
        import subprocess
        deploy_script = REPO_ROOT / "scripts" / "automations" / "deploy_n8n_all.py"
        result = subprocess.run(
            [sys.executable, str(deploy_script), f"--env={args.env}", "--apply", "--out", str(out_dir)],
            cwd=REPO_ROOT,
        )
        if result.returncode != 0:
            log("  ✗ Deploy phase failed", force=True)
            return 2

    # Summary
    total_issues = len(stale) + len(workflows["stray"])
    log(f"\n=== Complete. Issues: {total_issues}  Opportunities: {len(opps)}", force=True)
    log(f"  Artifacts: {out_dir}/", force=True)

    # Severity-gated exit (if --fail-on specified)
    if args.fail_on:
        severity_order = {"P0": 0, "P1": 1, "P2": 2}
        threshold = severity_order[args.fail_on]
        blocking = [
            item for item in opps
            if severity_order.get(item.get("priority", "P2"), 2) <= threshold
        ]
        if blocking:
            log(f"[FAIL] {len(blocking)} finding(s) at {args.fail_on} or higher.", force=True)
            return 1

    return 1 if total_issues > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
