#!/usr/bin/env python3
"""
scripts/ci/check_n8n_workflows_ssot.py

Static contract validator for automations/n8n/.

Checks (no network, no runtime):
  1. Workflow directory structure exists
  2. No hardcoded secrets in workflow JSON files
  3. No direct Odoo PostgreSQL access (Postgres node pointing to SoR host)
  4. Integration register exists (ssot/integrations/n8n.yaml) and has required fields
  5. Integration is registered in ssot/integrations/_index.yaml
  6. CREDENTIALS.md declaration file exists

Exit 0 = all checks pass
Exit 1 = one or more checks failed (details printed to stderr)
"""

import sys
import json
import re
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
N8N_DIR = ROOT / "automations/n8n"
WORKFLOWS_DIR = N8N_DIR / "workflows"
CREDENTIALS_DOC = N8N_DIR / "CREDENTIALS.md"
SSOT_INDEX = ROOT / "ssot/integrations/_index.yaml"
N8N_YAML = ROOT / "ssot/integrations/n8n.yaml"

ERRORS: list[str] = []

# Secret patterns that must never appear as literal values in workflow JSON.
# Each pattern matches what should only come from $credentials.* or $env.*
SECRET_PATTERNS = [
    # Common API key formats
    r'"value"\s*:\s*"(sk_live_[A-Za-z0-9]{20,})',    # Stripe live key
    r'"value"\s*:\s*"(sk_test_[A-Za-z0-9]{20,})',    # Stripe test key
    r'"value"\s*:\s*"(xoxb-[0-9]+-[0-9]+-[A-Za-z0-9]+)',  # Slack bot token
    r'"value"\s*:\s*"(xoxp-[0-9]+-[0-9]+-[A-Za-z0-9]+)',  # Slack user token
    r'"value"\s*:\s*"(ghp_[A-Za-z0-9]{36,})',         # GitHub PAT
    r'"value"\s*:\s*"(gho_[A-Za-z0-9]{36,})',         # GitHub OAuth token
    r'"value"\s*:\s*"(ghs_[A-Za-z0-9]{36,})',         # GitHub app install token
    r'"value"\s*:\s*"(sbp_[A-Za-z0-9]{40,})',         # Supabase PAT
    r'"value"\s*:\s*"(eyJ[A-Za-z0-9_-]{40,})',        # JWT (Supabase anon/service key)
    r'"password"\s*:\s*"(?!.*\$(?:credentials|env))(.{10,})"', # Literal password field
    r'"apiKey"\s*:\s*"(?!.*\$(?:credentials|env))(.{10,})"',   # Literal apiKey field
]

# Postgres node type identifiers in n8n workflow JSON
POSTGRES_NODE_TYPES = [
    "n8n-nodes-base.postgres",
    "n8n-nodes-base.postgresTrigger",
]

# Known Odoo production hosts that should never appear in Postgres nodes
ODOO_DB_HOSTS = [
    "178.128.112.214",  # odoo-production droplet (SoR)
    "localhost",        # could be Odoo DB if running on-droplet
    "127.0.0.1",
]


def fail(msg: str) -> None:
    ERRORS.append(msg)
    print(f"  FAIL: {msg}", file=sys.stderr)


def ok(msg: str) -> None:
    print(f"  ok:   {msg}")


def warn(msg: str) -> None:
    print(f"  warn: {msg}")


# ── 1. Workflow directory structure ──────────────────────────────────────────

def check_directory_structure() -> None:
    print("\n[1] Workflow directory structure")
    if WORKFLOWS_DIR.exists():
        json_count = len(list(WORKFLOWS_DIR.rglob("*.json")))
        ok(f"automations/n8n/workflows/ exists ({json_count} workflow files)")
    else:
        fail("Missing: automations/n8n/workflows/ — workflow-as-code directory required")

    if N8N_DIR.exists():
        ok("automations/n8n/ root exists")
    else:
        fail("Missing: automations/n8n/ — n8n automation directory required")


# ── 2. No hardcoded secrets ───────────────────────────────────────────────────

def check_no_hardcoded_secrets() -> None:
    print("\n[2] No hardcoded secrets in workflow JSON")
    if not WORKFLOWS_DIR.exists():
        warn("Skipping: workflows directory missing (flagged in check 1)")
        return

    clean = 0
    for json_file in WORKFLOWS_DIR.rglob("*.json"):
        content = json_file.read_text(errors="replace")
        file_issues = []
        for pattern in SECRET_PATTERNS:
            matches = re.findall(pattern, content)
            if matches:
                # Show only first 8 chars of each match to avoid leaking values
                redacted = [f"{m[:8]}..." for m in matches[:3]]
                file_issues.append(f"pattern match: {redacted}")

        rel = json_file.relative_to(ROOT)
        if file_issues:
            for issue in file_issues:
                fail(f"{rel}: potential hardcoded secret ({issue}) — use $credentials.* or $env.*")
        else:
            clean += 1

    if clean > 0:
        ok(f"{clean} workflow file(s) passed secret scan")


# ── 3. No direct Odoo PostgreSQL access ──────────────────────────────────────

def check_no_direct_odoo_db() -> None:
    print("\n[3] No direct Odoo PostgreSQL access (SoR isolation)")
    if not WORKFLOWS_DIR.exists():
        warn("Skipping: workflows directory missing (flagged in check 1)")
        return

    violations = 0
    for json_file in WORKFLOWS_DIR.rglob("*.json"):
        try:
            data = json.loads(json_file.read_text(errors="replace"))
        except json.JSONDecodeError:
            warn(f"{json_file.relative_to(ROOT)}: not valid JSON — skipping")
            continue

        nodes = data.get("nodes", [])
        for node in nodes:
            node_type = node.get("type", "")
            if node_type not in POSTGRES_NODE_TYPES:
                continue

            # Check if this Postgres node targets an Odoo host
            params = node.get("parameters", {})
            host = params.get("host", "")
            database = params.get("database", "")
            credentials_str = json.dumps(node.get("credentials", {}))

            is_odoo_host = any(odoo_h in str(host) for odoo_h in ODOO_DB_HOSTS)
            is_odoo_db = database in ("odoo", "odoo_dev")

            rel = json_file.relative_to(ROOT)
            node_name = node.get("name", "unnamed")

            if is_odoo_host or is_odoo_db:
                fail(
                    f"{rel}: node '{node_name}' (type={node_type}) targets Odoo DB "
                    f"(host={host!r}, db={database!r}) — "
                    "use Odoo XML-RPC/JSON-RPC API node instead of direct Postgres access"
                )
                violations += 1
            elif node_type in POSTGRES_NODE_TYPES:
                # Postgres node exists but doesn't point to Odoo — that's fine
                ok(f"{rel}: Postgres node '{node_name}' does not target Odoo DB (OK for Supabase/analytics)")

    if violations == 0:
        ok("No direct Odoo PostgreSQL access found in workflow files")


# ── 4. Integration register complete ─────────────────────────────────────────

def check_n8n_yaml() -> None:
    print("\n[4] n8n integration register")
    if not N8N_YAML.exists():
        fail(f"Missing: {N8N_YAML.relative_to(ROOT)}")
        return
    ok(f"{N8N_YAML.relative_to(ROOT)} exists")

    try:
        data = yaml.safe_load(N8N_YAML.read_text())
    except yaml.YAMLError as exc:
        fail(f"YAML parse error in n8n.yaml: {exc}")
        return

    required_fields = ["version", "schema", "name", "status", "provider", "components", "boundary_rules", "risk_flags"]
    for field in required_fields:
        if field in data:
            ok(f"  field present: {field}")
        else:
            fail(f"n8n.yaml missing required field: {field}")

    # Schema must be ssot.integrations.v1
    schema = data.get("schema", "")
    if schema == "ssot.integrations.v1":
        ok(f"  schema: {schema}")
    else:
        fail(f"n8n.yaml schema must be 'ssot.integrations.v1', got '{schema}'")


# ── 5. Registered in _index.yaml ─────────────────────────────────────────────

def check_index_registration() -> None:
    print("\n[5] Integration index registration")
    if not SSOT_INDEX.exists():
        fail(f"Missing: {SSOT_INDEX.relative_to(ROOT)}")
        return
    ok(f"{SSOT_INDEX.relative_to(ROOT)} exists")

    try:
        data = yaml.safe_load(SSOT_INDEX.read_text())
    except yaml.YAMLError as exc:
        fail(f"YAML parse error in _index.yaml: {exc}")
        return

    ids = [entry.get("id") for entry in data.get("integrations", [])]
    if "n8n_automation" in ids:
        ok("  n8n_automation registered in _index.yaml")
    else:
        fail("n8n_automation NOT found in ssot/integrations/_index.yaml — add it")


# ── 6. CREDENTIALS.md declaration exists ─────────────────────────────────────

def check_credentials_doc() -> None:
    print("\n[6] CREDENTIALS.md declaration")
    if CREDENTIALS_DOC.exists():
        ok(f"{CREDENTIALS_DOC.relative_to(ROOT)} exists")
    else:
        fail(
            f"Missing: {CREDENTIALS_DOC.relative_to(ROOT)} — "
            "credential names must be declared; create automations/n8n/CREDENTIALS.md"
        )


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== n8n Workflows SSOT Validator ===")
    print(f"Root: {ROOT}")

    check_directory_structure()
    check_no_hardcoded_secrets()
    check_no_direct_odoo_db()
    check_n8n_yaml()
    check_index_registration()
    check_credentials_doc()

    print()
    if ERRORS:
        print(f"RESULT: FAIL ({len(ERRORS)} error(s))", file=sys.stderr)
        sys.exit(1)
    else:
        print("RESULT: PASS — all n8n workflow SSOT invariants satisfied")
        sys.exit(0)
