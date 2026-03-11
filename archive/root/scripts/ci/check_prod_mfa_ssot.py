#!/usr/bin/env python3
"""
check_prod_mfa_ssot.py — MFA policy SSOT gate with optional live runtime probe.

Modes:
  --mode schema   (default) — validate SSOT structure only; no network calls.
  --mode live     — schema checks PLUS Supabase Management API probe to verify
                    TOTP is actually enabled in the project.
                    Requires env vars:
                      SUPABASE_PROJECT_REF   (e.g. spdtwktxdalcfigzeqrz)
                      SUPABASE_MANAGEMENT_TOKEN  (sbp_... PAT)

Rules (schema mode):
  1. auth.mfa.provider must be "supabase" (never "odoo").
  2. auth.mfa.odoo_totp.enabled must be false.
  3. auth.identity_sor must be "supabase" (MFA provider must match SoR).

Rules (live mode, additional):
  4. If auth.mfa.totp.required == true OR auth.mfa.enforcement == "required",
     the Supabase project must have MFA TOTP enabled via Management API.
     If not enabled → fail with actionable error.
  5. If enforcement == "optional", live probe still runs but only warns
     (does not fail CI) — avoids blocking prod on a non-enforced setting.

Exit codes:
  0  all checks pass
  1  schema violation
  2  live probe: TOTP not enabled and SSOT requires it
  3  live probe: API call failed (treat as warning when optional)
"""
from __future__ import annotations

import argparse
import os
import sys
import urllib.request
import urllib.error
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
PROD_SETTINGS = ROOT / "ssot/runtime/prod_settings.yaml"

SUPABASE_MGMT_API = "https://api.supabase.com"


def die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def warn(msg: str) -> None:
    print(f"WARN: {msg}", file=sys.stderr)


def load_yaml(p: Path) -> dict:
    if not p.exists():
        die(f"Missing required file: {p}")
    return yaml.safe_load(p.read_text()) or {}


def schema_checks(ps: dict) -> None:
    """Validate MFA policy structure in SSOT. Exits on first category of error."""
    auth = ps.get("auth") or {}

    # Rule 1: identity_sor must be supabase
    sor = auth.get("identity_sor")
    if sor != "supabase":
        die(f"auth.identity_sor must be 'supabase', got '{sor}'")

    mfa = auth.get("mfa") or {}

    # Rule 1: MFA provider must be supabase
    provider = mfa.get("provider")
    if provider != "supabase":
        die(
            f"auth.mfa.provider must be 'supabase' (got '{provider}'). "
            f"MFA must not be delegated to a non-IdP system."
        )

    # Rule 2: Odoo TOTP must be explicitly disabled
    odoo_totp = mfa.get("odoo_totp") or {}
    if odoo_totp.get("enabled") is not False:
        die(
            "auth.mfa.odoo_totp.enabled must be false. "
            "Parallel Odoo TOTP creates split-brain MFA; Supabase is the only MFA system."
        )

    print("OK (schema): MFA policy is consistent — provider=supabase, odoo_totp disabled.")


def live_probe(ps: dict) -> None:
    """Call Supabase Management API to verify TOTP is actually enabled."""
    ref = os.environ.get("SUPABASE_PROJECT_REF", "").strip()
    token = os.environ.get("SUPABASE_MANAGEMENT_TOKEN", "").strip()

    if not ref or not token:
        die(
            "live mode requires SUPABASE_PROJECT_REF and SUPABASE_MANAGEMENT_TOKEN env vars. "
            "Set SUPABASE_PROJECT_REF (e.g. spdtwktxdalcfigzeqrz) and "
            "SUPABASE_MANAGEMENT_TOKEN (sbp_... PAT from Supabase Dashboard → Account → Access Tokens)."
        )

    auth = ps.get("auth") or {}
    mfa = auth.get("mfa") or {}
    totp = mfa.get("totp") or {}

    required_by_ssot = (
        mfa.get("enforcement") == "required"
        or totp.get("required") is True
    )

    url = f"{SUPABASE_MGMT_API}/v1/projects/{ref}/config/auth"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        msg = f"Supabase Management API returned HTTP {e.code}: {body[:200]}"
        if required_by_ssot:
            die(msg, code=3)
        else:
            warn(f"{msg} (enforcement=optional — not failing CI)")
            print("OK (live/warn): API unreachable but enforcement is optional.")
            return
    except Exception as e:
        msg = f"Supabase Management API call failed: {e}"
        if required_by_ssot:
            die(msg, code=3)
        else:
            warn(f"{msg} (enforcement=optional — not failing CI)")
            print("OK (live/warn): API error but enforcement is optional.")
            return

    # Supabase Management API returns auth config; MFA TOTP is typically under
    # mfa_enabled / security_mfa_type. Field names may vary by API version.
    # See: https://api.supabase.com/api/v1#tag/projects/GET/v1/projects/{ref}/config/auth
    mfa_enabled = data.get("mfa_enabled", None)
    security_mfa_type = data.get("security_mfa_type", "")  # "totp" | "phone" | ""

    totp_on = mfa_enabled is True or "totp" in str(security_mfa_type).lower()

    if not totp_on:
        msg = (
            f"Supabase project {ref}: MFA TOTP is NOT enabled (mfa_enabled={mfa_enabled}, "
            f"security_mfa_type={security_mfa_type!r}). "
            f"Enable in Supabase Dashboard → Auth → Multi Factor Authentication → TOTP."
        )
        if required_by_ssot:
            die(msg, code=2)
        else:
            warn(f"{msg} (enforcement=optional — not failing CI)")
            print("OK (live/warn): TOTP not yet enabled but enforcement is optional.")
            return

    print(
        f"OK (live): Supabase project {ref} MFA TOTP is enabled "
        f"(mfa_enabled={mfa_enabled}, security_mfa_type={security_mfa_type!r})."
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="MFA policy SSOT gate")
    parser.add_argument(
        "--mode",
        choices=["schema", "live"],
        default="schema",
        help="schema = SSOT-only (default); live = SSOT + Supabase Management API probe",
    )
    args = parser.parse_args()

    ps = load_yaml(PROD_SETTINGS)

    if ps.get("version") != 1:
        die("prod_settings.yaml must have version: 1")

    schema_checks(ps)

    if args.mode == "live":
        live_probe(ps)

    return 0


if __name__ == "__main__":
    sys.exit(main())
