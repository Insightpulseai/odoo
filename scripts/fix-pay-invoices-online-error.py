#!/usr/bin/env python3
"""
Fix OwlError: res.config.settings.pay_invoices_online field is undefined

This script removes orphaned field references from Odoo views that cause
the OWL lifecycle error on erp.insightpulseai.net.

Error context:
- Field: res.config.settings.pay_invoices_online
- Likely from: account_payment module (Odoo Enterprise feature)
- Root cause: View references field that doesn't exist in CE

Solution approaches:
1. Remove orphaned view field references (safest for CE)
2. Install missing module dependency (if field is needed)
3. Update module if field definition exists but isn't loaded
"""

import os
import sys
import logging
import xmlrpc.client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Odoo connection details
ODOO_URL = os.getenv('ODOO_URL', 'https://erp.insightpulseai.net')
ODOO_DB = os.getenv('ODOO_DB', 'production')
ODOO_USERNAME = os.getenv('ODOO_USERNAME')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD')

def connect_odoo():
    """Establish XML-RPC connection to Odoo"""
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})

    if not uid:
        raise Exception("Authentication failed")

    logger.info(f"Connected to {ODOO_URL} as user ID {uid}")
    return xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object'), uid

def find_orphaned_views(models, uid):
    """Find views that reference pay_invoices_online field"""

    logger.info("Searching for views with pay_invoices_online reference...")

    # Search for views containing the field
    view_ids = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'ir.ui.view', 'search',
        [[['arch_db', 'ilike', '%pay_invoices_online%']]]
    )

    if not view_ids:
        logger.info("No views found with pay_invoices_online reference")
        return []

    # Read view details
    views = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'ir.ui.view', 'read',
        [view_ids, ['id', 'name', 'model', 'arch_db', 'inherit_id']]
    )

    logger.info(f"Found {len(views)} view(s) with pay_invoices_online:")
    for view in views:
        logger.info(f"  - ID: {view['id']}, Name: {view['name']}, Model: {view['model']}")

    return views

def check_field_exists(models, uid):
    """Check if pay_invoices_online field actually exists"""

    try:
        field_info = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.model.fields', 'search_read',
            [[['model', '=', 'res.config.settings'], ['name', '=', 'pay_invoices_online']]],
            {'fields': ['id', 'name', 'field_description', 'ttype']}
        )

        if field_info:
            logger.info(f"Field EXISTS in database: {field_info[0]}")
            return True
        else:
            logger.info("Field DOES NOT EXIST in database")
            return False
    except Exception as e:
        logger.error(f"Error checking field: {e}")
        return False

def remove_field_from_views(models, uid, view_ids, dry_run=True):
    """Remove pay_invoices_online field references from views"""

    if dry_run:
        logger.info("DRY RUN MODE - No changes will be made")

    for view_id in view_ids:
        try:
            view = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'ir.ui.view', 'read',
                [[view_id], ['arch_db']]
            )[0]

            arch = view['arch_db']

            # Remove the field element (handles various XML formats)
            import re

            # Pattern 1: <field name="pay_invoices_online" ... />
            pattern1 = r'<field[^>]*name="pay_invoices_online"[^>]*/>'
            # Pattern 2: <field name="pay_invoices_online" ...>...</field>
            pattern2 = r'<field[^>]*name="pay_invoices_online"[^>]*>.*?</field>'

            new_arch = arch
            new_arch = re.sub(pattern1, '', new_arch, flags=re.DOTALL)
            new_arch = re.sub(pattern2, '', new_arch, flags=re.DOTALL)

            if arch != new_arch:
                logger.info(f"View ID {view_id}: Field reference found and will be removed")

                if not dry_run:
                    # Update the view
                    models.execute_kw(
                        ODOO_DB, uid, ODOO_PASSWORD,
                        'ir.ui.view', 'write',
                        [[view_id], {'arch_db': new_arch}]
                    )
                    logger.info(f"View ID {view_id}: Updated successfully")
            else:
                logger.info(f"View ID {view_id}: No field reference found in arch_db")

        except Exception as e:
            logger.error(f"Error processing view {view_id}: {e}")

def install_account_payment_module(models, uid, dry_run=True):
    """
    Install account_payment module if it's available but not installed
    (Enterprise feature - may not be available in CE)
    """

    if dry_run:
        logger.info("DRY RUN MODE - Would attempt to install account_payment module")
        return

    try:
        # Search for account_payment module
        module_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.module.module', 'search',
            [[['name', '=', 'account_payment']]]
        )

        if not module_ids:
            logger.warning("account_payment module not found (likely CE vs Enterprise issue)")
            return

        module = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.module.module', 'read',
            [module_ids, ['state', 'name']]
        )[0]

        if module['state'] == 'uninstalled':
            logger.info("Installing account_payment module...")
            models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'ir.module.module', 'button_immediate_install',
                [module_ids]
            )
            logger.info("Module installation triggered (requires restart)")
        elif module['state'] == 'installed':
            logger.info("account_payment module is already installed")
            logger.info("Attempting module upgrade...")
            models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'ir.module.module', 'button_immediate_upgrade',
                [module_ids]
            )
        else:
            logger.info(f"Module state: {module['state']}")

    except Exception as e:
        logger.error(f"Error with module operation: {e}")

def main():
    """Main execution flow"""

    import argparse
    parser = argparse.ArgumentParser(description='Fix pay_invoices_online field error')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--remove-field', action='store_true', help='Remove field references from views')
    parser.add_argument('--install-module', action='store_true', help='Attempt to install/upgrade account_payment module')
    args = parser.parse_args()

    if not ODOO_USERNAME or not ODOO_PASSWORD:
        logger.error("ODOO_USERNAME and ODOO_PASSWORD environment variables required")
        sys.exit(1)

    try:
        # Connect to Odoo
        models, uid = connect_odoo()

        # Check if field exists
        field_exists = check_field_exists(models, uid)

        # Find affected views
        views = find_orphaned_views(models, uid)

        if not views:
            logger.info("No orphaned views found. Error may be from cached assets.")
            logger.info("Recommendation: Clear browser cache and Odoo assets cache")
            return

        # Decide on action
        if args.install_module and not field_exists:
            logger.info("\n=== ATTEMPTING MODULE INSTALLATION ===")
            install_account_payment_module(models, uid, dry_run=args.dry_run)

        if args.remove_field or (not field_exists and not args.install_module):
            logger.info("\n=== REMOVING FIELD REFERENCES ===")
            remove_field_from_views(models, uid, [v['id'] for v in views], dry_run=args.dry_run)

        if args.dry_run:
            logger.info("\n=== DRY RUN COMPLETE ===")
            logger.info("Run without --dry-run to apply changes")
        else:
            logger.info("\n=== CHANGES APPLIED ===")
            logger.info("Recommendation:")
            logger.info("1. Restart Odoo service: docker compose restart odoo-ce")
            logger.info("2. Clear browser cache")
            logger.info("3. Visit erp.insightpulseai.net and verify error is gone")

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
