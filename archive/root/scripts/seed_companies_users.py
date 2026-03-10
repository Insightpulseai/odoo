#!/usr/bin/env python3
"""
Idempotent org seeder for Odoo CE.
Creates companies + users with stable external IDs (ir.model.data),
so re-running is safe.

Run via: odoo-bin shell -d <db> -c <conf> --no-http < scripts/seed_companies_users.py
"""
from __future__ import annotations

import re

# ---- helpers ----
def ensure_xmlid(env, model, res_id, xmlid: str):
    """Bind (or ensure) an external id for a record."""
    if "." not in xmlid:
        raise ValueError("xmlid must be in form module.name")
    module, name = xmlid.split(".", 1)
    imd = env["ir.model.data"].sudo()
    existing = imd.search([("module", "=", module), ("name", "=", name)], limit=1)
    if existing:
        if existing.model != model or existing.res_id != res_id:
            # update binding to current record (keeps idempotent behavior)
            existing.write({"model": model, "res_id": res_id})
        return existing
    return imd.create({"module": module, "name": name, "model": model, "res_id": res_id})


def ref(env, xmlid: str):
    return env.ref(xmlid, raise_if_not_found=False)


def upsert_company(env, xmlid: str, vals: dict):
    company = ref(env, xmlid)
    if company:
        company.sudo().write(vals)
        return company
    company = env["res.company"].sudo().create(vals)
    ensure_xmlid(env, "res.company", company.id, xmlid)
    return company


def upsert_user(env, xmlid: str, login: str, vals: dict, groups_xmlids: list[str], company, allowed_companies):
    user = ref(env, xmlid)
    Users = env["res.users"].sudo()

    # groups
    gids = []
    for g in groups_xmlids:
        rec = ref(env, g)
        if not rec:
            raise RuntimeError(f"Missing group xmlid: {g}")
        gids.append(rec.id)

    if user:
        user.write({
            **vals,
            "login": login,
            "company_id": company.id,
            "company_ids": [(6, 0, [c.id for c in allowed_companies])],
            "groups_id": [(6, 0, gids)],
        })
        return user

    user = Users.create({
        **vals,
        "login": login,
        "company_id": company.id,
        "company_ids": [(6, 0, [c.id for c in allowed_companies])],
        "groups_id": [(6, 0, gids)],
    })
    ensure_xmlid(env, "res.users", user.id, xmlid)
    return user


def upsert_partner(env, xmlid: str, vals: dict):
    partner = ref(env, xmlid)
    Partners = env["res.partner"].sudo()
    if partner:
        partner.write(vals)
        return partner
    partner = Partners.create(vals)
    ensure_xmlid(env, "res.partner", partner.id, xmlid)
    return partner


def sanitize_name(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


# ---- CONFIG (edit safely) ----
# NOTE: These are company records in Odoo. BIR branch-codes can be stored as tags/fields later via OCA.
COMPANIES = [
    {
        "xmlid": "ipai_org.company_dataverse",
        "name": "Dataverse IT Consultancy",
        "street": "Callista Bldg, Levina Place, Jenny's Ave, Exit",
        "street2": "Brgy. Maybunga",
        "city": "Pasig",
        "country_code": "PH",
        "email": "business@insightpulseai.com",
        "phone": "",
        "vat": "215-308-716-000",  # Dataverse TIN (as provided)
        "comment": "BIR Branch 000 (HO) - Pasig RDO to be confirmed via COR/BIR 2303.",
    },
    {
        "xmlid": "ipai_org.company_w9",
        "name": "W9 Studio",
        "street": "La Fuerza Plaza",
        "street2": "2241 Chino Roces Ave, Bangkal",
        "city": "Makati",
        "country_code": "PH",
        "email": "business@w9studio.net",
        "phone": "",
        "vat": "",  # same TIN under Dataverse if branch; keep blank if you don't want duplicative vat field
        "comment": "BIR Branch 001 (Makati - La Fuerza). Lease docs exist; treat as branch under same TIN.",
    },
    {
        "xmlid": "ipai_org.company_evidencelab",
        "name": "Project Meta – EvidenceLab Consulting",
        "street": "",
        "street2": "",
        "city": "Pasig",
        "country_code": "PH",
        "email": "business@insightpulseai.com",
        "phone": "",
        "vat": "",
        "comment": "BIR Branch 002 (Pasig or virtual tied to HO). Invoice issuance source must be clarified: Dataverse (same TIN) vs separate registration.",
    },
    {
        "xmlid": "ipai_org.company_tbwa_smp",
        "name": r"TBWA\\SMP",
        "street": "",
        "street2": "",
        "city": "",
        "country_code": "PH",
        "email": "business@insightpulseai.com",
        "phone": "",
        "vat": "",
        "comment": "Operating entity/project in your stack. If this is client-side only, keep minimal master data; do not mix TIN unless legally applicable.",
    },
]

# Users (adjust emails/logins)
USERS = [
    # Super admin-type operational user (multi-company)
    {
        "xmlid": "ipai_org.user_jake",
        "name": "Jake Tolentino",
        "login": "jgtolentino@yahoo.com",
        "email": "jgtolentino@yahoo.com",
        "groups": [
            "base.group_system",  # Settings (technical)
        ],
        "home_company_xmlid": "ipai_org.company_dataverse",
        "allowed_company_xmlids": [
            "ipai_org.company_dataverse",
            "ipai_org.company_w9",
            "ipai_org.company_evidencelab",
            "ipai_org.company_tbwa_smp",
        ],
    },
    # Accounting / Finance operator (multi-company but not technical admin)
    {
        "xmlid": "ipai_org.user_finance",
        "name": "Finance Ops",
        "login": "finance@insightpulseai.com",
        "email": "finance@insightpulseai.com",
        "groups": [
            "account.group_account_manager",
        ],
        "home_company_xmlid": "ipai_org.company_dataverse",
        "allowed_company_xmlids": [
            "ipai_org.company_dataverse",
            "ipai_org.company_w9",
            "ipai_org.company_evidencelab",
        ],
    },
]

# ---- execution (odoo shell provides `env`) ----
Country = env["res.country"].sudo()
PH = Country.search([("code", "=", "PH")], limit=1)

created_companies = {}
for c in COMPANIES:
    vals = {
        "name": sanitize_name(c["name"]),
        "email": c.get("email") or False,
        "phone": c.get("phone") or False,
        "street": c.get("street") or False,
        "street2": c.get("street2") or False,
        "city": c.get("city") or False,
        "vat": c.get("vat") or False,
        "country_id": PH.id if PH else False,
        "company_registry": False,
        "report_header": False,
        "report_footer": c.get("comment") or False,
    }
    company = upsert_company(env, c["xmlid"], vals)
    created_companies[c["xmlid"]] = company

# Ensure partners for companies are updated with same address basics (optional but keeps consistency)
for xmlid, company in created_companies.items():
    partner_xmlid = xmlid.replace("company_", "partner_")
    upsert_partner(env, partner_xmlid, {
        "name": company.name,
        "is_company": True,
        "street": company.street,
        "street2": company.street2,
        "city": company.city,
        "country_id": company.country_id.id if company.country_id else False,
        "email": company.email,
        "phone": company.phone,
        "vat": company.vat,
    })

# Users
for u in USERS:
    home = created_companies[u["home_company_xmlid"]]
    allowed = [created_companies[x] for x in u["allowed_company_xmlids"]]
    user = upsert_user(
        env,
        u["xmlid"],
        u["login"],
        vals={"name": u["name"], "email": u.get("email") or False},
        groups_xmlids=u["groups"],
        company=home,
        allowed_companies=allowed,
    )

print("✅ Seed complete")
print("Companies:", [created_companies[x].name for x in created_companies])
print("Users:", [env.ref(x).login for x in [u["xmlid"] for u in USERS] if env.ref(x, raise_if_not_found=False)])
