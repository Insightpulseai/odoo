import os

OLD_COMPANY_NAME = os.getenv("ODOO_OLD_COMPANY_NAME", "YourCompany")
NEW_COMPANY_NAME = os.getenv("ODOO_NEW_COMPANY_NAME", "InsightPulseAI")
TBWA_COMPANY_NAME = os.getenv("ODOO_TBWA_COMPANY_NAME", r"TBWA\SMP")
TARGET_USER_LOGIN = os.getenv("ODOO_TARGET_USER_LOGIN", "admin")

Company = env["res.company"].sudo()
Users = env["res.users"].sudo()
Groups = env["res.groups"].sudo()

# 1) Rename existing company (prefer exact match; fallback to first company)
old = Company.search([("name", "=", OLD_COMPANY_NAME)], limit=1)
if not old:
    old = Company.search([], limit=1)
if not old:
    raise RuntimeError("No company found to rename.")

old.write({"name": NEW_COMPANY_NAME})
if old.partner_id:
    old.partner_id.write({"name": NEW_COMPANY_NAME})

# 2) Create TBWA\SMP if missing
tbwa = Company.search([("name", "=", TBWA_COMPANY_NAME)], limit=1)
if not tbwa:
    tbwa = Company.create({"name": TBWA_COMPANY_NAME})
    if tbwa.partner_id:
        tbwa.partner_id.write({"name": TBWA_COMPANY_NAME})

# 3) Ensure target user can switch companies
user = Users.search([("login", "=", TARGET_USER_LOGIN)], limit=1)
if not user:
    raise RuntimeError(f"User not found: {TARGET_USER_LOGIN}")

# Multi-company group (best-effort)
group_multi = Groups.search([("xml_id", "=", "base.group_multi_company")], limit=1)
if not group_multi:
    group_multi = Groups.search([("name", "ilike", "Multi")], limit=1)
if group_multi:
    user.groups_id = [(4, group_multi.id)]

allowed = set(user.company_ids.ids)
allowed.update([old.id, tbwa.id])
user.company_ids = [(6, 0, list(allowed))]
user.company_id = old.id  # default = InsightPulseAI

print("OK")
print("Renamed:", old.id, old.name)
print("TBWA:", tbwa.id, tbwa.name)
print("User:", user.login, "default=", user.company_id.name, "allowed=", [c.name for c in user.company_ids])
