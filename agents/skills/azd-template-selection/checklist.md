# Checklist — azd-template-selection

## Pre-selection

- [ ] Workload type identified (web app, API, function, full-stack)
- [ ] Language/runtime specified
- [ ] Target Azure services identified
- [ ] Authentication requirements documented
- [ ] Data tier requirements documented

## Template evaluation

- [ ] Template found in azd gallery
- [ ] Template last updated within 6 months
- [ ] Template uses managed identity (not API keys)
- [ ] Template includes VNet integration
- [ ] Template supports keyless access pattern
- [ ] Template language/runtime matches requirement
- [ ] Template targets ACA (not App Service or VM)

## CI/CD compatibility

- [ ] GitHub Actions workflow included
- [ ] Azure Pipelines support (if needed)
- [ ] Pipeline uses federated credentials (not secrets)

## Platform alignment

- [ ] Compatible with Azure PostgreSQL Flexible Server
- [ ] Compatible with Azure Key Vault for secrets
- [ ] Compatible with Azure Front Door for edge routing
- [ ] Container registry pull uses managed identity
- [ ] No hard dependencies on services not in platform stack
