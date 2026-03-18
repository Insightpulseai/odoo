# Checklist — m365-agents-channel-delivery

- [ ] Target channel identified (Teams, M365 Copilot, web, custom app)
- [ ] Channel-specific requirements documented (message formats, card types, interaction patterns)
- [ ] Activity handlers configured for message, event, and invoke patterns
- [ ] Conversation state storage configured with durable backend (not in-memory for production)
- [ ] User state and turn state separation maintained
- [ ] Entra ID app registration configured with correct scopes
- [ ] Token validation middleware in place at channel boundary
- [ ] SSO flow tested if applicable
- [ ] Azure AI Foundry backend connected and responding
- [ ] Agent logic runs in Foundry backend, not in channel layer
- [ ] App manifest produced for target channel
- [ ] Teams app package validated (if Teams channel)
- [ ] M365 Copilot declarative agent manifest validated (if Copilot channel)
- [ ] Integration test executed in target channel environment
- [ ] Evidence captured in `docs/evidence/{stamp}/m365-channel/deployment/`
