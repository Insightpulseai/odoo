# Constitution — Builder Factory

## Non-negotiable rules

1. Builder-factory lives inside `agent-platform`, not as a separate repo
2. Foundry SDK is the default for Foundry-native agent/eval features
3. Agent Framework is the default for multi-agent orchestration in code
4. OpenAI SDK only for maximum OpenAI API compatibility
5. Doctrine assets (personas, skills, judges) live in `agents/`, not here
6. Data products live in `data-intelligence/`, not here
7. ERP logic lives in `odoo/`, not here
8. All agents must pass pre-publish evals before Foundry deployment
9. Security-judge review required before any public-facing agent
10. Builder-factory is not the data engineering or lakehouse platform
