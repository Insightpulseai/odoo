#!/usr/bin/env python3
"""
Coding Agent Eval Harness (SWE-bench-like replay)

Executes a suite of recorded cases:
  - create a temporary git worktree
  - apply a patch (git apply)
  - run a test command
  - emit evidence pack (logs + patch + metadata)

This is intentionally deterministic and CI-friendly: it does not invoke an LLM.

Exit 0 = all cases pass (or empty suite), exit 2 = at least one case failed.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. pip install pyyaml")
    sys.exit(2)


REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass
class SuiteDefaults:
    timeout_seconds: int
    evidence_root: Path
    allowlisted_test_command_regex: List[re.Pattern]


def _run(cmd: List[str], cwd: Optional[Path] = None, timeout: Optional[int] = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=timeout,
        check=False,
    )


def _git(cmd: List[str], cwd: Optional[Path] = None, timeout: Optional[int] = None) -> subprocess.CompletedProcess:
    return _run(["git", *cmd], cwd=cwd, timeout=timeout)


def load_suite(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Suite not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Suite YAML must be a mapping")
    return data


def compile_defaults(data: Dict[str, Any]) -> SuiteDefaults:
    defaults = data.get("defaults", {}) or {}
    timeout = int(defaults.get("timeout_seconds", 900))
    evidence_root = REPO_ROOT / str(defaults.get("evidence_root", "docs/evidence/coding_agent_eval"))
    allowlist = defaults.get("allowlisted_test_command_regex", []) or []
    patterns = [re.compile(p) for p in allowlist]
    return SuiteDefaults(timeout_seconds=timeout, evidence_root=evidence_root, allowlisted_test_command_regex=patterns)


def ensure_git_clean() -> None:
    cp = _git(["status", "--porcelain"], cwd=REPO_ROOT)
    if cp.returncode != 0:
        raise RuntimeError(f"git status failed:\n{cp.stdout}")
    if cp.stdout.strip():
        raise RuntimeError("Working tree is not clean. Commit/stash changes before running eval.")


def allowlisted(cmd: str, patterns: List[re.Pattern]) -> bool:
    return any(p.search(cmd.strip()) for p in patterns)


def write_evidence(evidence_dir: Path, filename: str, content: str) -> None:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / filename).write_text(content, encoding="utf-8")


def run_case(
    case: Dict[str, Any],
    defaults: SuiteDefaults,
    suite_path: Path,
    run_id: str,
    base_ref: str,
) -> bool:
    cid = str(case.get("id", "")).strip()
    if not cid:
        raise ValueError("Case missing required field: id")
    desc = str(case.get("description", "")).strip()
    patch_rel = case.get("patch")
    test_cmd = str(case.get("test_command", "")).strip()
    timeout = int(case.get("timeout_seconds", defaults.timeout_seconds))

    if test_cmd and not allowlisted(test_cmd, defaults.allowlisted_test_command_regex):
        raise ValueError(f"Case {cid}: test_command not allowlisted: {test_cmd}")

    ts = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    evidence_dir = defaults.evidence_root / run_id / cid / ts
    evidence_dir.mkdir(parents=True, exist_ok=True)

    # Record metadata early.
    meta = {
        "case_id": cid,
        "description": desc,
        "suite": str(suite_path),
        "base_ref": base_ref,
        "timestamp_utc": ts,
        "patch": patch_rel,
        "test_command": test_cmd,
        "timeout_seconds": timeout,
    }
    write_evidence(evidence_dir, "meta.json", json.dumps(meta, indent=2))

    # Create isolated worktree.
    with tempfile.TemporaryDirectory(prefix=f"coding-agent-eval-{cid}-") as tmpdir:
        wt = Path(tmpdir) / "worktree"
        add = _git(["worktree", "add", "--detach", str(wt), base_ref], cwd=REPO_ROOT)
        write_evidence(evidence_dir, "git_worktree_add.log", add.stdout)
        if add.returncode != 0:
            write_evidence(evidence_dir, "result.txt", "FAIL: git worktree add")
            return False

        try:
            # Apply patch if present.
            if patch_rel:
                patch_path = REPO_ROOT / str(patch_rel)
                if not patch_path.exists():
                    write_evidence(evidence_dir, "result.txt", f"FAIL: patch not found: {patch_path}")
                    return False
                # Copy patch into evidence pack
                shutil.copy2(patch_path, evidence_dir / "patch.diff")
                ap = _git(["apply", "--whitespace=nowarn", str(patch_path)], cwd=wt)
                write_evidence(evidence_dir, "git_apply.log", ap.stdout)
                if ap.returncode != 0:
                    write_evidence(evidence_dir, "result.txt", "FAIL: git apply")
                    return False

            # Run tests (or smoke) in the worktree.
            if test_cmd:
                # Run via shell to respect compound commands, but keep allowlist tight.
                cp = subprocess.run(
                    test_cmd,
                    cwd=str(wt),
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    timeout=timeout,
                )
                write_evidence(evidence_dir, "tests.log", cp.stdout)
                if cp.returncode != 0:
                    write_evidence(evidence_dir, "result.txt", f"FAIL: tests rc={cp.returncode}")
                    return False
            else:
                write_evidence(evidence_dir, "tests.log", "SKIP: no test_command provided")

            # Capture final diff for traceability.
            d = _git(["diff"], cwd=wt)
            write_evidence(evidence_dir, "final.diff", d.stdout)

            write_evidence(evidence_dir, "result.txt", "PASS")
            return True

        finally:
            rm = _git(["worktree", "remove", "--force", str(wt)], cwd=REPO_ROOT)
            write_evidence(evidence_dir, "git_worktree_remove.log", rm.stdout)


def main() -> int:
    ap = argparse.ArgumentParser(description="Coding Agent Eval Harness (SWE-bench-like replay)")
    ap.add_argument("--suite", default="ssot/evals/coding_agent_eval_suite.yaml", help="Path to suite YAML")
    ap.add_argument("--base-ref", default="HEAD", help="Git ref to evaluate from (default: HEAD)")
    ap.add_argument("--run-id", default="", help="Run id for evidence folder (default: timestamp)")
    args = ap.parse_args()

    suite_path = (REPO_ROOT / args.suite).resolve()
    data = load_suite(suite_path)
    defaults = compile_defaults(data)

    run_id = args.run_id.strip() or time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    base_ref = args.base_ref.strip()

    ensure_git_clean()

    cases = data.get("cases", []) or []
    if not isinstance(cases, list):
        raise ValueError("Suite 'cases' must be a list")

    if not cases:
        # Suite exists but no cases yet — treat as PASS to avoid blocking early adoption.
        defaults.evidence_root.mkdir(parents=True, exist_ok=True)
        (defaults.evidence_root / run_id).mkdir(parents=True, exist_ok=True)
        (defaults.evidence_root / run_id / "summary.json").write_text(
            json.dumps({"run_id": run_id, "base_ref": base_ref, "cases": 0, "status": "PASS_EMPTY_SUITE"}, indent=2),
            encoding="utf-8",
        )
        print("PASS (empty suite): no cases defined.")
        return 0

    results: Dict[str, bool] = {}
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("Each case must be a mapping")
        ok = run_case(case, defaults, suite_path, run_id, base_ref)
        results[str(case.get("id", "<missing>"))] = ok

    summary = {
        "run_id": run_id,
        "base_ref": base_ref,
        "passed": [k for k, v in results.items() if v],
        "failed": [k for k, v in results.items() if not v],
        "status": "PASS" if all(results.values()) else "FAIL",
        "evidence_root": str(defaults.evidence_root / run_id),
    }
    (defaults.evidence_root / run_id).mkdir(parents=True, exist_ok=True)
    (defaults.evidence_root / run_id / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    if summary["status"] == "FAIL":
        print(json.dumps(summary, indent=2))
        return 2

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
