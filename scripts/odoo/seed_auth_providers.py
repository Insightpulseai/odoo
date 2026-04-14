#!/usr/bin/env python3
"""Seed Odoo auth.oauth.provider records from SSOT — infra-side config, no custom module.

Replaces the deprecated `ipai_auth_oidc` module. Providers are driven entirely by
`ssot/identity/` YAML files and injected via XML-RPC at post-deploy time.

Doctrine (CLAUDE.md §"Odoo extension and customization doctrine"):
- CE 18 `auth_oauth` provides the runtime
- Providers are `auth.oauth.provider` config records — not code
- Secrets live in Azure Key Vault; client IDs live in SSOT
- Memory: feedback_no_custom_default.md

Usage:
    export ODOO_URL=https://erp.insightpulseai.com
    export ODOO_DB=odoo
    export ODOO_ADMIN_USER=admin
    export ODOO_ADMIN_PASSWORD=<from-kv>
    python3 scripts/odoo/seed_auth_providers.py

    # Dry-run
    python3 scripts/odoo/seed_auth_providers.py --dry-run
"""

from __future__ import annotations

import argparse
import os
import sys
import xmlrpc.client
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. pip install pyyaml", file=sys.stderr)
    sys.exit(2)


SSOT_IDENTITY_DIR = Path(__file__).resolve().parents[2] / "ssot" / "identity"


# Static fallback providers (Keycloak, Google) — Microsoft comes from SSOT YAML.
# Entra client_id is SSOT-driven; these are reference-only endpoints.
STATIC_PROVIDERS = [
    {
        "xmlrpc_xml_id": "auth_provider_keycloak",
        "name": "InsightPulse AI SSO (Keycloak)",
        "enabled": False,  # flip on after realm is provisioned
        "client_id": "ipai-odoo",
        "auth_endpoint": "https://auth.insightpulseai.com/realms/ipai/protocol/openid-connect/auth",
        "validation_endpoint": "https://auth.insightpulseai.com/realms/ipai/protocol/openid-connect/userinfo",
        "scope": "openid email profile",
        "css_class": "fa fa-fw fa-lock",
        "body": "Sign in with InsightPulse AI",
        "sequence": 10,
    },
    {
        "xmlrpc_xml_id": "auth_provider_google_oidc",
        "name": "Google (OIDC)",
        "enabled": False,  # flip on when Google OAuth credentials are in KV
        "client_id": "PLACEHOLDER_SET_VIA_ENV",
        "auth_endpoint": "https://accounts.google.com/o/oauth2/v2/auth",
        "validation_endpoint": "https://openidconnect.googleapis.com/v1/userinfo",
        "scope": "openid email profile",
        "css_class": "fa fa-fw fa-google",
        "body": "Sign in with Google",
        "sequence": 20,
    },
]


def load_microsoft_provider_from_ssot() -> dict:
    """Pull Microsoft/Entra provider config from ssot/identity/odoo-azure-oauth.yaml."""
    path = SSOT_IDENTITY_DIR / "odoo-azure-oauth.yaml"
    if not path.exists():
        print(f"WARN: SSOT missing at {path}; skipping Microsoft provider seed")
        return {}

    with path.open() as f:
        ssot = yaml.safe_load(f)

    prov = ssot["provider"]
    tenant = prov["tenant_id"]
    auth_ep = prov["authority"].replace("{tenant_id}", tenant)
    return {
        "xmlrpc_xml_id": "auth_provider_microsoft_entra",
        "name": prov["name"],
        "enabled": True,
        "client_id": prov["client_id"],
        "auth_endpoint": auth_ep,
        "validation_endpoint": prov["validation_endpoint"],
        "scope": " ".join(prov["scopes"]),
        "css_class": "fa fa-fw fa-windows",
        "body": prov["display_label"],
        "sequence": 1,  # primary — appears first on login
    }


def upsert_provider(
    models_proxy,
    db: str,
    uid: int,
    password: str,
    provider: dict,
    dry_run: bool = False,
) -> None:
    """Create or update an auth.oauth.provider by matching on name."""
    values = {k: v for k, v in provider.items() if k != "xmlrpc_xml_id"}

    existing_ids = models_proxy.execute_kw(
        db,
        uid,
        password,
        "auth.oauth.provider",
        "search",
        [[["name", "=", provider["name"]]]],
    )

    if existing_ids:
        print(f"  UPDATE  {provider['name']} (id={existing_ids[0]})")
        if not dry_run:
            models_proxy.execute_kw(
                db,
                uid,
                password,
                "auth.oauth.provider",
                "write",
                [existing_ids, values],
            )
    else:
        print(f"  CREATE  {provider['name']}")
        if not dry_run:
            new_id = models_proxy.execute_kw(
                db,
                uid,
                password,
                "auth.oauth.provider",
                "create",
                [values],
            )
            print(f"           -> id={new_id}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="show plan, no writes")
    parser.add_argument(
        "--odoo-url",
        default=os.environ.get("ODOO_URL", "http://localhost:8069"),
        help="Odoo base URL",
    )
    parser.add_argument("--db", default=os.environ.get("ODOO_DB", "odoo_dev"))
    parser.add_argument("--user", default=os.environ.get("ODOO_ADMIN_USER", "admin"))
    parser.add_argument("--password", default=os.environ.get("ODOO_ADMIN_PASSWORD"))
    args = parser.parse_args()

    if not args.password and not args.dry_run:
        print(
            "ERROR: ODOO_ADMIN_PASSWORD env var is required (or pull from "
            "kv-ipai-dev-sea secret 'odoo-admin-password')",
            file=sys.stderr,
        )
        return 2

    providers = list(STATIC_PROVIDERS)
    ms = load_microsoft_provider_from_ssot()
    if ms:
        providers.append(ms)

    print(
        f"Seeding {len(providers)} providers to {args.odoo_url} "
        f"(db={args.db}, dry_run={args.dry_run})"
    )

    if args.dry_run:
        for p in providers:
            print(f"  PLAN  {p['name']:<40}  enabled={p['enabled']}  "
                  f"scope={p['scope']}")
        return 0

    # Authenticate via Odoo XML-RPC
    common = xmlrpc.client.ServerProxy(f"{args.odoo_url}/xmlrpc/2/common")
    uid = common.authenticate(args.db, args.user, args.password, {})
    if not uid:
        print(
            f"ERROR: authentication failed for {args.user}@{args.odoo_url}/{args.db}",
            file=sys.stderr,
        )
        return 3

    models = xmlrpc.client.ServerProxy(f"{args.odoo_url}/xmlrpc/2/object")

    for p in providers:
        upsert_provider(models, args.db, uid, args.password, p, dry_run=False)

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
