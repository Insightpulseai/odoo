# Runbook: digitalocean

## Scope
This runbook is generated from spec/platforms/platform-capabilities.template.md.

## Required Secrets
- TODO: list secrets for digitalocean

## Apply
```bash
# TODO: apply commands for digitalocean
```

## Test / Verify
```bash
# TODO: verification commands for digitalocean
```

## Deploy / Rollback
```bash
# TODO: deploy
# TODO: rollback
```

## Production Validation
```bash
# TODO: health checks + logs
```

## Notes / Risks
- TODO

---

## Template (reference)

# Platform Capabilities SSOT (Template)

## Platforms
- Supabase
- Vercel
- DigitalOcean
- Superset
- Figma Sites

## For each platform, define:
### Identity / Auth
- auth_method:
- required_secrets:
- token_rotation_policy:
- least_privilege_notes:

### Provisioning / IaC
- terraform_module:
- cli_tools:
- docker_images:
- networking:

### Deploy
- deploy_command:
- rollback_command:
- smoke_tests:
- health_checks:

### Observability
- logs_command:
- metrics:
- alerts:

### Agent Hooks
- repo_hooks:
- mcp_servers:
- allowed_network:
