# PRD: Copilot Reverse-Engineering Parity Agent

## Goal
Continuously discover, map, and validate parity paths for EE-only capabilities across Odoo/ERPNext/Superset/n8n/Mattermost/Supabase.

## Outputs (hard requirements)
- Parity Matrix (feature->parity path->status->evidence)
- Gap Report (what's missing, why, and best next action)
- Contract Test Suite (API/data/event/UI behavior contracts)
- KB Index (versioned sources + extracted facts + embeddings optional)

## Parity Paths (ranked)
1) OCA/Upstream module
2) External service (Superset/n8n/Mattermost/etc.)
3) Thin bridge module/service (ipai_* glue)
4) Partial parity (explicitly scoped + documented)
