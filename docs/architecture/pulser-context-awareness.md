# Pulser Context Awareness & Domain Packs

**Status**: canonical
**Authority**:
- [platform/ssot/agents/pulser-context-awareness.yaml](../../platform/ssot/agents/pulser-context-awareness.yaml)
- [platform/ssot/agents/pulser-domain-packs.yaml](../../platform/ssot/agents/pulser-domain-packs.yaml)

---

## One-sentence doctrine

Pulser Core resolves actor, tenant, domain, branch, environment, and contact
into a typed context envelope, then selects persona, task plan, tools, and
judges from governed domain packs. Orchestration, policy, audit, and
resolution stay centralized; split personas, tasks, and judges by domain
only when authority, risk, ontology, or tenancy meaningfully diverge.

---

## Why

Pulser is NOT a single prompt with lots of instructions. It is a
context-resolved orchestration layer with:

1. A typed **context envelope** (actor / tenant / organization / domain /
   environment / contact / policy / task).
2. A **resolution pipeline** that starts with context, not with a model call.
3. A **policy engine** that reads the envelope and decides allowed tools,
   approvals, and classification handling.
4. **Scoped skills** grouped into governed **domain packs** (one core + N
   domain packs).

---

## Separation of concerns — do not collapse

| Object | Meaning | Decides |
|---|---|---|
| Persona | How the assistant behaves/communicates | Voice, framing, output shape |
| Task | What job is happening right now | Planner, tool chain, success criteria |
| Judge | Who evaluates quality/safety/policy | Acceptance, escalation |
| Role | What permissions/authority the actor has | Data visibility, write permission |
| Expertise | How much explanation is needed | Jargon level, verbosity |

Persona does NOT decide authority. Role + policy engine own authority.

---

## Resolution pipeline (10 steps)

Pulser MUST NOT start with a model call.

```
1  identify actor
2  resolve tenant / domain / branch / environment
3  resolve contact or object context
4  resolve requested task
5  select persona
6  build allowed toolset
7  apply policy and judges
8  plan
9  execute or answer
10 audit and store context evidence
```

Runtime placement:

| Component | Path |
|---|---|
| Context resolver | `agent-platform/src/agent_platform/orchestration/context_resolver.py` |
| Persona router | `agent-platform/src/agent_platform/orchestration/persona_router.py` |
| Task router | `agent-platform/src/agent_platform/orchestration/task_router.py` |
| Policy engine | `agent-platform/src/agent_platform/policy/` |
| Judge pipeline | `agent-platform/src/agent_platform/orchestration/judges/` |
| Execution engine | `agent-platform/src/agent_platform/runtime/` |

---

## Awareness dimensions

| Dimension | Definition | Drives |
|---|---|---|
| Contact-aware | Who the interaction is ABOUT, not just who is asking | Retrieval scope, tone, object filtering, approval routing, allowed disclosure |
| Environment-aware | dev/staging/prod + read-only vs execution-capable | Tool endpoints, auth targets, mutation permissions, safety thresholds |
| Branch-aware | Legal entity / branch / trade name / tax context | Journal selection, document numbering, BIR/tax context, branding |
| Domain-aware | Which business domain (ERP/finance/projects/…) | Planner, vocabulary, retrieval sources, toolset, escalation |
| Tenant-aware | Platform internal vs client vs workspace vs guest | Data partitions, tool tenancy, branding, compliance policy |

---

## Context inheritance (global → session → request)

| Scope | Fields |
|---|---|
| Global | actor, environment, tenant |
| Workspace / session | domain, branch, trade_name, selected_contact/account/project |
| Request | task, object, approval_mode, persona_override |

Rule: request overrides session, session overrides global. Never the reverse.

---

## Domain-pack model — one core + six+ domain packs

### Core (stay centralized)

Every Pulser experience needs these. Home: `agent-platform/` (runtime) +
`platform/ssot/agents/` (bindings).

- identity and actor resolution
- context envelope builder
- policy engine
- tool registry
- environment resolution
- audit/event model
- session/memory primitives
- citation/grounding framework
- judge orchestration framework
- telemetry/eval scaffolding

### Shared role packs (influenced by agency-agents taxonomy)

- `pulser_marketing`, `pulser_sales`, `pulser_support`, `pulser_strategy`, `pulser_product`, `pulser_engineering`, `pulser_project_management`

Home: `agents/shared/<category>/`.

### IPAI-owned domain-specific packs

- `pulser_prismalab`, `pulser_odoo_finance`, `pulser_odoo_erp`, `pulser_identity_ops`, `pulser_analytics`, `pulser_release_ops`

Home: `agents/domain/<domain>/`.

### Split triggers

Do **not** split just because prompts get longer. Split only when:

1. Different authority surface (ERP vs website vs PrismaLab vs identity admin)
2. Different risk profile (public content vs financial posting vs privileged identity)
3. Different domain ontology (finance vocabulary vs research vs marketing)
4. Different tenant isolation
5. Different latency/runtime profile
6. Different evaluation contract (finance accuracy/auditability vs content tone/brand)

---

## Per-site pack mapping

Three distinct operating surfaces. Not one product with three skins.

### `www.insightpulseai.com` — flagship platform

- **Role**: corporate/platform front door; product entry points
- **Shared**: strategy, product, web, support, release_ops
- **Optional**: finance, identity_ops
- **Domain**: platform_overview
- **Do**: present a platform operating model
- **Do not**: turn into an "agency roster UI"

### `www.w9studio.net` — commercial branch site

- **Role**: marketing, services showcase, lead intake
- **Shared**: marketing, sales, support
- **Optional**: project_management
- **Domain**: studio_commerce
- **Do not**: adopt deep agent orchestration, research workflows, or enterprise copilot governance

### `prismalab.insightpulseai.com` — specialized domain workspace

- **Role**: PRISMA-aligned systematic reviews & meta-analysis
- **Shared**: support
- **Domain**: prismalab_research, prismalab_screening, prismalab_extraction, prismalab_synthesis, prismalab_quality_judges
- **Why split earlier**: distinct ontology, evidence requirements, judges, task graph, higher grounding/audit expectations

---

## Upstream reference — `msitarzewski/agency-agents`

**Classification**: persona library reference only.

**Adopt**:
- Role decomposition
- Deliverable-oriented persona design
- Specialist team mental model
- Category-based agent packaging

**Never adopt as**:
- Runtime engine
- Multi-tenant control plane
- Production security model
- Tool execution framework
- Governed eval framework

---

## Repo placement

| Repo | Owns |
|---|---|
| `agent-platform/` | Context resolution runtime, policy engine, planner/router, judge execution, tool execution, sessions, audit trail |
| `agents/` | Persona definitions, task definitions, judge configs, expertise profiles, domain packs |
| `platform/` | Tenant/domain/branch/environment bindings, allowed-tool matrices, feature flags, identity-to-role mappings, context defaults |
| `web/` | Current workspace selection, branch/contact picker UX, domain surface hints, session state handoff to runtime |
| `addons/` (Odoo) | Canonical business objects, branch/legal/trade-name truth, transactional permissions, business-safe tool endpoints |

---

## Non-goals

- Not a single prompt with lots of instructions.
- Not a place for persona content (definitions live in `agents/`).
- Not a RBAC matrix (identity SSOT owns that).
- Not a tool registry (`agent_platform.tools.registry` owns that).
- Not fragmenting into many unrelated assistants before authority/risk/ontology/tenancy diverge.

---

## References

- Context-awareness SSOT: [platform/ssot/agents/pulser-context-awareness.yaml](../../platform/ssot/agents/pulser-context-awareness.yaml)
- Domain-pack SSOT: [platform/ssot/agents/pulser-domain-packs.yaml](../../platform/ssot/agents/pulser-domain-packs.yaml)
- Context boundary: [platform/ssot/agents/context-boundary.yaml](../../platform/ssot/agents/context-boundary.yaml)
- Agent framework adoption: [agent-framework-adoption.md](agent-framework-adoption.md)
- Business dimensions: [../../ssot/odoo/business_dimensions.yaml](../../ssot/odoo/business_dimensions.yaml)
- Site template adoption: [site-template-adoption.md](site-template-adoption.md)
