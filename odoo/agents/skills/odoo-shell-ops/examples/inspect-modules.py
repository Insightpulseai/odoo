# Example: Inspect installed modules via Odoo shell
# Run with: odoo-bin shell -d odoo_dev < inspect-modules.py

# List all installed modules
installed = self.env['ir.module.module'].search([('state', '=', 'installed')])
print(f"\nInstalled modules: {len(installed)}")
for mod in installed.sorted('name'):
    print(f"  {mod.name} ({mod.shortdesc})")

# Check IPAI modules specifically
ipai_modules = self.env['ir.module.module'].search([
    ('name', 'like', 'ipai_%'),
    ('state', '=', 'installed'),
])
print(f"\nIPAI modules installed: {len(ipai_modules)}")
for mod in ipai_modules.sorted('name'):
    print(f"  {mod.name}: {mod.state}")

# Check for uninstalled IPAI modules
ipai_available = self.env['ir.module.module'].search([
    ('name', 'like', 'ipai_%'),
    ('state', '!=', 'installed'),
])
print(f"\nIPAI modules NOT installed: {len(ipai_available)}")
for mod in ipai_available.sorted('name'):
    print(f"  {mod.name}: {mod.state}")
