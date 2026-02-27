#!/usr/bin/env python3
"""
check_contract_versions.py — Contract Version Drift Gate

Verifies that "Contract version: X.Y.Z" lines in the three runbook/arch docs
match the authoritative code/manifest artifact versions. Fails the PR if any
version line has drifted.

Authoritative sources (code/manifest) are always the single source of truth.
Docs must match; if they don't, bump the doc — never the code.

Checks:
  1. docs/architecture/ODOO_SH_EQUIVALENT.md
       → must match scripts/odoo_neutralize.py  __version__
  2. docs/runbooks/SECRETS_SSOT.md
       → must match scripts/check_no_plaintext_secrets.py  CONTRACT_VERSION
  3. docs/runbooks/ODOO19_GO_LIVE_CHECKLIST.md
       → must match ssot/go_live/odoo19_checklist.manifest.yaml  version

Exit codes:
  0 — all versions aligned
  1 — version mismatch (drift detected)
  2 — parse error (version not found in one or more files)
"""

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml required — pip install pyyaml", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


# --------------------------------------------------------------------------- #
# Extractors
# --------------------------------------------------------------------------- #

def _read(rel_path: str) -> str:
    p = REPO_ROOT / rel_path
    if not p.exists():
        raise FileNotFoundError(f"File not found: {rel_path}")
    return p.read_text(encoding="utf-8")


def extract_doc_version(doc_path: str) -> str:
    """Extract **Contract version: X.Y.Z** from a Markdown doc header."""
    content = _read(doc_path)
    m = re.search(
        r"\*\*Contract version:\s*([0-9]+\.[0-9]+(?:\.[0-9]+)?)\*\*",
        content,
    )
    if not m:
        raise ValueError(
            f"No '**Contract version: X.Y.Z**' line found in {doc_path}\n"
            f"  Expected format: **Contract version: 1.1.0** (must match ...)"
        )
    return m.group(1)


def extract_py_constant(py_path: str, attr: str) -> str:
    """Extract attr = 'X.Y.Z' from a Python file (top-level constant)."""
    content = _read(py_path)
    m = re.search(
        rf'^{re.escape(attr)}\s*=\s*["\']([^"\']+)["\']',
        content,
        re.MULTILINE,
    )
    if not m:
        raise ValueError(
            f"No top-level `{attr} = '...'` found in {py_path}"
        )
    return m.group(1)


def extract_yaml_version(yaml_path: str) -> str:
    """Extract top-level version: field from a YAML file (string or numeric)."""
    content = _read(yaml_path)
    data = yaml.safe_load(content)
    v = data.get("version")
    if v is None:
        raise ValueError(
            f"No top-level `version:` key in {yaml_path}"
        )
    return str(v)


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

CHECKS = [
    # (label, doc_path, authoritative_description, extractor_fn, *extractor_args)
    (
        "neutralization",
        "docs/architecture/ODOO_SH_EQUIVALENT.md",
        "scripts/odoo_neutralize.py __version__",
        extract_py_constant,
        "scripts/odoo_neutralize.py",
        "__version__",
    ),
    (
        "secrets-ssot",
        "docs/runbooks/SECRETS_SSOT.md",
        "scripts/check_no_plaintext_secrets.py CONTRACT_VERSION",
        extract_py_constant,
        "scripts/check_no_plaintext_secrets.py",
        "CONTRACT_VERSION",
    ),
    (
        "go-live-manifest",
        "docs/runbooks/ODOO19_GO_LIVE_CHECKLIST.md",
        "ssot/go_live/odoo19_checklist.manifest.yaml version",
        extract_yaml_version,
        "ssot/go_live/odoo19_checklist.manifest.yaml",
    ),
]


def main() -> int:
    results = []
    parse_errors = []

    for entry in CHECKS:
        label = entry[0]
        doc_path = entry[1]
        auth_desc = entry[2]
        extractor = entry[3]
        extractor_args = entry[4:]

        try:
            doc_v = extract_doc_version(doc_path)
        except (ValueError, FileNotFoundError) as e:
            parse_errors.append(f"[{label}] doc parse: {e}")
            continue

        try:
            auth_v = extractor(*extractor_args)
        except (ValueError, FileNotFoundError) as e:
            parse_errors.append(f"[{label}] source parse: {e}")
            continue

        results.append((label, doc_path, doc_v, auth_desc, auth_v))

    if parse_errors:
        print("PARSE ERRORS — cannot verify contract versions:", file=sys.stderr)
        for err in parse_errors:
            print(f"  {err}", file=sys.stderr)
        return 2

    mismatches = [r for r in results if r[2] != r[4]]

    if mismatches:
        print("CONTRACT VERSION DRIFT DETECTED", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        for label, doc_path, doc_v, auth_desc, auth_v in mismatches:
            print(f"\n  [{label}]", file=sys.stderr)
            print(f"  doc  {doc_path}", file=sys.stderr)
            print(f"       Contract version: {doc_v}", file=sys.stderr)
            print(f"  src  {auth_desc}", file=sys.stderr)
            print(f"       version: {auth_v}", file=sys.stderr)
            print(f"  fix  Update the doc header to: **Contract version: {auth_v}**",
                  file=sys.stderr)
        print(file=sys.stderr)
        return 1

    # All aligned
    for label, doc_path, doc_v, auth_desc, auth_v in results:
        print(f"  OK  [{label}]  doc={doc_v}  src={auth_v}  ({doc_path})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
