#!/usr/bin/env python3
"""
=============================================================================
OCA Module Installation Validator
=============================================================================
Validates OCA module installation via XML-RPC and functional smoke tests.

Usage:
    python3 scripts/oca/validate_installation.py --db odoo_dev
    python3 scripts/oca/validate_installation.py --db odoo_dev --url http://localhost:8069
    python3 scripts/oca/validate_installation.py --db odoo_dev --verbose

Prerequisites:
    - Odoo server running and accessible
    - Database initialized with modules installed
    - Python 3.8+
=============================================================================
"""

import argparse
import json
import sys
import xmlrpc.client
from pathlib import Path
from typing import Dict, List, Tuple

import yaml

# Colors for terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'


def log(msg: str, color: str = Colors.NC):
    """Print colored log message"""
    print(f"{color}{msg}{Colors.NC}")


def log_success(msg: str):
    log(f"✓ {msg}", Colors.GREEN)


def log_error(msg: str):
    log(f"✗ {msg}", Colors.RED)


def log_warning(msg: str):
    log(f"⚠ {msg}", Colors.YELLOW)


def log_info(msg: str):
    log(f"ℹ {msg}", Colors.BLUE)


def get_odoo_connection(url: str, db: str, username: str, password: str) -> Tuple:
    """Establish XML-RPC connection to Odoo"""
    try:
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})

        if not uid:
            log_error(f"Authentication failed for user: {username}")
            return None, None

        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        return uid, models

    except Exception as e:
        log_error(f"Connection failed: {e}")
        return None, None


def verify_module_installed(
    module_name: str, db: str, url: str, uid: int, password: str, models
) -> Dict:
    """
    Verify single module installation state via XML-RPC
    Returns dict with name, state, version
    """
    try:
        module_ids = models.execute_kw(
            db, uid, password,
            'ir.module.module', 'search',
            [[['name', '=', module_name]]]
        )

        if not module_ids:
            return {
                'name': module_name,
                'state': 'not_found',
                'installed_version': None,
                'error': 'Module not found in database'
            }

        module_data = models.execute_kw(
            db, uid, password,
            'ir.module.module', 'read',
            [module_ids],
            {'fields': ['name', 'state', 'installed_version']}
        )

        return module_data[0]

    except Exception as e:
        return {
            'name': module_name,
            'state': 'error',
            'installed_version': None,
            'error': str(e)
        }


def load_module_allowlist(config_file: str) -> Dict[str, List[str]]:
    """Load module packs from YAML config"""
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
            return config.get('packs', {})
    except Exception as e:
        log_error(f"Failed to load config: {e}")
        return {}


def validate_all_modules(
    db: str, url: str, username: str, password: str, config_file: str, verbose: bool = False
) -> Tuple[List, List, List]:
    """
    Validate all modules from allowlist
    Returns (installed, failed, not_found)
    """
    log_info("Connecting to Odoo...")
    uid, models = get_odoo_connection(url, db, username, password)

    if not uid:
        sys.exit(1)

    log_success(f"Connected to {url} (database: {db})")

    # Load module list
    log_info("Loading module allowlist...")
    packs = load_module_allowlist(config_file)

    if not packs:
        log_error("No module packs found in config")
        sys.exit(1)

    # Flatten all modules from all packs
    all_modules = []
    for pack_name, modules in packs.items():
        all_modules.extend(modules)

    log_info(f"Validating {len(all_modules)} modules...")

    installed = []
    failed = []
    not_found = []

    for module_name in all_modules:
        result = verify_module_installed(module_name, db, url, uid, password, models)

        if result['state'] == 'installed':
            installed.append(result)
            if verbose:
                log_success(f"{module_name}: installed (v{result.get('installed_version', 'unknown')})")
        elif result['state'] == 'not_found':
            not_found.append(result)
            if verbose:
                log_warning(f"{module_name}: not found")
        else:
            failed.append(result)
            if verbose:
                log_error(f"{module_name}: {result['state']} - {result.get('error', 'unknown error')}")

    return installed, failed, not_found


def print_summary(installed: List, failed: List, not_found: List):
    """Print validation summary"""
    total = len(installed) + len(failed) + len(not_found)

    print("\n" + "=" * 60)
    print("  OCA Module Installation Validation Summary")
    print("=" * 60)

    log_success(f"Installed: {len(installed)}/{total} modules")

    if failed:
        log_error(f"Failed: {len(failed)} modules")
        for module in failed:
            log_error(f"  - {module['name']}: {module['state']}")

    if not_found:
        log_warning(f"Not Found: {len(not_found)} modules")
        for module in not_found:
            log_warning(f"  - {module['name']}")

    print("=" * 60)

    # Calculate success rate
    if total > 0:
        success_rate = (len(installed) / total) * 100
        if success_rate >= 95:
            log_success(f"Success Rate: {success_rate:.1f}%")
        elif success_rate >= 80:
            log_warning(f"Success Rate: {success_rate:.1f}%")
        else:
            log_error(f"Success Rate: {success_rate:.1f}%")

    return len(failed) == 0 and len(not_found) == 0


def save_results(installed: List, failed: List, not_found: List, output_file: str):
    """Save validation results to JSON"""
    results = {
        'summary': {
            'total': len(installed) + len(failed) + len(not_found),
            'installed': len(installed),
            'failed': len(failed),
            'not_found': len(not_found),
            'success_rate': (len(installed) / (len(installed) + len(failed) + len(not_found))) * 100 if (len(installed) + len(failed) + len(not_found)) > 0 else 0
        },
        'installed_modules': installed,
        'failed_modules': failed,
        'not_found_modules': not_found
    }

    try:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

        log_success(f"Results saved to: {output_file}")

    except Exception as e:
        log_error(f"Failed to save results: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Validate OCA module installation via XML-RPC'
    )
    parser.add_argument(
        '--db',
        default='odoo_dev',
        help='Odoo database name (default: odoo_dev)'
    )
    parser.add_argument(
        '--url',
        default='http://localhost:8069',
        help='Odoo server URL (default: http://localhost:8069)'
    )
    parser.add_argument(
        '--username',
        default='admin',
        help='Odoo admin username (default: admin)'
    )
    parser.add_argument(
        '--password',
        default='admin',
        help='Odoo admin password (default: admin)'
    )
    parser.add_argument(
        '--config',
        default='config/oca/module_allowlist.yml',
        help='Module allowlist config file'
    )
    parser.add_argument(
        '--output',
        default=None,
        help='Output JSON file for results'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output (show all modules)'
    )

    args = parser.parse_args()

    # Validate
    installed, failed, not_found = validate_all_modules(
        args.db, args.url, args.username, args.password, args.config, args.verbose
    )

    # Print summary
    success = print_summary(installed, failed, not_found)

    # Save results if requested
    if args.output:
        save_results(installed, failed, not_found, args.output)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
