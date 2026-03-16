import sys
sys.path.append('/usr/lib/python3/dist-packages')
import odoo

# Initialize Odoo
odoo.tools.config.parse_config(['-c', '/etc/odoo/odoo.conf'])
odoo.netsvc.init_logger()
from odoo.modules.registry import Registry

# Get the registry
registry = Registry.new('odoo')

# Check module status
with registry.cursor() as cr:
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})

    # Find the module
    module = env['ir.module.module'].search([('name', '=', 'ipai_finance_ppm')])
    if module:
        print(f'Module found: {module.name}')
        print(f'State: {module.state}')
        print(f'Latest version: {module.latest_version}')

        # Check if project task fields exist
        fields = env['ir.model.fields'].search([('model', '=', 'project.task'), ('name', 'like', 'finance_%')])
        print(f'Finance PPM fields in project.task: {len(fields)}')
        for field in fields:
            print(f'  - {field.name}: {field.field_description}')
    else:
        print('Module not found')
