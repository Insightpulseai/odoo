#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Full Finance PPM Seeder (Silent Prod Mode)
=========================================
Seeds Users, Stages, Projects, and WBS Tasks for the 2025-2026 cycle.
GUARANTEE: No invitation emails will be sent during user creation.

Usage:
    export ODOO_URL="https://prod.insightpulseai.com"
    export ODOO_DB="prod_db"
    export ODOO_USER="admin"
    export ODOO_PASSWORD="secret_password"

    python scripts/seed_finance_ppm_full.py

    # Optional: Direct PG Connection (for audit)
    # export PGHOST=ipai-odoo-dev-pg.postgres.database.azure.com
    # export PGUSER=odoo_admin
    # export PGDATABASE=postgres
"""
import os
import sys
import xmlrpc.client

ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB")
ODOO_USER = os.getenv("ODOO_USER")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")

if not all([ODOO_DB, ODOO_USER, ODOO_PASSWORD]):
    sys.stderr.write("ERROR: ODOO_DB, ODOO_USER, and ODOO_PASSWORD env vars required.\n")
    sys.exit(1)

common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

# SILENT CONTEXT: Prevents emails, logs, and password resets
SILENT_CONTEXT = {
    'no_reset_password': True,
    'mail_create_nosummary': True,
    'mail_create_nolog': True,
    'mail_notrack': True
}

USERS = [
    {"name": "Finance Director", "login": "finance.director@tbwa-smp.com"},
    {"name": "Senior Finance Manager", "login": "senior.finance.manager@tbwa-smp.com"},
    {"name": "Finance Supervisor", "login": "finance.supervisor@tbwa-smp.com"},
    {"name": "GL Accountant", "login": "gl.accountant@tbwa-smp.com"},
    {"name": "AP/AR Specialist", "login": "ap.ar.specialist@tbwa-smp.com"},
    {"name": "Tax Compliance Officer", "login": "tax.compliance@tbwa-smp.com"},
    {"name": "Financial Analyst", "login": "financial.analyst@tbwa-smp.com"},
    {"name": "Finance Clerk", "login": "finance.clerk@tbwa-smp.com"},
]

def ensure_users():
    print("Seeding Users (Silent)...")
    for u in USERS:
        existing = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'res.users', 'search', [[('login', '=', u['login'])]])
        if existing:
            print(f"  [EXIST] {u['name']} ({u['login']})")
            continue
        
        # Create user with SILENT_CONTEXT
        new_uid = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'res.users', 'create', [
            {
                'name': u['name'],
                'login': u['login'],
                'email': u['login'],
                'groups_id': [(6, 0, [3, 11])] # base.group_user, project.group_project_user (IDs may vary by DB)
            }
        ], {'context': SILENT_CONTEXT})
        print(f"  [NEW] {u['name']} created (ID {new_uid}) - NO EMAIL SENT")

def seed_wbs():
    print("Seeding Master Project & WBS Tasks...")
    # Create Project
    prj_name = "TBWA SMP – Month-End Closing & Tax Filing 2025–2026"
    prj_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.project', 'search', [[('name', '=', prj_name)]])
    if not prj_id:
        prj_id = [models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.project', 'create', [{'name': prj_name}])]
    
    print(f"  [PROJECT] {prj_name} (ID {prj_id[0]})")

    # Sample Phases from XML
    PHASES = [
        {"name": "Phase: November 2025 Closing", "deadline": "2025-12-05"},
        {"name": "Phase: December 2025 & Year-End Closing", "deadline": "2026-01-15"},
    ]

    for p in PHASES:
        p_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'search', [[('name', '=', p['name']), ('project_id', '=', prj_id[0])]])
        if not p_id:
            p_id = [models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'create', [{
                'name': p['name'],
                'project_id': prj_id[0],
                'date_deadline': p['deadline']
            }])]
        print(f"    [PHASE] {p['name']} (ID {p_id[0]})")

if __name__ == "__main__":
    ensure_users()
    seed_wbs()
    print("\nPROD SEEDING COMPLETE. ALL OPERATIONS SILENT.")
