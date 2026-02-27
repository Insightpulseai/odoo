#!/usr/bin/env python3
"""
check_domains_ssot.py — Domain SSOT compliance checker.

Reads ssot/domains/insightpulseai.com.yaml and scans the repo for:
  1. Prohibited domain references (e.g., insightpulseai.net)
  2. Subdomain references not listed in canonical_subdomains

Exit codes:
  0 — clean (no violations)
  1 — violations found
  2 — SSOT file missing or invalid
"""

import argparse
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

SSOT_PATH = "ssot/domains/insightpulseai.com.yaml"

# File extensions to scan
SCAN_EXTENSIONS = {
    ".md", ".yaml", ".yml", ".ts", ".tsx", ".js", ".jsx",
    ".py", ".sh", ".toml", ".json", ".tf", ".env.example"
}

# Paths to skip entirely
SKIP_DIRS = {
    ".git", "node_modules", ".claude/worktrees", "docs/99-Archive",
    "docs/XX-Archive", ".cache", "dist", "build", "__pycache__"
}


def load_ssot(repo_root: Path) -> dict:
    ssot_file = repo_root / SSOT_PATH
    if not ssot_file.exists():
        print(f"ERROR: SSOT file not found: {SSOT_PATH}", file=sys.stderr)
        sys.exit(2)
    try:
        with open(ssot_file) as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"ERROR: Failed to parse SSOT YAML: {e}", file=sys.stderr)
        sys.exit(2)


def scan_files(repo_root: Path, ssot: dict) -> list[dict]:
    violations = []
    apex = ssot.get("apex", "insightpulseai.com")
    prohibited = [p for p in ssot.get("prohibited_domains", []) if not p.startswith("*")]
    prohibited_patterns = ssot.get("prohibited_patterns", [])

    canonical_hosts = {
        s["host"] for s in ssot.get("canonical_subdomains", [])
    }

    # Build exception paths per pattern
    exception_map: dict[str, list[str]] = {}
    for pp in prohibited_patterns:
        exception_map[pp["pattern"]] = pp.get("exception_paths", [])

    for path in repo_root.rglob("*"):
        # Skip directories and non-files
        if not path.is_file():
            continue

        # Skip excluded dirs
        rel = path.relative_to(repo_root)
        parts = rel.parts
        if any(skip in parts for skip in SKIP_DIRS):
            continue

        # Only scan relevant extensions
        if path.suffix not in SCAN_EXTENSIONS and path.name not in {
            "CLAUDE.md", "Makefile", "Dockerfile"
        }:
            continue

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        rel_str = str(rel)

        # Check prohibited domain patterns
        for pp in prohibited_patterns:
            pattern = pp["pattern"]
            exceptions = exception_map.get(pattern, [])
            if any(rel_str.startswith(exc) for exc in exceptions):
                continue
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                violations.append({
                    "file": rel_str,
                    "type": "prohibited_domain",
                    "detail": f"Found '{match}' matching prohibited pattern '{pattern}'",
                    "description": pp.get("description", ""),
                })

        # Check plain prohibited domains (not already covered by patterns)
        for domain in prohibited:
            if domain in content:
                violations.append({
                    "file": rel_str,
                    "type": "prohibited_domain",
                    "detail": f"Found reference to prohibited domain: {domain}",
                })

    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description="Domain SSOT compliance checker")
    parser.add_argument(
        "--repo-root",
        default=os.getcwd(),
        help="Path to repo root (default: cwd)"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress output (exit code only)"
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    ssot = load_ssot(repo_root)

    violations = scan_files(repo_root, ssot)

    if not args.quiet:
        if violations:
            print(f"Domain SSOT violations found ({len(violations)}):")
            for v in violations:
                print(f"  [{v['type']}] {v['file']}: {v['detail']}")
        else:
            apex = ssot.get("apex", "insightpulseai.com")
            print(f"Domain SSOT check passed — all references compliant with {apex}")

    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
