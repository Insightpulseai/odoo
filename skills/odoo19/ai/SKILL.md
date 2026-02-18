---
name: ai
description: AI application providing agents, Ask AI assistant, text generation, document sorting, and voice features
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# ai -- Odoo 19.0 Skill Reference

## Overview

The Odoo AI application provides intelligent, context-aware assistance across all Odoo apps. It features the "Ask AI" natural-language assistant accessible via the command palette (Ctrl+K) or the AI button, customizable AI agents with topics and tools, text generation/improvement in chatter, document auto-sorting, and integration with ChatGPT (OpenAI) and Google Gemini as LLM providers. The standard Ask AI agent can answer questions, open views, and improve content but cannot modify database records by default.

## Key Concepts

- **Ask AI**: The default AI assistant available everywhere via command palette (Ctrl+K) or the AI button in the top-right corner. Understands natural language for questions, view navigation, and content improvement.
- **AI Agent**: A configurable assistant with a defined purpose, system prompt, topics, tools, sources, and response style. Created in the AI app.
- **System Prompt**: The core mission statement defining an agent's role, purpose, and behavior.
- **Topics**: Collections of instructions and tools that define what an agent can do. Without topics, an agent can only provide information, not take actions.
- **Tools**: Functions the agent can perform in Odoo (e.g., create a lead, open a view). Available tools depend on installed apps.
- **Sources**: Data the agent can reference (PDFs, weblinks, Documents app files, Knowledge articles). Can be restricted via "Restrict to Sources" toggle.
- **Instructions**: Topic-specific guidelines refining agent behavior within a particular context or workflow.
- **Response Style**: Analytical (deterministic, accurate), Balanced (mix), or Creative (varied, conversational).
- **LLM Model**: The AI provider model (ChatGPT or Gemini variants) used by the agent.
- **Default Prompts**: Pre-configured prompt actions on AI responses (Send as Message, Log as Note, Copy).
- **API Keys**: Required for Odoo.sh and on-premise; optional (but supported) for Odoo Online. Configurable at AI > Configuration > Settings.

## Core Workflows

1. **Use Ask AI via Command Palette**
   1. Press Ctrl+K to open the command palette.
   2. Type a natural language prompt.
   3. Press Enter or click the AI icon.
   4. Review the response; hover to Send as Message, Log as Note, or Copy.

2. **Use Ask AI via AI Button**
   1. Click the AI button in the top-right corner.
   2. Type a request or click a preconfigured prompt.
   3. Response appears in a conversation window.

3. **Create a Custom AI Agent**
   1. Navigate to AI app, click New.
   2. Enter Agent Name and optional description.
   3. Select LLM Model and Response Style.
   4. Optionally enable "Restrict to Sources."
   5. Select one or more Topics.
   6. Write the System Prompt.
   7. Add Sources in the Sources tab (PDFs, weblinks, Documents, Knowledge articles).
   8. Click Test to verify behavior.

4. **Configure API Keys**
   1. Go to AI > Configuration > Settings.
   2. Under Providers, tick "Use your own ChatGPT account" or "Use your own Google Gemini account."
   3. Paste the API key.
   4. Click Save.

5. **Common Ask AI Requests**
   - Translation: "Translate the most recent chatter message"
   - Summarize: "Summarize this chatter thread"
   - Text generation: "Generate a follow-up message"
   - Improve: "Improve this message draft"
   - Suggest: "Suggest next steps for the sales rep"

## Technical Reference

- **Key Models**: `ai.bot` (agent), `ai.bot.topic`, `ai.bot.tool`, `ai.bot.source`
- **Agent Fields**: `name`, `description`, `llm_model`, `response_style` (analytical/balanced/creative), `system_prompt`, `topic_ids`, `source_ids`, `restrict_to_sources`
- **Source Formats**: PDF, Weblink, Document (Documents app), Knowledge article. Status: Processing > Indexed.
- **Preconfigured Topics**: Natural Language Search, Information Retrieval, Create Leads (CRM required).
- **Settings Path**: AI > Configuration > Settings. Provider options: ChatGPT (OpenAI), Google Gemini.
- **API Key Creation**:
  - OpenAI: platform.openai.com/api-keys > Create new secret key
  - Gemini: aistudio.google.com/app/api-keys > Create API Key

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

- AI app is new in Odoo 19.0 as a standalone application.
- Ask AI agent available globally via command palette and dedicated AI button.
- Custom agents support Topics with Tools for database actions (e.g., Create Leads).
- Multiple LLM providers supported (ChatGPT and Gemini variants).
- Sources can be restricted to limit agent responses to provided materials only.
- Default prompts (Send as Message, Log as Note, Copy) are customizable.

## Common Pitfalls

- The standard Ask AI agent cannot create records or alter data. Database-modifying actions require custom agents with appropriate Topics and Tools.
- If a source fails to upload, it may conflict with the selected LLM model.
- API keys are required for Odoo.sh and on-premise deployments; Odoo Online users can optionally bring their own keys.
- The Ask AI agent is instructed not to display errors to users; if it cannot complete a query, it responds that it is unable to do so.
- OpenAI API keys cannot be viewed again after creation; store them securely.
