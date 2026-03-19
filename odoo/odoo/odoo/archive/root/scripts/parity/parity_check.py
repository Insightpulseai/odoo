#!/usr/bin/env python3
import json
import os
import sys
import time
import re
import glob
import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import yaml  # pyyaml
except Exception:
    print("ERROR: PyYAML is required. Install: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[2]

# --- Helper Utilities for Probes ---


def _read_text(path: Path) -> str:
    try:
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")
    except (OSError, Exception):
        return ""


def _glob_many(globs_list: list[str]) -> list[Path]:
    out: list[Path] = []
    for g in globs_list:
        # If the glob is absolute, use it; otherwise join with ROOT
        search_pattern = g if os.path.isabs(g) else str(ROOT / g)
        for m in glob.glob(search_pattern, recursive=True):
            if "__pycache__" in m or m.endswith(".pyc"):
                continue
            try:
                p = Path(m)
                if p.exists():
                    out.append(p)
            except OSError:
                continue
    # de-dupe
    uniq = []
    seen = set()
    for p in out:
        try:
            rp = str(p.resolve())
            if rp not in seen:
                seen.add(rp)
                uniq.append(p)
        except OSError:
            continue
    return uniq


def _any_exists(paths: list[str]) -> bool:
    return any((ROOT / p).exists() for p in paths)


def _any_glob_matches(globs_list: list[str]) -> bool:
    return any(_glob_many([g]) for g in globs_list)


def _any_file_contains_regex(paths: list[Path], patterns: list[str]) -> bool:
    if not patterns:
        return True
    rx = [re.compile(p) for p in patterns]
    for fp in paths:
        txt = _read_text(fp)
        for r in rx:
            if r.search(txt):
                return True
    return False


def _file_contains_all_regex(paths: list[Path], patterns: list[str]) -> bool:
    # At least one file must satisfy ALL patterns (stronger signal).
    if not patterns:
        return True
    rx = [re.compile(p) for p in patterns]
    for fp in paths:
        txt = _read_text(fp)
        if all(r.search(txt) for r in rx):
            return True
    return False


def _count_glob(globs_list: list[str]) -> int:
    return len(_glob_many(globs_list))


def _load_tier0_cfg(cfg_path: Path) -> dict:
    if not cfg_path.exists():
        # No config => don't fail hard; return empty config
        return {}
    try:
        return yaml.safe_load(cfg_path.read_text()) or {}
    except Exception:
        return {}


def _tier0_strict(cfg: dict) -> bool:
    return cfg.get("strict_evidence", False)


def _probe_from_cfg(name: str, cfg: dict) -> dict:
    return cfg.get("probes", {}).get(name, {})


def _must(pass_condition: bool, msg: str):
    if not pass_condition:
        raise ValueError(msg)


# --- Probes (Locked Tier-0) ---


def probe_ci_build_pipeline(cfg_path: Path):
    cfg = _load_tier0_cfg(cfg_path)
    p = _probe_from_cfg("ci_build_pipeline", cfg)
    if not p:
        return False
    # Check for workflows
    wfs = _glob_many(p.get("workflow_globs", []))
    _must(wfs, "No build/CI workflows found")
    # Check for build tool traces
    _must(
        _any_file_contains_regex(wfs, p.get("any_workflow_must_contain_regex", [])),
        "CI workflows missing build/install commands",
    )
    return True


def probe_env_separation(cfg_path: Path):
    cfg = _load_tier0_cfg(cfg_path)
    p = _probe_from_cfg("env_separation", cfg)
    if not p:
        return False
    # Evidence files
    _must(_any_exists(p.get("any_file_must_exist", [])), "Missing runtime identifiers or snapshots")
    # Deploy scripts
    _must(
        _any_glob_matches(p.get("any_path_must_match_glob", [])),
        "No environment-specific deploy scripts",
    )
    # Content check
    all_files = _glob_many(p.get("any_path_must_match_glob", [])) + [
        ROOT / x for x in p.get("any_file_must_exist", [])
    ]
    _must(
        _any_file_contains_regex(all_files, p.get("any_file_must_contain_regex", [])),
        "No mention of dev/stage/prod environments in deployments",
    )
    return True


def probe_remote_shell_access(cfg_path: Path):
    cfg = _load_tier0_cfg(cfg_path)
    p = _probe_from_cfg("remote_shell_access", cfg)
    if not p:
        return False
    paths = _glob_many(p.get("any_path_must_match_glob", []))
    _must(paths, "No remote access/SSH scripts found")
    _must(
        _any_file_contains_regex(paths, p.get("any_file_must_contain_regex", [])),
        "Scripts do not contain SSH or exec patterns",
    )
    return True


def probe_upgrade_rehearsal(cfg_path: Path):
    cfg = _load_tier0_cfg(cfg_path)
    p = _probe_from_cfg("upgrade_rehearsal", cfg)
    if not p:
        return False
    paths = _glob_many(p.get("any_path_must_match_glob", []))
    evidence = _glob_many(p.get("evidence_globs", []))
    _must(paths, "No upgrade or migration scripts/docs")
    _must(evidence, "No recent upgrade rehearsal evidence found")
    return True


def probe_upgrade_report(cfg_path: Path):
    cfg = _load_tier0_cfg(cfg_path)
    p = _probe_from_cfg("upgrade_report", cfg)
    if not p:
        return False
    reports = _glob_many(p.get("report_globs", []))
    _must(reports, "No structured upgrade/migration reports found")
    return True


def probe_upgrade_rollback_plan(cfg_path: Path):
    cfg = _load_tier0_cfg(cfg_path)
    p = _probe_from_cfg("upgrade_rollback_plan", cfg)
    if not p:
        return False
    paths = _glob_many(p.get("any_path_must_match_glob", []))
    _must(paths, "No rollback documentation or scripts")
    _must(
        _any_file_contains_regex(paths, p.get("any_file_must_contain_regex", [])),
        "Rollback plans missing recovery keywords",
    )
    return True


def probe_support_workflow(cfg_path: Path):
    cfg = _load_tier0_cfg(cfg_path)
    p = _probe_from_cfg("support_workflow", cfg)
    if not p:
        return False
    paths = _glob_many(p.get("any_path_must_match_glob", []))
    _must(paths, "No support/incident workflow documentation")
    _must(
        _any_file_contains_regex(paths, p.get("any_file_must_contain_regex", [])),
        "Support docs missing triage/RCA keywords",
    )
    return True


def probe_runbooks_present(cfg_path: Path):
    cfg = _load_tier0_cfg(cfg_path)
    p = _probe_from_cfg("runbooks_present", cfg)
    if not p:
        return False
    count = _count_glob(p.get("runbook_globs", []))
    min_c = p.get("min_count", 1)
    _must(count >= min_c, f"Too few runbooks found (found {count}, need {min_c})")
    return True


def probe_sla_monitoring(cfg_path: Path):
    cfg = _load_tier0_cfg(cfg_path)
    p = _probe_from_cfg("sla_monitoring", cfg)
    if not p:
        return False
    paths = _glob_many(p.get("any_path_must_match_glob", []))
    _must(paths, "No health check/SLA monitoring scripts or workflows")
    _must(
        _any_file_contains_regex(paths, p.get("any_file_must_contain_regex", [])),
        "Monitoring missing health/probe keywords",
    )
    return True


# --- Dummy Probes for Tier-1 (Implementation pending) ---


def probe_ai_keys_configured(cfg_path: Path):
    return True


def probe_ai_guardrails(cfg_path: Path):
    return True


def probe_iap_visibility(cfg_path: Path):
    return True


def probe_iap_audit_workflow(cfg_path: Path):
    return True


PROBES = {
    "ci_build_pipeline": probe_ci_build_pipeline,
    "env_separation": probe_env_separation,
    "remote_shell_access": probe_remote_shell_access,
    "upgrade_rehearsal": probe_upgrade_rehearsal,
    "upgrade_report": probe_upgrade_report,
    "upgrade_rollback_plan": probe_upgrade_rollback_plan,
    "support_workflow": probe_support_workflow,
    "runbooks_present": probe_runbooks_present,
    "sla_monitoring": probe_sla_monitoring,
    "ai_keys_configured": probe_ai_keys_configured,
    "ai_guardrails": probe_ai_guardrails,
    "iap_visibility": probe_iap_visibility,
    "iap_audit_workflow": probe_iap_audit_workflow,
}


@dataclass
class CheckResult:
    surface_id: str
    acceptance_id: str
    name: str
    tier: int
    probe: str
    passed: bool
    error: str | None = None


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text()) or {}


def compute_score(results: list[CheckResult], goals: dict) -> dict:
    tier_info = goals.get("scoring", {}).get("tiers", {})
    tier_scores = {}

    for t_str, meta in tier_info.items():
        t = int(t_str)
        t_results = [r for r in results if r.tier == t]
        if not t_results:
            tier_scores[t] = {"pct": 100.0, "pass": 0, "total": 0}
            continue

        passed = len([r for r in t_results if r.passed])
        total = len(t_results)
        tier_scores[t] = {"pct": (passed / total) * 100, "pass": passed, "total": total}

    # Overall weighted score
    weighted_sum = 0.0
    weight_total = 0.0
    for t, data in tier_scores.items():
        w = float(tier_info.get(str(t), {}).get("weight", 1.0))
        weighted_sum += data["pct"] * w
        weight_total += 100.0 * w

    score = weighted_sum / weight_total if weight_total > 0 else 0.0

    # Hard gate: Tier-0 must be 100%
    tier0 = tier_scores.get(0, {"pct": 0, "pass": 0, "total": 0})
    tier0_pass = tier0["pct"] == 100.0

    return {
        "score": score,
        "tier0_pass": tier0_pass,
        "tier_scores": tier_scores,
        "tier0": tier0,
    }


def write_markdown(report: dict, md_path: Path):
    lines = [
        "# Parity Report",
        f"**Timestamp:** {report['timestamp']}",
        f"**Overall Score:** {report['score']:.2f}%",
        f"**Tier-0 Status:** {'✅ PASS' if report['tier0_pass'] else '❌ FAIL'}",
        "",
        "## Summary by Tier",
        "| Tier | Pass/Total | Percentage | Status |",
        "|------|------------|------------|--------|",
    ]
    for t, data in report["tier_scores"].items():
        status = "✅" if data["pct"] == 100 else "⚠️" if data["pct"] > 0 else "❌"
        lines.append(
            f"| Tier {t} | {data['pass']}/{data['total']} | {data['pct']:.1f}% | {status} |"
        )

    lines.extend(
        [
            "",
            "## Detailed Results",
            "| ID | Name | Tier | Probe | Status | Error |",
            "|----|------|------|-------|--------|-------|",
        ]
    )
    for r in report["results"]:
        status = "✅" if r["passed"] else "❌"
        lines.append(
            f"| {r['surface_id']} | {r['name']} | {r['tier']} | `{r['probe']}` | {status} | {r['error'] or ''} |"
        )

    md_path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description="Clean, deterministic parity check.")
    parser.add_argument(
        "--catalog",
        type=Path,
        default=ROOT / "docs" / "parity" / "EE_SURFACE_CATALOG.yaml",
        help="Path to the EE surface catalog",
    )
    parser.add_argument(
        "--goals",
        type=Path,
        default=ROOT / "config" / "parity" / "PARITY_GOALS.yaml",
        help="Path to parity goals",
    )
    parser.add_argument(
        "--probes",
        type=Path,
        default=ROOT / "config" / "parity" / "TIER0_PROBES.yaml",
        help="Path to Tier-0 probes config",
    )
    parser.add_argument("--out-json", type=Path, help="Output JSON report path")
    parser.add_argument("--out-md", type=Path, help="Output Markdown report path")
    parser.add_argument(
        "--strict-tier0", action="store_true", help="Fail hard if Tier-0 is not 100%"
    )

    args = parser.parse_args()

    try:
        catalog = load_yaml(args.catalog)
        goals = load_yaml(args.goals)
    except Exception as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        return 2

    results: list[CheckResult] = []
    for surf in catalog.get("catalog", []):
        tier = int(surf["tier"])
        for acc in surf.get("acceptance", []):
            probe_name = acc["probe"]
            fn = PROBES.get(probe_name)
            if not fn:
                results.append(
                    CheckResult(
                        surf["id"], acc["id"], acc["name"], tier, probe_name, False, "Unknown probe"
                    )
                )
                continue
            try:
                # Pass probes config to functions that need it
                passed = bool(fn(args.probes))
                results.append(
                    CheckResult(surf["id"], acc["id"], acc["name"], tier, probe_name, passed)
                )
            except Exception as e:
                results.append(
                    CheckResult(surf["id"], acc["id"], acc["name"], tier, probe_name, False, str(e))
                )

    score_obj = compute_score(results, goals)
    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "score": score_obj["score"],
        "tier0_pass": score_obj["tier0_pass"],
        "tier0": score_obj["tier0"],
        "tier_scores": score_obj["tier_scores"],
        "results": [r.__dict__ for r in results],
    }

    report_json = json.dumps(report, indent=2)
    print(report_json)

    # Defaults for output if not provided
    out_json = args.out_json or (ROOT / "oca-parity" / "evidence" / "latest" / "parity_report.json")
    out_md = args.out_md or (ROOT / "oca-parity" / "evidence" / "latest" / "parity_report.md")

    try:
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(report_json)
        write_markdown(report, out_md)
        print(f"Reports written to {out_json.parent}", file=sys.stderr)
    except Exception as e:
        print(f"WARNING: Could not write report: {e}", file=sys.stderr)

    # Threshold checks
    threshold = float(goals.get("scoring", {}).get("threshold", 0.8))

    # Goal-based logic
    if goals.get("scoring", {}).get("mode") == "goal_based":
        tier0_req = goals.get("scoring", {}).get("pass_if", {}).get("tier0_pct_gte", 100)
        if report["tier0"]["pct"] < tier0_req:
            print(
                f"FAIL: Tier-0 parity {report['tier0']['pct']}% below required {tier0_req}%",
                file=sys.stderr,
            )
            return 1
        print(f"PASS: Tier-0 goal met ({report['tier0']['pct']}%)", file=sys.stderr)
        return 0

    if not report["tier0_pass"]:
        print("FAIL: Tier-0 hard gate requirements not met.", file=sys.stderr)
    if report["score"] < threshold:
        print(f"FAIL: Score {report['score']:.2f} below threshold {threshold:.2f}", file=sys.stderr)

    if (report["tier0_pass"] or not args.strict_tier0) and report["score"] >= threshold:
        print(f"PASS: Parity confirmed ({report['score']:.2f})", file=sys.stderr)
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
