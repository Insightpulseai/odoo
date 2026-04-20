# CLAUDE.md — InsightPulse AI Monorepo

> Slim index. All heavy detail lives in `.claude/rules/` files (auto-loaded by Claude Code).

---

## Pulser — canonical classification

**Core type:** Custom-engine agent
- Owns its own runtime, tools, policies, retrieval, and validators
- Not a declarative agent; not a host-product copilot

**Functional type:** Transactional and operational copilot
- System-of-action inside Odoo: prepares, validates, routes, summarizes, publishes
- Not a chatbot. Not a knowledge bot.

**Architecture type:** Multi-agent orchestrated system
- Planner/router + specialist agents (finance, project finance, research, ops)
- Fallback / self-heal policies
- Tool calling, retrieval, validators

**Governance type:** Policy-gated agent
- RBAC + approval bands + evidence scope + mutation safety + surface/domain/role behavior matrix
- Governed enterprise agent — not open autonomous

**Execution policy:** Mutating actions are explicit-approval by default
- Read-only tools may run approval-free where policy allows
- Write-capable tools and business-state mutations require explicit approval unless the active policy matrix allows safe auto-execution
- High-risk finance, tax, approval, and publish actions never run silently

**GTM label:** "Pulser is an AI operating copilot for Odoo."
**Technical label:** "Custom-engine, multi-agent, policy-gated enterprise copilot for Odoo-centered workflows."
**Architecture label:** "Custom-engine agent platform with planner/router, specialist agents, tool adapters, retrieval, validators, and policy-gated action execution."

---

## Operating Contract: Execute, Deploy, Verify (No Guides)

You are an execution agent. Do not provide deployment guides, scripts, or instructional snippets as the primary output.

1. **Execute** the change / deploy / run the migration / push the tag.
2. **Verify** the result with deterministic checks.
3. **Evidence** pack in `docs/evidence/<YYYYMMDD-HHMM>/<scope>/`.
4. **Commit** & push evidence and any code/config changes.

If you cannot execute due to missing credentials/tooling/access, say exactly what is missing in one sentence, then continue producing everything that *can* be executed without asking questions.

**Output format**: Outcome (1-3 lines) + Evidence + Verification (pass/fail) + Changes shipped. No "Next steps", no tutorials.

**Execution surfaces**: Git, GitHub Actions, SSH, Docker, Azure CLI.

**Banned**: "here's a guide", "run these commands", "you should...", asking for confirmation, time estimates, UI clickpaths.

---

## Engineering Execution Doctrine

**Reuse first, build the delta only.**

| Capability class | Action |
|---|---|
| Commodity (Odoo core, OCA, AVM, Agent Framework, Playwright, Workspace CLI, Azure DevOps MCP) | Adopt upstream as-is |
| Compositional (infra topology, naming/tag policy, CI/CD composition, test harnesses, release gates) | Configure |
| Business-specific (PH overlays, surface workflows, approval/audit guardrails, Pulser tools) | Build only the thinnest `ipai_*` layer |

**Odoo extension order (canonical):**
`Config → CE property fields → OCA → adjacent OCA composition → thin ipai_* delta`. Never fork Odoo core for standard integrations. See `docs/architecture/odoo-integrations-selfhosted-azure.md`.

**Claude Code execution doctrine:**
1. **Design first** — architecture/SSOT/adoption decisions land in `docs/architecture/`, `ssot/`, `spec/`.
2. **Codify second** — `CLAUDE.md` (enduring doctrine, keep ≤ 200 lines), `.claude/rules/*.md` (path-scoped), `.claude/skills/` (reusable workflows), `.mcp.json` (team-approved shared MCP servers).
3. **Execute third** — Claude Code (CLI / VS Code extension) is the preferred repo-local execution engine. It must follow repo doctrine; it does not invent platform choices ad hoc.

**Repo doctrine layering:**

| Layer | Purpose | Status |
|---|---|---|
| `CLAUDE.md` | Enduring repo doctrine (always loaded) | Committed |
| `.claude/rules/*.md` | Path-scoped rules, loaded on demand | Committed |
| `.claude/skills/` | Reusable workflows | Committed |
| `.mcp.json` | Team-approved shared MCP servers | Committed (no secrets) |
| `CLAUDE.local.md` | Personal/local overrides | Gitignored |
| Auto memory (`~/.claude/projects/<repo>/memory/`) | Learned operational notes | Machine-local, NOT canonical architecture |
| Branch protection / CI / tool permissions | Real hard enforcement | — |

`CLAUDE.md` and `.claude/rules/` shape behavior but do not hard-block; enforcement lives in CI gates, branch protection, and tool permissions.

**Verification contract:** Every meaningful task ends with at least one of — Odoo test run, Playwright smoke, schema/policy validation, CI workflow result, rendered artifact diff, runtime health check. Self-verification is mandatory; generation alone is not "done".

**Execution loop (Anthropic best practice):** `Explore → Plan → Implement → Verify → Commit/PR`. Use Plan Mode for non-trivial changes.

**Agent teams (experimental):** Default = single session. Subagents for focused delegation. Agent teams (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) only for parallel execution/review with separable file or plane ownership — never for architecture/SSOT drafting or tightly coupled refactors. 3–5 teammates, ~5–6 tasks each.

---

## Core Operating Paradigm (2026-04 refresh)

### Upstream-first adoption

Assume Microsoft has already shipped the baseline before proposing custom work.

Order of operations:
1. Verify whether Microsoft already provides the capability.
2. Classify the upstream artifact (baseline / pattern / primitive / skip — per Rule 25).
3. Adopt and adapt the smallest valid baseline.
4. Build only the thin IPAI delta.

Never default to:
- greenfield architecture
- hand-rolled scaffolding
- custom runtimes
- dismissing a Microsoft repo without inspecting its actual code and deployment shape

### Discussion is not delivery

Architecture discussion, doctrine refinement, registry indexing, repo creation, plugin installs, memory entries, and Azure resource provisioning are **NOT** treated as execution.

A workstream is "working" only when ALL of the following exist as evidence:
- real input arrives
- live orchestration runs (not stub)
- real tool calls fire (not mock)
- concrete output artifact produced
- evaluation result recorded
- persisted trace/audit event emitted

Anything short of end-to-end execution is sense-making, not delivery. Sense-making is necessary but never sufficient.

### Product strategy

IPAI is **not primarily a custom software shop** in this lane.

IPAI **packages, configures, and sells** deployable Microsoft baselines plus thin domain overlays.

Default commercial posture (in order):
- adopt — fork or install the canonical Microsoft baseline
- configure — overlay tenant + brand + region settings
- package — wrap as customer-readable 3-slide spec (per Rule 26)
- prove — run end-to-end against a real scenario with eval evidence
- sell — list on AppSource (per Rule 26 Aug-Sep 2026 target)

The commercial unit is the packaged adoption offer, not the custom build.

---

## Quick Reference

| Item | Value |
|------|-------|
| **Stack** | Odoo CE 18.0 + OCA + n8n + Slack + PostgreSQL 16 |
| **Domain** | `insightpulseai.com` (`.net` is deprecated) |
| **DNS** | Azure DNS (authoritative, delegated from Squarespace) |
| **Mail** | Zoho SMTP (`smtp.zoho.com:587`, domain: `insightpulseai.com`) |
| **Hosting** | Azure Container Apps (behind Azure Front Door) |
| **Node** | >= 18.0.0 (pnpm workspaces, Turborepo) |
| **Python** | 3.10+ (Odoo 18) |
| **Web/CMS** | Azure Container Apps (public + internal), Odoo website |
| **EE Parity** | Target >=80% via `CE + OCA + ipai_*` (current: ~35-45%, audited 2026-03-08) |
| **Repo** | `Insightpulseai/odoo` (renamed from `odoo-ce`) |

---

## Secrets Policy

Never hardcode, never echo, never ask user to paste. Secrets in `.env*` / env vars / Azure Key Vault only.
See `.claude/rules/security-baseline.md` for full policy (sections 2.1-2.6).

---

## Repo Map

| Path | Owns |
|------|------|
| `addons/ipai/` | 69 custom IPAI modules |
| `addons/oca/` | OCA community modules (hydrated at runtime, not tracked) |
| `apps/` | 9 applications (ops-console, mcp-jobs, slack-agent, etc.) |
| `packages/` | Shared packages (agents, taskbus) |
| `spec/` | 76 spec bundles |
| `scripts/` | 1000 automation scripts in 86 categories |
| `odoo18/` | Canonical Odoo 18 setup (config, scripts, backups) |
| `mcp/servers/` | MCP server implementations (plane is the only live one) |
| `.github/workflows/` | 355 CI/CD pipelines |
| `docker/`, `deploy/` | Docker configs and deployment |
| `platform/` | Canonical platform control-plane (replaces `ops-platform`) |
| `data-intelligence/`| Canonical lakehouse/Databricks code (replaces `lakehouse`) |
| `agents/` | Canonical agent/skill assets (personas, judges, skills) |
| `agent-platform/` | Canonical agent runtime/orchestration engine |
| `infra/` | Shared infrastructure and edge configuration |
| `design/` | Shared design tokens and assets (replaces `design-system`) |
| `ssot/` | Intended-state truth for platform and ERP runtime |

---

## Cross-Repo Invariants

- **Microsoft 365 Agents SDK** is a channel layer for enterprise delivery (Copilot, Teams, Web). It does NOT replace the canonical `agent-platform` runtime.
- **Service-to-service auth**: All internal flows must use Managed Identities + Azure Key Vault.

1. **Secrets**: `.env` files only, never hardcode. Azure Key Vault for runtime.
2. **Database**: Odoo uses PostgreSQL (local or Azure managed). All Azure-native.
3. **No Supabase**: Supabase is fully deprecated (2026-03-26). All services are Azure-native.
4. **CE Only**: No Enterprise modules, no odoo.com IAP dependencies.
5. **OCA First**: Prefer OCA modules over custom `ipai_*` when available. Config -> OCA -> Delta.
6. **Specs Required**: Significant changes must reference a spec bundle.
9. **Databricks Governance**: Databricks + Unity Catalog is the mandatory governed transformation, engineering, and serving plane.
10. **MCP First**: MCP is required for all reusable agent tools (Google Cloud contract).
10a. **Three-protocol model + supervisor-mediated orchestration**: Every Pulser agent publishes an Agent Card at `/.well-known/agent-card.json`. Three industry-standard protocols, orthogonal and all mandatory:
   - **A2A** (Linux Foundation, `a2a-protocol.org`) = agent ↔ agent interop (incl. client ↔ agent entry point into the orchestrator)
   - **MCP** (Anthropic-originated standard) = agent ↔ tool (incl. retrieval, DB, APIs)
   - **Agent365 SDK** (Microsoft) = agent ↔ M365 user surface (Copilot Chat, Teams, Outlook discovery/invocation/auth). Non-M365 surfaces (ADO extension, Odoo chatter, Slack, Claude Code) skip Agent365 and speak A2A directly to the orchestrator.

   **Orchestration pattern — supervisor-mediated only.** Workers never invoke workers directly. `agents/` owns definitions (runtime-free): personas, skills, judges, evals, prompt contracts, registries. `agent-platform/` owns runtime: supervisor, router, dispatcher, retries, approvals, workflow state, judge loops, envelopes, handoffs. Canonical flow: `client → intake → planner/router → specialist workers (parallel ok) → judge → synthesizer → persist trace → response`. No free-form agent-to-agent chat. SSOT: `docs/architecture/agent-orchestration-model.md`, `docs/architecture/three-protocol-model.md`, `ssot/governance/agent-interop-matrix.yaml`, `agent-platform/contracts/envelopes/`.

   **Runtime substrate — Microsoft Agent Framework (MAF).** `agent-platform/` runtime is built on `microsoft/agent-framework` (Python-first, src-layout package `agent_platform`; .NET allowed only for existing .NET surfaces). MAF imports are permitted ONLY under `agent-platform/src/agent_platform/` — never in `agents/`, `odoo/`, `addons/`, `platform/`, `infra/`, `data-intelligence/`, `web/`, or `apps/`. Canonical shape: `src/agent_platform/runtime/` (engine, registry, graph_builder, checkpointing, middleware) + `src/agent_platform/orchestration/` (router, planner, supervisor, handoffs, human_in_loop) + `src/agent_platform/providers/foundry/` (DEFAULT provider) + `src/agent_platform/tools/{odoo,databricks,docintel,storage,communications}/` (typed adapters, not prompt blobs) + `src/agent_platform/{retrieval,evals,observability,security,sessions,attachments,workers,api}/`. Foundry is the default model/provider lane. The `microsoft-foundry` org is reference material only — do not mirror its repo layout. SSOT: `ssot/agent-platform/agent_framework_adoption.yaml`. Placement contract: `docs/architecture/agent-framework-adoption.md`.

   **Two operating modes (locked).** Team mode = Codespaces/local dev → agent-platform on ACA → Foundry cloud (`ipai-copilot-resource`, gpt-4.1). Solo mode = local Mac → agent-platform in devcontainer → Foundry Local (phi-4/qwen, on-device NPU/GPU). Forbidden: Foundry Local inside Codespaces (wrong runtime pairing). Agent Card is identical across modes; backing model swaps via env var. Pattern reference: Claude Code itself (local CLI, remote Anthropic brain, MCP for tools).
11. **SaaS Authority**: The **Azure SaaS Workload Documentation** is the canonical design framework for the platform.
12. **Consumption**: **Power BI** is the primary mandatory business-facing reporting surface.
13. **Fabric Complement**: Fabric is for mirroring and OneLake integration; it never replaces Databricks engineering.
14. **Stateless Agents**: Session state must be stored externally (Stateless Application rule).
15. **Sequential Default**: Use Sequential orchestration for deterministic finance flows; Maker-Checker for gates.
16. **Release Gate**: All production releases must pass the [Feature Ship-Readiness Checklist](docs/release/FEATURE_SHIP_READINESS_CHECKLIST.md) (5 gates: Product, Correctness, Runtime, Safety, Evidence). SSOT: `ssot/release/feature-ship-readiness-gates.yaml`.
17. **SAP Adapter Only**: SAP is an integrated external enterprise surface. Use Azure Functions or App Service with SAP Cloud SDK for adapter services. Do not adopt SAP infrastructure hosting templates (NetWeaver, HANA, LaMa, S/4HANA) as canonical platform architecture unless SAP runtime hosting is explicitly in scope.
18. **iOS Wrapper Skill Pack**: When working on the iOS native wrapper (`web/mobile/`), apply `docs/skills/ios-native-wrapper.md`. Prefer native auth (`AuthenticationServices`), native biometrics (`LocalAuthentication`), allowlist-based webview navigation, automated simulator smoke tests, and CI + `fastlane` release automation. No cross-platform frameworks.
19. **Apple Design Authority (iOS)**: For iOS wrapper UI, treat Apple's current App design and UI / Liquid Glass guidance as the visual system authority. Native shell chrome follows current Apple design language. `Icon Composer` for app icons, `SF Symbols` for native shell iconography. Liquid Glass applies to native shell surfaces, not arbitrary overlays on hosted web content.
20. **iOS Wrapper UI Contract**: For wrapper-shell changes (`WrapperViewController`, `BiometricAuth`, native chrome, auth handoff, icon assets), apply `docs/skills/ios-wrapper-ui-contract.md`. This contract is subordinate to `docs/skills/ios-native-wrapper.md` and defines enforceable code-review gates.
21. **iOS Wrapper Code Contract**: When editing wrapper-shell implementation files, also apply `docs/skills/ios-wrapper-code-contract.md`. File-level review emphasis: `WrapperViewController.swift` owns shell orchestration only, `BiometricAuth.swift` owns biometric policy/orchestration only, `Assets.xcassets` stays minimal and governed, `Environment.swift` remains the source of routing/environment configuration, `Info.plist` remains aligned with native auth/biometric requirements.
22. **Odoo Integration Adoption**: Check Odoo 18 native integrations first (payments, bank sync, EDI, commerce connectors, website). If native is insufficient, check OCA before creating `ipai_*`. Reserve `ipai_*` for thin bridges to external Azure/Foundry services only. SSOT: `ssot/odoo/integration_adoption.yaml`.
23. **Engineering Execution Doctrine**: Reuse upstream for commodity capability; configure for compositional concerns; build only the thinnest `ipai_*` layer for business-specific deltas. Design first (`docs/architecture/`, `ssot/`, `spec/`) → codify second (`CLAUDE.md`, `.claude/rules/`, `.claude/skills/`, `.mcp.json`) → execute third (Claude Code follows doctrine, never invents platform choices). Auto memory is learned ops notes, not canonical architecture. See "Engineering Execution Doctrine" section above.

24. **Adopt Reflex (paradigm)**: Before authoring any artifact (code, skill, agent, accelerator, eval, MCP server), search the Microsoft canonical catalog AND the IPAI registry first. Default to "find it" over "build it." Dismissal of any Microsoft surface as "not strategic" or "reference only" must be backed by deep inspection (read the code, run the sample) — surface-level dismissal is forbidden because it has been wrong repeatedly. The proof bar for `ipai_*` custom code is high: must demonstrate that no Microsoft / canonical upstream solves the need with configuration. SSOT: `ssot/microsoft-artifact-registry/` (when landed). Memory pointer: `feedback_adopt_dont_build.md`.

25. **Microsoft Adoption Registry — canonical surface IPAI uses**: This is the locked surface; everything else is OUT until a registry entry justifies it.

    **Layer 0 — Platform bootstrap**:
    - `Azure/ALZ-Bicep` (Enterprise-Scale ALZ — mgmt groups, identity, network, policy, monitoring)
    - `Azure/Azure-Verified-Modules` (peer-reviewed Bicep + Terraform modules)

    **Layer 1 — Workload accelerators (Microsoft-canonical, fork-and-configure)**:
    - `microsoft/unified-data-foundation-with-fabric-solution-accelerator` → `data-intelligence/` baseline
    - `microsoft/agentic-applications-for-unified-data-foundation-solution-accelerator` → `agent-platform/` baseline
    - `microsoft/Multi-Agent-Custom-Automation-Engine-Solution-Accelerator` (MACAE) → borrow supervisor pattern
    - `microsoft/Prior-Authorization-Multi-Agent-Solution-Accelerator` → borrow approval-gate pattern
    - `microsoft/content-processing-solution-accelerator` → adopt for BIR/invoice doc extraction

    **Layer 2 — Frameworks + tools (adopt as deps)**:
    - `microsoft/agent-framework` (MAF) — runtime substrate (per Rule 10a)
    - `microsoft/azure-skills` plugin — operator workflow skills (24 skills, installed)
    - `microsoft/markitdown` — corpus ingestion (PDF/DOCX/XLSX → Markdown)
    - `microsoft/Foundry-Local` — solo-mode runtime
    - `microsoft/playwright-mcp` — browser automation MCP (in `.mcp.json`)
    - `azure-ai-foundry/mcp-foundry` — Foundry MCP (in `.mcp.json`)
    - **Azure SDK family** (canonical reference: `azure.github.io/azure-sdk/releases`) — Python SDKs for IPAI: `azure-ai-projects`, `azure-ai-agents-persistent`, `azure-ai-inference`, `azure-ai-openai`, `azure-search-documents`, `azure-ai-documentintelligence`, `azure-ai-contentsafety`, `azure-ai-contentunderstanding`, `azure-identity`, `azure-keyvault-{secrets,keys,certificates}`, `azure-storage-blob`, `azure-cosmos`, `azure-servicebus`, `azure-eventgrid`, `azure-monitor-{query-logs,query-metrics,ingestion,opentelemetry}`. Never hand-roll HTTP clients for any Azure service — adopt the canonical SDK.

    **Layer 3 — Code reference library (clone, adapt notebooks)**:
    - `microsoft/ai-agents-for-beginners` (17 lessons, 99.7% Python notebooks on MAF + Foundry V2): primary lessons to adapt = 14 (MAF orchestration: handoff/human-loop/middleware/conditional/concurrent/sequential), 11 (MCP+A2A+NLWeb protocols), 5 (Agentic RAG with Foundry V2), 6 (trustworthy agents), 8 (multi-agent), 13 (memory). Sparse-checkout to skip 50+ language translations. NOT for runtime install — for direct code adaptation into `agent-platform/`.

    **Layer 4 — Microsoft Agent 365 + Foundry IQ (productized M365 lane, GA via Frontier)**:
    - **Microsoft Entra Agent ID** — productized agent identity (Zero Trust, least privilege)
    - **Agent 365 SDK** — any-agent-stack interop with M365 + Notifications + tools
    - **Agent 365 MCP servers** (7) — Outlook Mail, Outlook Calendar, Teams, Copilot Search, SharePoint+OneDrive, User Profile, Dataverse (GA)
    - **Foundry IQ** — agent-callable knowledge layer on Azure AI Search agentic retrieval (Entra ACL + Purview label aware)
    - **AI in SharePoint** — human-facing knowledge surface (replaces wiki concept; Viva Topics retired)
    - **Microsoft Purview Unified Catalog** — governance plane (sensitivity labels, AI compliance)
    - **Evals for Agent Interop** (`aka.ms/EvalsForAgentInterop`, Jan 2026) — eval harness with scenario format + judges + leaderboard

    **Layer 4.5 — Runtime Governance (Microsoft Agent Governance Toolkit / AGT)**:
    - **`microsoft/agent-governance-toolkit`** (v3.1.0, Microsoft-signed Public Preview, MIT, 9,500+ tests, all 10 OWASP Agentic Top 10 risks covered, sub-millisecond deterministic policy enforcement). NATIVE MAF middleware; sits between MAF runtime and tool execution. Replaces ALL custom-built policy / approval / audit / kill-switch / sandboxing / SRE infrastructure. Components — Policy Engine (YAML/OPA/Cedar, deterministic, < 0.1ms), Zero-Trust Identity (Ed25519 + ML-DSA-65 quantum-safe, trust scoring 0-1000, SPIFFE/SVID), Execution Sandboxing (4-tier privilege rings, saga orchestration, kill switch), Agent SRE (SLOs, error budgets, replay debugging, chaos engineering, circuit breakers), MCP Security Scanner (tool poisoning + typosquatting + hidden instruction detection on `.mcp.json` declared servers), Shadow AI Discovery, Agent Lifecycle (provisioning → rotation → orphan detection → decommissioning), Governance Dashboard, PromptDefense Evaluator (12-vector prompt injection audit), Unified `agt` CLI. Key marketplace differentiator: 0.00% policy violation rate (deterministic) vs 26.67% for prompt-based safety (red-team verified). Compliance: NIST AI RMF + EU AI Act + Colorado AI Act + SOC 2.

    **Skip list (verified — do not adopt for new IPAI work)**:
    - `microsoft/semantic-kernel` — superseded by MAF (Microsoft's official position; SK is predecessor)
    - `microsoft/autogen` — superseded by MAF (also a predecessor)
    - `microsoft/CDM` repo — 16 months stale; Microsoft data-modeling investment moved to Fabric semantic models. CDM FinancialServices schema is reference vocabulary only.
    - OData libraries (`Microsoft.AspNetCore.OData`) — adjacent, not core; learn 5 query parameters for Microsoft Graph only
    - Glean — closed model + cost-prohibitive; use Foundry IQ instead
    - SAP Signavio — different paradigm (BPM-first vs LLM-first); cannot swap from MAF stack

26. **Pulser product packaging (GTM)**: Pulser is positioned as a packaged ISV offering on Microsoft AppSource / Azure Marketplace (target Aug-Sep 2026 per ISV Success engagement). Every Pulser specialist MUST ship with a customer-readable 3-slide spec following the Microsoft AI Agent for Finance template format: (Slide 1) Overview card with From → To, Current Workflow Challenges, Key Features, Business Impact, Key Users; (Slide 2) 6-step workflow with AI Agent connections + Benefits + KPIs impacted + Value benefit; (Slide 3) Reference architecture with Key Considerations, Inputs needed, Agent-to-Agent Workflow, Architecture diagram. Each spec doubles as: customer pitch + internal contract + eval scenario seed + architecture review. SSOT for spec template: `docs/agent-specs/template.md` (when landed). Customer audience vocabulary varies: "AI operating copilot" (Microsoft co-sell), "process automation agent" (CFO buyers), "specialized LLM agent" (technical buyers) — same artifact, three vocabularies.

27. **Agent product pattern (4-phase + 6-section)**: All Pulser specialists implement the same convergent industry pattern (Microsoft Finance template + Anthropic investment-memo use case + scenario-based eval methodology):

    **4-phase workflow per specialist**:
    1. RETRIEVE — pull from N sources via MCP connectors (Foundry IQ KB + Odoo bridge + Agent 365 MCPs)
    2. ANALYZE — named calculations + comparisons + risk flags (declarative in YAML)
    3. GENERATE — formatted deliverable matching the 6-section template
    4. REFINE — citations + drill-downs + alternative formats (PowerPoint, SharePoint page, Word)

    **6-section deliverable template (every Pulser output)**:
    1. EXECUTIVE SUMMARY — recommendation/decision/status
    2. CONTEXT / SCOPE — what was reviewed/processed
    3. PRIMARY ANALYSIS — calculations / reconciliations
    4. COMPARATIVE / TREND — vs budget / vs prior period / vs benchmark
    5. CONFIDENCE / METHOD — data sources, assumptions, calculation walk
    6. RISKS / OPEN ITEMS — what needs human review or follow-up

    Each specialist's spec is one YAML file (~80 lines) — declarative, no engine code. Microsoft Agent 365 + MAF + Foundry IQ + Evals for Agent Interop run the spec.

28. **Two-layer corpus model**: All Pulser knowledge retrieval is two-layered:
    - **Layer 1 — Microsoft authority**: Microsoft Learn docs + Sample Browser (~4,545 samples) — accessed via `microsoft-learn` MCP server (already in `.mcp.json`). ZERO local indexing; Microsoft maintains.
    - **Layer 2 — IPAI authority**: doctrine + ssot + research + BIR forms + tenant configs + Pulser persona — indexed in Foundry IQ KB (per-tenant). Ingested via markitdown → Blob → Azure AI Search indexer.
    Both queryable by Pulser. Both governed via Purview labels. Neither requires custom code in the engine.

29. **Builder / Operator / Judge triad (human-equivalent role model)**: Every Microsoft artifact AND every Pulser specialist is classified across three roles — the stable human responsibility model sitting on top of the technical stack. Not "what layer is this?" but "who behaves like the builder, the operator, the judge for this artifact?" This triad is the registry schema's `human_equivalent` field; it also maps to the supervisor-mediated orchestration pattern (Rule 10a — planner=builder, specialist=operator, judge=judge).

    **Build — who implements it?** (Microsoft cert lane: technical implementation)
    - `AZ-204` Azure Developer Associate
    - `AI-102` Azure AI Engineer Associate
    - `DP-700` Fabric Data Engineer Associate
    - `GH-200` GitHub Actions
    - `GH-300` GitHub Copilot
    - IPAI hire profile: implementer / integration engineer / toolsmith / runtime builder

    **Operate — who runs it in business context?** (Microsoft cert lane: AI business solutions)
    - `AB-730` AI Business Professional
    - `AB-731` AI Transformation Leader
    - `AB-900` Microsoft 365 Copilot and Agent Administration Fundamentals
    - IPAI hire profile: business operator / domain specialist / workflow owner / agent supervisor

    **Judge — who approves / governs?** (Microsoft cert lane: architect + security + governance)
    - `AZ-305` Azure Solutions Architect Expert
    - `SC-100` Cybersecurity Architect Expert
    - `SC-200` Security Operations Analyst Associate
    - `SC-300` Identity and Access Administrator Associate
    - `AZ-500` Azure Security Engineer Associate
    - `PL-600` Power Platform Solution Architect Expert
    - `AB-100` Agentic AI Business Solutions Architect
    - IPAI hire profile: architecture judge / security judge / governance judge / approval authority

    **Application to registry entries**: every artifact in `ssot/microsoft-artifact-registry/` (per Rule 25) gets a `human_equivalent` field with `builder_roles`, `operator_roles`, `judge_roles` arrays.

    **Application to Pulser specialists**: every specialist's 3-slide spec (per Rule 26) declares Build/Operate/Judge owners — Build = `agent-platform/` engineer wiring it, Operate = the customer's domain user, Judge = the customer's architect/compliance authority + an LLM judge agent.

    **Application to Jake's certification roadmap (matches the triad):**
    - Build lane: AI-102 (mid-2026)
    - Judge lane: SC-300 (2026 Q3) → AZ-305 (2026 Q4)
    - Operate lane: AB-731 (when hiring expands) — see `user_deakin_sig787.md` for math foundation pre-req

30. **Runtime Governance via AGT (mandatory for all Pulser specialists)**: `agent-platform/` MUST integrate `microsoft/agent-governance-toolkit` (AGT) as native MAF middleware. AGT sits between MAF runtime and tool execution; every tool call, resource access, and inter-agent message is evaluated against deterministic policy before execution (sub-millisecond, < 0.1ms p50). NEVER custom-build policy engine, audit logger, kill switch, sandboxing, MCP security scanner, shadow AI discovery, agent lifecycle manager, SRE for agents, or compliance dashboards — AGT covers all. Policies authored in YAML/OPA/Cedar live in `ssot/governance/agt-policies/<scope>/<policy-name>.yaml` (per tenant + per specialist + per band). Required AGT components for Pulser production: Policy Engine, Zero-Trust Identity (complements Entra Agent ID), Execution Sandboxing (4-tier privilege rings + kill switch), Agent SRE (SLOs + circuit breakers), MCP Security Scanner (validates `.mcp.json` declared servers), PromptDefense Evaluator (12-vector audit for ISV compliance evidence), Governance Dashboard (operator + customer visibility). Marketplace differentiator: AGT enforcement is deterministic (0.00% policy violation rate) vs prompt-based safety (26.67% violation rate per Microsoft red-team). This is the productized realization of CLAUDE.md "policy-gated agent" canonical classification — Pulser specialists carry AGT enforcement as a runtime promise, not a marketing claim. Compliance evidence pack auto-generated for NIST AI RMF + EU AI Act + Colorado AI Act + SOC 2 — required artifacts for AppSource listing (Rule 26 Aug-Sep 2026 target). CLI: `agt verify` runs in CI per pull request; `agt verify --evidence ./agt-evidence.json --strict` is the deployment gate. SSOT pointer: `ssot/governance/agt-adoption.yaml` (when landed). Memory pointer: `project_agt_runtime_governance.md`.

31. **Owned-repo taxonomy — 5 post-development lanes, 11 repos in `Insightpulse-ai`**: Codified 2026-04-20 (revised the same day from a too-coarse 3-repo audience model). The org is shaped by **post-development lifecycle stage**, not by coding discipline or audience. The enterprise (`ipai`) is the governance shell (policies, billing, security defaults, organization inventory); the org (`Insightpulse-ai`) is the operating portfolio for what you **package, prove, publish, and operate**.

    **Lifecycle → repo mapping (the canonical shape)**:

    ```
    discover/adopt        → accelerators-catalog
    compose/build         → agent-platform · data-intelligence · web
    package               → marketplace-publishing
    deploy/operate        → platform · infra
    govern/standardize    → .github · docs · templates · design
    ```

    **The 11 owned repos (5 lanes)**:

    | Lane | Repo | Purpose |
    |---|---|---|
    | **A. Governance / shared standards** | `.github` | Org-level CODEOWNERS, dependabot, issue/PR templates, org profile |
    | A | `docs` | Architecture records, publishing checklists, package blueprints, public/private package docs, onboarding, proofs, GTM/demo narratives |
    | A | `templates` | Repo standards, scaffold templates (new specialist, new accelerator adoption, new bundle) |
    | **B. Platform / publishing / commercialization** | `platform` | Platform contracts, environment definitions, deployment governance, control-plane shell. **NOT** a UI shell. |
    | B | `marketplace-publishing` | AppSource/Azure-Marketplace + Databricks Marketplace offer packaging, transactable mechanics, fulfillment/metering, listing assets, `Azure/Commercial-Marketplace-SaaS-Accelerator` adoption |
    | B | `infra` | Landing zones (ALZ adoption), shared infra baselines, networking, identity, AVM module composition |
    | **C. Product / app surfaces** | `web` | User-facing apps + product UX shells (current Fluent UI v9 work belongs HERE, not in `platform`) |
    | C | `agent-platform` | Pulser agent runtime; MAF wiring, supervisor/router, specialist YAML specs (Rule 27), AGT middleware (Rule 30), evals, MCP/tool adapters |
    | C | `data-intelligence` | Databricks bundles, Unity Catalog schemas, DLT pipelines, BIR/regulatory data products, Power BI semantic layer |
    | C | `pulser-odoo` (OR `odoo`) | Odoo runtime composition (per the Odoo boundary rule below) — packaged commercial product surface |
    | **D. Design system** | `design` | Fluent UI v9 adoption guidance, design tokens, shared components, shell patterns, page templates, brand-safe primitives |
    | **E. Adoption / accelerator intake** | `accelerators-catalog` | Microsoft + Databricks + Azure accelerator index; classification (baseline / pattern / primitive / skip per Rule 25); adoption decisions; extracted patterns; modernization notes; one-time discovery memory (avoid re-discovering) |

    **Optional later** (only when real demand exists): `automations`, `agents` (definitions split from runtime), `customer-packages`, `demos`, `patterns-lab`, `upstream-intake`. **Never one repo per accelerator** — those become junk immediately.

    **Ownership boundary (one-sentence rule, unchanged)**: **Upstream = capability. Yours = composition + thin delta + package.** Never re-author, mirror, or fork what upstream already maintains.

    **Upstream — NOT yours** (reference, pin, evaluate, adapt around):
    - `odoo/odoo` (core ERP — base apps + l10n_ph + huge addon surface; Odoo SA maintains)
    - All OCA repos (community modules; OCA maintains)
    - `microsoft/fluentui` (design upstream → influences `design`/`web`, never fork unless contributing back)
    - `microsoft/agent-framework` (MAF), `microsoft/agent-governance-toolkit` (AGT), `microsoft/azure-skills`, `microsoft/markitdown`, `microsoft/Foundry-Local`, `microsoft/playwright-mcp`, `azure-ai-foundry/mcp-foundry`
    - All Microsoft solution accelerators (UDF + agentic-UDF + MACAE + Prior-Auth + content-processing + Deploy-Your-AI-App-In-Production)
    - `Azure/ALZ-Bicep`, `Azure/Azure-Verified-Modules`, `Azure/Commercial-Marketplace-SaaS-Accelerator` (pattern donor for `marketplace-publishing`)
    - `databricks-industry-solutions`, `databrickslabs/fsi-solution-accelerators` (extract patterns into `data-intelligence` and `accelerators-catalog`; never fork the whole org)
    - `microsoft/ai-agents-for-beginners` (clone + adapt notebooks, do not mirror)

    **Odoo-lane boundary (one repo, NOT a fork of `odoo/odoo` or OCA)**: The Odoo repo (whether named `odoo` or `pulser-odoo`) owns ONLY (1) version pin + module selection + dependency ordering + lock files; (2) `addons/ipai/` thin bridge layer (Odoo↔MCP, Odoo↔Pulser, BIR/PH overlays); (3) runtime config + Docker/compose + scripts + migration notes + tests + deployment contract; (4) SSOT addon inventory + upstream pins + composition policy. Internal layout: `addons/oca/` (upstream-selected modules, hydrated/pinned at runtime — not re-authored), `addons/ipai/` (thin bridge/domain modules), `addons/local/` (only if truly needed). Choose `pulser-odoo` if positioning as packaged commercial product; choose `odoo` if positioning as ERP runtime composition.

    **Forking policy**: Do NOT fork by default. Fork only if (a) you must carry a temporary patch awaiting upstream merge, or (b) you intend to contribute back upstream. Otherwise keep upstream external and put your delta in your own repo. **Never one repo per accelerator** — adoption intelligence lives in `accelerators-catalog`, not as 50+ mirror repos.

    **What NOT to do**:
    - Don't organize by **vendor** (no `microsoft-repos`, `azure-repos`, `databricks-repos`)
    - Don't organize by **job title** (no `dev`, `design`, `ops`, `data` as repo names)
    - Don't make **one repo per accelerator** (junk on day one)
    - Don't mix **upstream mirrors with product truth** (the org contains adopted truth + packaging + thin delta, not bulk copies)

    **Application to current state (2026-04-20)**: Legacy `Insightpulseai` org has 17 repos (16 active + 1 archived). Migration mapping to the 11-repo `Insightpulse-ai` shape:

    | Source (`Insightpulseai/`) | Target (`Insightpulse-ai/`) | Lane | Action |
    |---|---|---|---|
    | `odoo` | `pulser-odoo` (or `odoo`) | C | rename + migrate |
    | `agent-platform` | `agent-platform` | C | migrate as-is |
    | `data-intelligence` | `data-intelligence` | C | migrate as-is |
    | `web` | `web` | C | migrate as-is |
    | `agents` | `agent-platform/agents/` | C | fold via `git subtree add` |
    | `infra` | `infra` | B | migrate as-is |
    | `automations` | `agent-platform/automations/` (until volume justifies own repo) | C | fold |
    | `powerbi-skills` | `data-intelligence/skills/powerbi/` | C | fold |
    | `ugc-mediaops-kit` | `agent-platform/skills/mediaops/` OR archive | C | fold or archive |
    | `design` | `design` | D | migrate as-is |
    | `templates` | `templates` | A | migrate as-is |
    | `docs` | `docs` | A | migrate as-is |
    | `landing.io` (archived) | absorbed into `docs/landing/` | A | drop from migration scope |
    | `.github` | `.github` | A | migrate as-is |
    | `dotfiles` | personal `tbwa/dotfiles` | — | move to personal account |
    | `demo-repository` (both orgs) | archive | — | archive, don't migrate |
    | `Insightpulseai/platform` (current legacy) | `platform` | B | migrate; **purge any UI/Fluent content** — that lives in `web`/`design` |

    **Repos to create from scratch in `Insightpulse-ai`** (no legacy source): `marketplace-publishing` (B), `accelerators-catalog` (E).

    **Current `Insightpulse-ai/ipai-platform` repo** (Vite + Fluent UI v9 scratch from 2026-04-19): misnamed for the lane model. Decision required — either (a) rename to `web` (or `ops-console`) and migrate; (b) repurpose into the real `platform` control-plane shell quickly; or (c) delete and start `web` clean.

    **Migration path**: consolidate-then-migrate via `git subtree add` (preserves history) before `gh gei migrate-repo`. SSOT pointer: `ssot/governance/owned-repos.yaml` (when landed).

    **Connected memory entries**: `feedback_adopt_dont_build.md`, `project_microsoft_adoption_registry_2026-04-19.md` (Rule 25 — what's upstream; the `accelerators-catalog` repo is the productized realization of Rule 25).

---

## Execution Gate

Before proposing custom code, every contributor (human or agent) MUST satisfy:

1. **Search for Microsoft upstream first.** Use `microsoft-learn` MCP (already in `.mcp.json`), `microsoft_code_sample_search`, `gh search repos --owner microsoft --owner Azure --owner Azure-Samples --owner azure-ai-foundry`, and `microsoft/azure-skills` plugin. The default assumption is "Microsoft has shipped this."

2. **Inspect actual repo structure, code samples, and deployability.** Surface-level dismissal is forbidden (per Rule 24). Read the README, list the `samples/` and `code-samples/` directories, check `last push` date, verify license, run `claude plugin list` if it's an installable plugin.

3. **Prefer clone-and-adapt over scaffold-and-design.** If a Microsoft notebook/sample/accelerator covers the pattern, fork+adapt is the path — never write from scratch.

4. **Prefer one live proof over additional doctrine text.** If you have a working architecture document but no end-to-end run, the doctrine is incomplete. The next correct action is execution, not more doctrine.

A workstream is **NOT "done"** because:
- repos were created
- docs were written
- memories were saved
- plugins were installed
- Azure resources were provisioned
- ADRs landed
- registry entries authored

A workstream is **only "working"** when an end-to-end path executes against real input and produces evidence (output artifact + eval result + persisted trace).

This gate applies to every PR, every session, every adoption decision. It is the operational complement to Rule 24 (Adopt Reflex) and the Core Operating Paradigm above.

---

## Common Workflows

### Agent Pattern

```
explore -> plan -> implement -> verify -> commit
```

| Command | Purpose |
|---------|---------|
| `/project:plan` | Create detailed implementation plan |
| `/project:implement` | Execute plan with minimal changes |
| `/project:verify` | Run all verification checks |
| `/project:ship` | Orchestrate full workflow end-to-end |
| `/project:fix-github-issue` | Fix a specific GitHub issue |

### Verification (run before every commit)

```bash
./scripts/repo_health.sh       # Check repo structure
./scripts/spec_validate.sh     # Validate spec bundles
./scripts/ci_local.sh          # Run local CI checks
```

### Agent Rules

1. **Never guess**: Read files first, then change them
2. **Simplicity first**: Prefer the simplest implementation
3. **Verify always**: Include verification after any mutation
4. **Minimal diffs**: Keep changes small and reviewable
5. **Update together**: Docs and tests change with code

### Common Commands

```bash
docker compose up -d                    # Start full stack
./scripts/deploy-odoo-modules.sh        # Deploy IPAI modules
./scripts/ci/run_odoo_tests.sh          # Run Odoo unit tests
pnpm install                            # Install Node dependencies
```

---

## Odoo extension and customization doctrine

When implementing new capability in Odoo, follow this decision order:

1. **Odoo CE 18 native capability first**
   - Prefer standard CE behavior before adding modules or code.

2. **Odoo property fields second, when the requirement is parent-scoped metadata**
   - Use property fields when the need is lightweight, configurable, form-level metadata tied to a parent record (e.g., project-specific task attributes, team-specific CRM qualifiers, category-scoped product enrichment).
   - Property fields are pseudo-fields, not stored as normal database columns, scoped by a parent record.
   - **NOT appropriate for:** core accounting logic, strong relational domain models, cross-parent canonical master data, heavy reporting, integration contracts, workflow-critical fields, fields needing robust server logic or DB-level consistency.

3. **OCA 18 same-domain modules third**
   - Search the primary OCA repository for the functional domain before writing custom code.

4. **Adjacent OCA 18 modules fourth**
   - Check neighboring OCA domains before concluding there is a gap.
   - Example: project need → also inspect `timesheet`, `project-reporting`, `knowledge`, `account-analytic`, `connector-*`, `l10n-*`.
   - Compose CE + property fields + OCA modules where possible.

5. **Custom `ipai_*` modules last**
   - Custom modules are a last-resort extension path only.
   - `ipai_*` must stay thin and bridge-oriented: integration bridges, orchestration glue, AI/copilot overlays, adapters, narrow opinionated extensions.
   - **Do not create `ipai_*` modules to duplicate viable CE/OCA parity.**

### Mandatory requirements for any approved custom `ipai_*` module

Every custom module is incomplete unless it includes:

- `README.md`
- `docs/MODULE_INTROSPECTION.md`
- `docs/TECHNICAL_GUIDE.md`

Required minimum structure:

```
addons/ipai/<module_name>/
  README.md
  docs/
    MODULE_INTROSPECTION.md
    TECHNICAL_GUIDE.md
  __manifest__.py
  models/
  views/
  security/
  data/
  tests/
```

### Required contents of `MODULE_INTROSPECTION.md`

- Why this module exists
- Business problem
- CE 18 coverage checked
- **Property-field assessment** (could properties solve this? If not, why not?)
- OCA 18 same-domain coverage checked
- Adjacent OCA modules reviewed
- Why CE + property fields + OCA composition was insufficient
- Why custom code is justified
- Module type: bridge / overlay / adapter / extension
- Functional boundaries
- Extension points used (`_inherit`, view inheritance, hooks, server actions, APIs)
- Blast radius
- Upgrade risk
- Owner
- Retirement / replacement criteria

### Required contents of `TECHNICAL_GUIDE.md`

- Architecture
- Models extended
- Fields added
- Methods overridden
- View inheritance points
- Security model
- Data files loaded
- Jobs / cron / queues / webhooks
- External integrations
- Test strategy
- Upgrade / rollback notes
- Known limitations and failure modes

### Implementation rules

- Prefer `_inherit`, view inheritance, additive extension, and modular composition over invasive overrides.
- Override CRUD/core methods only when necessary, and always preserve parent behavior via `super()`.
- A custom module is **not justified** if the requirement can be solved by CE 18, property fields, OCA 18, or composition of those layers.

### Canonical doctrine sentence

> Doctrine: CE 18 first → property fields for parent-scoped lightweight metadata → OCA 18 same-domain → adjacent OCA → compose CE + properties + OCA → custom `ipai_*` as last resort with mandatory module introspection and technical guide.

---

## Deprecated (Never Use)

| Item | Replacement | Date |
|------|-------------|------|
| `insightpulseai.net` | `insightpulseai.com` | 2026-02 |
| `odoo-ce` repo name | `odoo` | 2026-02-03 |
| Mattermost (all) | Slack | 2026-01-28 |
| Appfine (all) | Removed | 2026-02 |
| `ipai_mattermost_connector` | `ipai_slack_connector` | 2026-01-28 |
| Supabase (all instances, all usage) | Azure-native services | 2026-03-26 |
| Cloudflare (DNS proxy) | Azure DNS (authoritative) | 2026-03-26 |
| `ipai_ai_widget` (global patches) | Native Odoo 18 Ask AI + `ipai_ai_copilot` | 2026-03-09 |
| DigitalOcean (all) | Azure (ACA + VM + managed PG) | 2026-03-15 |
| Public nginx edge | Azure Front Door | 2026-03-15 |
| Self-hosted runners | GitHub-hosted / Azure DevOps pool | 2026-03-15 |
| Mailgun (`mg.insightpulseai.com`) | Zoho SMTP | 2026-03-11 |
| Vercel deployment | Azure Container Apps | 2026-03-11 |
| GitHub Actions (blanket deprecation) | GitHub Actions = CI + website/docs deploy; Azure DevOps = Odoo/Databricks/Infra deploy (see `ssot/governance/platform-authority-split.yaml`) | 2026-03-30 |
| `ipai-odoo-dev-pg` (Burstable PG) | `pg-ipai-odoo` (General Purpose, Fabric mirroring) | 2026-03-21 |
| Superset (as canonical BI) | Power BI (primary) + Superset (supplemental only) | 2026-03-21 |
| Notion (as data source) | Removed from Databricks bundle | 2026-03-21 |
| Wix (all — hosting, CMS, DNS, API) | Azure DNS + Azure Container Apps + Odoo CMS | 2026-04-02 |
| `microsoft/semantic-kernel` (for new IPAI work) | `microsoft/agent-framework` (MAF — official Microsoft successor; SK is predecessor) | 2026-04-19 |
| `microsoft/autogen` (for new IPAI work) | `microsoft/agent-framework` (MAF — also subsumes AutoGen patterns) | 2026-04-19 |
| `microsoft/CDM` repo as runtime dependency | Fabric semantic models + Dataverse-native CDM (CDM repo is reference vocabulary only; 16 months stale) | 2026-04-19 |
| Custom OData libraries / API authoring (`Microsoft.AspNetCore.OData`) | Skip — not in IPAI stack; learn 5 OData query parameters only when calling Microsoft Graph | 2026-04-19 |
| SAP Signavio adoption (as IPAI agent platform) | Skip — different paradigm (BPM-first vs LLM-first); cannot swap from MAF stack | 2026-04-19 |
| Glean (enterprise search) | Foundry IQ (Microsoft canonical, Entra+Purview-aware, MCP-callable) | 2026-04-19 |
| Notion AI / Mem.ai / Obsidian (as IPAI knowledge manager) | AI in SharePoint (human surface) + Foundry IQ (agent surface) — Microsoft canonical | 2026-04-19 |
| Custom-built eval harness for `agent-platform/evals/` | `Evals for Agent Interop` (`aka.ms/EvalsForAgentInterop`, Microsoft, Jan 2026) | 2026-04-19 |
| Local indexing of Microsoft Learn docs | Microsoft Learn MCP server (`microsoft-learn` already in `.mcp.json`) — Microsoft maintains | 2026-04-19 |
| Custom synthetic data seeder skill | Foundry simulators (adversarial + context-appropriate) + AI Red Teaming Agent (PyRIT) + Faker/Mimesis/Presidio for IPAI delta | 2026-04-19 |
| Custom Pulser identity scheme | Microsoft Entra Agent ID (productized via Frontier early access) | 2026-04-19 |
| Custom M365 tool integration (Outlook/Teams/SharePoint) | Agent 365 MCP servers (7 GA/preview, Nov 2025) | 2026-04-19 |
| `microsoft/ai-agents-for-beginners` as "curriculum-only" classification | RECLASSIFIED 2026-04-19 — primary working code reference for MAF + Foundry V2 (clone + adapt lesson 14 + 11 + 5 + 6 + 8 notebooks) | 2026-04-19 |
| Custom policy engine for Pulser approval bands | `microsoft/agent-governance-toolkit` (AGT) Policy Engine (YAML/OPA/Cedar, sub-ms deterministic, Layer 4.5) | 2026-04-19 |
| Custom audit logger for Pulser actions | AGT audit logger + Governance Dashboard (auto-generated compliance evidence) | 2026-04-19 |
| Custom kill switch / circuit breaker for Pulser | AGT Execution Sandboxing (4-tier privilege rings + kill switch) + Agent SRE (circuit breakers) | 2026-04-19 |
| Custom MCP security validation | AGT MCP Security Scanner (tool poisoning + typosquatting + hidden instruction detection) | 2026-04-19 |
| Custom shadow AI / unregistered agent detection | AGT Shadow AI Discovery | 2026-04-19 |
| Custom agent credential rotation / lifecycle | AGT Agent Lifecycle (provisioning → rotation → orphan detection → decommissioning) | 2026-04-19 |
| Custom prompt injection defense (12-vector) | AGT PromptDefense Evaluator | 2026-04-19 |
| Custom SRE for autonomous agents (SLOs / error budgets / replay / chaos) | AGT Agent SRE | 2026-04-19 |
| Custom compliance evidence pack for AppSource listing | AGT compliance dashboards + auto-generated NIST AI RMF + EU AI Act + Colorado AI Act + SOC 2 mappings | 2026-04-19 |
| Prompt-based safety guardrails ("please follow rules") for Pulser mutations | AGT deterministic policy enforcement (0.00% violation rate vs 26.67% prompt-based per Microsoft red-team) | 2026-04-19 |
| `Azure-Samples/azure-databricks-mlops-mlflow` for fine-tuning | Wrong repo (classic ML regression, no LLM fine-tuning, 12 months stale). Use `databricks_genai` SDK + `databricks/mlops-stacks` scaffold + `databricks/genai-cookbook` patterns for Databricks fine-tuning; Foundry portal + `azure-ai-projects` SDK for Foundry SFT/DPO/RFT. | 2026-04-19 |
| `Azure/azureml-examples track_with_databricks_deploy_aml.ipynb` (deploying to Azure ML endpoints) | Wrong serving plane — IPAI uses Foundry (Layer 4) and Mosaic AI Model Serving (Layer 1), not Azure ML. Adopting Azure ML endpoints fragments the stack into 3 serving planes. | 2026-04-19 |
| `HuggingFaceTB/smol-training-playbook` + `huggingface/smollm` + `huggingface/nanotron` as fine-tuning paths | Wrong scope — these are PRE-TRAINING from scratch, not fine-tuning. Pre-training costs $10K-$100K+ vs fine-tuning $50-$500. Useful as EDUCATION ONLY (transformer math + attention internals; pairs with Deakin SIG787). For production fine-tuning use `databricks_genai` (Databricks) or `azure-ai-projects` (Foundry). | 2026-04-19 |
| Declaring a Microsoft artifact "reference only", "curriculum only", or "not relevant" without inspecting its actual code, structure, and deployment shape | Per Rule 24 (Adopt Reflex) + Execution Gate: surface-level dismissal is forbidden because it has been wrong repeatedly. Run `gh repo view`, list `samples/` + `code-samples/` directories, check last-push date, read the README, install the plugin if it is one — THEN decide. | 2026-04-19 |
| Building custom scaffolds when an active Microsoft baseline already exists | Per Rule 24 + Rule 25: search Microsoft canonical catalog first. Active baselines exist for: agent runtime (MAF), policy engine (AGT), eval harness (Evals for Agent Interop), data foundation (UDF accelerator), agent platform (agentic-UDF accelerator), corpus ingestion (markitdown), knowledge layer (Foundry IQ), identity (Entra Agent ID), governance (Purview), serving (Foundry + Mosaic AI Model Serving). Do not scaffold custom replacements. | 2026-04-19 |
| Treating architecture discussion, doctrine refinement, repo creation, plugin installs, memory entries, or Azure provisioning as runtime delivery | Per Execution Gate: a workstream is "working" only when end-to-end execution produces evidence (input → orchestration → tool calls → output → eval → trace). Sense-making is necessary but never sufficient. | 2026-04-19 |
| Evaluating only L5 solution accelerators while ignoring L1 services, L2 frameworks, L3 tools, L4 reference samples | Per Rule 25: production assembly composes P0 governance + L5 baseline + L4 patterns + L3 primitives + L2 runtime + L1 services. Any single-layer evaluation produces incomplete adoption decisions. | 2026-04-19 |
| Hand-rolling agent runtimes where Microsoft Agent Framework + Foundry Agent Service V2 already fit | MAF is the declared runtime substrate (Rule 10a). Foundry Agent Service V2 is the productized hosting (`azure-ai-projects` + `azure-ai-agents-persistent`). Custom agent runtime in `agent-platform/src/agent_platform/runtime/` must be MAF-imports only — never reimplement orchestration, registry, or graph builders that MAF already provides. | 2026-04-19 |
| Creating bespoke eval harnesses before checking Microsoft-provided eval assets | `Evals for Agent Interop` (`aka.ms/EvalsForAgentInterop`, Microsoft, Jan 2026) + Foundry observability evaluators (built-in safety/quality/RAG/agent evaluators) + AGT PromptDefense Evaluator + AI Red Teaming Agent (PyRIT) cover the eval landscape. Custom Python eval framework in `agent-platform/evals/` is forbidden — use the Microsoft-shipped harness + author scenario YAMLs only. | 2026-04-19 |
| Expanding IPAI custom code beyond thin overlays when the upstream baseline is sufficient | Per Rule 24 + Rule 27: IPAI delta is bounded to (a) Odoo MCP bridge, (b) declarative agent YAML specs, (c) BIR/PH ontology + thresholds in `ssot/`, (d) tenant configs, (e) Pulser persona definitions, (f) reporting/memo templates. ANY new Python module in `addons/ipai/`, `agent-platform/`, `data-intelligence/`, or `agents/` requires a registry entry justifying the delta against the canonical Microsoft baseline. | 2026-04-19 |

### Engineering & Delivery Authority (Option C)

Authoritative rule:
- **GitHub Actions** remains the default CI authority and the deploy authority for docs/web properties.
- **Azure DevOps** remains the deploy authority for Odoo, Databricks, and infra lanes requiring environment/service-connection gating.
- **Azure Boards** is the portfolio/planning system of record.
- **GitHub Issues** is the engineering execution backlog.
- See `ssot/governance/platform-authority-split.yaml`, `ssot/governance/ci-cd-authority-matrix.yaml`, and `ssot/governance/repo-delivery-disposition.yaml`.

### Engineering & Delivery Authority (REVISED 2026-04-19)

**GitHub Actions is the default repo CI + nonprod deploy + package/image publish authority using OIDC federation to Azure. Azure Pipelines remains the sole authority for production deploys, approval-gated promotions, and release evidence capture. Azure-subscription billing enforced. Zero long-lived secrets.**

| System | Role | Status |
|---|---|---|
| **Azure Pipelines** | **Sole authority** for production deploys, approval-gated promotions, release evidence capture, Odoo cloud platform promotions, finance-affecting mutations | ✅ Canonical |
| **GitHub Actions** | **Default** for repo CI, nonprod deploys (dev + staging), package/image publish to GHCR, PR validation, scheduled maintenance. OIDC federation to Azure; no client secrets. Azure-subscription billing. | ✅ Canonical (expanded 2026-04-19) |
| **Azure DevOps Boards** | Portfolio/planning system of record | ✅ Canonical |
| **GitHub** | Source control + PRs + Issues (engineering execution backlog) | ✅ Canonical |
| **Vercel** | **FORBIDDEN** — deprecated 2026-04-07, fully removed | ❌ REMOVED |

### GHA Allowed Scopes (REVISED 2026-04-19)

GHA is allowed for the following scopes. Any new workflow outside these scopes is a doctrine violation and blocked at code review.

| Allowed scope | Rationale |
|---|---|
| **repo_builds** (lint/test/build on PR + push) | Default repo CI lane |
| **package_publish** (npm → GHCR, container images → GHCR) | Per `platform/ssot/org/package-and-artifact-topology.yaml` |
| **image_builds** (container image build + push to GHCR) | Release tags immutable; preview tags short-lived |
| **nonprod_deploys** (dev + staging only, via OIDC managed identity) | Production is Azure Pipelines only |
| **pr_validation** (Copilot Coding Agent autogen, Dependabot checks) | GitHub-native PR context |
| **scheduled_maintenance** (drift detection, SSO health, dependency audits) | Repo-scoped automation |
| **repo_scoped_policy_checks** (CodeQL break-glass, docs link validation) | Defender for DevOps remains primary for code scanning |

**Never in GitHub Actions:** production deploys requiring human approval gates, Odoo ERP prod promotions, finance-affecting mutations without FD approval, any workflow using long-lived client secrets, Key Vault write operations.

### GHA Hard Rules (scoped exception conditions)

1. **Billing MUST route through Azure subscription.** No direct GitHub billing for GHA minutes. Configure at Org → Billing → "Billed through Azure subscription" with Insightpulseai Azure subscription linked.
2. **Every GHA workflow MUST have a sibling Azure Pipeline** that enforces the same gate (defense-in-depth). If sibling pipeline doesn't exist, the GHA workflow isn't allowed.
3. **Azure Pipelines remains the merge gate on `main`.** GHA checks can inform review but cannot be the only required check.
4. **Zero secrets in GHA.** If a workflow needs Azure access, use OIDC federation to a Managed Identity (no PAT, no client secret). Key Vault access is forbidden from GHA.
5. **New GHA workflow requires a PR with:**
   - Explicit reference to one of the allowed scopes above
   - Sibling Azure Pipeline already merged
   - Review from platform-engineering
6. **Workflow location**: `.github/workflows/` is permitted ONLY for scope-exception workflows + non-CI config (CODEOWNERS, dependabot, issue templates).

### Migration evidence (2026-04-14, 2026-04-16)

- 2026-04-14: Deleted `.github/workflows/*.yml` (12 files) including claude-headless-pr-review, claude-headless-spec-check, deploy-erp-canonical, deploy-m365-bot-proxy, devcontainer-ci, foundry-name-guard, odoo-pr-preview, platform-restoration, post-deploy-smoke, spec-bundle-validate, validate-plugins
- 2026-04-14: Replacement Azure Pipelines: existing `azure-pipelines/*.yml` (26 files) + new pipelines for PR preview, spec-bundle-validate, foundry-name-guard, plugin-validate
- 2026-04-16: Scoped exception doctrine landed; billing wiring MUST be completed before any GHA workflow is created. See `ssot/governance/gha-scoped-exception.yaml`.

### Agentic Workflow Security Doctrine (added 2026-04-14)

Per Microsoft's GitHub Agentic Workflows architecture paper + DevBlogs Agentic Platform Engineering, ALL Pulser mutating agents must adopt the **3-tier defense pattern** — implemented on **Azure Pipelines + ACA**, not GitHub Actions.

| Tier | Responsibility | IPAI implementation (Azure-native) |
|---|---|---|
| **Substrate** | OS/container isolation per agent invocation | ACA dedicated container (NOT GitHub Actions runner), read-only host fs, tmpfs overlay, chroot/userns |
| **Configuration** | Declarative policy (allowlists, firewall, zero-secret) | Per-agent manifest in repo, MCP allowlist, Azure Key Vault holds creds (agent ZERO direct access) |
| **Planning** | Runtime execution control + Safe Outputs | 3-stage vetting via Pulser middleware: filter ops → moderate content → remove secrets; rate limit per stage |

**Core rules:**
- **Zero-secret agents:** Pulser agents NEVER hold credentials directly; API proxy (ACA app) + Key Vault own auth.
- **Allowlisted MCPs only:** No dynamic tool acquisition. Each agent's MCP set declared in manifest.
- **Safe Outputs subsystem mandatory** for every mutating tool (filter / moderate / sanitize + rate-limit).
- **Microsoft Content Safety** integration for prompt-injection + bias detection.
- **Audit traceability** (who-acted-when + before/after diff + replay) per ADO Issue `#623`.

**GitHub Copilot Coding Agent positioning:**
- Routine code-gen (boilerplate, tests, docs, parity-record population) → **Coding Agent** generates PRs from Issues.
- Architecture / SSOT / multi-step / cross-doctrine work → **Claude Code** (per session execution).
- Coding Agent PRs are **validated by Azure Pipelines** (not GitHub Actions) before merge.
- Both consume same `.mcp.json` shared MCP servers.
- Both honor CLAUDE.md doctrine.

**No-GitHub-Actions clarification:** Adopting the GitHub Agentic Workflows *security pattern* (3-tier defense, Safe Outputs, zero-secret agents) does NOT mean adopting GitHub Actions as runtime. The pattern is implemented on Azure Pipelines + ACA. GitHub's blog is the architecture reference; the implementation is Azure-native.

**Anchors:**
- ADO Issues: #341/#628 (3-tier defense on ACA), #240/#629 (Coding Agent → Azure Pipelines validation), #524/#630 (Safe Outputs on Pulser middleware)
- GitHub blog (pattern reference only): agentic-workflows-security-architecture
- Microsoft DevBlogs (pattern reference only): agentic-platform-engineering-with-github-copilot
- `docs/research/ms-copilot-d365-m365-agents-catalog-for-ipai.md` (86-agent reference catalog)
- `ssot/governance/platform-authority-split.yaml` (canonical authority matrix)

---

## Deep Reference

| Topic | Location |
|-------|----------|
| Directory structure & inventory | `.claude/rules/repo-topology.md` |
| Architecture, Docker, integrations | `.claude/rules/platform-architecture.md` |
| Secrets policy, GHAS, allowed tools | `.claude/rules/security-baseline.md` |
| GitHub governance, CI/CD, PR rules | `.claude/rules/github-governance.md` |
| Enterprise parity strategy & tables | `.claude/rules/ee-parity.md` |
| Odoo CE 18 rules, modules, testing | `.claude/rules/odoo-rules.md` |
| Supabase usage & activation | `.claude/rules/supabase-usage.md` |
| BIR compliance (PH tax/payroll) | `.claude/rules/bir-compliance.md` |
| MCP Jobs system | `.claude/rules/mcp-jobs.md` |
| n8n automations & Claude integration | `.claude/rules/automations.md` |
| Spec kit structure & bundles | `.claude/rules/spec-kit.md` |
| SSOT platform rules | `.claude/rules/ssot-platform.md` |
| Architecture & stack | `docs/ai/ARCHITECTURE.md` |
| IPAI module naming | `docs/ai/IPAI_MODULES.md` |
| OCA workflow | `docs/ai/OCA_WORKFLOW.md` |
| Testing recipes | `docs/ai/TESTING.md` |
| Docker commands | `docs/ai/DOCKER.md` |
| Troubleshooting | `docs/ai/TROUBLESHOOTING.md` |

---

*Last updated: 2026-03-30*
