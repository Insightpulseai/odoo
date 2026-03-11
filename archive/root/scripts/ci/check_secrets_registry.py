#!/usr/bin/env python3
"""
check_secrets_registry.py — Secrets Registry SSOT compliance checker.

Reads ssot/secrets/registry.yaml and:
  1. Validates schema: every v2_entry must have purpose, consumers, status.severity_if_missing.
  2. Scans .github/workflows/ and apps/ for secret references:
       - ${{ secrets.NAME }}
       - process.env.NAME  (where NAME is ALL_CAPS with optional underscores)
       - Deno.env.get("NAME")
  3. Warns if referenced secrets are not in the v2 registry (soft-fail).
  4. Hard-fails (exit 1) on schema violations only.

Exit codes:
  0 — schema clean (warnings may have been emitted for unregistered references)
  1 — schema violations found
  2 — registry file missing or invalid YAML
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

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "ssot" / "secrets" / "registry.yaml"
SCAN_DIRS = [
    REPO_ROOT / ".github" / "workflows",
    REPO_ROOT / "apps",
]

# Patterns for secret references
GH_ACTIONS_PATTERN = re.compile(r"\$\{\{\s*secrets\.([A-Z0-9_]+)\s*\}\}")
NODE_ENV_PATTERN = re.compile(r"process\.env\.([A-Z][A-Z0-9_]{3,})")
DENO_ENV_PATTERN = re.compile(r'Deno\.env\.get\(["\']([A-Z][A-Z0-9_]{3,})["\']\)')

# File extensions to scan
SCAN_EXTENSIONS = {".yml", ".yaml", ".ts", ".tsx", ".js", ".mjs", ".sh"}

# Keys we expect to be ALL_CAPS that are NOT secrets (common false positives)
ALLOWLISTED_REFS = {
    "NODE_ENV",
    "NEXT_PUBLIC_",  # prefix check handled separately
    "CI",
    "HOME",
    "PATH",
    "USER",
    "SHELL",
    "TERM",
    "LANG",
    "TZ",
}

# ---------------------------------------------------------------------------
# Load registry
# ---------------------------------------------------------------------------

def load_registry(path: Path) -> dict:
    if not path.exists():
        print(f"ERROR: Registry not found at {path}", file=sys.stderr)
        sys.exit(2)
    try:
        with path.open() as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            print(f"ERROR: Registry is not a valid YAML mapping: {path}", file=sys.stderr)
            sys.exit(2)
        return data
    except yaml.YAMLError as e:
        print(f"ERROR: Invalid YAML in registry: {e}", file=sys.stderr)
        sys.exit(2)


# ---------------------------------------------------------------------------
# Extract v2 entry keys
# ---------------------------------------------------------------------------

def extract_v2_keys(registry: dict) -> set[str]:
    """Return set of all secret keys from v2_entries section."""
    v2 = registry.get("v2_entries", {})
    if not isinstance(v2, dict):
        return set()
    return set(v2.keys())


def extract_legacy_keys(registry: dict) -> set[str]:
    """Return set of all secret keys from legacy (flat) secrets section."""
    secrets = registry.get("secrets", {})
    if not isinstance(secrets, dict):
        return set()
    return set(secrets.keys())


# ---------------------------------------------------------------------------
# Validate v2 entry schema
# ---------------------------------------------------------------------------

REQUIRED_V2_FIELDS = ["purpose", "consumers", "status"]

def validate_v2_entries(registry: dict) -> list[str]:
    """Return list of schema violation messages."""
    violations = []
    v2 = registry.get("v2_entries", {})
    if not isinstance(v2, dict):
        violations.append("v2_entries is missing or not a mapping")
        return violations

    for key, entry in v2.items():
        if not isinstance(entry, dict):
            violations.append(f"v2_entries.{key}: entry is not a mapping")
            continue

        # Check required fields
        for field in REQUIRED_V2_FIELDS:
            if field not in entry:
                violations.append(
                    f"v2_entries.{key}: missing required field '{field}'"
                )

        # Validate status.severity_if_missing
        status = entry.get("status", {})
        if isinstance(status, dict):
            sev = status.get("severity_if_missing")
            if sev not in ("critical", "high", "medium", "low"):
                violations.append(
                    f"v2_entries.{key}.status.severity_if_missing: invalid value '{sev}' "
                    f"(must be critical|high|medium|low)"
                )
        else:
            violations.append(
                f"v2_entries.{key}.status: must be a mapping with severity_if_missing"
            )

        # Validate consumers is a list
        consumers = entry.get("consumers", [])
        if not isinstance(consumers, list) or len(consumers) == 0:
            violations.append(
                f"v2_entries.{key}.consumers: must be a non-empty list"
            )
        else:
            for i, consumer in enumerate(consumers):
                if not isinstance(consumer, dict):
                    violations.append(
                        f"v2_entries.{key}.consumers[{i}]: must be a mapping"
                    )
                    continue
                if "kind" not in consumer:
                    violations.append(
                        f"v2_entries.{key}.consumers[{i}]: missing 'kind'"
                    )
                if "name" not in consumer:
                    violations.append(
                        f"v2_entries.{key}.consumers[{i}]: missing 'name'"
                    )

    return violations


# ---------------------------------------------------------------------------
# Scan files for secret references
# ---------------------------------------------------------------------------

def scan_for_secret_refs(dirs: list[Path]) -> dict[str, list[str]]:
    """
    Scan directories for env/secret references.
    Returns dict: secret_name -> list of "file:line" locations.
    """
    refs: dict[str, list[str]] = {}

    for scan_dir in dirs:
        if not scan_dir.exists():
            continue
        for fpath in scan_dir.rglob("*"):
            if fpath.suffix not in SCAN_EXTENSIONS:
                continue
            if any(part.startswith(".") for part in fpath.parts):
                # skip hidden dirs like .git, .next, .turbo
                continue
            try:
                text = fpath.read_text(errors="ignore")
            except OSError:
                continue

            for line_no, line in enumerate(text.splitlines(), 1):
                location = f"{fpath.relative_to(REPO_ROOT)}:{line_no}"
                for pattern in (GH_ACTIONS_PATTERN, NODE_ENV_PATTERN, DENO_ENV_PATTERN):
                    for match in pattern.finditer(line):
                        name = match.group(1)
                        # Skip obvious non-secrets
                        if name in ALLOWLISTED_REFS:
                            continue
                        if name.startswith("NEXT_PUBLIC_") and not name.endswith("KEY"):
                            continue
                        refs.setdefault(name, []).append(location)

    return refs


# ---------------------------------------------------------------------------
# Map referenced names to registry keys (best-effort)
# ---------------------------------------------------------------------------

def map_ref_to_registry_key(ref_name: str, v2_keys: set[str], legacy_keys: set[str]) -> str | None:
    """Try to find which registry key corresponds to a raw env var name."""
    # Direct match (case-insensitive snake_case lookup)
    lower = ref_name.lower()
    if lower in v2_keys:
        return lower
    if lower in legacy_keys:
        return f"(legacy){lower}"

    # Common normalisations: strip leading NEXT_PUBLIC_
    if lower.startswith("next_public_"):
        stripped = lower[len("next_public_"):]
        if stripped in v2_keys:
            return stripped
        if stripped in legacy_keys:
            return f"(legacy){stripped}"

    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Validate secrets registry SSOT")
    parser.add_argument("--warn-unregistered", action="store_true",
                        help="Emit warnings for unregistered secret refs (default: always warn)")
    parser.add_argument("--no-scan", action="store_true",
                        help="Skip scanning source files for secret references")
    args = parser.parse_args()

    print(f"[check_secrets_registry] Registry: {REGISTRY_PATH.relative_to(REPO_ROOT)}")

    registry = load_registry(REGISTRY_PATH)
    v2_keys = extract_v2_keys(registry)
    legacy_keys = extract_legacy_keys(registry)

    print(f"[check_secrets_registry] v2 entries: {len(v2_keys)}, legacy entries: {len(legacy_keys)}")

    # --- Schema validation (hard fail) ---
    violations = validate_v2_entries(registry)
    if violations:
        print("\n[FAIL] Schema violations found in v2_entries:", file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        return 1

    print(f"[check_secrets_registry] Schema OK — {len(v2_keys)} v2 entries validated")

    # --- Source file scan (soft warn) ---
    if not args.no_scan:
        print(f"[check_secrets_registry] Scanning {len(SCAN_DIRS)} directories for secret references...")
        refs = scan_for_secret_refs(SCAN_DIRS)

        unregistered = []
        for ref_name, locations in refs.items():
            key = map_ref_to_registry_key(ref_name, v2_keys, legacy_keys)
            if key is None:
                # Only warn for things that look like secrets (not generic env vars)
                if len(ref_name) > 5 and not ref_name.endswith("_URL"):
                    unregistered.append((ref_name, locations))

        if unregistered:
            print(
                f"\n[WARN] {len(unregistered)} secret-like reference(s) not found in registry "
                f"(informational only — not a hard failure):"
            )
            for ref_name, locations in sorted(unregistered):
                sample = locations[:3]
                print(f"  {ref_name}: {', '.join(sample)}"
                      + (f" (+{len(locations)-3} more)" if len(locations) > 3 else ""))
            print("  Suggestion: add these to ssot/secrets/registry.yaml#v2_entries if they are secrets.")
        else:
            print("[check_secrets_registry] All detected secret refs are in registry (or allowlisted)")

    print("\n[check_secrets_registry] PASS — no schema violations")
    return 0


if __name__ == "__main__":
    sys.exit(main())
