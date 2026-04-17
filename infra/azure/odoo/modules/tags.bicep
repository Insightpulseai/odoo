@description('Base tag contract from parameters')
param baseTags object

output tags object = union(baseTags, {
  'managed-by': 'bicep'
  stack: 'odoo-only'
})
