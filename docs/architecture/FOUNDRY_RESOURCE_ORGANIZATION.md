# Foundry Resource Organization

> Topology model for Azure AI Foundry resources across the IPAI platform.
>
> **Doctrine**: Use Foundry's enterprise-readiness model for `agent-platform` and the AI resource plane. Keep Odoo as the transactional consumer of AI services.

---

## 1. Organizational pattern

**Selected**: Resource per environment, projects per use case.

Microsoft documents three patterns:

| Pattern | Fit for IPAI | Why |
|---|---|---|
| Resource per team | Poor | Single builder, no team isolation needed |
| Resource per product/project | Good later | Right when multiple product lines diverge |
| **Resource per environment** | **Best now** | Matches dev/test/prod promotion model |
| Single shared resource | Poor | Microsoft warns this leads to clutter, weak isolation, and governance problems at scale |

### Near-term target

```
ai-foundry-dev     (Dev environment)
├── project: ipai-copilot
├── project: tax-compliance-intel
├── project: document-intel
└── project: shared-retrieval

ai-foundry-test    (Test environment)
├── (mirrors dev projects)

ai-foundry-prod    (Production environment)
├── (mirrors dev projects, promoted)
```

---

## 2. Repo ownership

| Concern | Owner repo | Foundry scope |
|---|---|---|
| Foundry resource provisioning | `infra` | Resource-level IaC |
| Environment separation / RBAC | `infra` | Resource-level policy |
| APIM / gateway / networking | `infra` | Network-level controls |
| Project workspace usage | `agent-platform` | Project-level code |
| Retrieval / orchestration | `agent-platform` | Project-level pipelines |
| Attachment ingestion | `agent-platform` | Project-level data flows |
| Shared AI service integration | `agent-platform` | Cross-project contracts |
| Governance hooks / policy metadata | `platform` | Control-plane references |
| Odoo copilot consumption | `odoo` | Consumer only — no Foundry ownership |

---

## 3. What Odoo owns vs. does not own

### Odoo owns
- Transactional ERP surface
- Copilot UI (systray panel, chat, action dispatch)
- Skill routing to AI services
- `ir.attachment` lifecycle for user-uploaded files

### Odoo does not own
- Foundry project configuration
- Model deployment or selection
- Retrieval index management
- Agent orchestration runtime
- AI service boundaries or scaling

Odoo **consumes** AI services. It does not **host** them.

---

## 4. Project-to-use-case mapping

| Foundry project | Use case | Primary consumer |
|---|---|---|
| `ipai-copilot` | Odoo copilot chat, action dispatch, contextual assistance | `odoo` (via `agent-platform` API) |
| `tax-compliance-intel` | BIR tax validation, compliance explanation, review workflows | `odoo` BIR modules + `agent-platform` |
| `document-intel` | Invoice/receipt extraction, attachment intelligence | `odoo` + Azure Document Intelligence |
| `shared-retrieval` | Cross-project search index, knowledge base retrieval | All consumers via `agent-platform` |

---

## 5. Environment promotion model

```
Dev  ──→  Test  ──→  Prod
 │          │          │
 └──────────┴──────────┘
   IaC-driven promotion
   (infra/ repo, AzDO pipelines)
```

- Each environment has its own Foundry resource
- Projects are mirrored across environments
- Model deployments are pinned per environment
- Promotion is IaC-driven, not console-driven

---

## 6. RBAC caveat

Microsoft's current Foundry RBAC has a known limitation: some permissions inherit from the parent resource scope rather than being fully isolated per project. This means:

- Do not assume perfect per-project access isolation without testing in tenant
- Validate RBAC boundaries before granting cross-team access to individual projects
- Monitor Microsoft updates — project-scoped RBAC is expected to improve

Source: community feedback on [Organising the AI Foundry: A Practical Guide for Enterprise Readiness](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/organising-the-ai-foundry-a-practical-guide-for-enterprise-readiness/4433720).

---

## 7. What this document does NOT cover

- Foundry SDK v2 migration details → see `reference_foundry_sdk_v2_migration.md` in memory
- Model catalog selection → see `reference_foundry_model_catalog.md` in memory
- Agent identity lifecycle → see `reference_entra_agent_id.md` in memory
- Runtime benchmark hierarchy → see [BENCHMARK_MODEL.md](BENCHMARK_MODEL.md)

---

## 8. Doctrine

1. **Resource per environment** is the default Foundry organizational model.
2. **Projects per use case** within each environment.
3. **`agent-platform`** owns Foundry project-level code and orchestration.
4. **`infra`** owns Foundry resource provisioning and environment separation.
5. **Odoo** is a consumer of AI services, never the Foundry runtime authority.
6. **Console-only changes are banned** — all Foundry configuration must have a repo commit.

---

*Created: 2026-04-09*
