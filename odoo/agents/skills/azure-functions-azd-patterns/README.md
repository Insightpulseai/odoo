# azure-functions-azd-patterns

Deploy Azure Functions with azd using secure-by-default patterns.

## Owner

functions-platform-engineer

## When to use

- New serverless / event-driven workload
- Timer job, webhook handler, event processor
- Migration from Classic to Flex Consumption plan

## Key principle

Flex Consumption + managed identity + VNet + azd = secure-by-default Functions. Cold start must be documented for user-facing triggers.

## Related skills

- azd-template-selection (select Functions-appropriate template)
- azd-secure-default-deployment (shared secure-by-default patterns)
- azd-environment-bootstrap (environment setup)
