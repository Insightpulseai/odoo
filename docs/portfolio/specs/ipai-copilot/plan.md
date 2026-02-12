# Plan: IPAI Copilot

## Phase 1: Odoo Addon (`ipai_copilot`)
- [ ] Scaffold addon structure
- [ ] Implement `res.config.settings` for API URL/Key
- [ ] Implement `main.py` controller (proxy)
- [ ] Implement OWL Systray & Panel Components
- [ ] Implement Service/Store logic

## Phase 2: RAG Backend (Supabase)
- [ ] Create migration `202601030001_docs.sql`
- [ ] Setup Edge Function `ipai-copilot` (stub for v1)

## Phase 3: Ingestion & Data
- [ ] Create `scripts/copilot_ingest.py`
- [ ] Seed initial finance docs (markdown)

## Phase 4: CI & Verification
- [ ] Add `bin/copilot_drift_check.sh`
- [ ] Manual verification via UI
