# Checklist — azd-secure-default-deployment

## Pre-deployment security review

- [ ] azure.yaml declares managed identity for all services
- [ ] IaC includes VNet resource and subnet definitions
- [ ] Private endpoints defined for PostgreSQL
- [ ] Private endpoints defined for Key Vault
- [ ] Private endpoints defined for ACR
- [ ] No connection strings with embedded passwords in IaC
- [ ] No API keys hardcoded in application configuration
- [ ] ACR pull configured via managed identity

## Provisioning

- [ ] azd provision completes without errors
- [ ] Resource group created with correct naming (rg-ipai-{env})
- [ ] VNet created with correct address space
- [ ] Private endpoints active and connected
- [ ] Managed identity assigned to all services
- [ ] Key Vault access policies reference managed identity

## Deployment

- [ ] azd deploy completes without errors
- [ ] Container images pulled from ACR via managed identity
- [ ] Application starts and passes health probes
- [ ] No secrets exposed in deployment logs

## Post-deployment verification

- [ ] Health endpoint responds with 200
- [ ] Application functions correctly
- [ ] No public endpoints for data services
- [ ] Security posture report generated
