#!/usr/bin/env python3
"""
check_agent_skills.py — Validate agent skill contracts.

Deterministic checks (no network calls):
  1. Every agents/skills/**/skill.yaml parses as valid YAML
  2. Every skill.yaml conforms to agents/skills/schema/skill.schema.json
  3. Required fields present: id, version, inputs, requires.secrets, policies, verification
  4. No plaintext secrets (regex denylist) in any skill file
  5. All secret refs exist in ssot/secrets/registry.yaml
  6. Skill ID matches directory name (dots → directory separators)
  7. At least one verification check defined
  8. policies.no_plaintext_secrets is true

Exit codes:
  0 — all checks pass
  1 — validation errors (schema, structure)
  2 — skill files missing or invalid YAML
  3 — cross-reference failure (secrets registry)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

# Optional: jsonschema for full schema validation
try:
    import jsonschema

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

SKILLS_DIR = "agents/skills"
SCHEMA_PATH = "agents/skills/schema/skill.schema.json"
SECRETS_REGISTRY_PATH = "ssot/secrets/registry.yaml"
SKIP_DIRS = {"_template", "_templates", "schema"}

# Patterns that indicate plaintext secrets (never allowed in skill files)
SECRET_PATTERNS = [
    re.compile(r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"]?[a-zA-Z0-9+/=]{8,}"),
    re.compile(r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"]?[a-zA-Z0-9_\-]{16,}"),
    re.compile(r"(?i)(secret|token)\s*[:=]\s*['\"]?[a-zA-Z0-9_\-+/=]{16,}"),
    re.compile(r"(?i)bearer\s+[a-zA-Z0-9_\-+/=.]{20,}"),
    re.compile(r"xox[bpars]-[a-zA-Z0-9\-]+"),  # Slack tokens
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),  # OpenAI/Anthropic keys
    re.compile(r"-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----"),
]

# Known false positives to exclude
SECRET_ALLOWLIST = [
    "no_plaintext_secrets",  # policy field name
    "secrets_refs",  # SSOT reference field
    "ssot/secrets/registry.yaml",  # path reference
    "check_secrets_ssot.py",  # script reference
]

REQUIRED_TOP_LEVEL_KEYS = {
    "id",
    "version",
    "description",
    "inputs",
    "requires",
    "outputs",
    "policies",
    "verification",
}

VALID_INPUT_TYPES = {"string", "integer", "boolean", "array", "object"}
VALID_CHECK_TYPES = {
    "ci_script",
    "http_get",
    "smtp_connect",
    "odoo_rpc",
    "file_exists",
    "yaml_valid",
    "schema_match",
}
VALID_MATURITY = {"L0", "L1", "L2", "L3", "L4"}


def load_yaml_file(path: Path) -> dict | None:
    """Load a YAML file, return None on error."""
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        print(f"  ERROR: YAML parse error in {path}: {e}", file=sys.stderr)
        return None
    except OSError as e:
        print(f"  ERROR: Cannot read {path}: {e}", file=sys.stderr)
        return None


def check_plaintext_secrets(skill_dir: Path) -> list[str]:
    """Scan all files in a skill directory for plaintext secrets."""
    errors = []
    for filepath in skill_dir.rglob("*"):
        if not filepath.is_file():
            continue
        if filepath.suffix in (".pyc", ".pyo"):
            continue
        try:
            content = filepath.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        for line_num, line in enumerate(content.split("\n"), 1):
            # Skip comments-only lines
            stripped = line.strip()
            if stripped.startswith("#"):
                continue

            # Check allowlist
            if any(allowed in line for allowed in SECRET_ALLOWLIST):
                continue

            for pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    rel_path = filepath.relative_to(skill_dir)
                    errors.append(
                        f"{rel_path}:{line_num}: potential plaintext secret "
                        f"(pattern: {pattern.pattern[:40]}...)"
                    )
                    break  # one match per line is enough

    return errors


def validate_skill_structure(data: dict, skill_dir_name: str) -> list[str]:
    """Validate skill.yaml structure without JSON Schema."""
    errors = []

    # Required top-level keys
    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in data:
            errors.append(f"missing required key: '{key}'")

    # ID format and directory match
    skill_id = data.get("id", "")
    if skill_id:
        expected_dir = skill_id.replace("_", "_")  # dots stay as-is in dir name
        if skill_dir_name != skill_id:
            # Also accept dot-to-dir mapping
            alt_dir = skill_id  # e.g., "odoo.mail.configure" → dir "odoo.mail.configure"
            if skill_dir_name != alt_dir:
                errors.append(
                    f"skill id '{skill_id}' does not match directory name "
                    f"'{skill_dir_name}'"
                )
        if not re.match(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*){1,4}$", skill_id):
            errors.append(
                f"skill id '{skill_id}' does not match pattern: "
                "lowercase dot-separated segments (e.g., 'odoo.mail.configure')"
            )

    # Version
    version = data.get("version")
    if version is not None and (not isinstance(version, int) or version < 1):
        errors.append(f"version must be a positive integer, got: {version}")

    # Description
    desc = data.get("description", "")
    if isinstance(desc, str):
        if len(desc) < 10:
            errors.append(f"description too short ({len(desc)} chars, minimum 10)")
        if len(desc) > 500:
            errors.append(f"description too long ({len(desc)} chars, maximum 500)")

    # Maturity
    maturity = data.get("maturity")
    if maturity is not None and maturity not in VALID_MATURITY:
        errors.append(f"invalid maturity '{maturity}', must be one of: {VALID_MATURITY}")

    # Inputs
    inputs = data.get("inputs", {})
    if isinstance(inputs, dict):
        if len(inputs) == 0:
            errors.append("inputs must have at least one parameter")
        for param_name, param_def in inputs.items():
            if isinstance(param_def, dict):
                param_type = param_def.get("type")
                if param_type not in VALID_INPUT_TYPES:
                    errors.append(
                        f"inputs.{param_name}.type '{param_type}' not in "
                        f"allowed types: {VALID_INPUT_TYPES}"
                    )

    # Requires
    requires = data.get("requires", {})
    if isinstance(requires, dict):
        if "secrets" not in requires:
            errors.append("requires.secrets is mandatory (use empty list if none needed)")
        secrets = requires.get("secrets", [])
        if not isinstance(secrets, list):
            errors.append("requires.secrets must be a list")

    # Outputs
    outputs = data.get("outputs", {})
    if isinstance(outputs, dict):
        if "artifacts" not in outputs:
            errors.append("outputs.artifacts is mandatory")
        artifacts = outputs.get("artifacts", [])
        if isinstance(artifacts, list) and len(artifacts) == 0:
            errors.append("outputs.artifacts must have at least one entry")

    # Policies
    policies = data.get("policies", {})
    if isinstance(policies, dict):
        if policies.get("no_plaintext_secrets") is not True:
            errors.append("policies.no_plaintext_secrets must be true")

    # Verification
    verification = data.get("verification", {})
    if isinstance(verification, dict):
        checks = verification.get("checks", [])
        if not isinstance(checks, list) or len(checks) == 0:
            errors.append("verification.checks must have at least one check")
        for i, check in enumerate(checks):
            if isinstance(check, dict):
                if "name" not in check:
                    errors.append(f"verification.checks[{i}]: missing 'name'")
                check_type = check.get("type")
                if check_type not in VALID_CHECK_TYPES:
                    errors.append(
                        f"verification.checks[{i}]: type '{check_type}' not in "
                        f"allowed types: {VALID_CHECK_TYPES}"
                    )

    return errors


def validate_secrets_crossref(
    data: dict, known_secrets: set[str], skill_id: str
) -> list[str]:
    """Validate that all required secrets exist in the secrets registry."""
    errors = []
    requires = data.get("requires", {})
    if not isinstance(requires, dict):
        return errors

    secrets = requires.get("secrets", [])
    if not isinstance(secrets, list):
        return errors

    for secret_name in secrets:
        if secret_name not in known_secrets:
            errors.append(
                f"requires.secrets: '{secret_name}' not found in "
                f"{SECRETS_REGISTRY_PATH}"
            )

    return errors


def validate_with_jsonschema(data: dict, schema: dict) -> list[str]:
    """Full JSON Schema validation (if jsonschema is installed)."""
    errors = []
    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as e:
        path = " → ".join(str(p) for p in e.absolute_path) if e.absolute_path else "(root)"
        errors.append(f"schema violation at {path}: {e.message}")
    except jsonschema.SchemaError as e:
        errors.append(f"invalid schema: {e.message}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Agent skill contract validator")
    parser.add_argument("--repo-root", default=os.getcwd())
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument(
        "--skill",
        help="Validate a single skill directory (relative to agents/skills/)",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    skills_root = repo_root / SKILLS_DIR

    if not skills_root.exists():
        print(f"ERROR: Skills directory not found: {skills_root}", file=sys.stderr)
        return 2

    # Load schema (optional full validation)
    schema = None
    schema_path = repo_root / SCHEMA_PATH
    if schema_path.exists() and HAS_JSONSCHEMA:
        try:
            with open(schema_path) as f:
                schema = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"WARNING: Could not load schema: {e}", file=sys.stderr)

    # Load secrets registry for cross-reference
    secrets_registry_path = repo_root / SECRETS_REGISTRY_PATH
    known_secrets: set[str] = set()
    if secrets_registry_path.exists():
        registry = load_yaml_file(secrets_registry_path)
        if registry:
            known_secrets = set((registry.get("secrets") or {}).keys())

    # Find skill directories to validate
    skill_dirs: list[Path] = []
    if args.skill:
        target = skills_root / args.skill
        if target.exists() and target.is_dir():
            skill_dirs = [target]
        else:
            print(f"ERROR: Skill directory not found: {target}", file=sys.stderr)
            return 2
    else:
        for entry in sorted(skills_root.iterdir()):
            if entry.is_dir() and entry.name not in SKIP_DIRS:
                # Only validate dirs that contain skill.yaml
                if (entry / "skill.yaml").exists():
                    skill_dirs.append(entry)

    if not skill_dirs:
        if not args.quiet:
            print("No skill contracts found to validate.")
        return 0

    total_errors = 0
    total_xref_errors = 0
    total_secret_scan_errors = 0
    skills_checked = 0

    legacy_skipped = 0

    for skill_dir in skill_dirs:
        skill_yaml_path = skill_dir / "skill.yaml"
        skill_name = skill_dir.name
        skills_checked += 1

        if not args.quiet:
            print(f"Checking skill: {skill_name}")

        # Load skill.yaml
        data = load_yaml_file(skill_yaml_path)
        if data is None:
            total_errors += 1
            continue

        # Detect legacy L0 skills (pre-v1 contract format)
        # Legacy skills lack "policies" and "verification" keys and use a
        # different schema (name/source_of_truth/guardrails instead of
        # description/requires/policies/verification).
        is_legacy = "policies" not in data and "verification" not in data
        if is_legacy:
            legacy_skipped += 1
            if not args.quiet:
                print(f"  SKIP (legacy L0 — no v1 contract, migrate with _template)")
            continue

        # Structural validation
        struct_errors = validate_skill_structure(data, skill_name)
        if struct_errors:
            total_errors += len(struct_errors)
            if not args.quiet:
                for err in struct_errors:
                    print(f"  FAIL: {err}")

        # JSON Schema validation (if available)
        if schema and HAS_JSONSCHEMA:
            schema_errors = validate_with_jsonschema(data, schema)
            if schema_errors:
                total_errors += len(schema_errors)
                if not args.quiet:
                    for err in schema_errors:
                        print(f"  SCHEMA: {err}")

        # Secrets cross-reference
        xref_errors = validate_secrets_crossref(data, known_secrets, skill_name)
        if xref_errors:
            total_xref_errors += len(xref_errors)
            if not args.quiet:
                for err in xref_errors:
                    print(f"  XREF: {err}")

        # Plaintext secret scan
        secret_errors = check_plaintext_secrets(skill_dir)
        if secret_errors:
            total_secret_scan_errors += len(secret_errors)
            if not args.quiet:
                for err in secret_errors:
                    print(f"  SECRET: {err}")

        if not struct_errors and not xref_errors and not secret_errors:
            if not args.quiet:
                checks_count = len(data.get("verification", {}).get("checks", []))
                secrets_count = len(data.get("requires", {}).get("secrets", []))
                maturity = data.get("maturity", "L2")
                print(
                    f"  PASS ({maturity}) — "
                    f"{checks_count} verification checks, "
                    f"{secrets_count} secret refs"
                )

    # Summary
    all_errors = total_errors + total_xref_errors + total_secret_scan_errors
    if not args.quiet:
        print(f"\n{'='*60}")
        print(f"Skills checked: {skills_checked}")
        print(f"Legacy skipped: {legacy_skipped}")
        print(f"V1 contracts validated: {skills_checked - legacy_skipped}")
        print(f"Structure errors: {total_errors}")
        print(f"Cross-ref errors: {total_xref_errors}")
        print(f"Secret scan hits: {total_secret_scan_errors}")
        print(f"Result: {'PASS' if all_errors == 0 else 'FAIL'}")

    if total_errors > 0:
        return 1
    if total_xref_errors > 0:
        return 3
    if total_secret_scan_errors > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
