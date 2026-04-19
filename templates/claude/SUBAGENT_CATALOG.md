# Subagent Catalog (IPAI)

Canonical subagent roles and when to invoke each. Complements `Agent` tool built-in agents.

**Rule**: default dispatch model is `sonnet` per CLAUDE.md routing. Use `haiku` for parsing/grep; `opus` only when task needs architecture-level reasoning.

---

## When to use a subagent

- 2+ independent tasks that can parallelize with separable file/plane ownership
- Context-protection (delegate heavy research so main session doesn't flood)
- Role specialization matches
- Explicit user request

**Don't** use subagents for:
- SSOT / architecture drafting (main session owns)
- Tightly coupled refactors
- Single simple task (use direct tools)

---

## Maker agents (execute work)

| Agent | Purpose | When |
|---|---|---|
| `python-expert` | Production Python code, typing, async, performance | Python implementation work |
| `python-pro` | Idiomatic Python, design patterns, testing | Python refactor / optimization |
| `backend-architect` | Reliable backend systems, data integrity, fault tolerance | Backend system design |
| `frontend-architect` | Accessible UI, user experience, modern frameworks | UI/UX work |
| `database-architect` | Data modeling, scalability, tech selection | Schema design decisions |
| `database-optimizer` | SQL optimization, N+1 problems, indexing | Query performance |
| `neon-database-architect` | Neon + Drizzle ORM | Neon-specific schema |
| `supabase-schema-architect` | Supabase schema + RLS (**IPAI deprecated — do not use**) |  |
| `terraform-specialist` | Terraform modules, state, drift | IaC work |
| `cloud-architect` | AWS/Azure/GCP infra design | Cloud architecture |
| `devops-architect` | Automated infra + deployment | DevOps pipelines |
| `deployment-engineer` | CI/CD, Docker, K8s, GH Actions | Deployment automation |
| `network-engineer` | Networking, load balancers, DNS, SSL, CDN | Network work |
| `MCP Builder` | Design + build MCP servers | New MCP server |
| `Azure AVM Bicep mode` | Bicep IaC via Azure Verified Modules | Azure Bicep |
| `Azure AVM Terraform mode` | Terraform IaC via AVM | Azure Terraform |
| `Azure Logic Apps Expert Mode` | Logic Apps workflow design | Logic Apps |
| `Azure Principal Architect mode` | Well-Architected guidance | Azure architecture review |
| `Azure SaaS Architect mode` | Multitenant SaaS on Azure | SaaS architecture |
| `Expert React Frontend Engineer` | React 19.2, Server Components, Actions | React work |
| `Odoo Reviewer` | Odoo module review (CE compliance, OCA-first, 18) | Odoo module PR review |
| `neon-auth-specialist` | Stack Auth + Neon | Auth integration |
| `neon-expert` | Neon general | Neon general |

---

## Judge agents (evaluate / review)

| Agent | Purpose | When |
|---|---|---|
| `quality-engineer` | Testing strategy, edge case detection | Test coverage, QA design |
| `Reality Checker` | Stops fantasy approvals, evidence-based certification | Final review before "done" |
| `Evidence Collector` | Screenshot-obsessed QA specialist | Visual evidence capture |
| `security-engineer` | Security architecture + compliance | Security review |
| `Security Reviewer` | Secrets, RBAC, Key Vault, baseline compliance | Security PR review |
| `SSOT Reviewer` | SSOT compliance, no generated-file edits, cross-boundary contracts | SSOT PR review |
| `Architecture Judge` | Evaluate against target architecture | Architecture review |
| `Agent Governance Reviewer` | Agent safety + governance controls | Agent PR review |
| `Agentic Identity & Trust Architect` | Agent identity + trust | Agent identity design |
| `Automation Governance Architect` | Audit value, risk, maintainability of automations | Automation proposals |
| `Compliance Auditor` | SOC 2 / ISO 27001 / HIPAA / PCI-DSS | Compliance audit |
| `monitoring-specialist` | Metrics, alerting, logs, tracing, SLAs | Observability |
| `devops-troubleshooter` | Debug, log analysis, incident response | Production incidents |
| `database-admin` | DB ops, backups, replication | DB operations |
| `Agents Orchestrator` | Autonomous pipeline manager | End-to-end workflow lead |

---

## Research / investigation agents

| Agent | Purpose | When |
|---|---|---|
| `Explore` | Fast codebase exploration | Search for files / code / patterns |
| `Plan` | Implementation plan design | Complex multi-file planning |
| `Context Architect` | Identify relevant context for multi-file changes | Scoping changes |
| `deep-research-agent` | Adaptive research strategies | Deep research questions |
| `root-cause-analyst` | Evidence-based hypothesis testing | Complex bugs |
| `business-panel-experts` | Strategy panel (Christensen, Porter, etc.) | Strategic framing |
| `requirements-analyst` | Transform ambiguous ideas into specs | Spec drafting |
| `Compliance Auditor` | Audit existing posture | Compliance gap |
| `Azure Policy Analyzer` | Azure compliance posture | Azure policy review |
| `Defender Scout KQL` | Defender XDR KQL hunting | Security hunting |
| `Kusto Assistant` | KQL / Azure Data Explorer | KQL queries |
| `general-purpose` | Default catch-all | When no specialist fits |

---

## Platform-specific

| Agent | Purpose |
|---|---|
| `pm-agent` | Self-improvement workflow executor |
| `ADR Generator` | Architectural Decision Records |
| `claude-code-guide` | Claude Code / SDK / API questions |
| `MCP M365 Agent Expert` | M365 Copilot MCP declarative agents |
| `azure-iac-exporter` | Export Azure to IaC |
| `azure-iac-generator` | Generate IaC |
| `vercel-deployment-specialist` | Vercel (**IPAI deprecated**) |

---

## Support / UX / writing

| Agent | Purpose |
|---|---|
| `technical-writer` | Documentation tailored to audience |
| `learning-guide` | Teach programming concepts |
| `socratic-mentor` | Discovery learning via questions |
| `Bookkeeper & Controller` | Accounting operations, reconciliations |
| `FP&A Analyst` | Financial planning + analysis |
| `Tax Strategist` | Tax optimization + compliance |
| `refactoring-expert` | Code quality improvement |
| `performance-engineer` | Bottleneck elimination |

---

## Dispatch pattern

```python
Agent(
    subagent_type="python-expert",
    description="4-word task summary",
    model="sonnet",  # sonnet default, haiku for parsing, opus for deep reasoning
    prompt="""
    Self-contained task context (the subagent has NO conversation memory).
    State: goal, what you know, what you've tried, expected output format.
    Specify: files to touch, files NOT to touch, commit message format.
    """,
    run_in_background=True,  # optional, if independent from main session
)
```

---

## Forbidden

- Dispatching subagents for SSOT / architecture drafting
- Dispatching subagents without self-contained prompt
- Duplicating work across parallel subagents
- Auto-merging subagent output without main-session review
- Using subagents to bypass approval boundaries in [CLAUDE_CODE_OPERATING_STANDARD.md §7](../../docs/operating/CLAUDE_CODE_OPERATING_STANDARD.md)

---

## IPAI-specific notes

- **Odoo-adjacent work** → fill [interoperability template](../../ssot/odoo/interoperability-template.yaml) BEFORE dispatching a subagent
- **Finance mutations** → `finance_correctness_judge` + `policy_judge` + `responsible_ai_judge` required
- **Identity / privileged** → `security-engineer` + human approval mandatory
- **Agent runtime work** → `agent-platform/src/agent_platform/` boundary; no `agent_framework` imports elsewhere

---

## Related

- [CLAUDE_CODE_OPERATING_STANDARD.md](../../docs/operating/CLAUDE_CODE_OPERATING_STANDARD.md)
- [SESSION_LIFECYCLE.md](../../docs/operating/SESSION_LIFECYCLE.md)
- [HEADLESS_AGENT_WORKFLOWS.md](../../docs/operating/HEADLESS_AGENT_WORKFLOWS.md)
- [agents/ catalog](../../agents/)
- [Pulser pack matrix](../../platform/ssot/agents/pulser-pack-matrix.yaml)
