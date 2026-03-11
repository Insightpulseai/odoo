import os, sys
import xmlrpc.client

ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "odoo")
ODOO_USER = os.getenv("ODOO_USER", "admin")
ODOO_PASS = os.getenv("ODOO_PASS")

if not ODOO_PASS:
    print("Set ODOO_PASS in env", file=sys.stderr)
    sys.exit(2)

OLD_COMPANY_NAME = os.getenv("ODOO_OLD_COMPANY_NAME", "YourCompany")
NEW_COMPANY_NAME = os.getenv("ODOO_NEW_COMPANY_NAME", "InsightPulseAI")
NEW_COMPANY_EMAIL = os.getenv("ODOO_NEW_COMPANY_EMAIL", "business@insightpulseai.com")
NEW_COMPANY_WEBSITE = os.getenv(
    "ODOO_NEW_COMPANY_WEBSITE", "https://insightpulseai.com"
)
TBWA_COMPANY_NAME = os.getenv("ODOO_TBWA_COMPANY_NAME", r"TBWA\SMP")
TBWA_COMPANY_EMAIL = os.getenv("ODOO_TBWA_COMPANY_EMAIL", "business@insightpulseai.com")
TARGET_USER_LOGIN = os.getenv("ODOO_TARGET_USER_LOGIN", "admin")

common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
if not uid:
    raise RuntimeError("Authentication failed")

models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")


def search(model, domain, limit=0):
    return models.execute_kw(
        ODOO_DB,
        uid,
        ODOO_PASS,
        model,
        "search",
        [domain],
        {"limit": limit} if limit else {},
    )


def read(model, ids, fields):
    return models.execute_kw(
        ODOO_DB, uid, ODOO_PASS, model, "read", [ids], {"fields": fields}
    )


def write(model, ids, vals):
    return models.execute_kw(ODOO_DB, uid, ODOO_PASS, model, "write", [ids, vals])


def create(model, vals):
    return models.execute_kw(ODOO_DB, uid, ODOO_PASS, model, "create", [vals])


# find company to rename
cid = search("res.company", [["name", "=", OLD_COMPANY_NAME]], limit=1)
if not cid:
    cid = search("res.company", [], limit=1)
if not cid:
    raise RuntimeError("No company found")
cid = cid[0]

write(
    "res.company",
    [cid],
    {
        "name": NEW_COMPANY_NAME,
        "email": NEW_COMPANY_EMAIL,
        "website": NEW_COMPANY_WEBSITE,
    },
)

# create TBWA if missing
tbwa = search("res.company", [["name", "=", TBWA_COMPANY_NAME]], limit=1)
if not tbwa:
    tbwa_id = create(
        "res.company", {"name": TBWA_COMPANY_NAME, "email": TBWA_COMPANY_EMAIL}
    )
else:
    tbwa_id = tbwa[0]

# update user allowed companies + default
u = search("res.users", [["login", "=", TARGET_USER_LOGIN]], limit=1)
if not u:
    raise RuntimeError("Target user not found")
u = u[0]
uinfo = read("res.users", [u], ["company_ids"])[0]
allowed = set(uinfo.get("company_ids", []))
allowed.update([cid, tbwa_id])

# (6,0,ids) sets allowed companies; company_id sets default company
write("res.users", [u], {"company_ids": [(6, 0, list(allowed))], "company_id": cid})

print("OK")
print("renamed_company_id", cid)
print("tbwa_company_id", tbwa_id)
