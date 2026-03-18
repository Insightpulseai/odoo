#!/usr/bin/env python3
"""
check_dns_dual_writer.py
────────────────────────
Scan a repo (other than Insightpulseai/odoo) for Cloudflare Terraform resources
that write to the insightpulseai.com zone. Fails if any are found.

This script is invoked:
  - In Insightpulseai/odoo CI when PRs touch infra/dns/**  (self-validation)
  - In other repos via their own CI pointing at their checkout

Exit codes:
  0   Clean — no dual-writer resources found
  1   Violation — zone-write resources detected; see output for paths
  2   Usage error

Usage:
  python3 check_dns_dual_writer.py [--repo-root PATH] [--allow-odoo-repo]

  --repo-root PATH     Root of the repo to scan (default: cwd)
  --allow-odoo-repo    Skip the check if GITHUB_REPOSITORY is Insightpulseai/odoo
                       (used when this script is run inside the authoritative repo)
"""

import argparse
import os
import re
import sys
from pathlib import Path

# ── Constants ──────────────────────────────────────────────────────────────────

AUTHORITATIVE_REPO = "Insightpulseai/odoo"
TARGET_ZONE = "insightpulseai.com"

# Patterns that indicate a zone-write Terraform resource for the target zone
# We match resource declarations, not data sources.
WRITE_RESOURCE_PATTERNS = [
    # resource "cloudflare_record" "..." { zone_id = ... }
    r'resource\s+"cloudflare_record"',
    # resource "cloudflare_zone" "..."
    r'resource\s+"cloudflare_zone"',
    # resource "cloudflare_zone_settings_override" "..."
    r'resource\s+"cloudflare_zone_settings_override"',
    # resource "cloudflare_page_rule" "..."
    r'resource\s+"cloudflare_page_rule"',
]

# Allowed: data sources (read-only references)
# resource-level read patterns that we explicitly do NOT flag
ALLOWED_PATTERNS = [
    r'data\s+"cloudflare_zones"',
    r'data\s+"cloudflare_zone"',
    r'data\s+"cloudflare_record"',
]

# File extensions to scan
TF_EXTENSIONS = {".tf", ".tf.json"}

# Directories to skip entirely
SKIP_DIRS = {
    ".git", ".github", "node_modules", "__pycache__",
    ".terraform", ".cache", "vendor",
    # Worktree roots — these are copies of the repo at other branches.
    # We only scan the live working tree, not worktree clones.
    ".worktrees", ".claude",
}


# ── Scanner ────────────────────────────────────────────────────────────────────

def is_zone_write_resource(content: str, filepath: Path) -> list[tuple[int, str]]:
    """
    Return list of (line_number, line) for lines containing a write resource
    declaration. We do a simple grep — a false-positive review is acceptable;
    the CI comment will explain.
    """
    violations = []
    lines = content.splitlines()
    for lineno, line in enumerate(lines, start=1):
        stripped = line.strip()
        # Skip comments
        if stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("*"):
            continue
        for pattern in WRITE_RESOURCE_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                # Double-check it's not an allowed data source on same line
                is_allowed = any(
                    re.search(a, line, re.IGNORECASE) for a in ALLOWED_PATTERNS
                )
                if not is_allowed:
                    violations.append((lineno, line.rstrip()))
                break
    return violations


def scan_repo(repo_root: Path) -> dict[Path, list[tuple[int, str]]]:
    """
    Walk repo_root recursively and scan all .tf/.tf.json files for write resources.
    Returns {filepath: [(lineno, line), ...]} for files with violations.
    """
    findings: dict[Path, list[tuple[int, str]]] = {}

    for dirpath, dirnames, filenames in os.walk(repo_root):
        # Prune skip dirs in-place
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

        for fname in filenames:
            fpath = Path(dirpath) / fname
            if fpath.suffix not in TF_EXTENSIONS:
                continue
            try:
                content = fpath.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            hits = is_zone_write_resource(content, fpath)
            if hits:
                findings[fpath] = hits

    return findings


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo-root", default=os.getcwd(), help="Root of repo to scan")
    parser.add_argument("--allow-odoo-repo", action="store_true",
                        help="Silently pass if GITHUB_REPOSITORY is the authoritative repo")
    args = parser.parse_args()

    current_repo = os.environ.get("GITHUB_REPOSITORY", "")
    repo_root = Path(args.repo_root).resolve()

    # Detect authoritative repo: either via GITHUB_REPOSITORY env var (CI)
    # or by the presence of the canonical SSOT file (local dev).
    ssot_sentinel = repo_root / "infra" / "dns" / "subdomain-registry.yaml"
    is_authoritative = (current_repo == AUTHORITATIVE_REPO) or ssot_sentinel.exists()

    if args.allow_odoo_repo and is_authoritative:
        print(f"✅ Authoritative repo ({AUTHORITATIVE_REPO}) — dual-writer check skipped.")
        return 0

    print(f"🔍 Scanning {repo_root} for Cloudflare zone-write resources targeting {TARGET_ZONE}…")

    findings = scan_repo(repo_root)

    if not findings:
        print(f"✅ No dual-writer violations found — this repo does not manage the {TARGET_ZONE} zone.")
        return 0

    # Report violations
    print(f"\n❌ DUAL-WRITER VIOLATION: {len(findings)} file(s) contain Cloudflare write resources.")
    print(f"   Only Insightpulseai/odoo may apply changes to the {TARGET_ZONE} Cloudflare zone.")
    print(f"   See: docs/architecture/DNS_AUTHORITY_CONTRACT.md\n")

    for fpath, hits in sorted(findings.items()):
        rel = fpath.relative_to(repo_root) if fpath.is_relative_to(repo_root) else fpath
        print(f"  FILE: {rel}")
        for lineno, line in hits:
            print(f"    L{lineno}: {line}")

    print("\n  Remediation options:")
    print("  A) Remove the resource from this repo and open a PR to Insightpulseai/odoo")
    print("     to add the record via infra/dns/subdomain-registry.yaml.")
    print("  B) Convert to a data source if you only need to read the record.")
    print("  C) If this is the authoritative repo, run with --allow-odoo-repo flag.")

    return 1


if __name__ == "__main__":
    sys.exit(main())
