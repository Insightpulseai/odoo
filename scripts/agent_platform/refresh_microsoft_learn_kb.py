#!/usr/bin/env python3
"""Microsoft Learn KB refresh and validation script.

Validates knowledge manifests, checks repo-local SSOT file existence,
generates MCP query plans, and produces evidence reports.

Usage:
    python scripts/agent_platform/refresh_microsoft_learn_kb.py
    python scripts/agent_platform/refresh_microsoft_learn_kb.py \
        --execute --output-dir docs/evidence/custom/
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# SSOT manifest paths
SSOT_DIR = REPO_ROOT / "ssot" / "agent-platform"
TOPIC_MAP = SSOT_DIR / "learn_mcp_topic_map.yaml"
KNOWLEDGE_SOURCES = SSOT_DIR / "knowledge_sources.yaml"
SKILLS_MANIFEST = SSOT_DIR / "skills_manifest.yaml"
TAXONOMY = SSOT_DIR / "knowledge_taxonomy.yaml"

# Skills root
SKILLS_DIR = REPO_ROOT / ".github" / "skills"

# MCP endpoint (informational — not called here)
MCP_ENDPOINT = "https://learn.microsoft.com/api/mcp"
MCP_TOOLS = [
    "microsoft_docs_search",
    "microsoft_code_sample_search",
    "microsoft_docs_fetch",
]

# Required fields per topic entry in learn_mcp_topic_map.yaml
# (topics is a dict keyed by topic_id)
REQUIRED_TOPIC_FIELDS = {
    "topic_key",
    "canonical_product",
    "mvp_critical",
    "recommended_queries",
}

# Valid source type names (in precedence order)
VALID_SOURCE_TYPE_ORDER = [
    "repo_ssot",
    "architecture_reference_docs",
    "microsoft_learn_mcp",
    "official_microsoft_github_samples",
    "secondary_sources",
]


def load_yaml(path: Path) -> dict | None:
    """Load a YAML file; return None if missing or invalid."""
    try:
        import yaml
    except ImportError:
        print(
            "ERROR: PyYAML required. Install: pip install pyyaml",
            file=sys.stderr,
        )
        sys.exit(1)

    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def check_manifest_existence() -> dict:
    """Check all required SSOT manifests exist."""
    manifests = {
        "learn_mcp_topic_map": TOPIC_MAP,
        "knowledge_sources": KNOWLEDGE_SOURCES,
        "skills_manifest": SKILLS_MANIFEST,
        "knowledge_taxonomy": TAXONOMY,
    }
    return {
        name: {
            "path": str(path.relative_to(REPO_ROOT)),
            "exists": path.exists(),
        }
        for name, path in manifests.items()
    }


def validate_topic_map(topic_map: dict) -> dict:
    """Validate learn_mcp_topic_map.yaml structure and fields.

    topics is a dict keyed by topic_id; each value is a mapping with
    fields: topic_key, canonical_product, mvp_critical,
    recommended_queries, fallback_urls, exclusion_notes.
    """
    raw = topic_map.get("topics", {}) if topic_map else {}
    if isinstance(raw, list):
        topics_dict = {
            t.get("id", f"idx-{i}"): t for i, t in enumerate(raw)
        }
    elif isinstance(raw, dict):
        topics_dict = raw
    else:
        topics_dict = {}

    gaps = []
    valid = []
    query_plan = []

    for topic_id, entry in topics_dict.items():
        if not isinstance(entry, dict):
            gaps.append({
                "topic": topic_id,
                "error": "value is not a mapping",
            })
            continue
        missing = REQUIRED_TOPIC_FIELDS - set(entry.keys())
        if missing:
            gaps.append({
                "topic": topic_id,
                "missing_fields": sorted(missing),
            })
        else:
            valid.append(topic_id)
            mvp = entry.get("mvp_critical", False)
            for q in entry.get("recommended_queries", []):
                query_plan.append({
                    "topic": topic_id,
                    "tool": "microsoft_docs_search",
                    "query": q,
                    "mvp_critical": mvp,
                })

    return {
        "total": len(topics_dict),
        "valid": valid,
        "gaps": gaps,
        "query_plan": query_plan,
    }


def validate_knowledge_sources(sources: dict) -> dict:
    """Validate source precedence order and repo-local file existence."""
    if not sources:
        return {"error": "knowledge_sources.yaml missing or empty"}

    entries = sources.get("source_precedence", [])
    actual_types = [
        e.get("type") if isinstance(e, dict) else e for e in entries
    ]
    order_ok = actual_types == VALID_SOURCE_TYPE_ORDER
    order_issues = []
    if not order_ok:
        order_issues.append(
            f"Expected {VALID_SOURCE_TYPE_ORDER}, got {actual_types}"
        )

    path_checks = []
    for entry in sources.get("sources", []):
        src_type = entry.get("type", "")
        if src_type not in ("repo_ssot", "architecture_reference_docs"):
            continue
        for rel_path in entry.get("paths", []):
            if "*" in rel_path:
                continue
            full = REPO_ROOT / rel_path
            path_checks.append({
                "path": rel_path,
                "exists": full.exists(),
                "type": src_type,
            })

    missing_paths = [p for p in path_checks if not p["exists"]]
    return {
        "source_order_valid": order_ok,
        "order_issues": order_issues,
        "paths_checked": len(path_checks),
        "missing_paths": missing_paths,
    }


def validate_skills_manifest(manifest: dict) -> dict:
    """Validate skills_manifest.yaml references skills that exist."""
    if not manifest:
        return {"error": "skills_manifest.yaml missing or empty"}

    skills = manifest.get("skills", [])
    missing_dirs = []
    missing_files = []
    valid = []

    for skill in skills:
        sid = skill.get("id", "<unknown>")
        loc = skill.get("location", f".github/skills/{sid}/")
        skill_dir = REPO_ROOT / loc
        if not skill_dir.exists():
            missing_dirs.append(f"{sid} -> {loc}")
        else:
            valid.append(sid)
            for fname in ("SKILL.md", "examples.md"):
                if not (skill_dir / fname).exists():
                    missing_files.append(f"{sid}/{fname}")

    return {
        "total": len(skills),
        "valid": valid,
        "missing_skill_dirs": missing_dirs,
        "missing_required_files": missing_files,
    }


def validate_taxonomy(taxonomy: dict) -> dict:
    """Validate knowledge_taxonomy.yaml deferred list integrity."""
    if not taxonomy:
        return {"error": "knowledge_taxonomy.yaml missing or empty"}

    deferred_section = (
        taxonomy
        .get("taxonomy", {})
        .get("deferred_optional", {})
    )
    deferred_topics = deferred_section.get("topics", [])

    mvp_in_deferred = [
        e.get("id", "<unknown>")
        for e in deferred_topics
        if e.get("mvp_critical") is True
    ]
    missing_alt = [
        e.get("id", "<unknown>")
        for e in deferred_topics
        if not e.get("approved_alternative")
    ]
    ids = [e.get("id") for e in deferred_topics if e.get("id")]
    duplicates = [i for i in ids if ids.count(i) > 1]

    return {
        "deferred_count": len(deferred_topics),
        "mvp_critical_in_deferred": mvp_in_deferred,
        "missing_approved_alternative": missing_alt,
        "duplicate_ids": list(set(duplicates)),
    }


def check_skills_on_disk() -> dict:
    """Scan .github/skills/ for skills missing required files."""
    if not SKILLS_DIR.exists():
        return {"error": f"{SKILLS_DIR} does not exist"}

    skills_found = []
    incomplete = []
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue
        name = skill_dir.name
        has_skill = (skill_dir / "SKILL.md").exists()
        has_examples = (skill_dir / "examples.md").exists()
        skills_found.append(name)
        if not has_skill or not has_examples:
            incomplete.append({
                "skill": name,
                "missing": [
                    fname
                    for fname, ok in [
                        ("SKILL.md", has_skill),
                        ("examples.md", has_examples),
                    ]
                    if not ok
                ],
            })

    return {
        "total_on_disk": len(skills_found),
        "skills": skills_found,
        "incomplete": incomplete,
    }


def write_report(report: dict, output_dir: Path) -> Path:
    """Write the evidence report to output_dir/report.yaml."""
    try:
        import yaml
    except ImportError:
        print("ERROR: PyYAML required.", file=sys.stderr)
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "report.yaml"
    with open(report_path, "w", encoding="utf-8") as f:
        yaml.dump(report, f, default_flow_style=False, sort_keys=False)
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate knowledge manifests and generate MCP query plan"
        )
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Write evidence report to disk (default: dry-run only)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Override evidence output directory",
    )
    args = parser.parse_args()

    dry_run = not args.execute
    stamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d-%H%M")

    if args.output_dir:
        output_dir = args.output_dir / "kb-refresh"
    else:
        output_dir = (
            REPO_ROOT / "docs" / "evidence" / stamp / "kb-refresh"
        )

    print(f"[kb-refresh] stamp={stamp} dry_run={dry_run}")
    print(f"[kb-refresh] output_dir={output_dir}")

    topic_map = load_yaml(TOPIC_MAP)
    sources = load_yaml(KNOWLEDGE_SOURCES)
    skills_mf = load_yaml(SKILLS_MANIFEST)
    taxonomy = load_yaml(TAXONOMY)

    manifest_check = check_manifest_existence()
    topic_validation = validate_topic_map(topic_map or {})
    sources_validation = validate_knowledge_sources(sources or {})
    skills_validation = validate_skills_manifest(skills_mf or {})
    taxonomy_validation = validate_taxonomy(taxonomy or {})
    disk_skills = check_skills_on_disk()

    missing_manifests = [
        k for k, v in manifest_check.items() if not v["exists"]
    ]
    gaps_count = len(topic_validation.get("gaps", []))
    missing_paths = sources_validation.get("missing_paths", [])
    mvp_deferred = taxonomy_validation.get("mvp_critical_in_deferred", [])
    incomplete_skills = disk_skills.get("incomplete", [])

    report = {
        "stamp": stamp,
        "dry_run": dry_run,
        "mcp_endpoint": MCP_ENDPOINT,
        "mcp_tools": MCP_TOOLS,
        "manifests": manifest_check,
        "topic_map": topic_validation,
        "knowledge_sources": sources_validation,
        "skills_manifest": skills_validation,
        "taxonomy": taxonomy_validation,
        "skills_on_disk": disk_skills,
        "summary": {
            "missing_manifests": missing_manifests,
            "topic_gaps": gaps_count,
            "missing_repo_paths": len(missing_paths),
            "mvp_topics_in_deferred": len(mvp_deferred),
            "incomplete_skills_on_disk": len(incomplete_skills),
            "query_plan_entries": len(
                topic_validation.get("query_plan", [])
            ),
        },
    }

    print("\n--- Summary ---")
    print(f"  Missing manifests:         {len(missing_manifests)}")
    print(f"  Topic map gaps:            {gaps_count}")
    print(f"  Missing repo paths:        {len(missing_paths)}")
    print(f"  MVP topics in deferred:    {len(mvp_deferred)}")
    print(f"  Incomplete skills on disk: {len(incomplete_skills)}")
    print(
        "  MCP query plan entries:    "
        f"{len(topic_validation.get('query_plan', []))}"
    )

    if dry_run:
        print(
            "\n[DRY RUN] Report not written. "
            f"Pass --execute to write to {output_dir}/report.yaml"
        )
        return 0

    report_path = write_report(report, output_dir)
    print(f"\n[WRITTEN] {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
