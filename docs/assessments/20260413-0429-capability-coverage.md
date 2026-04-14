# Capability-to-Spec Coverage Assessment — 2026-04-13

**Scope:** `Insightpulseai/odoo` monorepo · assessed read-only, no resource changes
**Inventory stamp:** 2026-04-13T04:29Z

## 1. Executive summary

- **54** spec bundles in scope
- **FULL coverage: 19** · **PARTIAL: 24** · **UNCOVERED: 8** · **SUPERSEDED: 3**
- **Top 3 gaps**: ① no repo-scoped skill for **Fabric / Power BI Serving** (user-scope skills are Power BI only, no Fabric workspace admin at repo level); ② no skill or subagent for **Meta / Google Ads integration** (referenced by `meta-integration-bridge` and `marketing-agency-stack`); ③ no canonical skill for **task router / orchestration hardening** (specs `task-router-hardening`, `release-gates-hardening` have no matching capability artifact).

## 2. Capability-to-spec matrix

| Spec bundle | Status | Required capabilities | Covered by | Gaps |
|---|---|---|---|---|
| **pulser-odoo** (umbrella) | FULL | cross-cutting architecture, RBAC, evidence, governance | `ipai-agent-platform`, `ipai-resource-map`, `spec-kit-review`, `ssot-reviewer`, `architecture-judge`, `entra-identity-governance`, `azure-runtime-review` | — |
| **pulser-project-to-profit** | PARTIAL | project lifecycle, margin, billing, Doc Intel | `odoo-oca-governance`, `azure-document-intelligence`, `ipai-agent-platform` | Missing: project-accounting domain skill; WBS/margin evaluator |
| **pulser-record-to-report** | PARTIAL | close, reconciliation, BIR, reporting, tax evidence | `odoo-oca-governance`, `azure-document-intelligence`, `ipai-resource-map` | Missing: close-orchestration skill; BIR-form validator |
| **pulser-odoo-ph** | PARTIAL | PH BIR + payroll specialization | `odoo-oca-governance`, `azure-document-intelligence` | Missing: BIR compliance skill |
| **pulser-entra-agent-id** | FULL | Entra app regs, MIs, Bot Framework, Agent 365 | `entra-identity-governance`, `ipai-agent-platform`, `azure-identity-py`, `microsoft-foundry`, `agents-v2-py`, `azure-ai-projects-py` | — |
| **odoo-on-azure / odoo-on-azure-operations** | FULL | ACA, AFD, KV, PG, MI, tags | `azure-container-apps`, `azure-front-door`, `azure-key-vault`, `azure-database-postgresql`, `azure-container-registry`, `azure-runtime-review`, `ipai-resource-map` | — |
| **odoo-sh-azure-equivalent / odoo-sh-equivalent-staging** | FULL | staged refresh, sanitization, gated promotion, ACA env | `azure-container-apps`, `azure-runtime-review`, `ipai-resource-map`, `ship`, `deploy`, `land-and-deploy` | — |
| **odoo-chatgpt-connector** | FULL | OAuth (Entra), TS runtime, MCP adapter | `azure-identity-py`, `azure-postgres-ts`, `entra-identity-governance`, `ipai-agent-platform` | — |
| **odoo-foundry-vscode-extension** | PARTIAL | VS Code extension dev, Foundry SDK 2.x | `microsoft-foundry`, `azure-ai-projects-py`, `ipai-agent-platform` | Missing: VS Code extension dev skill (TS + vsce patterns) |
| **odoo-ios-mobile** | UNCOVERED | iOS webview wrapper, biometric, App Store | `docs/skills/ios-native-wrapper.md` (markdown only, no SKILL.md) | No Claude skill yet — consider porting the doc to a SKILL.md |
| **expense-parity-odoo** | PARTIAL | expense claim, receipt extraction, BIR 2307 | `azure-document-intelligence`, `odoo-oca-governance` | Missing: expense-policy validator |
| **reverse-avatax-odoo18-pulser** | PARTIAL | tax engine comparison, VAT rules | `azure-document-intelligence`, `ipai-resource-map` | Missing: tax-engine-benchmark skill |
| **reverse-sap-concur / sap-joule-concur-odoo-azure** | UNCOVERED | SAP Concur API, Joule patterns | — | No SAP-adapter skill; CLAUDE.md invariant #17 says SAP is benchmark-only |
| **agentic-global-compliance-cloud** | FULL | compliance rules, policy gating, audit trail | `entra-identity-governance`, `ci-workflow-audit`, `cso`, `security-reviewer`, `ssot-reviewer` | — |
| **agent-factory** | PARTIAL | agent scaffolding, skill creation | `librarian-indexer`, `ipai-agent-platform`, `superpowers:writing-skills` | Missing: agent test-harness skill |
| **agent-deployments-hardening** | PARTIAL | rollout, canary, guardrails | `azure-runtime-review`, `canary`, `land-and-deploy`, `deployment:blue-green-deployment` | Missing: agent-specific rollout/safety skill |
| **task-router-hardening** | UNCOVERED | multi-agent routing, planner/router patterns | — | **P0 gap** — no skill covers planner/router hardening for Pulser's multi-agent model |
| **release-gates-hardening** | UNCOVERED | gate definition, pre-merge validation, ship-readiness | `spec-kit-review`, `review`, `ship`, `superpowers:verification-before-completion` (partial) | **P0 gap** — no canonical release-gate skill; drifts across 4 artifacts |
| **eval-engine-hardening** | PARTIAL | eval suite, judge panel, scoring | `agents/foundry/gates/`, `review`, `architecture-judge` | Missing: eval-engine skill (currently only documented in agent-platform/) |
| **release-manager** | PARTIAL | version bump, changelog, release automation | `ship`, `deploy`, `claude-mem:version-bump`, `git-workflow:create-pr` | Missing: release-manager skill (has IaC but no Claude skill) |
| **target-platform-architecture** | FULL | platform topology, SaaS authority, CAF alignment | `azure-runtime-review`, `ipai-resource-map`, `architecture-judge`, `ssot-reviewer` | — |
| **azure-devops-pipeline-baseline** | PARTIAL | AzDO pipelines, YAML patterns | MCP `azure-devops/*` tools, `ci-workflow-audit` | Missing: AzDO-native skill (only MCP, no pattern skill) |
| **azure-selfhost-migration** | FULL | Azure migration, IaC, secrets | `azure-container-apps`, `azure-key-vault`, `entra-identity-governance`, `azure-runtime-review` | — |
| **entra-identity-migration** | FULL | Entra tenant bootstrap, OIDC, MI | `entra-identity-governance`, `azure-identity-py`, `ipai-resource-map` | — |
| **databricks-bundles-foundation** | PARTIAL | Databricks Asset Bundles, DLT | `docs/databricks/LOCAL_DEV.md` (doc only) | Missing: Databricks Asset Bundle skill (doc exists, no SKILL.md) |
| **fabric-power-bi-serving** | PARTIAL | Fabric workspace, Power BI serving, mirroring | user-scope PBI skills (dax-*, fabric-deploy, model-*, report-*, workspace-admin, usage-metrics) | **P1 gap** — all PBI skills are user-scoped; no repo-scoped Fabric/PBI skill; teammates who clone don't get them |
| **adls-etl-reverse-etl** | PARTIAL | ADLS Gen2, ETL patterns | `azure-container-apps`, `azure-postgres-ts` (for pg→adls) | Missing: ADLS + ETL skill |
| **document-intelligence** | FULL | Azure DI prebuilt + custom | `azure-document-intelligence`, `azure-ai-contentsafety-py` | — |
| **finance-domain-intelligence** | PARTIAL | finance LLM, BIR grounding | `azure-document-intelligence`, `ipai-agent-platform` | Missing: finance-domain LLM skill |
| **finance-unified** | PARTIAL | unified finance ops, close, reporting | `azure-document-intelligence`, `odoo-oca-governance` | Missing: close-orchestration skill (same gap as R2R) |
| **taxpulse-ph / tax-pulse-sub-agent / pulsetax-agentic-control-plane** | PARTIAL | PH BIR, tax sub-agent, control plane | `azure-document-intelligence`, `ipai-agent-platform` | Missing: BIR tax compliance skill (cited in 3+ bundles) |
| **meta-integration-bridge** | UNCOVERED | Meta CAPI, Graph API, attribution | — | **P1 gap** — no Meta/Facebook integration skill |
| **unified-api-gateway** | PARTIAL | API gateway patterns, APIM | `azure-container-apps`, MCP `azure/apim` | Missing: APIM-native skill |
| **gmail-inbox-addon / gmail-mail-plugin** | PARTIAL | Google Workspace addon, OAuth | `docs/skills/gmail-addon-marketplace-publishing.md` (doc only) | Missing: SKILL.md form of Gmail addon skill |
| **plane-unified-docs** | PARTIAL | Plane project mgmt, unified docs | MCP `plane/*` tools | Missing: Plane-native skill |
| **microsoft-marketplace-go-to-market / microsoft-practice-build** | PARTIAL | Partner Center, marketplace publishing | `docs/runbooks/activate-partner-center-benefits.md`, `docs/gtm/MARKETPLACE_OFFER.md` | Missing: Partner-Center SKILL.md form |
| **marketing-agency-stack / ugc-mediaops-kit** | UNCOVERED | marketing agency workflows, UGC ops | user-scope `design-*` (only) | No marketing-ops skill |
| **w9-studio-copilot** | UNCOVERED | studio booking, photo ops, gym crossover | — | No W9 Studio skill |
| **diva-goals** | SUPERSEDED | Viva Goals migration | — | Memory `project_pulser_capability_taxonomy` cites this as deprecated |
| **landing-ai** | UNCOVERED | Landing AI, extract | `azure-document-intelligence` (partial substitute) | No Landing AI skill |
| **fluent-designer-agent** | PARTIAL | Fluent 2 design | `kasangkap-fluent` (user-scope), `ui-ux-pro-max` | Missing: repo-scope Fluent skill |
| **seed-dedup-remediation** | SUPERSEDED | seed cleanup (one-time) | — | Completed per spec STATUS |
| **docs-platform** | SUPERSEDED | docs site platform | — | docs-site exists; bundle is historical |
| **wholesale-saas-erp-azure** | PARTIAL | wholesale ERP vertical | `odoo-oca-governance`, `azure-runtime-review` | Missing: wholesale-domain skill |

## 3. Gaps by severity

### P0 (blocks in-flight work)

| # | Gap | Affected specs | Recommended action |
|---|---|---|---|
| 1 | Task router / planner hardening skill | task-router-hardening, agent-factory, pulser-odoo | Author `.claude/skills/agent-router-hardening/SKILL.md` — planner patterns, fallback policy, circuit breaking, evidence linkage |
| 2 | Release-gate skill (canonical) | release-gates-hardening, pulser-odoo, eval-engine-hardening | Author `.claude/skills/release-gates/SKILL.md` consolidating current gate logic from `agents/foundry/gates/` + `spec-kit-review` + `review` |

### P1 (blocks next-up bundles)

| # | Gap | Affected specs | Recommended action |
|---|---|---|---|
| 3 | BIR compliance skill (Philippines tax) | taxpulse-ph, tax-pulse-sub-agent, pulsetax-agentic-control-plane, pulser-odoo-ph | Author `.claude/skills/bir-compliance-ph/SKILL.md` — 2550Q/SLSP/SAWT forms, deadlines, e-filing |
| 4 | Close orchestration skill | pulser-record-to-report, finance-unified | Author `.claude/skills/close-orchestration/SKILL.md` — month-end checklist, accrual candidates, variance gates |
| 5 | Fabric / Power BI repo-scoped skill | fabric-power-bi-serving | Port user-scope `fabric-deploy` + `model-designer` + `workspace-admin` into one repo-scoped `fabric-serving` skill |
| 6 | Meta CAPI / attribution skill | meta-integration-bridge, marketing-agency-stack | Author `.claude/skills/meta-capi-bridge/SKILL.md` — CAPI events, conversion API, Graph API patterns |
| 7 | Databricks Asset Bundles skill | databricks-bundles-foundation | Port `docs/databricks/LOCAL_DEV.md` into `.claude/skills/databricks-bundles/SKILL.md` + DLT patterns |

### P2 (nice-to-have)

| # | Gap | Affected specs |
|---|---|---|
| 8 | VS Code extension dev skill | odoo-foundry-vscode-extension |
| 9 | iOS wrapper SKILL.md | odoo-ios-mobile (doc exists, needs skill frontmatter) |
| 10 | APIM-native skill | unified-api-gateway |
| 11 | Gmail add-on SKILL.md | gmail-inbox-addon, gmail-mail-plugin (doc exists) |
| 12 | Wholesale-ERP vertical skill | wholesale-saas-erp-azure |
| 13 | Marketing-ops skill | marketing-agency-stack, ugc-mediaops-kit |

## 4. Duplication / drift

| # | Finding | Evidence |
|---|---|---|
| 1 | **3 overlapping release-workflow skills** — `ship`, `land-and-deploy`, `deploy` — all cover merge→deploy→verify paths with slight variations | `~/.claude/skills/{ship,land-and-deploy,deploy}/SKILL.md` |
| 2 | **2 overlapping design-review skills** — `design-review` + `plan-design-review` both audit UI quality | `~/.claude/skills/design-review/`, `~/.claude/skills/plan-design-review/` |
| 3 | **6 Power BI skills live user-scoped only** — none in repo, so teammates cloning don't get them despite `fabric-power-bi-serving` spec requiring them | `~/.claude/skills/dax-*`, `fabric-deploy`, `workspace-admin`, etc. |
| 4 | **Orphan skills** (no spec references them) — `kasangkap-fluent`, `creative-web-pages`, `office-hours`, `pair-agent`, `scout-sari-commands`, `meta-analysis-pipeline` | These are personal/experimental — consider archiving or formalizing |
| 5 | **Stale skill — `odoo-check-env`, `odoo-audit-repo`** claim "Odoo 19" in description but repo is Odoo 18 CE | `~/.claude/skills/odoo-{check-env,audit-repo}/SKILL.md` — update descriptions |
| 6 | **Stale skill — `odoo-oca-governance`** references 19.0 CI status | `.claude/skills/odoo-oca-governance/SKILL.md` — update to 18.0 |
| 7 | **Duplicated governance skill — `roadmap-ssot-guard`** references "Supabase mirror" which is deprecated per CLAUDE.md | Update to reflect Azure-native posture (Supabase deprecated 2026-03-26) |
| 8 | **`azure-runtime-review`** and `architecture-judge` overlap on ACA review surface | One canonical choice needed — recommend keeping `azure-runtime-review` for pre-merge, `architecture-judge` for post-design |

## 5. Next 3 unblockers (ordered by leverage)

| # | Action | Affected specs | Effort | Who |
|---|---|---|---|---|
| 1 | **Author `release-gates/SKILL.md`** consolidating `agents/foundry/gates/` + `spec-kit-review` + `review` into one canonical pre-merge skill | release-gates-hardening, pulser-odoo, eval-engine-hardening (3 bundles) | M | Platform team (2-4h with existing content as source) |
| 2 | **Author `bir-compliance-ph/SKILL.md`** covering BIR 2550Q/2307/SLSP/SAWT/1601C forms, e-filing, grounding hierarchy | taxpulse-ph, tax-pulse-sub-agent, pulsetax-agentic-control-plane, pulser-odoo-ph, pulser-record-to-report (5 bundles — highest leverage single skill) | M | Finance + Platform pair (4-6h; memory `project_ph_grounding_hierarchy` already has 6-tier source model) |
| 3 | **Update stale Odoo skill descriptions** from "19" to "18 CE" in `odoo-oca-governance`, `odoo-check-env`, `odoo-audit-repo`, `roadmap-ssot-guard` | All 9 `pulser-*` + `odoo-*` specs (~20 bundles) | S | Repo owner (30 min — grep + Edit) |

---

## Methodology notes

- Spec names were parsed for domain keywords (odoo, azure, finance, tax, agent, etc.) and matched against skill descriptions.
- A spec is **FULL** only if every major capability domain has at least one covering skill or subagent. **PARTIAL** = some covered but material gaps. **UNCOVERED** = no matching artifact. **SUPERSEDED** = marked deprecated or completed.
- User-scoped skills (`~/.claude/skills/`) are counted as "available" for the executing developer, but flagged as non-portable — anyone cloning this repo fresh doesn't get them.
- No resource mutations performed during assessment.

## Inventory snapshot

- **54 spec bundles** in `spec/`
- **10 repo-scoped skills** in `.claude/skills/` (+ 2 uncommitted overlays)
- **~80 user-scoped skills** in `~/.claude/skills/` (including 14 Microsoft-official installed this session)
- **5 subagents** in `.claude/agents/` (architecture-judge, azure-startup-advisor, odoo-reviewer, security-reviewer, ssot-reviewer)
- **Agent framework**: `agent-platform/` runtime + `agents/foundry/` judges + `agents/studio/` (6 studios) + `agents/registry/skills-index.json`

---

*Assessment generated 2026-04-13T04:29Z — read-only, no resource changes*
