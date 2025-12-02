# Prompt Library & Context Engineering

Reusable prompts, contexts, and LLM rules for InsightPulse AI agents.

## Quick Start

```bash
# Use a template
cat prompts/templates/code-generation/odoo-model.hbs

# Load context
cat prompts/contexts/odoo/model-context.md

# Apply rules
cat prompts/rules/odoo-development.md
```

## Directory Structure

- **contexts/** - Reusable context snippets for specific domains
- **contexts/odoo/ipai_workspace_codex_prompt.md** - Codex-ready prompt for the ipai_* Notion-style workspace integrated with Supabase, n8n, and enterprise modules
- **contexts/odoo/ipai_confluence_codex_prompt.md** - Codex-ready prompt to add a Confluence-like layer (spaces, labels, history, approvals, macros) atop ipai_workspace
- **contexts/odoo/ipai_docsaurus_codex_prompt.md** - Codex-ready prompt to build a Docusaurus-like docs layer with versioning, sidebars, Markdown export, and n8n/GitHub deployment hooks
- **contexts/odoo/ipai_hr_hire_to_retire_codex_prompt.md** - Codex-ready prompt to integrate the Hire-to-Retire BPMN + DOLE/SLA draft into the ipai_* workspace/docs stack
- **templates/** - Handlebars templates for code generation, reviews, docs
- **rules/** - LLM behavior rules and coding standards
- **examples/** - Working examples of complete implementations

## Usage

See `/docs/PROMPT_LIBRARY_SYSTEM.md` for complete documentation.

## Global LLM Rules

The `.llmrules` file at project root contains global rules that apply to all AI interactions.
