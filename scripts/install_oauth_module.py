#!/usr/bin/env python3
"""Install ipai_auth_oauth_internal module"""

import odoo
from odoo import api, SUPERUSER_ID
import sys

# Database connection
db_name = 'odoo_core'

# Initialize Odoo registry
registry = odoo.registry(db_name)

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Update module list
    print("Updating module list...")
    env['ir.module.module'].sudo().update_list()
    cr.commit()

    # Search for the module
    module = env['ir.module.module'].sudo().search([
        ('name', '=', 'ipai_auth_oauth_internal')
    ], limit=1)

    if not module:
        print("ERROR: Module 'ipai_auth_oauth_internal' not found after update_list()")
        print("Checking addon paths...")
        sys.exit(1)

    print(f"Module found: {module.name}, state: {module.state}")

    if module.state == 'installed':
        print("Module already installed")
    elif module.state in ('uninstalled', 'to install'):
        print("Installing module...")
        module.button_immediate_install()
        print("Module installed successfully")
    else:
        print(f"Module in unexpected state: {module.state}")
