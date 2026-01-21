# Odoo 18 CE — company bootstrap (no UI)
# Run with: docker exec -i <odoo_container> odoo shell -d odoo --no-http < scripts/odoo/company_bootstrap.py
import os

TARGET_DB = os.getenv("ODOO_DB", "odoo")
OLD_COMPANY_NAME = os.getenv("ODOO_OLD_COMPANY_NAME", "YourCompany")
NEW_COMPANY_NAME = os.getenv("ODOO_NEW_COMPANY_NAME", "InsightPulseAI")
NEW_COMPANY_EMAIL = os.getenv("ODOO_NEW_COMPANY_EMAIL", "business@insightpulseai.com")
NEW_COMPANY_WEBSITE = os.getenv(
    "ODOO_NEW_COMPANY_WEBSITE", "https://insightpulseai.net"
)

TBWA_COMPANY_NAME = os.getenv("ODOO_TBWA_COMPANY_NAME", r"TBWA\SMP")
TBWA_COMPANY_EMAIL = os.getenv("ODOO_TBWA_COMPANY_EMAIL", "business@insightpulseai.com")
TBWA_COMPANY_WEBSITE = os.getenv("ODOO_TBWA_COMPANY_WEBSITE", "")

TARGET_USER_LOGIN = os.getenv("ODOO_TARGET_USER_LOGIN", "admin")

# Currency/Country defaults (PH)
COUNTRY_CODE = os.getenv("ODOO_COUNTRY_CODE", "PH")
CURRENCY_CODE = os.getenv("ODOO_CURRENCY_CODE", "PHP")

env.cr.execute("SELECT 1")  # ensure cursor live

Company = env["res.company"].sudo()
Users = env["res.users"].sudo()
Groups = env["res.groups"].sudo()
Country = env["res.country"].sudo()
Currency = env["res.currency"].sudo()


def must_one(recordset, msg):
    if not recordset or len(recordset) != 1:
        raise RuntimeError(f"{msg} (found={len(recordset) if recordset else 0})")
    return recordset


def get_country(code):
    r = Country.search([("code", "=", code)], limit=1)
    if not r:
        r = Country.search([("name", "ilike", "Philippines")], limit=1)
    return r


def get_currency(code):
    r = Currency.search([("name", "=", code)], limit=1)
    if not r:
        r = Currency.search([("symbol", "=", "₱")], limit=1)
    return r


country = get_country(COUNTRY_CODE)
currency = get_currency(CURRENCY_CODE)

# 1) Rename existing company
old = Company.search([("name", "=", OLD_COMPANY_NAME)], limit=1)
if not old:
    # fallback: try first company
    old = Company.search([], limit=1)

if not old:
    raise RuntimeError("No company found to rename.")

old.write(
    {
        "name": NEW_COMPANY_NAME,
        "email": NEW_COMPANY_EMAIL,
        "website": NEW_COMPANY_WEBSITE,
    }
)
# keep partner aligned (header pulls from company.name but partner is what invoices/contacts show)
if old.partner_id:
    old.partner_id.write(
        {
            "name": NEW_COMPANY_NAME,
            "email": NEW_COMPANY_EMAIL,
            "website": NEW_COMPANY_WEBSITE,
            **({"country_id": country.id} if country else {}),
        }
    )
if currency and old.currency_id != currency:
    old.currency_id = currency.id
if country and old.country_id != country:
    old.country_id = country.id

# 2) Create TBWA\SMP company if missing
tbwa = Company.search([("name", "=", TBWA_COMPANY_NAME)], limit=1)
if not tbwa:
    vals = {
        "name": TBWA_COMPANY_NAME,
        "email": TBWA_COMPANY_EMAIL,
        "website": TBWA_COMPANY_WEBSITE,
    }
    if currency:
        vals["currency_id"] = currency.id
    if country:
        vals["country_id"] = country.id
    tbwa = Company.create(vals)
    if tbwa.partner_id:
        tbwa.partner_id.write(
            {
                "name": TBWA_COMPANY_NAME,
                "email": TBWA_COMPANY_EMAIL,
                "website": TBWA_COMPANY_WEBSITE,
                **({"country_id": country.id} if country else {}),
            }
        )

# 3) Grant multi-company access to target user and allow both companies
user = Users.search([("login", "=", TARGET_USER_LOGIN)], limit=1)
if not user:
    raise RuntimeError(f"Target user not found: login={TARGET_USER_LOGIN}")

group_multi = Groups.search([("xml_id", "=", "base.group_multi_company")], limit=1)
if not group_multi:
    # fallback by name (varies by language/labels)
    group_multi = Groups.search([("name", "ilike", "Multi Companies")], limit=1)

if group_multi:
    user.groups_id = [(4, group_multi.id)]

allowed = set(user.company_ids.ids)
allowed.update([old.id, tbwa.id])
user.company_ids = [(6, 0, list(allowed))]

# Default company stays InsightPulseAI (renamed old)
user.company_id = old.id

# 4) Output (logs)
print("OK")
print("Renamed company:", old.id, old.name)
print("TBWA company:", tbwa.id, tbwa.name)
print(
    "User updated:",
    user.id,
    user.login,
    "default_company=",
    user.company_id.name,
    "allowed=",
    [c.name for c in user.company_ids],
)
