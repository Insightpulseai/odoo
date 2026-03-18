#!/usr/bin/env python3
"""Odoo 19 Production Seed — Users & Companies.

Two execution modes:

  A) odoo shell (inside container):
     odoo shell -d odoo -c /etc/odoo/odoo.conf < seed_prod_users.py

  B) JSON-RPC (remote, no container access):
     python3 seed_prod_users.py --jsonrpc

IMPORTANT: Uses no_reset_password context to suppress email invites.
Idempotent — safe to re-run (uses search-or-create pattern).

Odoo 19 notes:
  - Field name is 'group_ids' (not 'groups_id' as in Odoo 18)
  - Portal and Internal User are exclusive groups — cannot assign both
  - Portal users must be created WITHOUT groups, then patched via write()
"""

import sys

# ============================================================================
# Shared configuration
# ============================================================================

COMPANIES = [
    {
        'name': 'InsightPulse AI',
        'street': 'BGC, Taguig City',
        'city': 'Manila',
        'email': 'business@insightpulseai.com',
        'website': 'https://insightpulseai.com',
    },
    {
        'name': 'TBWA\\Santiago Mangada Puno',
        'street': 'Makati City',
        'city': 'Manila',
    },
]

# Users — portal user is handled separately due to exclusive group constraint
INTERNAL_USERS = [
    {
        'name': 'CEO',
        'login': 'ceo@insightpulseai.com',
        'password': 'changeme',
        'group_xmlids': ['base.group_system', 'base.group_erp_manager'],
    },
    {
        'name': 'DevOps',
        'login': 'devops@insightpulseai.com',
        'password': 'changeme',
        'group_xmlids': ['base.group_system'],
    },
    {
        'name': 'Finance Manager',
        'login': 'finance@insightpulseai.com',
        'password': 'changeme',
        'group_xmlids': ['account.group_account_manager'],
    },
    {
        'name': 'Project Manager',
        'login': 'pm@insightpulseai.com',
        'password': 'changeme',
        'group_xmlids': ['project.group_project_manager'],
    },
]

PORTAL_USERS = [
    {
        'name': 'Portal User',
        'login': 'portal@insightpulseai.com',
        'password': 'changeme',
    },
]


# ============================================================================
# Mode A: odoo shell
# ============================================================================

def run_shell_mode():
    """Execute via odoo shell (cr and SUPERUSER_ID available in scope)."""
    from odoo import SUPERUSER_ID
    from odoo.api import Environment

    env = Environment(cr, SUPERUSER_ID, {  # noqa: F821 — cr is injected by odoo shell
        'no_reset_password': True,
        'mail_create_nosubscribe': True,
        'mail_notrack': True,
    })

    # -- Companies --
    print("\n=== Seeding Companies ===")
    for vals in COMPANIES:
        vals_copy = dict(vals)
        try:
            vals_copy['country_id'] = env.ref('base.ph').id
            vals_copy['currency_id'] = env.ref('base.PHP').id
        except Exception:
            pass
        existing = env['res.company'].search([('name', '=', vals_copy['name'])], limit=1)
        if existing:
            print(f"  SKIP company: {vals_copy['name']} (exists, id={existing.id})")
        else:
            rec = env['res.company'].create(vals_copy)
            print(f"  CREATE company: {vals_copy['name']} (id={rec.id})")

    ipai = env['res.company'].search([('name', '=', 'InsightPulse AI')], limit=1)
    if not ipai:
        ipai = env['res.company'].search([], limit=1)

    # -- Internal Users --
    print("\n=== Seeding Internal Users ===")
    ctx = dict(no_reset_password=True, mail_create_nosubscribe=True, mail_notrack=True)
    for u in INTERNAL_USERS:
        existing = env['res.users'].with_context(**ctx).search(
            [('login', '=', u['login'])], limit=1
        )
        if existing:
            print(f"  SKIP user: {u['login']} (exists, id={existing.id})")
            continue
        group_cmds = []
        for xmlid in u['group_xmlids']:
            try:
                group_cmds.append((4, env.ref(xmlid).id))
            except Exception:
                print(f"    WARN: group {xmlid} not found, skipping")
        user_vals = {
            'name': u['name'],
            'login': u['login'],
            'password': u['password'],
            'company_id': ipai.id,
            'company_ids': [(4, ipai.id)],
            'group_ids': group_cmds,
        }
        user = env['res.users'].with_context(**ctx).create(user_vals)
        print(f"  CREATE user: {u['login']} (id={user.id})")

    # -- Portal Users (exclusive group — create without groups, then patch) --
    print("\n=== Seeding Portal Users ===")
    grp_internal = env.ref('base.group_user').id
    grp_portal = env.ref('base.group_portal').id
    for u in PORTAL_USERS:
        existing = env['res.users'].with_context(**ctx).search(
            [('login', '=', u['login'])], limit=1
        )
        if existing:
            print(f"  SKIP user: {u['login']} (exists, id={existing.id})")
            continue
        user_vals = {
            'name': u['name'],
            'login': u['login'],
            'password': u['password'],
            'company_id': ipai.id,
            'company_ids': [(4, ipai.id)],
        }
        user = env['res.users'].with_context(**ctx).create(user_vals)
        # Remove internal group, add portal group
        user.write({'group_ids': [(3, grp_internal), (4, grp_portal)]})
        print(f"  CREATE user: {u['login']} (id={user.id}, portal=True)")

    env.cr.commit()
    print("\n=== Seed complete. Users created without email invites. ===")
    print("IMPORTANT: Change all 'changeme' passwords immediately.")


# ============================================================================
# Mode B: JSON-RPC (remote)
# ============================================================================

def run_jsonrpc_mode():
    """Execute via JSON-RPC against a running Odoo instance."""
    import json
    import urllib.request

    URL = "https://erp.insightpulseai.com/jsonrpc"
    DB = "odoo"
    UID = 2
    PWD = "admin"

    def rpc(service, method, *args):
        payload = json.dumps({
            "jsonrpc": "2.0", "method": "call", "id": 1,
            "params": {"service": service, "method": method, "args": list(args)},
        }).encode()
        req = urllib.request.Request(URL, payload, {"Content-Type": "application/json"})
        resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
        if "error" in resp:
            raise RuntimeError(resp["error"]["data"]["message"])
        return resp["result"]

    def call(model, method, args=None, kwargs=None):
        return rpc("object", "execute_kw", DB, UID, PWD, model, method,
                    args or [], kwargs or {})

    def get_group(xmlid):
        module, name = xmlid.split(".")
        ids = call("ir.model.data", "search_read",
                    [[(("module", "=", module)), ("name", "=", name),
                      ("model", "=", "res.groups")]],
                    {"fields": ["res_id"], "limit": 1})
        return ids[0]["res_id"] if ids else None

    no_email_ctx = {"context": {
        "no_reset_password": True,
        "mail_create_nosubscribe": True,
        "mail_notrack": True,
    }}

    # -- Companies --
    print("\n=== Seeding Companies ===")
    cos = call("res.company", "search_read", [[]], {"fields": ["id", "name"]})
    ipai_id = cos[0]["id"]
    for c in cos:
        print(f"  EXISTS company: {c['name']} (id={c['id']})")

    ph_ids = call("res.country", "search", [[("code", "=", "PH")]])
    php_ids = call("res.currency", "search", [[("name", "=", "PHP")]])

    main_co = cos[0]
    if main_co["name"] == "My Company":
        vals = {
            "name": "InsightPulse AI",
            "street": "BGC, Taguig City",
            "city": "Manila",
            "email": "business@insightpulseai.com",
            "website": "https://insightpulseai.com",
        }
        if ph_ids:
            vals["country_id"] = ph_ids[0]
        if php_ids:
            vals["currency_id"] = php_ids[0]
        call("res.company", "write", [[main_co["id"]], vals])
        print(f"  RENAME company: My Company -> InsightPulse AI (id={main_co['id']})")

    tbwa_exists = call("res.company", "search", [[("name", "like", "TBWA")]])
    if not tbwa_exists:
        vals = {"name": "TBWA\\Santiago Mangada Puno", "street": "Makati City", "city": "Manila"}
        if ph_ids:
            vals["country_id"] = ph_ids[0]
        if php_ids:
            vals["currency_id"] = php_ids[0]
        tbwa_id = call("res.company", "create", [vals])
        print(f"  CREATE company: TBWA\\SMP (id={tbwa_id})")

    # -- Internal Users --
    print("\n=== Seeding Internal Users ===")
    for u in INTERNAL_USERS:
        existing = call("res.users", "search", [[("login", "=", u["login"])]])
        if existing:
            print(f"  SKIP user: {u['login']} (exists, id={existing[0]})")
            continue
        groups = [g for g in [get_group(x) for x in u["group_xmlids"]] if g]
        create_vals = {
            "name": u["name"],
            "login": u["login"],
            "password": u["password"],
            "company_id": ipai_id,
            "company_ids": [(4, ipai_id)],
        }
        new_id = rpc("object", "execute_kw", DB, UID, PWD,
                      "res.users", "create", [create_vals], no_email_ctx)
        print(f"  CREATE user: {u['login']} (id={new_id})")
        if groups:
            call("res.users", "write", [[new_id], {"group_ids": [(4, g) for g in groups]}])
            print(f"    assigned {len(groups)} groups")

    # -- Portal Users --
    print("\n=== Seeding Portal Users ===")
    grp_internal = get_group("base.group_user")
    grp_portal = get_group("base.group_portal")
    for u in PORTAL_USERS:
        existing = call("res.users", "search", [[("login", "=", u["login"])]])
        if existing:
            print(f"  SKIP user: {u['login']} (exists, id={existing[0]})")
            continue
        create_vals = {
            "name": u["name"],
            "login": u["login"],
            "password": u["password"],
            "company_id": ipai_id,
            "company_ids": [(4, ipai_id)],
        }
        new_id = rpc("object", "execute_kw", DB, UID, PWD,
                      "res.users", "create", [create_vals], no_email_ctx)
        # Remove internal group, add portal group (exclusive constraint)
        if grp_internal:
            call("res.users", "write", [[new_id], {"group_ids": [(3, grp_internal)]}])
        if grp_portal:
            call("res.users", "write", [[new_id], {"group_ids": [(4, grp_portal)]}])
        print(f"  CREATE user: {u['login']} (id={new_id}, portal=True)")

    print("\n=== Seed complete. No emails sent. ===")
    print("IMPORTANT: Change all 'changeme' passwords immediately.")


# ============================================================================
# Entry point
# ============================================================================

if __name__ == "__main__":
    if "--jsonrpc" in sys.argv:
        run_jsonrpc_mode()
    else:
        print("Usage: python3 seed_prod_users.py --jsonrpc")
        print("   or: odoo shell -d odoo < seed_prod_users.py")
        sys.exit(1)
else:
    # Running inside odoo shell (cr is injected)
    run_shell_mode()
