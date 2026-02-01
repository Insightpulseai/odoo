# Claude for Slack Integration — TBWA Finance SSC

## Overview

Claude for Slack is now live in the TBWA Finance workspace. This enables the Finance SSC team to leverage AI assistance directly within Slack for financial operations, BIR compliance, and development tasks.

## Authentication Model

**Per-User Authentication**: Each team member connects their individual Claude.ai account.

| Aspect | Detail |
|--------|--------|
| Auth Type | Individual Claude.ai accounts |
| Usage Limits | Tied to personal subscription |
| SSO | Not available (Pro/Team tier) |
| Enterprise Option | Claude for Enterprise (team-wide billing, admin controls) |

## Team Directory

| Employee Code | Name | Email | Role |
|--------------|------|-------|------|
| CKVC | Khalil Veracruz | khalil.veracruz@omc.com | Finance Director |
| RIM | Rey Meran | rey.meran@tbwa-smp.com | Finance Staff |
| JPAL | Jinky Paladin | jinky.paladin@omc.com | Finance Staff |
| JLI | Jerald Loterte | jerald.loterte@omc.com | Finance Staff |
| JM | Joana Maravillas | joana.maravillas@omc.com | Finance Staff |
| JI | Jasmin Ignacio | jasmin.ignacio@omc.com | Finance Staff |
| JO | Jhoee Oliva | jhoee.oliva@omc.com | Finance Staff |

**Note**: These are employee codes within a single legal entity (TBWA SMP), NOT separate tenants/agencies.

## Getting Started

### For Team Members

1. Find "Claude" in the Apps section of your Slack sidebar
2. Click to open a DM with Claude
3. Connect your Claude.ai account when prompted

### Starter Prompts for Finance Workflows

**Month-End Closing:**
```
Walk me through the month-end closing checklist for the current period
```

**BIR Compliance:**
```
What's the deadline and requirements for BIR Form 2550Q this quarter?
```

**Journal Entries:**
```
Help me draft a journal entry for accrued expenses with proper account mapping
```

**Variance Analysis:**
```
Review this trial balance export and flag any unusual variances
```

**Tax Treatment:**
```
Explain the withholding tax treatment for professional fees under BIR rules
```

## Claude Connector Configuration

### Currently Connected

| Connector | Status | Purpose |
|-----------|--------|---------|
| Google Drive | Active | Document access |
| GitHub | Active | Code repository |

### Recommended Additions

| Connector | Priority | Purpose |
|-----------|----------|---------|
| **n8n** | Critical | Automation backbone, workflow visibility |
| **Gmail** | Critical | Invoice/receipt emails, BIR confirmations |
| **Google Calendar** | High | Month-end deadlines, BIR filing dates |
| **Vercel** | Medium | Deployment visibility |
| **Figma** | Low | Design work |

## Use Cases by Role

### Finance Staff (RIM, JPAL, JLI, JM, JI, JO)

- Quick BIR form questions
- Journal entry validation
- Receipt classification
- Deadline reminders
- Policy lookups

### Finance Director (CKVC)

- Variance analysis review
- Compliance status checks
- Month-end progress tracking
- Management report drafting

### Development Team

- Odoo/OCA module questions
- n8n workflow debugging
- CI/CD troubleshooting
- Code review assistance

## Integration with InsightPulse Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                   CLAUDE INTEGRATION POINTS                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Slack ◄────────► Claude for Slack                             │
│     │                   │                                        │
│     │                   ├──► n8n (via connector)                │
│     │                   │    • Trigger workflows                 │
│     │                   │    • Debug failed runs                 │
│     │                   │                                        │
│     │                   ├──► Google Drive (connected)            │
│     │                   │    • Document analysis                 │
│     │                   │    • Receipt OCR context               │
│     │                   │                                        │
│     │                   └──► GitHub (connected)                  │
│     │                        • Code search                       │
│     │                        • PR assistance                     │
│     │                                                            │
│     └─────────────────► Mattermost (future migration)           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Security Considerations

1. **Data Residency**: Claude processes data per Anthropic's policies
2. **Sensitive Data**: Avoid sharing TINs, bank account numbers, or PII in prompts
3. **Audit Trail**: Slack retains conversation logs per workspace settings
4. **Credentials**: Never share API keys, passwords, or tokens with Claude

## Future Migration: Mattermost

Mattermost is deployed at `https://chat.insightpulseai.com` as an eventual Slack replacement for:
- Full data sovereignty (self-hosted)
- Zero per-user licensing cost
- Native playbook/workflow support
- Better n8n/Odoo integration via webhooks

## Support

- Slack: Reach out to Jake (jgtolentino)
- Documentation: `/docs/integration/`
- Issues: https://github.com/jgtolentino/odoo-ce/issues
