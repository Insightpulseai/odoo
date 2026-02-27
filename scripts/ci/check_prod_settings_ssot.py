#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
PROD_SETTINGS = ROOT / "ssot/runtime/prod_settings.yaml"
SECRETS_REG = ROOT / "ssot/secrets/registry.yaml"
CANON_URLS = ROOT / "docs/architecture/CANONICAL_URLS.md"


def die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def load_yaml(p: Path) -> dict:
    if not p.exists():
        die(f"Missing required file: {p}")
    return yaml.safe_load(p.read_text()) or {}


def main() -> int:
    ps = load_yaml(PROD_SETTINGS)
    if ps.get("version") != 1:
        die("prod_settings.yaml must have version: 1")
    if ps.get("type") != "ssot.runtime.prod_settings":
        die("prod_settings.yaml must have type: ssot.runtime.prod_settings")
    if ps.get("environment") != "prod":
        die("prod_settings.yaml must set environment: prod")
    inv = (((ps.get("odoo") or {}).get("invariants")) or {})
    required_invariants = ["web_base_url", "web_base_url_freeze", "proxy_mode"]
    missing = [k for k in required_invariants if k not in inv]
    if missing:
        die(f"Missing odoo.invariants keys: {missing}")
    secrets = load_yaml(SECRETS_REG)
    secret_ids = set((secrets.get("secrets") or {}).keys()) if isinstance(secrets.get("secrets"), dict) else set()
    referenced: set[str] = set()

    def collect(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "secret" and isinstance(v, str):
                    referenced.add(v)
                elif k == "secrets" and isinstance(v, dict):
                    for _, sv in v.items():
                        if isinstance(sv, str):
                            referenced.add(sv)
                else:
                    collect(v)
        elif isinstance(obj, list):
            for i in obj:
                collect(i)

    collect(ps)
    missing_secrets = sorted([s for s in referenced if s not in secret_ids])
    if missing_secrets:
        die("Referenced secrets missing from ssot/secrets/registry.yaml: " + ", ".join(missing_secrets), code=2)
    canon_txt = CANON_URLS.read_text() if CANON_URLS.exists() else ""
    active_required = (((ps.get("urls") or {}).get("active_required")) or [])
    absent_urls = [u for u in active_required if u not in canon_txt]
    if absent_urls:
        die("URLs in ssot/runtime/prod_settings.yaml not found in docs/architecture/CANONICAL_URLS.md: " + ", ".join(absent_urls), code=3)
    ocr_health = ((((ps.get("ocr") or {}).get("endpoint")) or {}).get("health_path"))
    if isinstance(ocr_health, str) and not ocr_health.startswith("/"):
        die("ocr.endpoint.health_path must start with '/'", code=4)

    # Rule 5: Stripe payments block — validate when present and enabled
    stripe = ((ps.get("payments") or {}).get("stripe")) or {}
    if stripe and stripe.get("enabled"):
        mode = stripe.get("mode")
        if mode not in ("test", "live"):
            die(f"payments.stripe.mode must be 'test' or 'live', got {mode!r}", code=5)
        # Prod must use live mode (test keys must never reach production)
        if ps.get("environment") == "prod" and mode != "live":
            die(
                f"payments.stripe.mode must be 'live' in prod environment (got {mode!r}). "
                f"Provision sk_live_... in Supabase Vault and set mode: live.",
                code=5,
            )
        # Validate secret refs exist in registry
        stripe_secrets = (stripe.get("secrets") or {})
        for field in ("secret_key", "webhook_signing_secret"):
            sid = stripe_secrets.get(field)
            if not sid:
                die(f"payments.stripe.secrets.{field} is required when stripe is enabled", code=5)
            if sid not in secret_ids:
                die(
                    f"payments.stripe.secrets.{field} references '{sid}' which is absent "
                    f"from ssot/secrets/registry.yaml",
                    code=2,
                )
        # Validate optional publishable key ref if present
        pub_ref = ((stripe.get("public") or {}).get("publishable_key_ref"))
        if pub_ref and pub_ref not in secret_ids:
            die(
                f"payments.stripe.public.publishable_key_ref references '{pub_ref}' which is "
                f"absent from ssot/secrets/registry.yaml",
                code=2,
            )
        # Validate webhook contract when enabled
        webhook = stripe.get("webhook") or {}
        if webhook.get("enabled"):
            ep = webhook.get("endpoint_path")
            if not ep:
                die("payments.stripe.webhook.endpoint_path is required when webhook.enabled", code=5)
            if not ep.startswith("/"):
                die(f"payments.stripe.webhook.endpoint_path must start with '/', got {ep!r}", code=5)
            events = webhook.get("allowed_events")
            if not events or not isinstance(events, list) or len(events) == 0:
                die("payments.stripe.webhook.allowed_events must be a non-empty list", code=5)

    print("OK: prod settings SSOT is valid and secrets/URLs are consistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
