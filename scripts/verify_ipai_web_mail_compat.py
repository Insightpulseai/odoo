#!/usr/bin/env python3
# Copyright 2026 InsightPulse AI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""
CI/ops verifier: confirms ipai_web_mail_compat is installed and that the
asset contract is satisfied by inspecting the *fully resolved* bundle.

Uses IrAsset._get_asset_paths() which processes manifest-declared assets
(including '("remove", ...)' stanzas) and ir.asset dynamic records, giving
the FINAL resolved file list after all directives have been applied.

Tuple structure returned by _get_asset_paths():
    (path, full_path, bundle, last_modified)   — 4 elements

Exit codes
  0  all checks passed
  1  a check failed (mismatch printed to stdout)
  2  fatal setup / import error

Usage:
    python3 scripts/verify_ipai_web_mail_compat.py \\
        -d odoo_dev -c config/dev/odoo.conf

In CI (GitHub Actions, DO App):
    python3 scripts/verify_ipai_web_mail_compat.py \\
        -d "$ODOO_DB" -c "$ODOO_CONF"
"""

import argparse
import sys


# ── helpers ───────────────────────────────────────────────────────────────────

def ok(msg: str) -> None:
    print(f"[verify_ipai_web_mail_compat]  OK  {msg}", flush=True)


def fail(msg: str, code: int = 1) -> None:
    print(f"[verify_ipai_web_mail_compat] FAIL {msg}", file=sys.stderr, flush=True)
    sys.exit(code)


def die(msg: str) -> None:
    fail(msg, code=2)


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-d", "--db", required=True, help="Database name (e.g. odoo_dev)")
    ap.add_argument("-c", "--config", required=True, help="Path to odoo.conf")
    ap.add_argument(
        "--bundle",
        default="web.assets_backend",
        help="Asset bundle to inspect (default: web.assets_backend)",
    )
    args = ap.parse_args()

    # ── 0. Import Odoo runtime ────────────────────────────────────────────────
    try:
        import odoo
        from odoo import api, SUPERUSER_ID
        from odoo.modules.registry import Registry
        from odoo.tools import config as odoo_config
    except ModuleNotFoundError as exc:
        die(
            f"Cannot import odoo: {exc}\n"
            "Run this script inside the Odoo virtualenv / container."
        )

    odoo_config.parse_config(["-c", args.config, "-d", args.db, "--no-http"])

    # ── 1. Open DB registry ───────────────────────────────────────────────────
    try:
        registry = Registry(args.db)
    except Exception as exc:
        die(f"Failed to open registry for database '{args.db}': {exc}")

    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})

        # ── 2. Module installed? ──────────────────────────────────────────────
        module_name = "ipai_web_mail_compat"
        mod = env["ir.module.module"].search([(("name", "=", module_name))], limit=1)
        if not mod:
            fail(f"Module '{module_name}' not found in ir.module.module.")
        if mod.state != "installed":
            fail(f"Module '{module_name}' exists but state='{mod.state}' (expected 'installed').")
        ok(f"Module installed: {module_name}  version={mod.installed_version}")

        # ── 3. Probe contract ─────────────────────────────────────────────────
        try:
            probe = env["ipai.compat.probe"].mail_tracking()
        except Exception as exc:
            fail(f"ipai.compat.probe.mail_tracking() raised: {exc}")

        if not probe.get("active"):
            fail("Probe returned active=False — module may be installed but broken.")
        ok(f"Probe active. fixes={probe.get('fixes')}")

        removed_contract = probe.get("removed_upstream_assets") or []
        added_contract = probe.get("added_compat_assets") or []

        if len(removed_contract) != 2:
            fail(f"Probe.removed_upstream_assets expected 2 entries, got {removed_contract}")
        if len(added_contract) != 3:
            fail(f"Probe.added_compat_assets expected 3 entries, got {added_contract}")

        # ── 4. Resolved bundle check ──────────────────────────────────────────
        # _get_asset_paths() processes manifest-declared assets (including
        # '("remove", ...)' stanzas) PLUS ir.asset dynamic records and returns
        # the FINAL resolved list after all directives are applied.
        #
        # Tuple structure: (path, full_path, bundle, last_modified) — 4 elements.
        # We only need index 0 (the relative addon path).
        #
        # Correct verification semantics:
        #   • removed_upstream_assets  → must NOT be in the final bundle
        #   • added_compat_assets      → must be in the final bundle
        try:
            Asset = env["ir.asset"]
        except KeyError:
            die("'ir.asset' model not found — this Odoo build may be unusually old.")

        try:
            resolved = Asset._get_asset_paths(args.bundle, {})
        except Exception as exc:
            die(f"IrAsset._get_asset_paths('{args.bundle}') raised: {exc}")

        # Build path set from element 0 of each 4-tuple.
        # _get_asset_paths() returns paths with a leading slash when resolved
        # from the filesystem (e.g. '/mail_tracking/static/...' not
        # 'mail_tracking/static/...').  Strip the leading slash so both the
        # probe contract paths (no slash) and the resolved paths match.
        path_set = {entry[0].lstrip('/') for entry in resolved}

        if not path_set:
            fail(
                f"_get_asset_paths('{args.bundle}') returned an empty list.\n"
                "Possible causes: bundle name wrong, no installed addons declare assets."
            )
        ok(f"Resolved {len(path_set)} asset paths from '{args.bundle}'.")

        # 4a. Upstream broken files must NOT appear in the final bundle
        errors = []
        for upstream_path in removed_contract:
            if upstream_path in path_set:
                errors.append(
                    f"  STILL_PRESENT (expected removed): PATH={upstream_path!r}"
                )

        # 4b. Compat replacement files must be present in the final bundle
        for compat_path in added_contract:
            if compat_path not in path_set:
                errors.append(
                    f"  MISSING (expected present): PATH={compat_path!r}"
                )

        if errors:
            print("[verify_ipai_web_mail_compat] FAIL Asset contract mismatch:", file=sys.stderr)
            for e in errors:
                print(e, file=sys.stderr)
            sys.exit(1)

        ok("Asset contract verified: upstream removed, compat assets present.")

    ok("All checks passed ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
