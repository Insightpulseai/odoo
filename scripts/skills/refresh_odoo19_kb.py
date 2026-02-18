#!/usr/bin/env python3
"""
Orchestrator for SKILL: refresh-odoo19-kb
See agents/skills/refresh-odoo19-kb/SKILL.md for strict procedural definition.
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

# Paths
ROOT = Path(__file__).resolve().parents[2]
DOCS_EVIDENCE_ROOT = ROOT / "docs" / "evidence"
KB_ROOT = ROOT / "docs" / "kb" / "odoo19"
SCRIPTS_KB = ROOT / "scripts" / "kb"

# Inputs defaults
DEFAULT_UPSTREAM = "https://github.com/odoo/documentation"
DEFAULT_BRANCH = "19.0"


def _run_cmd(args: list[str], cwd: Path | None = None, env: dict | None = None) -> None:
    """Run a subprocess command, raising SystemExit on failure."""
    print(f">> Running: {' '.join(args)}", file=sys.stderr)
    try:
        subprocess.check_call(args, cwd=str(cwd) if cwd else None, env=env)
    except subprocess.CalledProcessError as e:
        print(f"!! Command failed with exit code {e.returncode}", file=sys.stderr)
        sys.exit(e.returncode)


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Skill: refresh-odoo19-kb")
    parser.add_argument("--commit", help="Optional explicit commit SHA to pin")
    parser.add_argument("--upstream-url", default=DEFAULT_UPSTREAM)
    parser.add_argument("--branch", default=DEFAULT_BRANCH)
    args = parser.parse_args()

    # --- Preconditions ---
    if not (SCRIPTS_KB / "vendor_odoo_docs.py").exists():
        sys.exit("Missing scripts/kb/vendor_odoo_docs.py")
    if not (SCRIPTS_KB / "verify_odoo_docs_pin.py").exists():
        sys.exit("Missing scripts/kb/verify_odoo_docs_pin.py")
    if not (SCRIPTS_KB / "index_odoo_docs.py").exists():
        sys.exit("Missing scripts/kb/index_odoo_docs.py")

    # --- Step 1: Create Evidence Run ---
    run_id = uuid.uuid4().hex[:8]
    today = dt.datetime.utcnow().strftime("%Y-%m-%d")
    evidence_dir = DOCS_EVIDENCE_ROOT / today / "kb" / "refresh" / run_id
    evidence_dir.mkdir(parents=True, exist_ok=True)

    print(f"Starting refresh-odoo19-kb run_id={run_id}")
    print(f"Evidence directory: {evidence_dir}")

    # Record inputs
    git_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(ROOT)).decode().strip()
    inputs = {
        "upstream_url": args.upstream_url,
        "branch": args.branch,
        "commit": args.commit,
        "timestamp_utc": dt.datetime.utcnow().isoformat() + "Z",
        "repo_head": git_head,
        "run_id": run_id,
    }
    (evidence_dir / "inputs.json").write_text(json.dumps(inputs, indent=2), encoding="utf-8")

    try:
        # --- Step 2: Vendor Upstream ---
        print("\n=== Step 2: Vendor Upstream ===")
        vendor_cmd = [
            "python3",
            str(SCRIPTS_KB / "vendor_odoo_docs.py"),
            f"--upstream-url={args.upstream_url}",
            f"--branch={args.branch}",
        ]
        if args.commit:
            vendor_cmd.append(f"--commit={args.commit}")

        _run_cmd(vendor_cmd, cwd=ROOT)

        # Check outputs
        if not (KB_ROOT / "upstream").exists():
            sys.exit("Step 2 Failed: docs/kb/odoo19/upstream/ missing")
        if not (KB_ROOT / "UPSTREAM_REV.txt").exists():
            sys.exit("Step 2 Failed: UPSTREAM_REV.txt missing")

        # --- Step 3: Verify Pin Integrity ---
        print("\n=== Step 3: Verify Pin ===")
        _run_cmd(["python3", str(SCRIPTS_KB / "verify_odoo_docs_pin.py")], cwd=ROOT)

        # --- Step 3.5: Generate Stack Docs ---
        print("\n=== Step 3.5: Generate Stack Docs ===")
        stack_gen_script = ROOT / "scripts" / "docs" / "generate_stack_docs.py"
        if stack_gen_script.exists():
            _run_cmd(["python3", str(stack_gen_script)], cwd=ROOT)
        else:
            print(
                "!! Warning: generate_stack_docs.py not found, skipping stack docs.",
                file=sys.stderr,
            )

        # --- Step 4: Index Content ---
        print("\n=== Step 4: Index Content (Upstream + Stack + Overrides) ===")
        # Force encoding for deterministic index generation
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        # Indexer now auto-detects layers based on ROOT relation
        _run_cmd(
            ["python3", str(SCRIPTS_KB / "index_odoo_docs.py"), "--fail-on-skill-coverage"],
            cwd=ROOT,
            env=env,
        )

        # Verify index artifacts exist
        index_files = [
            "manifest.json",
            "sections.json",
            "topics.json",
            "skills_coverage.json",
            "nav.json",
            "index.json",
        ]
        for f in index_files:
            p = KB_ROOT / "index" / f
            if not p.exists() or p.stat().st_size == 0:
                sys.exit(f"Step 4 Failed: Index artifact {f} missing or empty")

        # --- Step 5: Post-Index Validation ---
        print("\n=== Step 5: Validate Index ===")
        # Basic JSON validity check and ensure we strictly indexed 'upstream'
        manifest = json.loads((KB_ROOT / "index" / "manifest.json").read_text(encoding="utf-8"))
        # Sanity check: ensure at least some files were indexed
        if not manifest.get("entries"):
            sys.exit("Step 5 Failed: Manifest has no entries")

        # --- Step 6: Record Evidence ---
        print("\n=== Step 6: Record Evidence ===")
        shutil.copy2(KB_ROOT / "UPSTREAM_PIN.json", evidence_dir / "upstream_pin.json")
        shutil.copy2(KB_ROOT / "UPSTREAM_REV.txt", evidence_dir / "upstream_rev.txt")

        # Diff Summary (simple diff of UPSTREAM_REV if available? or just capture it)
        # Ideally we'd compare against previous run, but we don't have tracking here.

        index_manifest = {}
        for f in index_files:
            p = KB_ROOT / "index" / f
            index_manifest[f] = {"sha256": _sha256_file(p), "size": p.stat().st_size}
        (evidence_dir / "index_manifest.json").write_text(
            json.dumps(index_manifest, indent=2), encoding="utf-8"
        )

        # --- Step 7: Finalize ---
        print("\n=== Step 7: Finalize ===")
        status = {"status": "success", "completed_at_utc": dt.datetime.utcnow().isoformat() + "Z"}
        (evidence_dir / "final_status.json").write_text(
            json.dumps(status, indent=2), encoding="utf-8"
        )

        print(f"SUCCESS. Evidence recorded in {evidence_dir}")

    except Exception as e:
        status = {
            "status": "failed",
            "error": str(e),
            "failed_at_utc": dt.datetime.utcnow().isoformat() + "Z",
        }
        (evidence_dir / "final_status.json").write_text(
            json.dumps(status, indent=2), encoding="utf-8"
        )
        print(f"\nFAILED: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
