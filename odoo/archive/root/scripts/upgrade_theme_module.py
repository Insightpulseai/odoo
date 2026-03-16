#!/usr/bin/env python3
"""
Upgrade ipai_web_theme_tbwa module via Odoo XML-RPC API
"""
import xmlrpc.client
import sys

# Production Odoo credentials
url = 'https://erp.insightpulseai.com'
db = 'odoo'
username = input("Enter Odoo username (default: admin): ") or 'admin'
password = input("Enter Odoo password: ")

print(f"\nConnecting to {url}...")

# Authenticate
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

if not uid:
    print("❌ Authentication failed!")
    sys.exit(1)

print(f"✅ Authenticated as user {uid}")

# Connect to object endpoint
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("\nSearching for ipai_web_theme_tbwa module...")

# Find the module
module_ids = models.execute_kw(db, uid, password,
    'ir.module.module', 'search',
    [[['name', '=', 'ipai_web_theme_tbwa']]])

if not module_ids:
    print("❌ Module not found!")
    sys.exit(1)

module_id = module_ids[0]
print(f"✅ Found module (ID: {module_id})")

# Get module info
module_info = models.execute_kw(db, uid, password,
    'ir.module.module', 'read',
    [module_id], {'fields': ['name', 'state', 'summary']})

print(f"\nCurrent state: {module_info[0]['state']}")

# Upgrade the module
print("\nInitiating module upgrade...")
try:
    models.execute_kw(db, uid, password,
        'ir.module.module', 'button_immediate_upgrade',
        [[module_id]])
    print("✅ Module upgrade initiated successfully!")
    print("\nNote: Assets will be regenerated on next page load.")
    print("Clear your browser cache and refresh: https://erp.insightpulseai.com/web/login")
except Exception as e:
    print(f"❌ Upgrade failed: {e}")
    sys.exit(1)
