# AI Module Naming Convention (OCA-Aligned)

This document defines the **canonical, OCA-aligned naming convention** for AI Assistant and Agent modules in the IPAI stack.

## Vocabulary

| Term | Definition | Module Pattern |
|------|------------|----------------|
| **Assistant** | The UI shell (drawer, chat UI) | `ipai_ai_assistant` |
| **Agent** | A capability pack (finance, sales, helpdesk) | `ipai_ai_agent_<domain>` |
| **Tools** | Domain-specific tool packs | `ipai_ai_tools_<domain>` |

## Module Naming (OCA Pattern)

### Core Modules

| Module | Purpose |
|--------|---------|
| `ipai_ai_assistant` | UI drawer + thread/run models + router + audit |
| `ipai_ai_agent_core` | Base tools: summarize chatter, create activity, open action |

### Domain Agent Packs

| Module | Purpose |
|--------|---------|
| `ipai_ai_agent_finance` | Vendor bill drafting, reconciliations, close checklist |
| `ipai_ai_agent_sales` | Quote drafting, pipeline summaries, follow-ups |
| `ipai_ai_agent_helpdesk` | Triage, SLA suggestions, canned replies |
| `ipai_ai_agent_hr` | Leave management, onboarding, payroll queries |
| `ipai_ai_agent_project` | Task management, time tracking, milestone alerts |

### Optional Tool Packs

| Module | Purpose |
|--------|---------|
| `ipai_ai_tools_finance` | Finance-specific tool implementations |
| `ipai_ai_tools_sales` | Sales-specific tool implementations |

## Python Model Naming (OCA Pattern)

### Naming Rules

- Persistent objects: `ipai.ai.*`
- Use dot-separated model names
- Use snake_case for final segment

### Core Models

| Model Name | Purpose |
|------------|---------|
| `ipai.ai.thread` | Conversation thread |
| `ipai.ai.message` | Individual message |
| `ipai.ai.run` | Execution run |
| `ipai.ai.agent` | Agent registry |
| `ipai.ai.tool` | Tool registry/allowlist |

### Domain-Specific Models

| Model Name | Purpose |
|------------|---------|
| `ipai.ai.agent.finance` | Finance agent configuration |
| `ipai.ai.agent.sales` | Sales agent configuration |
| `ipai.ai.agent.helpdesk` | Helpdesk agent configuration |

## XML IDs (OCA Pattern)

### Format

```
<module>.<record_id>
```

### Examples

| XML ID | Purpose |
|--------|---------|
| `ipai_ai_assistant.action_open_drawer` | Open drawer action |
| `ipai_ai_assistant.menu_ai_assistant` | Main menu item |
| `ipai_ai_agent_finance.group_ai_agent_finance_user` | Finance agent user group |

### Rule

**Never reuse record_id across modules** unless intentionally namespaced.

## Security Groups + ACLs (OCA Pattern)

### Groups

| Group | Purpose |
|-------|---------|
| `group_ipai_ai_user` | Base AI access |
| `group_ipai_ai_manager` | AI admin access |
| `group_ipai_ai_agent_<domain>_user` | Domain agent user |
| `group_ipai_ai_agent_<domain>_manager` | Domain agent admin |

### ACL CSV Entries

Model access follows OCA conventions:

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_ipai_ai_thread_user,ipai.ai.thread user,model_ipai_ai_thread,group_ipai_ai_user,1,1,1,0
access_ipai_ai_message_user,ipai.ai.message user,model_ipai_ai_message,group_ipai_ai_user,1,1,1,0
```

### Record Rules

Pattern: `ipai_ai_rule_*`

## Controllers / Routes (Clean + Stable)

### Assistant Shell Endpoints

| Route | Purpose |
|-------|---------|
| `/ipai/ai/chat` | Chat endpoint |
| `/ipai/ai/run` | Run execution |
| `/ipai/ai/context` | Context retrieval |
| `/ipai/ai/threads` | Thread management |
| `/ipai/ai/messages` | Message management |

### Agent-Specific Endpoints

| Route | Purpose |
|-------|---------|
| `/ipai/ai/agent/finance/*` | Finance agent endpoints |
| `/ipai/ai/agent/sales/*` | Sales agent endpoints |
| `/ipai/ai/agent/helpdesk/*` | Helpdesk agent endpoints |

## Repository Layout (OCA Standard)

```
addons/ipai/
├── ipai_ai_assistant/
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── ai_thread.py
│   │   ├── ai_message.py
│   │   └── ai_run.py
│   ├── views/
│   │   ├── ai_thread_views.xml
│   │   └── menu.xml
│   ├── security/
│   │   ├── ir.model.access.csv
│   │   └── security.xml
│   ├── controllers/
│   │   ├── __init__.py
│   │   └── main.py
│   └── static/
│       └── src/
├── ipai_ai_agent_core/
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── ai_agent.py
│   │   └── ai_tool.py
│   ├── security/
│   └── data/
├── ipai_ai_agent_finance/
├── ipai_ai_agent_sales/
├── ipai_ai_agent_helpdesk/
└── ipai_ai_tools_finance/
```

### Module Rules

- No weird top-level folders
- No mixed concerns
- Standard Odoo module structure

## Agent Registry Model

The `ipai.ai.agent` model stores agent metadata:

```python
class IpaiAiAgent(models.Model):
    _name = 'ipai.ai.agent'
    _description = 'AI Agent Registry'

    technical_name = fields.Char(required=True)  # e.g., 'agent_finance'
    display_name = fields.Char(required=True)    # e.g., 'Finance Agent'
    module = fields.Char(required=True)          # e.g., 'ipai_ai_agent_finance'
    enabled = fields.Boolean(default=True)
    description = fields.Text()
    tool_ids = fields.Many2many('ipai.ai.tool')
```

## UI Label Mapping

Store labels in `ipai.ai.agent` records to rename UI without breaking IDs:

| Field | Example |
|-------|---------|
| `technical_name` | `agent_finance` |
| `display_name` | `Finance Copilot` |
| `module` | `ipai_ai_agent_finance` |
| `enabled` | `True` |

**User-facing naming** can still say:
- "Ask AI Copilot"
- "Copilot"
- "Finance Copilot"

But internally it stays:
- `ipai_ai_assistant` (shell)
- `ipai_ai_agent_*` (packs)

## Install Order (OCA-Clean)

```
1. CE/OCA base apps (mail, crm, sale, account, etc.)
2. OCA infra (queue_job, REST framework if used)
3. ipai_ai_assistant
4. ipai_ai_agent_core
5. Optional packs (ipai_ai_agent_finance, ipai_ai_agent_sales, ...)
```

## Dependency Graph

```
ipai_ai_assistant
    └── ipai_ai_agent_core
        ├── ipai_ai_agent_finance
        │   └── ipai_ai_tools_finance (optional)
        ├── ipai_ai_agent_sales
        └── ipai_ai_agent_helpdesk
```

## Migration from "Copilot" Naming

### What Changes

| Old | New (Canonical) |
|-----|-----------------|
| `ipai_ai_copilot` | `ipai_ai_assistant` |
| Mixed skills in one module | Separate `ipai_ai_agent_*` packs |
| `services/tools.py` | `ipai_ai_agent_core` + domain packs |

### Why This is Better

- One UI + thread/run/audit backbone (**assistant**) reused everywhere
- Multiple capability packs (**agents**) installable per client
- Cleaner dependency graph (OCA expectation)
- Ship "Finance Copilot" without dragging "Sales Copilot" code

## Validation Rules (CI Enforced)

The validator script checks:

| Rule | Pattern |
|------|---------|
| Module name matches folder | `addons/ipai/ipai_ai_*` |
| Model names start with | `ipai.ai.` |
| Groups are named | `group_ipai_ai_*` |
| Routes start with | `/ipai/ai/` |
| XML IDs are module-prefixed | `<module>.<record_id>` |
| No mixed "assistant/agent" naming in module ids | Enforced |

## Canonical Module List

### Minimum Viable Set

| Module | Priority | Purpose |
|--------|----------|---------|
| `ipai_ai_assistant` | P0 | Drawer + thread/run models + router + audit |
| `ipai_ai_agent_core` | P0 | Base tools: summarize, activity, open action |
| `ipai_ai_agent_finance` | P1 | Vendor bills, reconciliation, close checklist |
| `ipai_ai_agent_sales` | P1 | Quotes, pipeline, follow-ups |
| `ipai_ai_agent_helpdesk` | P2 | Triage, SLA, canned replies |

## Full Dependency Graph (YAML)

```yaml
# === Canonical OCA-style "Copilot" (Ask AI) module set ===
# Install order: CE/OCA base apps -> OCA infra -> Assistant shell -> Agent packs

ipai_ai_stack:
  ce_core_required:
    - base
    - web
    - mail
    - base_setup
    - contacts

  ce_business_by_domain:
    finance:
      - account
    sales:
      - sale_management
      - crm
    procurement:
      - purchase
    inventory_optional:
      - stock
    projects_optional:
      - project
      - hr_timesheet

  oca_infra_required:
    repos:
      - OCA/queue         # queue_job, queue_job_batch, etc.
    modules:
      - queue_job

  oca_infra_optional_recommended:
    repos:
      - OCA/rest-framework
    modules:
      - base_rest
      - base_rest_datamodel

  ipai_modules_ship_now:
    # 1) Assistant shell (UI + thread/run/audit backbone)
    - name: ipai_ai_assistant
      depends:
        - web
        - mail
        - queue_job

    # 2) Core agent (shared tool allowlist + router + permissions)
    - name: ipai_ai_agent_core
      depends:
        - ipai_ai_assistant
        - base_rest   # if you choose REST endpoints (optional)
        - base_rest_datamodel

    # 3) Domain packs (install only what client needs)
    - name: ipai_ai_agent_finance
      depends:
        - ipai_ai_agent_core
        - account

    - name: ipai_ai_agent_sales
      depends:
        - ipai_ai_agent_core
        - sale_management
        - crm

    - name: ipai_ai_agent_helpdesk
      depends:
        - ipai_ai_agent_core
        - helpdesk_mgmt   # OCA helpdesk

  oca_helpdesk_stack_if_used:
    repos:
      - OCA/helpdesk
    modules:
      - helpdesk_mgmt
      - helpdesk_mgmt_project     # optional bridge
      - helpdesk_mgmt_timesheet   # optional bridge
      - helpdesk_mgmt_sla         # optional

  optional_platform_bridge:
    - name: ipai_ai_gateway_bridge
      depends:
        - ipai_ai_agent_core
```

## Install Commands (CLI)

```bash
# === Minimal Odoo module install order (CLI-safe) ===
# Run in your Odoo container; adjust -d <db> and addons-path as needed.

odoo -d odoo -i queue_job --stop-after-init
odoo -d odoo -i ipai_ai_assistant --stop-after-init
odoo -d odoo -i ipai_ai_agent_core --stop-after-init
odoo -d odoo -i ipai_ai_agent_finance --stop-after-init
odoo -d odoo -i ipai_ai_agent_sales --stop-after-init
odoo -d odoo -i ipai_ai_agent_helpdesk --stop-after-init
```

## Coding Agent Prompt

Use this prompt when implementing the AI module stack with GitHub Copilot, Claude Code, or other coding agents:

```text
You are implementing the canonical OCA-style "Ask AI Copilot" stack for Odoo 18 CE + OCA.

Goal
- Replace any existing ipai_ai_copilot naming with OCA-style modules:
  1) ipai_ai_assistant (shell)
  2) ipai_ai_agent_core (shared tool router + allowlist)
  3) domain packs: ipai_ai_agent_finance, ipai_ai_agent_sales, ipai_ai_agent_helpdesk
- Keep custom code minimal and modular. The "Copilot" UX is the Assistant shell; capabilities live in agent packs.

Hard Rules
- OCA style: module names, XML IDs, models, security groups, manifests follow OCA conventions.
- No direct execution by LLM: the assistant creates "runs" (previews), and only allowlisted tools can execute.
- All tool execution must enforce ACL + record rules (no sudo() for user actions).
- Install order is strict: CE apps -> OCA infra (queue_job, optional base_rest) -> ipai_ai_assistant -> ipai_ai_agent_core -> packs.
- Add a simple validator script + CI job to enforce naming conventions and dependency rules.

Deliverables (write all to repo)
1) addons/ipai_ai_assistant/
   - models: ipai.ai.thread, ipai.ai.message, ipai.ai.run, ipai.ai.audit, ipai.ai.agent
   - controllers: /ipai/ai/chat, /ipai/ai/run, /ipai/ai/context
   - assets: OWL drawer + systray button + TBWA theme scss
   - security: base groups group_ipai_ai_user, group_ipai_ai_manager + ACL + record rules

2) addons/ipai_ai_agent_core/
   - services: router + tool registry + allowlist executor
   - tools: create_activity, open_action, summarize_chatter (read-only), draft_message (no send)
   - security: group_ipai_ai_agent_core_user/manager
   - optional REST datamodel usage if base_rest is installed

3) addons/ipai_ai_agent_finance/
   - depends: account
   - tools: draft vendor bill from PO/invoice context (preview only), create vendor bill (executed via tool with ACL)
   - security groups: group_ipai_ai_agent_finance_user/manager

4) addons/ipai_ai_agent_sales/
   - depends: sale_management, crm
   - tools: draft quotation email, summarize opportunity, create follow-up activity

5) addons/ipai_ai_agent_helpdesk/
   - depends: helpdesk_mgmt (OCA) OR provide a clean conditional dependency strategy
   - tools: triage ticket (suggest stage/assignee), draft reply, create activity

6) docs/ai/AI_ASSISTANT_ARCHITECTURE.md
   - explain assistant vs agent packs, tool-run contract, security model, install order

7) scripts/validate_ai_naming.py + .github/workflows/ai-naming-gate.yml
   - fail if:
     - module name doesn't match folder
     - models not prefixed ipai.ai.
     - groups not group_ipai_ai_*
     - routes not /ipai/ai/*
     - XML IDs missing module prefix

Verification Commands
- Odoo: install/upgrade modules in correct order
- Run unit checks (if present)
- Smoke: curl /ipai/ai/context (auth user), open drawer in UI
- Confirm tool execution respects ACL (attempt with restricted user)
```

---

*Last updated: 2026-01-08*
