# PRD — Platform Master Index

## Problem
Platform work is distributed across 50+ spec bundles, 170+ migrations,
40+ n8n workflows, 17 contracts, and multiple PRs. There is no single
view of:
- What was planned vs what shipped
- What is missing from the original scope
- Which dependencies block downstream work
- Deployment status of each component

## Solution
A master task index that cross-references all platform milestones,
maps each task to its evidence artifacts, tracks completion status
against real repo state, and surfaces gaps.

## Scope
This index covers the full platform stack:
- SoR/SSOT/SoW doctrine + ops ledger (E1)
- SoW workspace layer (E2)
- Slack agent surface (E3)
- Advisor engine + scoring (E4)
- Microsoft 365 Copilot interaction plane (E5)
- Plane Marketplace integrations (E6)
- Vercel deployment determinism (E7)
- GitHub Enterprise / PR automation (E8)
- DigitalOcean cost optimization (E9)

## Non-Goals
- Replacing individual spec bundles (they remain authoritative for their scope)
- Tracking Odoo module development (separate spec bundles)
- Day-to-day sprint planning (this is milestone-level)
