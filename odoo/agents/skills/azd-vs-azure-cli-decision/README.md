# azd-vs-azure-cli-decision

Judge skill that decides whether a task requires azd, Azure CLI, or both.

## Owner

azd-deployment-judge

## When to use

- Tool selection is ambiguous for an Azure task
- Reviewing proposed Azure commands before execution
- Training new team members on tool boundaries

## Key principle

azd = developer tool (bootstrap, provision, deploy, CI/CD). Azure CLI = admin tool (inventory, diagnose, maintain, configure). This skill enforces the boundary.

## Related skills

- azd-template-selection (uses azd)
- azd-environment-bootstrap (uses azd)
- azure-cli-resource-operations (uses Azure CLI)
