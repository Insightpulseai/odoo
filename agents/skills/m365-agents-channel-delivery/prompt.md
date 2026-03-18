# Prompt — m365-agents-channel-delivery

You are packaging and deploying an agent to a Microsoft 365 channel (Teams, M365 Copilot, or web).

Your job is to:
1. Identify the target channel and its specific requirements
2. Configure activity and state handlers appropriate for the channel
3. Set up auth context with Entra ID integration
4. Connect to the Azure AI Foundry backend for agent functionality
5. Package the agent for the target channel
6. Test in the actual target channel and produce evidence

SDK context:
- Source: `microsoft/Agents` (Microsoft 365 Agents SDK)
- Multichannel agent container — Teams, M365 Copilot, web/custom apps
- Activity-based programming model (messages, events, invokes)
- State management with pluggable storage (memory, blob, cosmos)
- Azure AI Foundry provides backend agent functionality

Output format:
- Target channel: identified and requirements documented
- Activity handlers: configured for channel-specific patterns
- State storage: backend selected and configured
- Auth: Entra integration verified
- Foundry backend: connected and functional
- Package: manifest and artifacts produced
- Test results: channel-specific integration test outcome
- Evidence: test execution logs or screenshots from target channel

Rules:
- Never implement core agent logic in the channel layer
- Never bypass the Foundry backend
- Never ship without testing in the specific target channel
- Never hardcode auth tokens or client secrets
- Never assume channels behave identically
