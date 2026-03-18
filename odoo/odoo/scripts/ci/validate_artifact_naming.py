#!/usr/bin/env python3
"""CI validation: enforce unified SSOT artifact naming convention.

Scans all ssot/ directories for .yaml/.json files matching the managed
artifact pattern and validates filename structure, header fields, and
cross-repo basename uniqueness.

Exit 0 if all checks pass, 1 if any fail.
"""
import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

try:
    import yaml
except ImportError:
    print("FATAL: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

FILENAME_RE = re.compile(
    r"^([a-z0-9_]+)__([a-z0-9_]+)__([a-z0-9_]+)__v([0-9]+)"
    r"\.(schema|registry|mapping|manifest|policy|contract|entity|catalog|inventory|config)"
    r"\.(yaml|json)$"
)

ALLOWED_ARTIFACT_TYPES = frozenset(
    ["schema", "registry", "mapping", "manifest", "policy",
     "contract", "entity", "catalog", "inventory", "config"]
)

YAML_REQUIRED_FIELDS = ("version", "namespace", "artifact_type",
                        "repo_key", "domain", "subject")

JSON_SCHEMA_REQUIRED_FIELDS = ("$schema", "$id")


def detect_repo_root() -> Path:
    """Auto-detect git repo root, fallback to cwd."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return Path.cwd()


def find_ssot_files(root: Path) -> list[Path]:
    """Recursively find .yaml/.json files under any ssot/ directory."""
    files = []
    for ssot_dir in root.rglob("ssot"):
        if not ssot_dir.is_dir():
            continue
        # Skip .git, .next, node_modules, archive
        parts = ssot_dir.parts
        if any(p in (".git", ".next", "node_modules", "archive") for p in parts):
            continue
        for ext in ("*.yaml", "*.json"):
            for f in ssot_dir.rglob(ext):
                f_parts = f.parts
                if any(p in (".git", ".next", "node_modules", "archive") for p in f_parts):
                    continue
                files.append(f)
    return sorted(files)


def is_managed_artifact(filename: str) -> bool:
    """Return True if filename matches the managed artifact pattern."""
    return FILENAME_RE.match(filename) is not None


def parse_filename(filename: str) -> dict | None:
    """Extract tokens from a conforming filename."""
    m = FILENAME_RE.match(filename)
    if not m:
        return None
    return {
        "repo_key": m.group(1),
        "domain": m.group(2),
        "subject": m.group(3),
        "version": int(m.group(4)),
        "artifact_type": m.group(5),
        "extension": m.group(6),
    }


def validate_file(filepath: Path) -> list[str]:
    """Validate a single managed artifact file. Returns list of errors."""
    errors: list[str] = []
    tokens = parse_filename(filepath.name)
    if tokens is None:
        errors.append(f"Filename does not match required pattern: {filepath.name}")
        return errors

    if tokens["artifact_type"] not in ALLOWED_ARTIFACT_TYPES:
        errors.append(f"artifact_type '{tokens['artifact_type']}' not in allowed list")

    # Parse and validate header
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        errors.append(f"Cannot read file: {e}")
        return errors

    if tokens["extension"] == "json":
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON: {e}")
            return errors
        # JSON schema files need $schema and $id
        if tokens["artifact_type"] == "schema":
            for field in JSON_SCHEMA_REQUIRED_FIELDS:
                if field not in data:
                    errors.append(f"Missing required JSON schema field: {field}")
        else:
            # Non-schema JSON: check YAML-style header fields if present
            for field in YAML_REQUIRED_FIELDS:
                if field not in data:
                    errors.append(f"Missing required header field: {field}")
            if not errors:
                errors.extend(_check_congruence(tokens, data))

    elif tokens["extension"] == "yaml":
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            errors.append(f"Invalid YAML: {e}")
            return errors
        if not isinstance(data, dict):
            errors.append("YAML root is not a mapping")
            return errors
        for field in YAML_REQUIRED_FIELDS:
            if field not in data:
                errors.append(f"Missing required header field: {field}")
        if not errors:
            errors.extend(_check_congruence(tokens, data))

    return errors


def _check_congruence(tokens: dict, data: dict) -> list[str]:
    """Check that filename tokens match header values."""
    errors: list[str] = []
    if str(data.get("version")) != str(tokens["version"]):
        errors.append(
            f"Version mismatch: filename v{tokens['version']} "
            f"vs header version={data.get('version')}"
        )
    if data.get("repo_key") != tokens["repo_key"]:
        errors.append(
            f"repo_key mismatch: filename '{tokens['repo_key']}' "
            f"vs header '{data.get('repo_key')}'"
        )
    if data.get("domain") != tokens["domain"]:
        errors.append(
            f"domain mismatch: filename '{tokens['domain']}' "
            f"vs header '{data.get('domain')}'"
        )
    if data.get("subject") != tokens["subject"]:
        errors.append(
            f"subject mismatch: filename '{tokens['subject']}' "
            f"vs header '{data.get('subject')}'"
        )
    if data.get("artifact_type") != tokens["artifact_type"]:
        errors.append(
            f"artifact_type mismatch: filename '{tokens['artifact_type']}' "
            f"vs header '{data.get('artifact_type')}'"
        )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate SSOT artifact naming conventions."
    )
    parser.add_argument(
        "--path", type=Path, default=None,
        help="Search root (default: auto-detect git repo root)",
    )
    args = parser.parse_args()

    root = args.path if args.path else detect_repo_root()
    if not root.is_dir():
        print(f"FATAL: path does not exist: {root}", file=sys.stderr)
        return 1

    all_files = find_ssot_files(root)
    managed = [f for f in all_files if is_managed_artifact(f.name)]
    skipped = [f for f in all_files if not is_managed_artifact(f.name)]

    results: dict[Path, list[str]] = {}
    pass_count = 0
    fail_count = 0

    # Per-file validation
    for filepath in managed:
        errs = validate_file(filepath)
        results[filepath] = errs
        if errs:
            fail_count += 1
        else:
            pass_count += 1

    # Duplicate basename check
    basename_map: dict[str, list[Path]] = defaultdict(list)
    for filepath in managed:
        basename_map[filepath.name].append(filepath)
    for basename, paths in basename_map.items():
        if len(paths) > 1:
            for p in paths:
                results.setdefault(p, []).append(
                    f"Duplicate basename '{basename}' found at: "
                    + ", ".join(str(x) for x in paths if x != p)
                )
                if not any(e for e in results[p] if "Duplicate" not in e):
                    # Only count as new failure if it was previously passing
                    pass

    # Recount after duplicate check
    fail_count = sum(1 for errs in results.values() if errs)
    pass_count = len(results) - fail_count

    # Report
    print(f"=== SSOT Artifact Naming Validation ===")
    print(f"Search root: {root}")
    print(f"Total files scanned: {len(all_files)}")
    print(f"Managed artifacts: {len(managed)}")
    print(f"Skipped (non-managed): {len(skipped)}")
    print()

    for filepath, errs in sorted(results.items()):
        rel = filepath.relative_to(root) if filepath.is_relative_to(root) else filepath
        if errs:
            print(f"FAIL  {rel}")
            for e in errs:
                print(f"      - {e}")
        else:
            print(f"PASS  {rel}")

    print()
    print(f"--- SUMMARY ---")
    print(f"passed={pass_count} failed={fail_count} skipped={len(skipped)} total={len(all_files)}")

    if fail_count > 0:
        print(f"RESULT: FAIL ({fail_count} artifact(s) have violations)")
        return 1
    else:
        print(f"RESULT: PASS (all {pass_count} managed artifacts conform)")
        return 0


if __name__ == "__main__":
    sys.exit(main())
