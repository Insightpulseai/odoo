# Claude MCP Integration — Checklist

## Tool Design
- [ ] Namespace prefixes applied (service_resource_action)
- [ ] Descriptions are capability-focused (not implementation)
- [ ] Responses return high-signal data only
- [ ] Error messages are actionable and educational
- [ ] Naming tested empirically if possible

## Auth
- [ ] Auth hierarchy applied (managed identity > OAuth2 > API key)
- [ ] Credentials sourced from Key Vault (never hardcoded)
- [ ] Auth method documented in MCP server config

## Registration
- [ ] MCP server registered with complete tool schemas
- [ ] Tool descriptions tested against sample prompts
- [ ] Dynamic discovery configured if >10 tools

## Validation
- [ ] End-to-end test: Claude → MCP → tool → response
- [ ] Error handling tested: tool returns actionable guidance
