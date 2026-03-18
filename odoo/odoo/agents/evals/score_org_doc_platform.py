#!/usr/bin/env python3
"""
Org Doc Platform Capability Scorer

Reads org_doc_platform_target_capabilities.yaml, computes maturity scores
per domain and overall, identifies release blockers, and outputs JSON + markdown.

Usage:
    python agents/evals/score_org_doc_platform.py

Outputs:
    artifacts/evals/org_doc_platform_eval.json
    artifacts/evals/org_doc_platform_eval.md

Contract: docs/contracts/ORG_DOC_PLATFORM_EVAL_CONTRACT.md
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml


# -- Maturity band classification -------------------------------------------

MATURITY_BANDS = [
    (0.00, 0.25, "missing"),
    (0.25, 0.50, "scaffolded"),
    (0.50, 0.75, "partial"),
    (0.75, 0.90, "operational"),
    (0.90, 1.01, "target"),
]


def classify_band(score: float) -> str:
    for low, high, band in MATURITY_BANDS:
        if low <= score < high:
            return band
    return "unknown"


# -- YAML loader ------------------------------------------------------------


def load_capability_file(path: str) -> dict:
    """Load a capability YAML file and return parsed dict."""
    with open(path) as f:
        return yaml.safe_load(f)


# -- Scoring engine ---------------------------------------------------------


def score_capabilities(data: dict) -> dict:
    """Score all capabilities in a capability YAML structure.

    Returns:
        dict with domain_scores, capabilities, blockers, next_highest_value, summary
    """
    domains = data.get("domains", {})
    all_capabilities = {}
    domain_scores = {}
    blockers = []
    gaps = []

    for domain_name, domain_data in domains.items():
        weight = domain_data.get("weight", 0.0)
        capabilities = domain_data.get("capabilities", [])

        if not capabilities:
            domain_scores[domain_name] = {
                "score": 0.0,
                "weight": weight,
                "weighted": 0.0,
                "capability_count": 0,
            }
            continue

        cap_scores = []
        for cap in capabilities:
            cap_id = cap["id"]
            current = cap.get("current", 0)
            target = cap.get("target", 4)
            cap_score = current / target if target > 0 else 0.0
            cap_scores.append(cap_score)

            all_capabilities[cap_id] = {
                "current": current,
                "target": target,
                "score": round(cap_score, 3),
                "domain": domain_name,
                "name": cap.get("name", cap_id),
                "release_blocker": cap.get("release_blocker", False),
                "evidence": cap.get("evidence", []),
                "notes": cap.get("notes", ""),
            }

            if cap.get("release_blocker", False) and current < 3:
                blockers.append(
                    "%s: current=%d (needs >=3, domain=%s)"
                    % (cap_id, current, domain_name)
                )

            gap = target - current
            if gap > 0:
                gaps.append((gap, cap_id, domain_name, current, target))

        domain_avg = sum(cap_scores) / len(cap_scores)
        domain_scores[domain_name] = {
            "score": round(domain_avg, 3),
            "weight": weight,
            "weighted": round(domain_avg * weight, 4),
            "capability_count": len(cap_scores),
        }

    overall_score = sum(d["weighted"] for d in domain_scores.values())

    # Next highest value actions sorted by gap * weight
    gaps.sort(key=lambda g: (-g[0], -domains.get(g[2], {}).get("weight", 0)))
    next_highest_value = []
    for gap_size, cap_id, domain_name, current, target in gaps[:10]:
        domain_weight = domains.get(domain_name, {}).get("weight", 0)
        value = gap_size * domain_weight
        next_highest_value.append(
            "Promote %s from %d to %d (gap=%d, domain=%s, weight=%.2f, value=%.3f)"
            % (cap_id, current, target, gap_size, domain_name, domain_weight, value)
        )

    return {
        "summary": {
            "overall_score": round(overall_score, 4),
            "maturity_band": classify_band(overall_score),
            "release_blocked": len(blockers) > 0,
            "blocker_count": len(blockers),
            "total_capabilities": len(all_capabilities),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        "domain_scores": {
            name: {
                "score": d["score"],
                "weight": d["weight"],
                "weighted": d["weighted"],
                "capability_count": d["capability_count"],
            }
            for name, d in domain_scores.items()
        },
        "blockers": blockers,
        "next_highest_value": next_highest_value,
        "capabilities": all_capabilities,
    }


# -- Markdown renderer ------------------------------------------------------


def render_markdown(result: dict) -> str:
    """Render scoring results as markdown report."""
    lines = []
    s = result["summary"]

    lines.append("# Org Doc Platform Capability Eval Report")
    lines.append("")
    lines.append("Generated: %s" % s["timestamp"])
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append("| Overall Score | %.4f |" % s["overall_score"])
    lines.append("| Maturity Band | %s |" % s["maturity_band"])
    lines.append(
        "| Release Blocked | %s |"
        % (
            "YES (%d blockers)" % s["blocker_count"]
            if s["release_blocked"]
            else "No"
        )
    )
    lines.append("| Total Capabilities | %d |" % s["total_capabilities"])
    lines.append("")

    lines.append("## Domain Scores")
    lines.append("")
    lines.append("| Domain | Score | Weight | Weighted | Capabilities |")
    lines.append("|--------|-------|--------|----------|-------------|")
    for name, d in sorted(
        result["domain_scores"].items(), key=lambda x: -x[1]["weighted"]
    ):
        lines.append(
            "| %s | %.3f | %.2f | %.4f | %d |"
            % (name, d["score"], d["weight"], d["weighted"], d["capability_count"])
        )
    lines.append("")

    if result["blockers"]:
        lines.append("## Release Blockers")
        lines.append("")
        for b in result["blockers"]:
            lines.append("- %s" % b)
        lines.append("")

    if result["next_highest_value"]:
        lines.append("## Next Highest-Value Actions")
        lines.append("")
        for i, action in enumerate(result["next_highest_value"][:10], 1):
            lines.append("%d. %s" % (i, action))
        lines.append("")

    lines.append("## Capability Details")
    lines.append("")
    lines.append("| Capability | Domain | Current | Target | Score | Blocker |")
    lines.append("|-----------|--------|---------|--------|-------|---------|")
    for cap_id, cap in sorted(
        result["capabilities"].items(), key=lambda x: (x[1]["domain"], x[0])
    ):
        blocker_mark = (
            "BLOCKED" if cap["release_blocker"] and cap["current"] < 3 else ""
        )
        lines.append(
            "| %s | %s | %d | %d | %.3f | %s |"
            % (
                cap_id,
                cap["domain"],
                cap["current"],
                cap["target"],
                cap["score"],
                blocker_mark,
            )
        )
    lines.append("")

    return "\n".join(lines)


# -- Main -------------------------------------------------------------------


def main():
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent

    yaml_path = repo_root / "agents" / "evals" / "org_doc_platform_target_capabilities.yaml"
    output_dir = repo_root / "artifacts" / "evals"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not yaml_path.exists():
        print("ERROR: %s not found" % yaml_path)
        sys.exit(1)

    print("Loading: %s" % yaml_path.relative_to(repo_root))
    data = load_capability_file(str(yaml_path))
    result = score_capabilities(data)

    # Write JSON
    json_path = output_dir / "org_doc_platform_eval.json"
    with open(json_path, "w") as f:
        json.dump(result, f, indent=2)
    print("JSON: %s" % json_path.relative_to(repo_root))

    # Write Markdown
    md_path = output_dir / "org_doc_platform_eval.md"
    md_content = render_markdown(result)
    with open(md_path, "w") as f:
        f.write(md_content)
    print("Markdown: %s" % md_path.relative_to(repo_root))

    # Print summary
    print("")
    print("=" * 60)
    print(
        "Overall Score: %.4f (%s)"
        % (result["summary"]["overall_score"], result["summary"]["maturity_band"])
    )
    print(
        "Release Blocked: %s"
        % ("YES" if result["summary"]["release_blocked"] else "No")
    )
    if result["blockers"]:
        print("Blockers (%d):" % len(result["blockers"]))
        for b in result["blockers"]:
            print("  - %s" % b)
    if result["next_highest_value"]:
        print("")
        print("Top 5 Next Actions:")
        for action in result["next_highest_value"][:5]:
            print("  - %s" % action)
    print("=" * 60)

    return 0 if not result["summary"]["release_blocked"] else 1


if __name__ == "__main__":
    sys.exit(main())
