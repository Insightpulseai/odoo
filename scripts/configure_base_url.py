#!/usr/bin/env python3
import os
import xmlrpc.client
import ssl
import argparse

# Usage: python3 scripts/configure_base_url.py https://erp.insightpulseai.net

def set_base_url(target_url):
    url = os.environ.get('ODOO_URL', 'http://localhost:8069')
    db = os.environ.get('ODOO_DB', 'odoo')
    username = os.environ.get('ODOO_USER', 'admin')
    password = os.environ.get('ODOO_PASSWORD', 'admin')

    print(f"📡 Connecting to {url} (DB: {db})...")

    try:
        context = ssl._create_unverified_context()
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', context=context)
        uid = common.authenticate(db, username, password, {})
        
        if not uid:
            print("❌ Authentication Failed.")
            return

        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', context=context)
        
        # 1. Set web.base.url
        print(f"🔧 Setting web.base.url = {target_url}")
        models.execute_kw(db, uid, password, 'ir.config_parameter', 'set_param', ['web.base.url', target_url])
        
        # 2. Set web.base.url.freeze = True
        print(f"❄️  Freezing web.base.url (web.base.url.freeze = True)")
        models.execute_kw(db, uid, password, 'ir.config_parameter', 'set_param', ['web.base.url.freeze', 'True'])
        
        print("✅ Success. Redirect URI mismatch should be resolved.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="The base URL (e.g., https://erp.insightpulseai.net)")
    args = parser.parse_args()
    
    set_base_url(args.url)
