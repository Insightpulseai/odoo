# Prompt — azd-secure-default-deployment

You are deploying an application to the InsightPulse AI platform with secure-by-default posture via azd.

Your job is to:
1. Verify the azd project enforces managed identity for all services
2. Confirm VNet integration is configured in IaC
3. Validate private endpoints for data services
4. Ensure keyless access patterns (no embedded credentials)
5. Execute azd provision + azd deploy (or azd up)
6. Verify deployment health and security posture

Secure-by-default requirements:
- **Managed identity**: Every service uses system-assigned or user-assigned managed identity
- **VNet integration**: All services connected via VNet, no public endpoints for data services
- **Private endpoints**: PostgreSQL, Key Vault, ACR accessed via private endpoints
- **Keyless access**: No API keys, no connection strings with passwords in configuration
- **ACR pull**: Container registry pull via managed identity, not admin credentials

Deployment workflow:
```
azd provision  →  creates infrastructure with secure defaults
azd deploy     →  deploys application code to provisioned infrastructure
azd up         →  combined provision + deploy (preferred)
```

Output format:
- Infrastructure: provisioned (yes/no)
- Services deployed: list with status
- Managed identity: all services (yes/no), list of gaps
- VNet: integrated (yes/no), subnets configured
- Private endpoints: list with status
- Keyless access: enforced (yes/no), exceptions
- Health checks: all passing (yes/no)
- Deployment URL: accessible (yes/no)
