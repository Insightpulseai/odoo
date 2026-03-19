#!/usr/bin/env python3
"""Seed benchmark personas into Odoo.

Creates 7 test users with correct group memberships for benchmark execution.
Run against a running Odoo instance before executing benchmarks.

Usage:
    python scripts/benchmark/seed_personas.py --url http://localhost:8069 --db odoo_dev
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request

PERSONAS = [
    {
        "login": "bench_sales_rep",
        "name": "Benchmark Sales Rep",
        "password": "benchmark",
        "groups": ["sales_team.group_sale_salesman"],
    },
    {
        "login": "bench_sales_mgr",
        "name": "Benchmark Sales Manager",
        "password": "benchmark",
        "groups": ["sales_team.group_sale_manager"],
    },
    {
        "login": "bench_accountant",
        "name": "Benchmark Accountant",
        "password": "benchmark",
        "groups": ["account.group_account_user"],
    },
    {
        "login": "bench_inv_operator",
        "name": "Benchmark Inventory Operator",
        "password": "benchmark",
        "groups": ["stock.group_stock_user"],
    },
    {
        "login": "bench_project_mgr",
        "name": "Benchmark Project Manager",
        "password": "benchmark",
        "groups": ["project.group_project_manager"],
    },
    # admin — uses existing admin user, no seed needed
    {
        "login": "bench_exec_readonly",
        "name": "Benchmark Read-Only Executive",
        "password": "benchmark",
        "groups": ["base.group_user"],
    },
]


def rpc_call(url: str, service: str, method: str, args: list) -> object:
    """JSON-RPC call to Odoo."""
    payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "call",
        "params": {"service": service, "method": method, "args": args},
        "id": 1,
    }).encode()
    req = urllib.request.Request(
        f"{url}/jsonrpc",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())
    if result.get("error"):
        err = result["error"]
        msg = err.get("data", {}).get("message", str(err))
        raise RuntimeError(f"RPC error: {msg}")
    return result.get("result")


def resolve_group_id(url: str, db: str, uid: int, password: str, xml_id: str) -> int | None:
    """Resolve an XML ID to a database ID."""
    parts = xml_id.split(".")
    if len(parts) != 2:
        return None
    module, name = parts
    result = rpc_call(url, "object", "execute_kw", [
        db, uid, password, "ir.model.data", "search_read",
        [[["module", "=", module], ["name", "=", name]]],
        {"fields": ["res_id"], "limit": 1},
    ])
    if result:
        return result[0]["res_id"]
    return None


def main():
    parser = argparse.ArgumentParser(description="Seed benchmark personas")
    parser.add_argument("--url", default="http://localhost:8069", help="Odoo URL")
    parser.add_argument("--db", default="odoo_dev", help="Odoo database")
    parser.add_argument("--admin-password", default="admin", help="Admin password")
    args = parser.parse_args()

    # Authenticate as admin
    uid = rpc_call(args.url, "common", "authenticate", [args.db, "admin", args.admin_password, {}])
    if not uid:
        print("ERROR: Admin authentication failed")
        sys.exit(1)
    print(f"Authenticated as admin (uid={uid})")

    for persona in PERSONAS:
        login = persona["login"]
        print(f"  Seeding {login}...", end=" ", flush=True)

        # Check if user exists
        existing = rpc_call(args.url, "object", "execute_kw", [
            args.db, uid, args.admin_password, "res.users", "search_read",
            [[["login", "=", login]]],
            {"fields": ["id"], "limit": 1},
        ])

        if existing:
            print(f"exists (id={existing[0]['id']})")
            continue

        # Resolve group IDs
        group_ids = []
        for xml_id in persona["groups"]:
            gid = resolve_group_id(args.url, args.db, uid, args.admin_password, xml_id)
            if gid:
                group_ids.append(gid)
            else:
                print(f"\n    WARNING: group {xml_id} not found — skipping")

        # Create user
        try:
            user_id = rpc_call(args.url, "object", "execute_kw", [
                args.db, uid, args.admin_password, "res.users", "create",
                [{
                    "login": login,
                    "name": persona["name"],
                    "password": persona["password"],
                    "groups_id": [(6, 0, group_ids)],
                }],
                {},
            ])
            print(f"created (id={user_id})")
        except RuntimeError as e:
            print(f"ERROR: {e}")

    print("\nPersona seeding complete.")


if __name__ == "__main__":
    main()
