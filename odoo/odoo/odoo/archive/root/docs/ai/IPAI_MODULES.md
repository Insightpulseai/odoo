# IPAI Module Naming Convention
> Extracted from root CLAUDE.md. See [CLAUDE.md](../../CLAUDE.md) for authoritative rules.

---

All custom modules use the `ipai_` prefix organized by domain:

| Domain | Prefix Pattern | Examples |
|--------|---------------|----------|
| AI/Agents | `ipai_ai_*`, `ipai_agent_*` | `ipai_ai_agent_builder`, `ipai_ai_tools`, `ipai_ai_automations`, `ipai_ai_fields`, `ipai_ai_rag`, `ipai_ai_livechat` |
| Finance | `ipai_finance_*` | `ipai_finance_ppm`, `ipai_finance_close_seed`, `ipai_finance_tax_return`, `ipai_finance_workflow` |
| Auth | `ipai_auth_*` | `ipai_auth_oidc` |
| Design/Theme | `ipai_theme_*`, `ipai_web_*`, `ipai_ui_*`, `ipai_design_*` | `ipai_theme_tbwa`, `ipai_theme_fluent2`, `ipai_theme_copilot`, `ipai_ui_brand_tokens`, `ipai_design_system`, `ipai_web_fluent2`, `ipai_web_icons_fluent`, `ipai_web_theme_tbwa` |
| Documents | `ipai_documents_*` | `ipai_documents_ai` |
| Enterprise | `ipai_enterprise_*` | `ipai_enterprise_bridge` |
| ESG | `ipai_esg_*` | `ipai_esg`, `ipai_esg_social` |
| Helpdesk | `ipai_helpdesk*` | `ipai_helpdesk`, `ipai_helpdesk_refund` |
| HR | `ipai_hr_*` | `ipai_hr_payroll_ph` |
| Industry | `ipai_vertical_*` | `ipai_vertical_media`, `ipai_vertical_retail` |
| Integrations | `ipai_*_connector` | `ipai_ops_connector`, `ipai_whatsapp_connector` |
| Planning | `ipai_planning_*` | `ipai_planning_attendance` |
| Platform | `ipai_platform_*` | `ipai_platform_theme` |
| Sign | `ipai_sign` | `ipai_sign` |
| Website | `ipai_website_*` | `ipai_website_coming_soon` |

## Key Module Hierarchy

```
ipai_foundation                # Base dependencies (install first)
    └── ipai_design_system     # Design system core
        ├── ipai_ai_tools      # AI tool integrations
        │   ├── ipai_ai_agent_builder  # Agent builder
        │   ├── ipai_ai_automations    # AI automations
        │   ├── ipai_ai_fields         # AI-powered fields
        │   ├── ipai_ai_rag            # RAG pipeline
        │   └── ipai_ai_livechat       # AI livechat
        ├── ipai_finance_ppm           # Finance PPM
        │   ├── ipai_finance_workflow  # Finance workflows
        │   ├── ipai_finance_close_seed # Month-end seeds
        │   └── ipai_finance_tax_return # Tax returns
        ├── ipai_enterprise_bridge     # EE parity bridge
        ├── ipai_helpdesk              # Helpdesk
        │   └── ipai_helpdesk_refund   # Refund handling
        └── [other modules]
```
