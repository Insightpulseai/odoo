-- 9003_ai_rag_agent_registry_seed.sql
-- Family: 9003_ai_rag - Agent registry seed
-- Purpose:
--   * Register core engines/agents (TE-Cheq, Retail-Intel, Doc-OCR, PPM,
--     NotebookLM-like, etc.) in agents/agent tables.
-- Safety:
--   * Demo / initial registry only.

BEGIN;

-- TODO: INSERT AGENT PROFILES
--   * agents.role
--   * agents.skill
--   * agents.binding
--   * agent.agents
--   * agent.agent_skills
--
-- Example (commented):
-- INSERT INTO agent.agents (id, slug, name, domain)
-- VALUES (gen_random_uuid(), 'te-cheq-coach', 'TE-Cheq Coach', 'finance');

COMMIT;
