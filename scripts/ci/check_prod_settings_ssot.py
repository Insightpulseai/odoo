#!/usr/bin/env python3
"""
check_prod_settings_ssot.py — Validate production readiness SSOT.

Deterministic checks (no network calls):
  1. YAML parses and schema matches ssot.runtime.prod_settings.v1
  2. Required top-level sections present (email, ocr, odoo, urls, ai)
  3. Every secret_ref in email/ocr/ai exists in ssot/secrets/registry.yaml
  4. Every URL in urls.active_required exists in docs/architecture/CANONICAL_URLS.md
  5. AI fail_closed policy is true
  6. Odoo invariants have expected values declared

Exit codes:
  0 — all checks pass
  1 — validation errors (schema, structure)
  2 — prod settings file missing or invalid YAML
  3 — cross-reference failure (secrets registry, canonical URLs)
"""
from __future__ import annotations

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

PROD_SETTINGS_PATH = "ssot/runtime/prod_settings.yaml"
SECRETS_REGISTRY_PATH = "ssot/secrets/registry.yaml"
CANONICAL_URLS_PATH = "docs/architecture/CANONICAL_URLS.md"

REQUIRED_SECTIONS = {"email", "ocr", "odoo", "urls", "ai"}
REQUIRED_EMAIL_KEYS = {"status", "provider", "secrets_refs"}
REQUIRED_OCR_KEYS = {"status", "provider", "base_url", "health_endpoint"}
REQUIRED_ODOO_KEYS = {"invariants"}
REQUIRED_URL_KEYS = {"active_required"}
REQUIRED_AI_KEYS = {"policy"}

# URL pattern: extract URLs from markdown tables in CANONICAL_URLS.md
URL_PATTERN = re.compile(r"https?://[a-zA-Z0-9._\-]+\.insightpulseai\.com")


def load_yaml(repo_root: Path, rel_path: str) -> dict:
    path = repo_root / rel_path
    if not path.exists():
        print(f"ERROR: File not found: {rel_path}", file=sys.stderr)
        sys.exit(2)
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        print(f"ERROR: YAML parse error in {rel_path}: {e}", file=sys.stderr)
        sys.exit(2)


def load_canonical_urls(repo_root: Path) -> set[str]:
    """Extract all insightpulseai.com URLs from CANONICAL_URLS.md Production Services."""
    path = repo_root / CANONICAL_URLS_PATH
    if not path.exists():
        return set()

    content = path.read_text(encoding="utf-8")

    # Find the Production Services section
    prod_section = ""
    in_prod = False
    for line in content.split("\n"):
        if "## Production Services" in line:
            in_prod = True
            continue
        if in_prod and line.startswith("## "):
            # Hit next section
            break
        if in_prod:
            prod_section += line + "\n"

    return set(URL_PATTERN.findall(prod_section))


def validate_schema(data: dict) -> list[str]:
    """Validate prod settings schema structure."""
    errors = []

    schema = data.get("schema", "")
    if schema != "ssot.runtime.prod_settings.v1":
        errors.append(
            f"Invalid schema: expected 'ssot.runtime.prod_settings.v1', got '{schema}'"
        )

    for section in REQUIRED_SECTIONS:
        if section not in data:
            errors.append(f"Missing required section: '{section}'")

    # Email section
    email = data.get("email", {})
    if isinstance(email, dict):
        for key in REQUIRED_EMAIL_KEYS:
            if key not in email:
                errors.append(f"email: missing required key '{key}'")
        if email.get("status") != "required":
            errors.append(f"email.status must be 'required', got '{email.get('status')}'")

    # OCR section
    ocr = data.get("ocr", {})
    if isinstance(ocr, dict):
        for key in REQUIRED_OCR_KEYS:
            if key not in ocr:
                errors.append(f"ocr: missing required key '{key}'")
        if ocr.get("status") != "required":
            errors.append(f"ocr.status must be 'required', got '{ocr.get('status')}'")

    # Odoo section
    odoo = data.get("odoo", {})
    if isinstance(odoo, dict):
        for key in REQUIRED_ODOO_KEYS:
            if key not in odoo:
                errors.append(f"odoo: missing required key '{key}'")
        invariants = odoo.get("invariants", {})
        if isinstance(invariants, dict):
            required_invariants = {"web_base_url", "web_base_url_freeze", "proxy_mode"}
            for inv in required_invariants:
                if inv not in invariants:
                    errors.append(f"odoo.invariants: missing required invariant '{inv}'")
                elif not invariants[inv].get("expected"):
                    errors.append(f"odoo.invariants.{inv}: missing 'expected' value")

    # URLs section
    urls = data.get("urls", {})
    if isinstance(urls, dict):
        for key in REQUIRED_URL_KEYS:
            if key not in urls:
                errors.append(f"urls: missing required key '{key}'")
        active = urls.get("active_required", [])
        if not isinstance(active, list) or len(active) == 0:
            errors.append("urls.active_required must be a non-empty list")

    # AI section
    ai = data.get("ai", {})
    if isinstance(ai, dict):
        for key in REQUIRED_AI_KEYS:
            if key not in ai:
                errors.append(f"ai: missing required key '{key}'")
        policy = ai.get("policy", {})
        if isinstance(policy, dict):
            if policy.get("fail_closed") is not True:
                errors.append("ai.policy.fail_closed must be true")

    return errors


def validate_secrets_refs(data: dict, secrets_registry: dict) -> list[str]:
    """Validate that all secret_refs exist in the secrets registry."""
    errors = []
    known_secrets = set((secrets_registry.get("secrets") or {}).keys())

    # Collect all secrets_refs from all sections
    all_refs: list[tuple[str, str]] = []

    for section_name in ("email", "ocr", "ai"):
        section = data.get(section_name, {})
        if isinstance(section, dict):
            refs = section.get("secrets_refs", [])
            if isinstance(refs, list):
                for ref in refs:
                    all_refs.append((section_name, ref))

    for section_name, ref in all_refs:
        if ref not in known_secrets:
            errors.append(
                f"{section_name}.secrets_refs: '{ref}' not found in "
                f"{SECRETS_REGISTRY_PATH}"
            )

    return errors


def validate_urls(data: dict, canonical_urls: set[str]) -> list[str]:
    """Validate that all active_required URLs exist in CANONICAL_URLS.md."""
    errors = []

    urls_section = data.get("urls", {})
    if not isinstance(urls_section, dict):
        return errors

    active = urls_section.get("active_required", [])
    if not isinstance(active, list):
        return errors

    for entry in active:
        if not isinstance(entry, dict):
            continue
        url = entry.get("url", "")
        if not url:
            errors.append("urls.active_required: entry missing 'url' key")
            continue
        if url not in canonical_urls:
            errors.append(
                f"urls.active_required: '{url}' not found in "
                f"{CANONICAL_URLS_PATH} Production Services section"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Production readiness SSOT validator"
    )
    parser.add_argument("--repo-root", default=os.getcwd())
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()

    # Load prod settings
    data = load_yaml(repo_root, PROD_SETTINGS_PATH)

    # Schema validation
    errors = validate_schema(data)

    # Cross-reference: secrets registry
    xref_errors = []
    secrets_registry = load_yaml(repo_root, SECRETS_REGISTRY_PATH)
    xref_errors.extend(validate_secrets_refs(data, secrets_registry))

    # Cross-reference: canonical URLs
    canonical_urls = load_canonical_urls(repo_root)
    xref_errors.extend(validate_urls(data, canonical_urls))

    if not args.quiet:
        if errors:
            print(f"Prod settings schema validation failed ({len(errors)} errors):")
            for err in errors:
                print(f"  {err}")
        if xref_errors:
            print(
                f"Prod settings cross-reference failed ({len(xref_errors)} errors):"
            )
            for err in xref_errors:
                print(f"  {err}")
        if not errors and not xref_errors:
            url_count = len(data.get("urls", {}).get("active_required", []))
            secret_count = sum(
                len(data.get(s, {}).get("secrets_refs", []))
                for s in ("email", "ocr", "ai")
            )
            print(
                f"Prod settings SSOT validation passed — "
                f"{url_count} required URLs, {secret_count} secret refs verified"
            )

    if errors:
        return 1
    if xref_errors:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
