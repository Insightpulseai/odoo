#!/usr/bin/env python3
"""
backlog_scan.py - Scan repository for Platform Kit / Config Console backlog items

Crawls the repository and all attached artifacts to identify backlog features
intended for the Platform Kit + Supabase UI Config Console, and produces a
deterministic Backlog Coverage Report.

Usage:
    python scripts/backlog_scan.py [--output-dir docs] [--json] [--strict]
"""

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


class BacklogStatus(Enum):
    IMPLEMENTED = "implemented"
    PARTIAL = "partial"
    MISSING = "missing"


class Priority(Enum):
    P0 = "P0"  # Critical - must be implemented
    P1 = "P1"  # High - should be implemented
    P2 = "P2"  # Medium - nice to have


class Category(Enum):
    UI = "UI"
    API = "API"
    DB = "DB"
    CI = "CI"
    ODOO = "Odoo"
    SYNC = "Sync"
    ALERTING = "Alerting"
    CONFIG = "Config"
    OBSERVABILITY = "Observability"


@dataclass
class BacklogItem:
    id: str
    title: str
    category: str
    source_file: str
    target_component: str
    status: str
    priority: str
    evidence: list = field(default_factory=list)
    owner: Optional[str] = None
    notes: str = ""


@dataclass
class ScanResult:
    timestamp: str
    git_sha: str
    total_items: int
    implemented: int
    partial: int
    missing: int
    items: list = field(default_factory=list)
    warnings: list = field(default_factory=list)


# Platform Kit required features (canonical checklist)
PLATFORM_KIT_FEATURES = [
    {
        "title": "Config Registry schema (ops.config_artifacts, config_versions)",
        "category": Category.DB.value,
        "priority": Priority.P0.value,
        "target_component": "supabase/migrations",
        "evidence_patterns": [
            "supabase/migrations/*config_registry*.sql",
            "ops.config_artifacts",
            "ops.config_versions",
        ],
    },
    {
        "title": "Config Registry RLS policies",
        "category": Category.DB.value,
        "priority": Priority.P0.value,
        "target_component": "supabase/migrations",
        "evidence_patterns": [
            "ops_admin_read_config",
            "service_role_config",
        ],
    },
    {
        "title": "Config publish Edge Function",
        "category": Category.API.value,
        "priority": Priority.P0.value,
        "target_component": "supabase/functions/config-publish",
        "evidence_patterns": [
            "supabase/functions/config-publish/index.ts",
        ],
    },
    {
        "title": "Consumer heartbeat Edge Function",
        "category": Category.API.value,
        "priority": Priority.P1.value,
        "target_component": "supabase/functions/consumer-heartbeat",
        "evidence_patterns": [
            "supabase/functions/consumer-heartbeat/index.ts",
        ],
    },
    {
        "title": "Config consumers table (ops.config_consumers)",
        "category": Category.DB.value,
        "priority": Priority.P0.value,
        "target_component": "supabase/migrations",
        "evidence_patterns": [
            "ops.config_consumers",
            "consumer_heartbeat",
        ],
    },
    {
        "title": "Config rollouts table (ops.config_rollouts)",
        "category": Category.DB.value,
        "priority": Priority.P1.value,
        "target_component": "supabase/migrations",
        "evidence_patterns": [
            "ops.config_rollouts",
        ],
    },
    {
        "title": "Drift detection function (ops.detect_config_drift)",
        "category": Category.DB.value,
        "priority": Priority.P1.value,
        "target_component": "supabase/migrations",
        "evidence_patterns": [
            "detect_config_drift",
            "config_drift_events",
        ],
    },
    {
        "title": "Config publish CI workflow",
        "category": Category.CI.value,
        "priority": Priority.P0.value,
        "target_component": ".github/workflows",
        "evidence_patterns": [
            ".github/workflows/config-publish.yml",
        ],
    },
    {
        "title": "Design tokens SSOT (config/tokens/tokens.json)",
        "category": Category.CONFIG.value,
        "priority": Priority.P0.value,
        "target_component": "config/tokens",
        "evidence_patterns": [
            "config/tokens/tokens.json",
        ],
    },
    {
        "title": "Consumers registry (config/consumers/consumers.json)",
        "category": Category.CONFIG.value,
        "priority": Priority.P1.value,
        "target_component": "config/consumers",
        "evidence_patterns": [
            "config/consumers/consumers.json",
        ],
    },
    {
        "title": "Control Room Platform Kit UI",
        "category": Category.UI.value,
        "priority": Priority.P1.value,
        "target_component": "apps/control-room",
        "evidence_patterns": [
            "apps/control-room/PLATFORM_KIT_SPEC.md",
            "ObservabilityManager",
        ],
    },
    {
        "title": "Ops health Edge Function",
        "category": Category.API.value,
        "priority": Priority.P1.value,
        "target_component": "supabase/functions/ops-health",
        "evidence_patterns": [
            "supabase/functions/ops-health/index.ts",
        ],
    },
    {
        "title": "Config rollback RPC function",
        "category": Category.DB.value,
        "priority": Priority.P1.value,
        "target_component": "supabase/migrations",
        "evidence_patterns": [
            "rollback_config",
        ],
    },
    {
        "title": "Backlog coverage CI gate",
        "category": Category.CI.value,
        "priority": Priority.P2.value,
        "target_component": ".github/workflows",
        "evidence_patterns": [
            ".github/workflows/backlog-coverage.yml",
            "backlog_scan.py",
        ],
    },
    {
        "title": "Spec bundle for Platform Kit observability",
        "category": Category.CONFIG.value,
        "priority": Priority.P1.value,
        "target_component": "spec/supabase-platform-kit-observability",
        "evidence_patterns": [
            "spec/supabase-platform-kit-observability/constitution.md",
            "spec/supabase-platform-kit-observability/prd.md",
        ],
    },
]


def compute_item_id(title: str, category: str) -> str:
    """Compute stable hash ID for a backlog item."""
    content = f"{category}:{title}"
    return hashlib.sha256(content.encode()).hexdigest()[:12]


def get_git_sha() -> str:
    """Get current git SHA."""
    try:
        import subprocess
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip()[:12] if result.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def check_file_exists(pattern: str, repo_root: Path) -> list[Path]:
    """Check if files matching pattern exist."""
    import glob
    full_pattern = str(repo_root / pattern)
    return [Path(p) for p in glob.glob(full_pattern, recursive=True)]


def check_content_exists(pattern: str, repo_root: Path, search_dirs: list[str]) -> list[tuple[Path, int]]:
    """Search for content pattern in files."""
    results = []
    for search_dir in search_dirs:
        dir_path = repo_root / search_dir
        if not dir_path.exists():
            continue

        for file_path in dir_path.rglob("*"):
            if not file_path.is_file():
                continue
            if file_path.suffix not in [".sql", ".ts", ".tsx", ".js", ".jsx", ".py", ".md", ".yml", ".yaml", ".json"]:
                continue
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                for line_num, line in enumerate(content.split("\n"), 1):
                    if pattern in line:
                        results.append((file_path, line_num))
                        break  # Only record first match per file
            except Exception:
                continue

    return results


def scan_backlog_item(feature: dict, repo_root: Path) -> BacklogItem:
    """Scan for evidence of a single backlog item."""
    evidence_files = []
    evidence_content = []

    search_dirs = ["supabase", "apps", ".github", "config", "spec", "scripts"]

    for pattern in feature["evidence_patterns"]:
        # Check if it's a file pattern (contains / or *)
        if "/" in pattern or "*" in pattern:
            files = check_file_exists(pattern, repo_root)
            evidence_files.extend([str(f.relative_to(repo_root)) for f in files])
        else:
            # Search for content pattern
            matches = check_content_exists(pattern, repo_root, search_dirs)
            evidence_content.extend([f"{f.relative_to(repo_root)}:{line}" for f, line in matches])

    all_evidence = list(set(evidence_files + evidence_content))

    # Determine status based on evidence
    if len(all_evidence) >= len(feature["evidence_patterns"]):
        status = BacklogStatus.IMPLEMENTED.value
    elif len(all_evidence) > 0:
        status = BacklogStatus.PARTIAL.value
    else:
        status = BacklogStatus.MISSING.value

    return BacklogItem(
        id=compute_item_id(feature["title"], feature["category"]),
        title=feature["title"],
        category=feature["category"],
        source_file="scripts/backlog_scan.py",
        target_component=feature["target_component"],
        status=status,
        priority=feature["priority"],
        evidence=all_evidence[:10],  # Limit evidence entries
    )


def scan_spec_tasks(repo_root: Path) -> list[BacklogItem]:
    """Scan spec/*/tasks.md files for additional backlog items."""
    items = []
    spec_dir = repo_root / "spec"

    if not spec_dir.exists():
        return items

    for tasks_file in spec_dir.rglob("tasks.md"):
        try:
            content = tasks_file.read_text(encoding="utf-8")
            spec_name = tasks_file.parent.name

            # Parse markdown checkboxes
            checkbox_pattern = r"^-\s*\[([ x])\]\s*(.+)$"
            for match in re.finditer(checkbox_pattern, content, re.MULTILINE):
                checked = match.group(1).lower() == "x"
                title = match.group(2).strip()

                # Only include Platform Kit related items
                if not any(kw in title.lower() for kw in ["platform", "config", "observability", "health", "drift"]):
                    continue

                status = BacklogStatus.IMPLEMENTED.value if checked else BacklogStatus.PENDING.value

                items.append(BacklogItem(
                    id=compute_item_id(title, spec_name),
                    title=title,
                    category=Category.CONFIG.value,
                    source_file=str(tasks_file.relative_to(repo_root)),
                    target_component=f"spec/{spec_name}",
                    status=status,
                    priority=Priority.P2.value,
                    evidence=[str(tasks_file.relative_to(repo_root))],
                ))
        except Exception:
            continue

    return items


def scan_todo_comments(repo_root: Path) -> list[BacklogItem]:
    """Scan for TODO/FIXME comments related to Platform Kit."""
    items = []
    search_dirs = ["supabase", "apps/control-room", "scripts"]

    for search_dir in search_dirs:
        dir_path = repo_root / search_dir
        if not dir_path.exists():
            continue

        for file_path in dir_path.rglob("*"):
            if not file_path.is_file():
                continue
            if file_path.suffix not in [".ts", ".tsx", ".js", ".py", ".sql"]:
                continue

            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                todo_pattern = r"(?:TODO|FIXME|XXX)[\s:]+(.+)$"

                for line_num, line in enumerate(content.split("\n"), 1):
                    match = re.search(todo_pattern, line, re.IGNORECASE)
                    if match:
                        title = match.group(1).strip()[:100]  # Limit title length

                        # Only include Platform Kit related TODOs
                        if not any(kw in title.lower() for kw in ["platform", "config", "token", "health", "drift", "registry"]):
                            continue

                        items.append(BacklogItem(
                            id=compute_item_id(title, "TODO"),
                            title=f"TODO: {title}",
                            category=Category.CONFIG.value,
                            source_file=f"{file_path.relative_to(repo_root)}:{line_num}",
                            target_component=str(file_path.parent.relative_to(repo_root)),
                            status=BacklogStatus.MISSING.value,
                            priority=Priority.P2.value,
                            evidence=[f"{file_path.relative_to(repo_root)}:{line_num}"],
                        ))
            except Exception:
                continue

    return items


def run_scan(repo_root: Path) -> ScanResult:
    """Run full backlog scan."""
    items = []
    warnings = []

    # Scan canonical Platform Kit features
    for feature in PLATFORM_KIT_FEATURES:
        item = scan_backlog_item(feature, repo_root)
        items.append(item)

    # Scan spec tasks
    spec_items = scan_spec_tasks(repo_root)
    items.extend(spec_items)

    # Scan TODO comments (limited to avoid noise)
    todo_items = scan_todo_comments(repo_root)
    items.extend(todo_items[:20])  # Limit TODOs

    # Deduplicate by ID
    seen_ids = set()
    unique_items = []
    for item in items:
        if item.id not in seen_ids:
            seen_ids.add(item.id)
            unique_items.append(item)

    # Count by status
    implemented = sum(1 for i in unique_items if i.status == BacklogStatus.IMPLEMENTED.value)
    partial = sum(1 for i in unique_items if i.status == BacklogStatus.PARTIAL.value)
    missing = sum(1 for i in unique_items if i.status == BacklogStatus.MISSING.value)

    # Generate warnings for P0 items that are missing
    for item in unique_items:
        if item.priority == Priority.P0.value and item.status == BacklogStatus.MISSING.value:
            warnings.append(f"P0 item missing: {item.title}")

    return ScanResult(
        timestamp=datetime.utcnow().isoformat() + "Z",
        git_sha=get_git_sha(),
        total_items=len(unique_items),
        implemented=implemented,
        partial=partial,
        missing=missing,
        items=[asdict(i) for i in unique_items],
        warnings=warnings,
    )


def generate_markdown_report(result: ScanResult) -> str:
    """Generate markdown report."""
    lines = [
        "# Backlog Coverage Report",
        "",
        f"**Generated**: {result.timestamp}",
        f"**Git SHA**: {result.git_sha}",
        "",
        "## Summary",
        "",
        f"| Status | Count |",
        f"|--------|-------|",
        f"| Implemented | {result.implemented} |",
        f"| Partial | {result.partial} |",
        f"| Missing | {result.missing} |",
        f"| **Total** | **{result.total_items}** |",
        "",
    ]

    if result.warnings:
        lines.extend([
            "## Warnings",
            "",
        ])
        for warning in result.warnings:
            lines.append(f"- {warning}")
        lines.append("")

    # Group by status
    for status_label, status_val in [
        ("Missing Features (Action Required)", BacklogStatus.MISSING.value),
        ("Partial Implementations", BacklogStatus.PARTIAL.value),
        ("Implemented Features", BacklogStatus.IMPLEMENTED.value),
    ]:
        status_items = [i for i in result.items if i["status"] == status_val]
        if not status_items:
            continue

        lines.extend([
            f"## {status_label}",
            "",
            "| Priority | Category | Title | Target Component | Evidence |",
            "|----------|----------|-------|------------------|----------|",
        ])

        for item in sorted(status_items, key=lambda x: (x["priority"], x["category"])):
            evidence_str = ", ".join(item["evidence"][:3]) or "-"
            lines.append(
                f"| {item['priority']} | {item['category']} | {item['title']} | {item['target_component']} | {evidence_str} |"
            )
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Scan repository for Platform Kit backlog coverage")
    parser.add_argument("--output-dir", default="docs", help="Output directory for reports")
    parser.add_argument("--json", action="store_true", help="Output JSON to stdout")
    parser.add_argument("--strict", action="store_true", help="Exit with error if any P0 items are missing")
    parser.add_argument("--repo-root", default=".", help="Repository root directory")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()

    if not (repo_root / ".git").exists() and not (repo_root / "supabase").exists():
        print(f"ERROR: {repo_root} does not appear to be the repository root", file=sys.stderr)
        sys.exit(1)

    result = run_scan(repo_root)

    if args.json:
        print(json.dumps(asdict(result), indent=2))
    else:
        # Write reports
        output_dir = repo_root / args.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        md_path = output_dir / "BACKLOG_COVERAGE_REPORT.md"
        json_path = output_dir / "BACKLOG_COVERAGE_REPORT.json"

        md_path.write_text(generate_markdown_report(result), encoding="utf-8")
        json_path.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")

        print(f"Reports generated:")
        print(f"  - {md_path}")
        print(f"  - {json_path}")
        print()
        print(f"Summary: {result.implemented} implemented, {result.partial} partial, {result.missing} missing")

    if args.strict and result.warnings:
        print(f"\nERROR: {len(result.warnings)} P0 items are missing:", file=sys.stderr)
        for warning in result.warnings:
            print(f"  - {warning}", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
