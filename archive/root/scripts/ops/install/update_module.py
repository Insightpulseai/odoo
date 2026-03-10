import sys
sys.path.append('/usr/lib/python3/dist-packages')
import odoo

# Initialize Odoo
odoo.tools.config.parse_config(['-c', '/etc/odoo/odoo.conf'])
odoo.netsvc.init_logger()
from odoo.modules.registry import Registry

# Get the registry
registry = Registry.new('odoo')

# Update the module
with registry.cursor() as cr:
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})

    # Find the module
    module = env['ir.module.module'].search([('name', '=', 'ipai_finance_ppm')])
    if module:
        print('Found module, updating...')
        module.button_immediate_upgrade()
        print('Module updated successfully')
    else:
        print('Module not found')
