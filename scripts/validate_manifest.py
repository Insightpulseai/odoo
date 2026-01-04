#!/usr/bin/env python3
import os
import ast
import sys
import xmlrpc.client
import ssl

# --- CONFIGURATION ---
ADDONS_DIR = "."

# Fallback list if server is offline (Expanded Core for robust pre-commit/offline checks)
# Includes standard Odoo 18 Core modules and common external deps to prevent false positives when offline.
FALLBACK_CORE = {
    'base', 'web', 'mail', 'account', 'sale', 'purchase', 'stock', 'crm', 
    'project', 'website', 'point_of_sale', 'hr', 'mrp', 'base_setup', 
    'bus', 'web_editor', 'web_tour', 'portal', 'digest', 'auth_signup',
    'product', 'analytic', 'resource', 'utm', 'iap', 'http_routing',
    'uom', 'contacts', 'calendar', 'spreadsheet', 'board',
    # Common External/OCA dependencies
    'server_mode', 'web_responsive', 'queue_job', 'sentry'
}

def load_manifest(manifest_path):
    try:
        with open(manifest_path, 'r') as f:
            return ast.literal_eval(f.read())
    except Exception as e:
        print(f"❌ SYNTAX ERROR: Could not parse {manifest_path}: {e}")
        return None

def get_live_modules():
    """Connects to Odoo via XML-RPC to get all available modules."""
    url = os.environ.get('ODOO_URL', 'http://localhost:8069')
    db = os.environ.get('ODOO_DB', 'odoo')
    username = os.environ.get('ODOO_USER', 'admin')
    password = os.environ.get('ODOO_PASSWORD', 'admin')

    # Only attempt connection if explicitly requested or if we are in an environment that likely has access
    # But for a robust check, let's try if the env vars suggest it, otherwise default to fallback quickly?
    # actually user's script tries to connect by default with defaults.
    
    print(f"📡 Connecting to Odoo at {url} (DB: {db})...")

    try:
        # Ignore SSL verification if using self-signed certs (common in dev)
        context = ssl._create_unverified_context()
        
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', context=context)
        uid = common.authenticate(db, username, password, {})
        
        if not uid:
            print("⚠️  Authentication Failed: Could not login to Odoo. Using fallback list.")
            return FALLBACK_CORE

        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', context=context)
        
        # Fetch ALL modules known to Odoo (installed or uninstalled)
        module_ids = models.execute_kw(db, uid, password,
            'ir.module.module', 'search_read',
            [[]], 
            {'fields': ['name']}
        )
        
        live_modules = {m['name'] for m in module_ids}
        print(f"✅ Retrieved {len(live_modules)} modules from live database.")
        return live_modules

    except Exception as e:
        print(f"⚠️  Connection Error: {e}")
        print("   (Using fallback core list. Validation may be less accurate.)")
        return FALLBACK_CORE

def discover_local_modules(root_dir):
    registry = set()
    for root, dirs, files in os.walk(root_dir):
        if '__manifest__.py' in files:
            registry.add(os.path.basename(root))
    return registry

def check_dependencies(manifest_path, data, valid_modules):
    depends = data.get('depends', [])
    module_name = os.path.basename(os.path.dirname(manifest_path))
    all_valid = True

    for dep in depends:
        if dep not in valid_modules:
            print(f"   [Depends] ❌ Missing: Module '{module_name}' depends on '{dep}' (Not found in Local Repo or Live DB/Fallback)")
            all_valid = False
    return all_valid

def check_icon(manifest_path, data):
    # (Same logic as V2)
    icon_path = data.get('icon')
    if not icon_path: return True
    
    if not icon_path.startswith('/'):
        print(f"   [Icon] ❌ Format: '{icon_path}' must start with '/'")
        return False

    parts = icon_path.strip('/').split('/', 1)
    if len(parts) < 2: return False
    
    module_name, relative = parts
    module_dir = os.path.dirname(manifest_path)
    if module_name != os.path.basename(module_dir):
        print(f"   [Icon] ❌ Scope: Path starts with '{module_name}', expected '{os.path.basename(module_dir)}'")
        return False

    full_path = os.path.join(module_dir, relative)
    if not os.path.isfile(full_path):
        print(f"   [Icon] ❌ Missing File: {full_path}")
        return False
    return True

def main():
    # 1. Get Live Modules (Remote)
    live_registry = get_live_modules()
    
    # 2. Get Local Modules (Repo)
    local_registry = discover_local_modules(ADDONS_DIR)
    
    # 3. Combine them
    valid_modules = live_registry.union(local_registry)
    
    has_error = False
    print(f"🔍 Validating modules against {len(valid_modules)} known apps...")

    for root, dirs, files in os.walk(ADDONS_DIR):
        if '__manifest__.py' in files:
            manifest_path = os.path.join(root, '__manifest__.py')
            # Skip node_modules or output directories
            if 'node_modules' in manifest_path or 'out/' in manifest_path or 'site-packages' in manifest_path:
                continue
                
            data = load_manifest(manifest_path)
            if not data:
                has_error = True
                continue

            if not check_icon(manifest_path, data): has_error = True
            if not check_dependencies(manifest_path, data, valid_modules): has_error = True

    if has_error:
        print("\n💥 Validation FAILED.")
        sys.exit(1)
    else:
        print("✅ Success.")
        sys.exit(0)

if __name__ == "__main__":
    main()
