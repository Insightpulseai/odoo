# azure-cli-resource-operations

Execute granular Azure resource operations via Azure CLI when azd is insufficient.

## Owner

azure-cli-admin

## When to use

- Resource inventory or compliance checks
- Diagnostics and log queries
- Individual resource configuration changes
- Maintenance operations (scaling, restart, certificate rotation)

## Key principle

Azure CLI is the admin tool for granular operations. Use azd first for app bootstrap/deployment. Azure CLI fills the gap for everything azd cannot do.

## Related skills

- azd-vs-azure-cli-decision (judge skill — determines when to use this)
- azure-load-testing-cli-patterns (specialized CLI operations)
