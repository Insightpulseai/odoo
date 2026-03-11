#!/usr/bin/env python3
"""
check_stripe_wrapper_activation.py — Gate Stripe FDW activation on Vault readiness.

Scans supabase/migrations/*stripe_wrapper*.sql for an ACTIVE (non-commented)
CREATE SERVER or IMPORT FOREIGN SCHEMA block. If the activation block is
uncommented, all three conditions must be satisfied or the script exits non-zero:

  Condition 1: ssot/secrets/registry.yaml contains 'stripe_secret_key'
  Condition 2: ssot/runtime/prod_settings.yaml declares
               payments.stripe.supabase_wrapper.vault_secret_id = 'stripe_secret_key'
  Condition 3: ssot/runtime/vault_provisioning.yaml has
               vault.stripe_secret_key.provisioned = true

If the activation block is still fully commented → OK (exit 0).

Exit codes:
  0  activation block absent/commented, or all conditions satisfied
  1  activation block detected but one or more conditions not met
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]

MIGRATION_GLOB = "supabase/migrations/*stripe_wrapper*.sql"
PROD_SETTINGS = ROOT / "ssot" / "runtime" / "prod_settings.yaml"
VAULT_PROVISION = ROOT / "ssot" / "runtime" / "vault_provisioning.yaml"
SECRETS_REGISTRY = ROOT / "ssot" / "secrets" / "registry.yaml"

# Patterns that signal the activation block is uncommented
_ACTIVATE_RE = re.compile(
    r"^\s*create\s+server\b.*stripe_server|^\s*import\s+foreign\s+schema\b",
    re.IGNORECASE,
)


def die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def warn(msg: str) -> None:
    print(f"WARN:  {msg}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Detection: is the activation block live in any migration?
# ---------------------------------------------------------------------------

def find_migration_files() -> list[Path]:
    return list(ROOT.glob(MIGRATION_GLOB))


def activation_block_is_live(migration: Path) -> bool:
    """Return True if any non-commented line matches an activation pattern."""
    for line in migration.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("--"):
            continue
        if _ACTIVATE_RE.search(stripped):
            return True
    return False


# ---------------------------------------------------------------------------
# Condition checks
# ---------------------------------------------------------------------------

def check_secrets_registry() -> tuple[bool, str]:
    if not SECRETS_REGISTRY.exists():
        return False, f"{SECRETS_REGISTRY.relative_to(ROOT)} not found"
    data = yaml.safe_load(SECRETS_REGISTRY.read_text(encoding="utf-8")) or {}
    secrets = data.get("secrets") or []
    ids = {s.get("id") for s in secrets if isinstance(s, dict)}
    if "stripe_secret_key" not in ids:
        return False, "'stripe_secret_key' not registered in ssot/secrets/registry.yaml"
    return True, "stripe_secret_key registered in secrets registry"


def check_prod_settings_vault_ref() -> tuple[bool, str]:
    if not PROD_SETTINGS.exists():
        return False, f"{PROD_SETTINGS.relative_to(ROOT)} not found"
    ps = yaml.safe_load(PROD_SETTINGS.read_text(encoding="utf-8")) or {}
    wrapper = (
        ((ps.get("payments") or {}).get("stripe") or {}).get("supabase_wrapper") or {}
    )
    vid = wrapper.get("vault_secret_id")
    if vid != "stripe_secret_key":
        return (
            False,
            f"payments.stripe.supabase_wrapper.vault_secret_id must be 'stripe_secret_key', "
            f"got {vid!r}",
        )
    return True, "prod_settings vault_secret_id = stripe_secret_key"


def check_vault_provisioned() -> tuple[bool, str]:
    if not VAULT_PROVISION.exists():
        return (
            False,
            f"{VAULT_PROVISION.relative_to(ROOT)} not found — "
            "create it with vault.stripe_secret_key.provisioned: false",
        )
    vp = yaml.safe_load(VAULT_PROVISION.read_text(encoding="utf-8")) or {}
    entry = ((vp.get("vault") or {}).get("stripe_secret_key") or {})
    if entry.get("provisioned") is not True:
        return (
            False,
            "vault_provisioning.yaml :: vault.stripe_secret_key.provisioned is not true. "
            "Provision the Vault secret first, then flip provisioned: true.",
        )
    return True, "Vault provisioning marker = true"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    migrations = find_migration_files()
    if not migrations:
        print("OK: no stripe_wrapper migration found — nothing to gate.")
        return 0

    live_migrations: list[Path] = []
    for m in migrations:
        if activation_block_is_live(m):
            live_migrations.append(m)

    if not live_migrations:
        print("OK: activation block is commented in all stripe_wrapper migrations.")
        return 0

    # Activation block is live — enforce all three conditions
    print(
        f"DETECTED: activation block is uncommented in: "
        + ", ".join(str(m.relative_to(ROOT)) for m in live_migrations)
    )
    print("Checking activation gate conditions...\n")

    checks = [
        check_secrets_registry(),
        check_prod_settings_vault_ref(),
        check_vault_provisioned(),
    ]

    failures: list[str] = []
    for ok, msg in checks:
        symbol = "✓" if ok else "✗"
        stream = sys.stdout if ok else sys.stderr
        print(f"  {symbol} {msg}", file=stream)
        if not ok:
            failures.append(msg)

    if failures:
        print(
            f"\nERROR: {len(failures)} activation gate condition(s) not met.\n"
            "Fix all conditions or re-comment the activation block before merging.",
            file=sys.stderr,
        )
        return 1

    print("\nOK: all activation gate conditions satisfied.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
