#!/usr/bin/env python3
"""
augment_parity_fields.py — Add delivery_mode, criticality, v19_status,
bridge_owner to every entry in odoo/ssot/parity_targets.yaml.

Also validates OCA module names against the installed allowlist and
prints a drift report.

Usage:
  python3 scripts/parity/augment_parity_fields.py [--dry-run]
  python3 scripts/parity/augment_parity_fields.py --report  # print report only

Output:
  odoo/ssot/parity_targets.yaml    (in-place update)
  docs/architecture/EE_PARITY_MATRIX.md  (regenerated tiered report)
"""

import sys
import re
import argparse
from pathlib import Path

try:
    import yaml
except ImportError:
    raise SystemExit("pyyaml missing. Run: pip install pyyaml")

REPO_ROOT = Path(__file__).parent.parent.parent
PARITY_FILE = REPO_ROOT / "odoo/ssot/parity_targets.yaml"
ALLOWLIST_FILE = REPO_ROOT / "odoo/ssot/oca_installed_allowlist.yaml"
REPORT_FILE = REPO_ROOT / "docs/architecture/EE_PARITY_MATRIX.md"

# ---------------------------------------------------------------------------
# Criticality map — keyed by capability_id
# Tier 1 = must_have | Tier 2 = scope_based | Tier 3 = optional
# ---------------------------------------------------------------------------
CRITICALITY: dict[str, str] = {
    # Core ERP
    "A01": "must_have",   # Chart of accounts
    "A02": "must_have",   # Invoicing/bills
    "A03": "must_have",   # PH withholding tax
    "A04": "must_have",   # Bank statement import
    "A05": "must_have",   # Bank reconciliation
    "A06": "must_have",   # Payment orders/SEPA
    "A07": "must_have",   # Financial reporting
    "A08": "must_have",   # Tax balance/analytic
    "A09": "must_have",   # Sales orders
    "A10": "scope_based", # Sale discounts
    "A11": "scope_based", # Sale order types/priorities
    "A12": "scope_based", # Sale automatic workflow
    "A13": "must_have",   # Purchase orders/RFQ
    "A14": "must_have",   # Inventory/moves
    "A15": "scope_based", # Manufacturing BOM/MO
    "A16": "scope_based", # MRP quality control
    "A17": "scope_based", # MRP operations extensions
    "A18": "scope_based", # Project/timesheets
    "A19": "scope_based", # Project stage mgmt
    "A20": "scope_based", # Timesheet controls
    "A21": "must_have",   # HR employees/leaves
    "A22": "scope_based", # HR recruitment
    "A23": "scope_based", # POS
    "A24": "must_have",   # CRM/leads
    # Compliance
    "B01": "must_have",   # BIR compliance (PH)
    "B02": "must_have",   # IBAN/VAT validation
    "B03": "must_have",   # Audit log
    "B04": "must_have",   # Partner dedup/GDPR
    "B05": "must_have",   # Field encryption
    # Mail
    "C01": "must_have",   # SMTP relay
    "C02": "scope_based", # Mail debranding
    "C03": "scope_based", # Activity reminders
    "C04": "optional",    # Optional autofollow
    "C05": "must_have",   # Outbound static domain
    "C06": "scope_based", # Deferred mail
    "C07": "scope_based", # Delivery confirmations
    "C08": "scope_based", # Mail tracking
    "C09": "must_have",   # Mass mailing
    # Security
    "D01": "must_have",   # SSO/OIDC
    "D02": "must_have",   # 2FA/TOTP
    "D03": "scope_based", # Passkey/WebAuthn
    "D04": "must_have",   # Session timeout
    "D05": "must_have",   # RBAC
    "D06": "scope_based", # Impersonation
    "D07": "must_have",   # Server environment tiering
    "D08": "must_have",   # DB access control
    # Platform
    "E01": "must_have",   # CI build/test
    "E02": "must_have",   # Staging environment
    "E03": "must_have",   # DB promotion
    "E04": "scope_based", # Preview deploys
    "E05": "must_have",   # DNS management
    "E06": "must_have",   # Observability
    "E07": "must_have",   # Backup/DR
    "E08": "scope_based", # GHAS security posture
    # Documents/OCR
    "F01": "scope_based", # Vendor bill OCR
    "F02": "scope_based", # DMS
    "F03": "scope_based", # Attachment indexing
    "F04": "scope_based", # File storage S3 (blocked)
    "F05": "scope_based", # e-Signature (planned)
    # BI/Reporting
    "G01": "must_have",   # MIS Builder
    "G02": "scope_based", # BI SQL views
    "G03": "must_have",   # Spreadsheet/pivot
    "G04": "scope_based", # External BI
    "G05": "scope_based", # REST API framework (blocked)
    # Integration
    "H01": "must_have",   # Job queue
    "H02": "must_have",   # Connector framework
    "H03": "must_have",   # n8n automation bus
    "H04": "scope_based", # External event bus
    "H05": "optional",    # AI/LLM copilot
}

# delivery_mode overrides (when different from resolution)
DELIVERY_MODE_OVERRIDE: dict[str, str] = {
    "E08": "PLATFORM",  # GitHub Advanced Security — not an Odoo module concern
    "F04": "BRIDGE",    # GAP → bridge via Supabase Storage
    "F05": "BRIDGE",    # GAP → bridge via external provider
    "G05": "BRIDGE",    # GAP → bridge via JSON-RPC / n8n
}


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_allowlist(path: Path) -> set[str]:
    data = load_yaml(path)
    return set(data.get("oca_modules") or [])


def augment_entry(entry: dict) -> dict:
    """Add delivery_mode, criticality, v19_status, bridge_owner to one entry."""
    cid = entry["capability_id"]
    resolution = entry.get("resolution", "CE")
    status = entry.get("status", "installed")
    bridge_services = entry.get("bridge_services") or []

    # delivery_mode
    entry["delivery_mode"] = DELIVERY_MODE_OVERRIDE.get(cid, resolution)

    # criticality
    entry["criticality"] = CRITICALITY.get(cid, "scope_based")

    # v19_status — mirrors status (kept separate for future divergence)
    entry["v19_status"] = status

    # bridge_owner — only when delivery_mode == BRIDGE/PLATFORM
    dm = entry["delivery_mode"]
    if dm in ("BRIDGE", "PLATFORM") and bridge_services:
        entry["bridge_owner"] = " + ".join(bridge_services)
    else:
        entry["bridge_owner"] = None

    return entry


def validate_oca_names(targets: list[dict], allowlist: set[str]) -> list[dict]:
    """Return drift report: modules in parity_targets not in allowlist."""
    drift = []
    for t in targets:
        for mod in t.get("oca_modules") or []:
            if mod not in allowlist:
                drift.append({
                    "capability_id": t["capability_id"],
                    "name": t["name"],
                    "module": mod,
                    "resolution": t.get("resolution"),
                })
    return drift


def write_yaml(targets: list[dict], source_path: Path) -> None:
    """Write augmented targets back preserving file header comments."""
    # Read original to get header comments (lines before 'parity_targets:')
    original = source_path.read_text(encoding="utf-8")
    header_lines = []
    for line in original.splitlines():
        if line.startswith("---") or line.startswith("parity_targets:"):
            break
        header_lines.append(line)

    # Build YAML body
    body_lines = [
        "# ERP SaaS Parity Targets — Machine-readable SSOT",
        "# Human-readable twin: docs/architecture/EE_PARITY_MATRIX.md",
        "# Validator: scripts/odoo/validate_parity_targets.py",
        "# Schema:",
        "#   capability_id: str (e.g. A01)",
        "#   name: str",
        "#   resolution: CE | OCA | PORT | BRIDGE | GAP  (how parity is achieved)",
        "#   delivery_mode: CE | OCA | BRIDGE | PORT | PLATFORM  (runtime delivery layer)",
        "#   criticality: must_have | scope_based | optional",
        "#   v19_status: installed | partial | planned | blocked",
        "#   oca_modules: list[str]   (for OCA/PORT only)",
        "#   ipai_connectors: list[str]  (connector-only ipai_* modules)",
        "#   bridge_services: list[str]  (external services)",
        "#   bridge_owner: str | null   (when delivery_mode=BRIDGE/PLATFORM)",
        "#   runbook: str | null  (path under docs/ops/ for BRIDGE; null otherwise)",
        "#   status: installed | partial | planned | blocked",
        "#   notes: str | null",
        "",
        "---",
        "parity_targets:",
        "",
    ]

    domain_comments = {
        "A": "  # ─── A. Core ERP ──────────────────────────────────────────────────────────",
        "B": "  # ─── B. Compliance & Localisation ─────────────────────────────────────────",
        "C": "  # ─── C. Mail & Communications ─────────────────────────────────────────────",
        "D": "  # ─── D. Security & Identity ───────────────────────────────────────────────",
        "E": "  # ─── E. Platform / Odoo.sh Parity ────────────────────────────────────────",
        "F": "  # ─── F. Document & OCR Pipeline ───────────────────────────────────────────",
        "G": "  # ─── G. BI & Reporting ────────────────────────────────────────────────────",
        "H": "  # ─── H. Integration Framework ─────────────────────────────────────────────",
    }
    current_domain = None

    for t in targets:
        domain = t["capability_id"][0]
        if domain != current_domain:
            current_domain = domain
            if domain in domain_comments:
                body_lines.append(domain_comments[domain])
                body_lines.append("")

        def yl(val):
            if val is None:
                return "null"
            if isinstance(val, list):
                if not val:
                    return "[]"
                return "[" + ", ".join(val) + "]"
            return str(val)

        def ystr(val):
            if val is None:
                return "null"
            # quote if contains special chars
            if any(c in str(val) for c in [':', '#', '{', '}']):
                return f'"{val}"'
            return f'"{val}"'

        oca = t.get("oca_modules") or []
        ipai = t.get("ipai_connectors") or []
        bridge = t.get("bridge_services") or []

        def mlist(lst):
            if not lst:
                return "[]"
            items = "\n" + "\n".join(f"      - {m}" for m in lst)
            return items

        notes = t.get("notes")
        notes_line = f'\n    notes: {ystr(notes)}' if notes else "\n    notes: null"

        block = f"""  - capability_id: {t["capability_id"]}
    name: {ystr(t["name"])}
    resolution: {t.get("resolution", "CE")}
    delivery_mode: {t.get("delivery_mode", "CE")}
    criticality: {t.get("criticality", "scope_based")}
    v19_status: {t.get("v19_status", "installed")}
    oca_modules: {yl(oca) if oca else "[]"}
    ipai_connectors: {yl(ipai) if ipai else "[]"}
    bridge_services: {yl(bridge) if bridge else "[]"}
    bridge_owner: {ystr(t.get("bridge_owner")) if t.get("bridge_owner") else "null"}
    runbook: {ystr(t.get("runbook")) if t.get("runbook") else "null"}
    status: {t.get("status", "installed")}{notes_line}
"""
        body_lines.append(block)

    source_path.write_text("\n".join(body_lines), encoding="utf-8")


def generate_report(targets: list[dict], drift: list[dict]) -> str:
    from datetime import datetime

    domains = {
        "A": "Core ERP",
        "B": "Compliance & Localisation",
        "C": "Mail & Communications",
        "D": "Security & Identity",
        "E": "Platform / Odoo.sh Parity",
        "F": "Document & OCR Pipeline",
        "G": "BI & Reporting",
        "H": "Integration Framework",
    }

    def tier_label(c: str) -> str:
        return {"must_have": "Tier 1", "scope_based": "Tier 2", "optional": "Tier 3"}.get(c, "—")

    def status_icon(s: str) -> str:
        return {"installed": "✅", "planned": "🔵", "blocked": "🔴", "partial": "⚠️"}.get(s, "—")

    def dm_badge(dm: str) -> str:
        return {"CE": "CE", "OCA": "OCA", "BRIDGE": "🔌 BRIDGE", "PORT": "PORT", "PLATFORM": "🏗️ PLATFORM", "GAP": "❌ GAP"}.get(dm, dm)

    by_resolution = {}
    by_status = {}
    by_criticality = {}
    for t in targets:
        by_resolution[t.get("resolution", "?")] = by_resolution.get(t.get("resolution", "?"), 0) + 1
        by_status[t.get("status", "?")] = by_status.get(t.get("status", "?"), 0) + 1
        by_criticality[t.get("criticality", "?")] = by_criticality.get(t.get("criticality", "?"), 0) + 1

    lines = [
        f"# EE Parity Matrix — Odoo CE 19",
        f"",
        f"> **Generated**: {datetime.now().strftime('%Y-%m-%d')}  ",
        f"> **Source**: `odoo/ssot/parity_targets.yaml`  ",
        f"> **Validator**: `scripts/parity/augment_parity_fields.py`",
        f"",
        f"## Coverage Summary",
        f"",
        f"| Total | Installed | Planned | Blocked |",
        f"|-------|-----------|---------|---------|",
        f"| {len(targets)} | {by_status.get('installed', 0)} | {by_status.get('planned', 0)} | {by_status.get('blocked', 0)} |",
        f"",
        f"| By Resolution | Count |",
        f"|---------------|-------|",
    ]
    for res, cnt in sorted(by_resolution.items()):
        lines.append(f"| {res} | {cnt} |")
    lines += [
        f"",
        f"| By Tier | Count |",
        f"|---------|-------|",
        f"| Tier 1 — must\\_have | {by_criticality.get('must_have', 0)} |",
        f"| Tier 2 — scope\\_based | {by_criticality.get('scope_based', 0)} |",
        f"| Tier 3 — optional | {by_criticality.get('optional', 0)} |",
        f"",
    ]

    # Tiered views
    for tier_key, tier_name in [("must_have", "Tier 1 — Must-Have Parity"), ("scope_based", "Tier 2 — Scope-Based Parity"), ("optional", "Tier 3 — Optional / Bridge-First")]:
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"## {tier_name}")
        lines.append(f"")
        lines.append(f"| ID | Capability | Delivery | Status | OCA Modules |")
        lines.append(f"|----|-----------|---------|--------|-------------|")
        for t in targets:
            if t.get("criticality") != tier_key:
                continue
            oca = ", ".join(f"`{m}`" for m in (t.get("oca_modules") or []))
            bridge = ", ".join(t.get("bridge_services") or [])
            detail = oca if oca else (f"bridge: {bridge}" if bridge else "—")
            dm = dm_badge(t.get("delivery_mode", t.get("resolution", "CE")))
            si = status_icon(t.get("status", "installed"))
            lines.append(f"| {t['capability_id']} | {t['name']} | {dm} | {si} {t.get('status','installed')} | {detail} |")
        lines.append(f"")

    # Domain detail
    lines.append("---")
    lines.append("")
    lines.append("## Capability Detail by Domain")
    lines.append("")
    for domain_letter, domain_name in domains.items():
        caps = [t for t in targets if t["capability_id"].startswith(domain_letter)]
        if not caps:
            continue
        lines.append(f"### {domain_letter}. {domain_name}")
        lines.append(f"")
        lines.append(f"| ID | Capability | Delivery | Tier | v19 Status | Bridge / Modules |")
        lines.append(f"|----|-----------|---------|------|-----------|-----------------|")
        for t in caps:
            oca = ", ".join(f"`{m}`" for m in (t.get("oca_modules") or []))
            bridge_owner = t.get("bridge_owner") or ""
            detail = oca if oca else (bridge_owner or "—")
            dm = dm_badge(t.get("delivery_mode", t.get("resolution", "CE")))
            si = status_icon(t.get("v19_status", "installed"))
            tier = tier_label(t.get("criticality", "scope_based"))
            lines.append(f"| {t['capability_id']} | {t['name']} | {dm} | {tier} | {si} {t.get('v19_status','installed')} | {detail} |")
        lines.append(f"")

    # Gaps section
    gaps = [t for t in targets if t.get("status") in ("blocked", "planned") or t.get("resolution") == "GAP"]
    if gaps:
        lines += [
            "---",
            "",
            "## Gaps & Blocked Capabilities",
            "",
            "| ID | Capability | Resolution | Status | Notes |",
            "|----|-----------|-----------|--------|-------|",
        ]
        for t in gaps:
            notes = (t.get("notes") or "").replace("|", "\\|")
            si = status_icon(t.get("status", "planned"))
            lines.append(f"| {t['capability_id']} | {t['name']} | {t.get('resolution')} | {si} {t.get('status')} | {notes} |")
        lines.append("")

    # OCA naming drift
    if drift:
        lines += [
            "---",
            "",
            "## ⚠️ OCA Module Naming Drift",
            "",
            "Modules listed in `parity_targets.yaml` not found in `oca_installed_allowlist.yaml`:",
            "",
            "| Capability | Module | Resolution | Action |",
            "|-----------|--------|-----------|--------|",
        ]
        for d in drift:
            lines.append(f"| {d['capability_id']} — {d['name']} | `{d['module']}` | {d['resolution']} | Verify module name or add to allowlist |")
        lines.append("")
    else:
        lines += ["", "---", "", "## OCA Naming Validation", "", "✅ All OCA modules in parity_targets.yaml are present in `oca_installed_allowlist.yaml`.", ""]

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Print diff, don't write files")
    parser.add_argument("--report", action="store_true", help="Print report to stdout only")
    args = parser.parse_args()

    data = load_yaml(PARITY_FILE)
    targets = data["parity_targets"]

    allowlist = load_allowlist(ALLOWLIST_FILE) if ALLOWLIST_FILE.exists() else set()

    # Augment
    targets = [augment_entry(dict(t)) for t in targets]

    # Validate OCA names
    drift = validate_oca_names(targets, allowlist)

    # Report
    report = generate_report(targets, drift)

    if args.report:
        print(report)
        return 0

    if drift:
        print(f"\n⚠️  OCA naming drift ({len(drift)} modules):")
        for d in drift:
            print(f"  {d['capability_id']} | {d['module']} ({d['resolution']})")
        print()

    if args.dry_run:
        print(f"[dry-run] Would write {PARITY_FILE}")
        print(f"[dry-run] Would write {REPORT_FILE}")
        print(f"[dry-run] {len(targets)} capabilities augmented")
        return 0

    write_yaml(targets, PARITY_FILE)
    REPORT_FILE.write_text(report, encoding="utf-8")

    print(f"✅ {PARITY_FILE.relative_to(REPO_ROOT)} — {len(targets)} capabilities augmented")
    print(f"✅ {REPORT_FILE.relative_to(REPO_ROOT)} — tiered report written")
    if drift:
        print(f"⚠️  {len(drift)} OCA module names need review (see report)")
    else:
        print(f"✅ OCA module names validated — no drift")
    return 0


if __name__ == "__main__":
    sys.exit(main())
