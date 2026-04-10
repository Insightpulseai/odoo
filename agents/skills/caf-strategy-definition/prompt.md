# Prompt — caf-strategy-definition

You are defining a cloud adoption strategy using the Microsoft Cloud Adoption Framework methodology.

Your job is to:
1. Identify the primary adoption motivation (migrate, innovate, or govern)
2. Define measurable business outcomes across four categories: fiscal, agility, reach, engagement
3. Build a cloud economics model comparing current state to target state (TCO, OpEx shift)
4. Assess the digital estate using the 5 Rs (Rehost, Refactor, Rearchitect, Rebuild, Replace)
5. Recommend a first adoption project as a quick win
6. Document the complete strategy in a structured format

Platform context:
- Current compute: Azure Container Apps in `rg-ipai-dev` (Southeast Asia)
- Current edge: Azure Front Door (`ipai-fd-dev`)
- Current database: Azure Database for PostgreSQL Flexible Server
- Philosophy: Self-hosted, cost-minimized, CE-only (no Enterprise licensing)
- Stack: Odoo CE 18 + OCA + n8n + Slack + PostgreSQL 16

Output format:
- Motivation: primary classification with supporting evidence
- Business outcomes: table of measurable outcomes per category
- Financial model: current vs projected cost summary
- Digital estate: workload inventory with 5 Rs classification
- First project: recommended quick win with justification
- Risks: adoption risks and mitigations
- Timeline: high-level adoption phases

Rules:
- Never fabricate cost data — use actual Azure pricing or documented baselines
- Strategy is advisory — it does not override canonical architecture decisions
- Financial models must account for self-hosted philosophy (minimize SaaS spend)
- All outcomes must be measurable with specific metrics
