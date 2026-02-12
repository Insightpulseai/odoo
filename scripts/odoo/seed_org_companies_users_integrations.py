#!/usr/bin/env python3
"""
Idempotent org + integrations seeder for Odoo CE/OCA.

Creates/updates:
- res.company (+ company partner info)
- res.users (multi-company allowed companies)
- Zoho SMTP (ir.mail_server) + alias domain/catchall best-effort parameters
- AI API keys into ir.config_parameter (names are configurable via env)

Run via:
  odoo-bin shell -d <db> -c <conf> --no-http < scripts/odoo/seed_org_companies_users_integrations.py
"""
from __future__ import annotations

import os
import re
import json

# ---------------- helpers ----------------
def ensure_xmlid(env, model: str, res_id: int, xmlid: str):
    if "." not in xmlid:
        raise ValueError("xmlid must be in form module.name")
    module, name = xmlid.split(".", 1)
    imd = env["ir.model.data"].sudo()
    existing = imd.search([("module", "=", module), ("name", "=", name)], limit=1)
    if existing:
        if existing.model != model or existing.res_id != res_id:
            existing.write({"model": model, "res_id": res_id})
        return existing
    return imd.create({"module": module, "name": name, "model": model, "res_id": res_id})


def ref(env, xmlid: str):
    return env.ref(xmlid, raise_if_not_found=False)


def sanitize_name(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def country_by_code(env, code: str):
    if not code:
        return False
    return env["res.country"].sudo().search([("code", "=", code.upper())], limit=1) or False


def upsert_company(env, xmlid: str, vals: dict):
    company = ref(env, xmlid)
    if company:
        company.sudo().write(vals)
        return company
    company = env["res.company"].sudo().create(vals)
    ensure_xmlid(env, "res.company", company.id, xmlid)
    return company


def upsert_partner_for_company(env, partner_xmlid: str, company, vals: dict):
    # company.partner_id exists; bind an xmlid to it so it's stable.
    p = company.partner_id.sudo()
    p.write(vals)
    ensure_xmlid(env, "res.partner", p.id, partner_xmlid)
    return p


def safe_group_ids(env, groups_xmlids: list[str]):
    gids = []
    for g in groups_xmlids or []:
        rec = ref(env, g)
        if not rec:
            # non-fatal: modules may not be installed yet
            print(f"WARN: missing group xmlid (skipping): {g}")
            continue
        gids.append(rec.id)
    return sorted(set(gids))


def upsert_user(env, xmlid: str, login: str, vals: dict, groups_xmlids: list[str], home_company, allowed_companies):
    user = ref(env, xmlid)
    Users = env["res.users"].sudo()

    gids = safe_group_ids(env, groups_xmlids)
    allowed_ids = [c.id for c in allowed_companies]

    payload = {
        **(vals or {}),
        "login": login,
        "company_id": home_company.id,
        "company_ids": [(6, 0, allowed_ids)],
    }
    if gids:
        payload["groups_id"] = [(6, 0, gids)]

    if user:
        user.write(payload)
        return user

    user = Users.create(payload)
    ensure_xmlid(env, "res.users", user.id, xmlid)
    return user


def set_icp(env, key: str, value: str):
    env["ir.config_parameter"].sudo().set_param(key, value)
    print(f"SET ICP {key}={value!r}")


def ensure_mail_server(env, name: str, smtp_host: str, smtp_port: int, smtp_user: str, smtp_pass: str, encryption: str = "starttls"):
    IMS = env["ir.mail_server"].sudo()
    rec = IMS.search([("name", "=", name)], limit=1)
    vals = {
        "name": name,
        "smtp_host": smtp_host,
        "smtp_port": int(smtp_port),
        "smtp_user": smtp_user,
        "smtp_pass": smtp_pass,
        "smtp_encryption": encryption,
        "active": True,
    }
    if rec:
        rec.write(vals)
        print(f"MAIL SERVER updated: {name}")
        return rec
    rec = IMS.create(vals)
    print(f"MAIL SERVER created: {name}")
    return rec


# ---------------- CONFIG (edit safely) ----------------
# NOTE: This is a script; xmlid module name can be any string.
MODULE = "ipai_org"

COMPANIES = [
    {
        "xmlid": f"{MODULE}.company_dataverse",
        "name": "Dataverse IT Consultancy",
        "country_code": "PH",
        "street": "Callista Bldg, Levina Place, Jenny's Ave, Exit",
        "street2": "Brgy. Maybunga",
        "city": "Pasig",
        "email": "business@insightpulseai.com",
        "phone": "",
        "vat": "215-308-716-000",
        "comment": "BIR Branch 000 (HO) - Pasig RDO to confirm via COR/BIR 2303.",
    },
    {
        "xmlid": f"{MODULE}.company_w9",
        "name": "W9 Studio",
        "country_code": "PH",
        "street": "La Fuerza Plaza",
        "street2": "2241 Chino Roces Ave, Bangkal",
        "city": "Makati",
        "email": "business@w9studio.net",
        "phone": "",
        "vat": "",
        "comment": "Branch under same TIN (if applicable).",
    },
    {
        "xmlid": f"{MODULE}.company_evidencelab",
        "name": "Project Meta – EvidenceLab Consulting",
        "country_code": "PH",
        "street": "",
        "street2": "",
        "city": "Pasig",
        "email": "business@insightpulseai.com",
        "phone": "",
        "vat": "",
        "comment": "Branch vs separate registration TBD; keep minimal until confirmed.",
    },
    {
        "xmlid": f"{MODULE}.company_tbwa_smp",
        "name": "TBWA\\SMP",
        "country_code": "PH",
        "street": "",
        "street2": "",
        "city": "",
        "email": "business@insightpulseai.com",
        "phone": "",
        "vat": "",
        "comment": "Treat as company only if you need strict segregation; otherwise model as customer/project.",
    },
]

# Overridable logins via env (so you don't have to edit the file for prod/stage)
JAKE_LOGIN = os.getenv("ODOO_ADMIN_LOGIN", "jgtolentino.rn@gmail.com").strip()
FIN_LOGIN  = os.getenv("ODOO_FINANCE_LOGIN", "finance@insightpulseai.com").strip()

USERS = [
    {
        "xmlid": f"{MODULE}.user_jake",
        "name": "Jake Tolentino",
        "login": JAKE_LOGIN,
        "email": JAKE_LOGIN,
        "groups": [
            "base.group_system",  # Settings/Technical admin
        ],
        "home_company_xmlid": f"{MODULE}.company_dataverse",
        "allowed_company_xmlids": [
            f"{MODULE}.company_dataverse",
            f"{MODULE}.company_w9",
            f"{MODULE}.company_evidencelab",
            f"{MODULE}.company_tbwa_smp",
        ],
    },
    {
        "xmlid": f"{MODULE}.user_finance",
        "name": "Finance Ops",
        "login": FIN_LOGIN,
        "email": FIN_LOGIN,
        "groups": [
            # If account module not installed yet, this will warn+skip (non-fatal).
            "account.group_account_manager",
            "base.group_user",
        ],
        "home_company_xmlid": f"{MODULE}.company_dataverse",
        "allowed_company_xmlids": [
            f"{MODULE}.company_dataverse",
            f"{MODULE}.company_w9",
            f"{MODULE}.company_evidencelab",
        ],
    },
]

# ---------------- Integrations (Zoho + AI keys) ----------------
# Zoho SMTP: configure via env vars (recommended)
ZOHO_ENABLE = os.getenv("ODOO_ZOHO_ENABLE", "0").strip() == "1"
ZOHO_SMTP_NAME = os.getenv("ODOO_ZOHO_SMTP_NAME", "Zoho SMTP").strip()
ZOHO_SMTP_HOST = os.getenv("ODOO_ZOHO_SMTP_HOST", "smtp.zoho.com").strip()
ZOHO_SMTP_PORT = int(os.getenv("ODOO_ZOHO_SMTP_PORT", "587").strip())
ZOHO_SMTP_USER = os.getenv("ODOO_ZOHO_SMTP_USER", "").strip()
ZOHO_SMTP_PASS = os.getenv("ODOO_ZOHO_SMTP_PASS", "").strip()
ZOHO_SMTP_ENC  = os.getenv("ODOO_ZOHO_SMTP_ENCRYPTION", "starttls").strip()

# Mail alias domain (affects mail aliases like help@yourdomain)
ALIAS_DOMAIN = os.getenv("ODOO_MAIL_ALIAS_DOMAIN", "").strip()  # e.g. insightpulseai.com
CATCHALL_ALIAS = os.getenv("ODOO_MAIL_CATCHALL_ALIAS", "catchall").strip()
BOUNCE_ALIAS   = os.getenv("ODOO_MAIL_BOUNCE_ALIAS", "bounce").strip()

# AI keys: pass JSON map {"some.icp.key":"value", ...} (so we don't invent names)
AI_KEYS_JSON = os.getenv("ODOO_AI_KEYS_JSON", "").strip()


# ---------------- execution (odoo shell provides `env`) ----------------
created_companies = {}

for c in COMPANIES:
    country = country_by_code(env, c.get("country_code"))
    vals = {
        "name": sanitize_name(c["name"]),
        "email": c.get("email") or False,
        "phone": c.get("phone") or False,
        "street": c.get("street") or False,
        "street2": c.get("street2") or False,
        "city": c.get("city") or False,
        "vat": c.get("vat") or False,
        "country_id": country.id if country else False,
        # Use footer/header for human notes; safe and visible in reports
        "report_footer": c.get("comment") or False,
    }
    company = upsert_company(env, c["xmlid"], vals)
    created_companies[c["xmlid"]] = company

    # Bind & update the company partner deterministically
    partner_xmlid = c["xmlid"].replace("company_", "partner_")
    upsert_partner_for_company(env, partner_xmlid, company, {
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
        vals={"name": u["name"], "email": u.get("email") or False, "active": True},
        groups_xmlids=u.get("groups") or [],
        home_company=home,
        allowed_companies=allowed,
    )
    print(f"USER ok: {user.login} home={home.name} allowed={[c.name for c in allowed]}")

# Zoho Mail SMTP + alias domain (best-effort ICP keys)
if ZOHO_ENABLE:
    if not (ZOHO_SMTP_USER and ZOHO_SMTP_PASS):
        raise RuntimeError("ZOHO enabled but ODOO_ZOHO_SMTP_USER/PASS not set")
    ensure_mail_server(env, ZOHO_SMTP_NAME, ZOHO_SMTP_HOST, ZOHO_SMTP_PORT, ZOHO_SMTP_USER, ZOHO_SMTP_PASS, ZOHO_SMTP_ENC)

    # Common ICP keys across versions/setups; harmless if unused.
    set_icp(env, "mail.catchall.alias", CATCHALL_ALIAS)
    set_icp(env, "mail.bounce.alias", BOUNCE_ALIAS)

    if ALIAS_DOMAIN:
        set_icp(env, "mail.catchall.domain", ALIAS_DOMAIN)
        # Some setups may also check this key name (non-fatal)
        set_icp(env, "mail.alias_domain", ALIAS_DOMAIN)

# AI API keys (store exactly what you specify)
if AI_KEYS_JSON:
    try:
        data = json.loads(AI_KEYS_JSON)
        if not isinstance(data, dict):
            raise ValueError("ODOO_AI_KEYS_JSON must be a JSON object map")
        for k, v in data.items():
            if not isinstance(k, str):
                continue
            set_icp(env, k, str(v))
    except Exception as e:
        raise RuntimeError(f"Invalid ODOO_AI_KEYS_JSON: {e}")

print("✅ Seed complete")
print("Companies:", [created_companies[x].name for x in created_companies])
print("Users:", [ref(env, u['xmlid']).login for u in USERS if ref(env, u["xmlid"])])
