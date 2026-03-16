# Foundry Integration

## Canonical SDK/runtime rule

**Use Foundry SDK** for builder-factory features that:
- Create or manage Foundry-native agents
- Run evaluations
- Use Foundry-specific capabilities (project endpoint, model catalog, connections)
- Depend on the Foundry project endpoint

**Use Agent Framework** for:
- Local multi-agent orchestration
- Cloud-agnostic orchestration logic
- Maker/judge orchestration patterns
- DevUI-compatible local development

**Use OpenAI SDK** only where maximum OpenAI API compatibility is specifically required.

## Endpoint rule

Builder-factory uses the Foundry project endpoint as the default runtime integration surface:
```
https://data-intel-ph-resource.services.ai.azure.com/api/projects/data-intel-ph
```

Authentication: `DefaultAzureCredential` (managed identity in ACA, az login locally).

## Non-goal

Builder-factory is not the data engineering or lakehouse platform. That remains `data-intelligence`.
Builder-factory is not the ERP system. That remains `odoo`.
Builder-factory is not the workspace UX. That remains `web`.
