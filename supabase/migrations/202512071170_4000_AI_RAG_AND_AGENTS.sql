-- 202512071170_4000_AI_RAG_AND_AGENTS.sql
-- Family: 4000 - AI / RAG / Agents / MCP
-- Purpose:
--   * Canonical tables for agent registry, tools, conversations and RAG stores.
-- Safety:
--   * Additive and non-destructive.

BEGIN;

CREATE SCHEMA IF NOT EXISTS ai;
CREATE SCHEMA IF NOT EXISTS agents;
CREATE SCHEMA IF NOT EXISTS agent;
CREATE SCHEMA IF NOT EXISTS mcp;
CREATE SCHEMA IF NOT EXISTS gold;
CREATE SCHEMA IF NOT EXISTS platinum;
CREATE SCHEMA IF NOT EXISTS ops;
CREATE SCHEMA IF NOT EXISTS opex;

-- TODO: AGENT REGISTRY
--   * agents.role
--   * agents.skill
--   * agents.binding
--   * agent.roles
--   * agent.skills
--   * agent.agents
--   * agent.agent_skills
--   * agent.task_queue
--   * agent.task_route

-- TODO: AI CONVERSATIONS / LOGS
--   * ai.conversations
--   * ai.messages
--   * ai.budget_suggestions
--   * ops.ai_audit
--   * ops.workflow_runs

-- TODO: RAG STORES
--   * gold.docs
--   * gold.doc_chunks
--   * platinum.ai_cache
--   * mcp.rag_embeddings
--   * mcp.skills_registry
--   * mcp.usage_metrics
--   * mcp.routing_cache
--   * opex.rag_queries

COMMIT;
