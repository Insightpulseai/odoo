#!/usr/bin/env python3
"""Strategy status report generator.

Reads all governance YAML layers and produces a Markdown status report.
Always exits 0 — this is a report generator, not a gate.

Usage:
    python scripts/ci/generate_strategy_status.py
    python scripts/ci/generate_strategy_status.py --output docs/reports/strategy_status.md
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

_YAML_PATHS = {
    "okrs": REPO_ROOT / "ssot/governance/enterprise_okrs.yaml",
    "strategy": REPO_ROOT / "ssot/governance/platform-strategy-2026.yaml",
    "index": REPO_ROOT / "ssot/governance/planning_system_index.yaml",
    "kpis": REPO_ROOT / "platform/data/contracts/control_room_kpis.yaml",
}


def _load(key: str) -> dict:
    path = _YAML_PATHS[key]
    if not path.exists():
        return {"_missing": str(path)}
    with path.open() as fh:
        return yaml.safe_load(fh) or {}


def _warn(msg: str, warnings: list) -> None:
    warnings.append(msg)


def _md_table(headers: list[str], rows: list[list[str]]) -> str:
    sep = ["-" * max(len(h), 4) for h in headers]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(sep) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(c) for c in row) + " |")
    return "\n".join(lines)


def _section_objectives(okrs: dict, warnings: list) -> str:
    objs = okrs.get("strategic_objectives", [])
    if not objs:
        _warn("enterprise_okrs.yaml: strategic_objectives missing or empty", warnings)
        return "## Strategic Objectives\n\n_No data._\n"

    rows = []
    for obj in objs:
        kr_count = len(obj.get("key_results", []))
        rows.append([obj.get("id", "?"), obj.get("name", "?"), str(kr_count)])

    return "## Strategic Objectives\n\n" + _md_table(
        ["ID", "Name", "KR Count"], rows
    ) + "\n"


def _section_canonical_okrs(okrs: dict, warnings: list) -> str:
    canon = okrs.get("canonical_okrs", [])
    if not canon:
        _warn("enterprise_okrs.yaml: canonical_okrs missing or empty", warnings)
        return "## Canonical OKRs\n\n_No data._\n"

    rows = []
    for okr in canon:
        parents = ", ".join(okr.get("parent_objectives", []))
        kr_count = len(okr.get("key_results", []))
        rows.append([okr.get("id", "?"), okr.get("name", "?"), parents, str(kr_count)])

    return "## Canonical OKRs\n\n" + _md_table(
        ["ID", "Name", "Parent Objectives", "KR Count"], rows
    ) + "\n"


def _section_kpi_coverage(okrs: dict, strategy: dict, kpis: dict, warnings: list) -> str:
    all_kpis = kpis.get("kpis", [])
    total_kpis = len(all_kpis)

    if total_kpis == 0:
        _warn("control_room_kpis.yaml: kpis list missing or empty", warnings)

    # KPI refs from enterprise_okrs (kpi_index values + inline kpi_ref fields)
    okr_kpi_refs: set[str] = set()
    kpi_index = okrs.get("kpi_index", {})
    for refs in kpi_index.values():
        okr_kpi_refs.update(refs)
    for obj in okrs.get("strategic_objectives", []):
        for kr in obj.get("key_results", []):
            ref = kr.get("kpi_ref")
            if ref:
                okr_kpi_refs.add(ref)
    for okr in okrs.get("canonical_okrs", []):
        for kr in okr.get("key_results", []):
            ref = kr.get("kpi_ref")
            if ref:
                okr_kpi_refs.add(ref)

    # KPI refs from strategy (strategy.kpis[].id)
    strategy_kpi_ids: set[str] = {
        kpi.get("id", "") for kpi in strategy.get("kpis", []) if kpi.get("id")
    }

    lines = [
        "## KPI Coverage\n",
        f"- Total KPIs defined in `control_room_kpis.yaml`: **{total_kpis}**",
        f"- Referenced in `enterprise_okrs.yaml` (kpi_index + kpi_ref): **{len(okr_kpi_refs)}**",
        f"- Defined in `platform-strategy-2026.yaml` (strategy.kpis): **{len(strategy_kpi_ids)}**",
    ]
    unreferenced = [k.get("id") for k in all_kpis if k.get("id") not in okr_kpi_refs]
    if unreferenced:
        lines.append(f"- KPIs in control_room not referenced by OKRs: {', '.join(unreferenced)}")

    return "\n".join(lines) + "\n"


def _section_planning_layers(index: dict, warnings: list) -> str:
    layers = index.get("layers", [])
    if not layers:
        _warn("planning_system_index.yaml: layers missing or empty", warnings)
        return "## Planning Layers\n\n_No data._\n"

    rows = []
    for layer in layers:
        layer_id = layer.get("id", "?")
        name = layer.get("name", "?")
        status = layer.get("status", "on_main")  # default assumption when field absent
        has_validator = "yes" if layer.get("validator") else "no"
        has_ci_gate = "yes" if layer.get("ci_gate") else "no"
        rows.append([layer_id, name, status, has_validator, has_ci_gate])

    return "## Planning Layers\n\n" + _md_table(
        ["ID", "Name", "Status", "Validator", "CI Gate"], rows
    ) + "\n"


def _section_crosslayer_health(index: dict, okrs: dict, warnings: list) -> str:
    crosswalks = index.get("crosswalks", [])
    kpi_index = okrs.get("kpi_index", {})

    lines = [
        "## Cross-Layer Health\n",
        f"- Crosswalks defined in planning index: **{len(crosswalks)}**",
        f"- KPI index entries in enterprise_okrs: **{len(kpi_index)}**",
    ]

    if warnings:
        lines.append(f"- Warnings: **{len(warnings)}**")
        for w in warnings:
            lines.append(f"  - {w}")
    else:
        lines.append("- Warnings: **0** — all layers loaded cleanly")

    return "\n".join(lines) + "\n"


def generate_report() -> str:
    warnings: list[str] = []

    okrs = _load("okrs")
    strategy = _load("strategy")
    index = _load("index")
    kpis = _load("kpis")

    for key, data in [("okrs", okrs), ("strategy", strategy), ("index", index), ("kpis", kpis)]:
        if data.get("_missing"):
            _warn(f"File not found: {data['_missing']}", warnings)

    stamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    sections = [
        f"# Strategy Status Report\n\nGenerated: `{stamp}`\n",
        _section_objectives(okrs, warnings),
        _section_canonical_okrs(okrs, warnings),
        _section_kpi_coverage(okrs, strategy, kpis, warnings),
        _section_planning_layers(index, warnings),
        _section_crosslayer_health(index, okrs, warnings),
    ]

    return "\n".join(sections)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a Markdown strategy status report from governance YAML layers."
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        help="Write report to FILE instead of stdout",
    )
    args = parser.parse_args()

    report = generate_report()

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding="utf-8")
        print(f"Report written to: {out_path}", file=sys.stderr)
    else:
        print(report)

    sys.exit(0)


if __name__ == "__main__":
    main()
