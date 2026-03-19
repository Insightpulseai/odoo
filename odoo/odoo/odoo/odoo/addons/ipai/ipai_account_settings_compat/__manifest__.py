# Copyright (C) InsightPulse AI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.en.html).
#
# SAFETY NET — intentionally kept even when OCA account-financial-tools is
# fully mounted in production.
#
# Root cause addressed:
#   infra/stack/compose.stack.yml was missing bind mounts for all /mnt/oca/*
#   paths listed in infra/odoo.conf addons_path.  Odoo silently skips missing
#   addons_path dirs at startup, leaving account_usability view XML stored in
#   the database but its Python fields unregistered.  The OWL frontend then
#   throws:
#     OwlError: "res.config.settings"."anglo_saxon_accounting" field is undefined
#
# Root-cause fix: compose.stack.yml now mounts all OCA repos (PR: fix(odoo):
#   mount OCA repos referenced by addons_path + add CI guardrail).
#
# Why keep this shim:
#   • Zero-cost: it only registers a related field that already exists on
#     res.company; no DB columns, no migrations, no functional side-effects.
#   • Defence-in-depth: if OCA volume hydration fails or is skipped the
#     Settings page still renders without an OwlError.
#   • Last-registered wins: if account_usability IS loaded, both modules
#     register the same related= field pointing to the same company column;
#     Odoo's _inherit system simply keeps the last definition — no conflict.
#
# CI guard: scripts/validate_addons_path.py enforces compose ↔ addons_path
#   parity so this scenario can never silently recur.
{
    "name": "IPAI Account Settings Compat",
    "version": "19.0.1.0.0",
    "summary": (
        "Safety-net shim: ensures res.config.settings.anglo_saxon_accounting is "
        "always registered, regardless of whether OCA account_usability is "
        "loadable. Fixes OwlError when Settings form renders and account_usability "
        "view XML is in the database but the OCA module is absent from addons_path."
    ),
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "category": "Accounting",
    "license": "AGPL-3",
    "depends": ["account"],
    "data": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
