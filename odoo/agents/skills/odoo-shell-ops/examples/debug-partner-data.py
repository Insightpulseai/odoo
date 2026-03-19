# Example: Debug partner data via Odoo shell
# Run with: odoo-bin shell -d odoo_dev < debug-partner-data.py

# Count partners
partners = self.env['res.partner'].search([])
print(f"\nTotal partners: {len(partners)}")

# Companies vs individuals
companies = partners.filtered(lambda p: p.is_company)
individuals = partners.filtered(lambda p: not p.is_company)
print(f"Companies: {len(companies)}, Individuals: {len(individuals)}")

# Partners with email
with_email = partners.filtered(lambda p: p.email)
print(f"Partners with email: {len(with_email)}")

# Check model fields
fields = self.env['res.partner'].fields_get(['name', 'email', 'phone', 'is_company'])
for fname, finfo in fields.items():
    print(f"  {fname}: {finfo['type']} — {finfo.get('string', 'N/A')}")

# Check access rights for current user
access = self.env['ir.model.access'].search([
    ('model_id.model', '=', 'res.partner'),
])
print(f"\nAccess rules for res.partner: {len(access)}")
for a in access:
    print(f"  {a.name}: read={a.perm_read} write={a.perm_write} create={a.perm_create} unlink={a.perm_unlink}")
