# scripts/odoo/configure_approval_bands.py
#
# Logic to seed the Financial Approval Bands (A-E) into the Odoo runtime.
# This script reads from platform/ssot/finance/approval_bands.yaml.

import yaml
from pathlib import Path

def configure_bands(env):
    ssot_path = Path(__file__).parent.parent.parent / 'platform' / 'ssot' / 'finance' / 'approval_bands.yaml'
    
    if not ssot_path.exists():
        print(f"❌ Error: SSOT not found at {ssot_path}")
        return

    with open(ssot_path, 'r') as f:
        config = yaml.safe_load(f)

    print(f"📍 Seeding {len(config['bands'])} Approval Bands into Odoo...")

    # We store these as ir.config_parameter or dedicated model records
    # Example: ipai.approval.band model in ipai_finance_ppm
    for band in config['bands']:
        param_key = f"ipai.approval.band.{band['id']}.limit"
        env['ir.config_parameter'].sudo().set_param(param_key, str(band['limit']))
        print(f"✅ Set {param_key} = {band['limit']}")

    # Configure global governance
    env['ir.config_parameter'].sudo().set_param('ipai.approval.agent_limit', config['governance']['agent_authority_limit'])
    print(f"✅ Set ipai.approval.agent_limit = {config['governance']['agent_authority_limit']}")

# Usage within Odoo Shell:
# from scripts.odoo.configure_approval_bands import configure_bands; configure_bands(env)
