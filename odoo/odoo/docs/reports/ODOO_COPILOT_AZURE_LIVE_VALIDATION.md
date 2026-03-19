# Odoo Copilot Azure Live Validation

## Status: PENDING

## Checklist

- [ ] `POST /ipai/copilot/chat` responds to authenticated request
- [ ] Azure OpenAI provider call succeeds
- [ ] Config seeded from env vars
- [ ] `/web/health` returns pass
- [ ] `/web/login` returns 200
- [ ] Deployment name correctly used (not base model name)
- [ ] API mode: (responses / chat_completions)

## Evidence

(To be filled after first successful Azure-backed request)

## Environment

- ACA resource: (TBD)
- Key Vault: kv-ipai-dev
- Azure OpenAI endpoint: (from AZURE_OPENAI_BASE_URL)
- Deployment: (from AZURE_OPENAI_DEPLOYMENT)
