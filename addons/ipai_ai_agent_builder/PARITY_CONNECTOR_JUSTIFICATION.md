# Connector Justification: ipai_ai_agent_builder

## What this module does
Provides Odoo 19 AI Agents feature parity for CE/OCA deployments, including configurable AI agents with system prompts, topic-based instruction bundles, callable business tools with permission gating, and RAG-enabled knowledge sources.

## What it is NOT
- Not an OCA parity addon
- Not an EE-module reimplementation

## Why LOC exceeds 1000
The module spans 1,597 LOC because it implements multiple provider adapters (OpenAI, Google Gemini), a full tool-execution engine with permission gating and audit trails, REST API controllers, and six distinct model classes (agent, run, run_event, tool, tool_call, topic) that together form the agent orchestration pipeline.

## Planned reduction path
- Extract provider adapters (`services/provider_openai.py`, `services/provider_google.py`) into a shared `ipai_ai_providers` utility package
- Move the tool executor service into the dependent `ipai_ai_rag` module or a shared `ipai_ai_core` library
- Split REST API controllers into per-resource files to reduce `controllers/main.py`
