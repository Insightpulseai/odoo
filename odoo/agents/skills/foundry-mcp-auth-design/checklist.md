# Checklist — foundry-mcp-auth-design

- [ ] MCP server type identified (Azure-native vs external)
- [ ] Hosting pattern documented (Azure Functions, ACA, external SaaS, on-premises)
- [ ] Managed identity feasibility checked
- [ ] Entra app registration feasibility checked
- [ ] Auth mode selected using preference order
- [ ] Rationale documented (especially if lower-preference mode chosen)
- [ ] Entra app registration requirements specified (if Entra OAuth2)
- [ ] Key Vault requirements specified (if key-based auth)
- [ ] Key rotation policy defined (if key-based auth)
- [ ] No hardcoded credentials in configuration
- [ ] Security assessment completed
- [ ] Evidence captured in `docs/evidence/{stamp}/foundry/mcp-auth/`
