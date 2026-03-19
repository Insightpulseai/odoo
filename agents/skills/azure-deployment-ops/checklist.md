# Checklist — azure-deployment-ops

- [ ] Resource group matches naming convention (`rg-ipai-{env}`)
- [ ] Container App is in correct ACA environment (`cae-ipai-{env}`)
- [ ] System-assigned or user-assigned managed identity is enabled
- [ ] Key Vault references use managed identity (no connection strings)
- [ ] Key Vault access policy or RBAC role grants identity read access
- [ ] Front Door origin group includes the Container App FQDN
- [ ] Custom domain is bound with valid TLS certificate
- [ ] Health probe endpoint configured and returning 200
- [ ] Container registry pull uses managed identity (not admin credentials)
- [ ] Ingress target port matches application listening port
- [ ] CORS and transport settings match platform policy
- [ ] Evidence captured in `docs/evidence/{stamp}/azure-ops/deployment/`
