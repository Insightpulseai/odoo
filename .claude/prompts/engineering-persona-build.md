---
name: engineering-persona-build
description: Deep-research agent prompt that crawls the Microsoft Foundry Python SDK docs and Anthropic's engineering blog, then produces a knowledge base, reusable skill, Principal Engineer persona, and engineering-decision judge for IPAI / Pulser.
target_agent: Claude Code (main) or Agent(subagent_type="deep-research-agent")
sources:
  - https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/sdk-overview?view=foundry&pivots=programming-language-python
  - https://www.anthropic.com/engineering
  - https://github.com/github/spec-kit
  - https://github.com/microsoft/azure-skills
  - https://www.kaggle.com/learn-guide/5-day-genai-agents  # Google 5-Day AI Agents Intensive (patterns only — Azure-native SDK substitution required)
  - https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-microsoft-agent-factory/4470732  # Microsoft Agent Factory announcement (Foundry Agent Service positioning)
  - https://github.com/anthropics/claude-cookbooks/tree/main/anthropic_cookbook  # Anthropic Cookbooks — runnable recipes (companion to engineering blog)
  - https://learn.microsoft.com/microsoftteams/platform/toolkit/  # Teams Toolkit docs (authoring surface for Teams delivery channel)
  - https://github.com/OfficeDev/TeamsFx  # Teams Toolkit source (real artifact behind the VS Code extension)
expected_runtime: 45-120 minutes
created: 2026-04-14
pairs_with: ms-startups-growth-build.md
---

# Engineering Persona Build — Foundry SDK + Anthropic Engineering

## Why this exists

The growth prompt (`ms-startups-growth-build.md`) produces the CGO half of the
founder's brain. This prompt produces the other half: a **Principal Engineer /
CTO-grade persona** grounded in the two sources that actually matter for
IPAI's stack:

1. **Microsoft Foundry Python SDK** — how to build Foundry agents the way
   Microsoft intends them to be built (not reinvented).
2. **Anthropic engineering** — how Anthropic builds production agents,
   designs context windows, handles tool use, and runs Claude Code itself.

Every engineering decision on IPAI should be pressure-tested against both.

## How to run

1. Start a fresh Claude Code session.
2. Paste the PROMPT block below.
3. If weekly limit is tight, dispatch via
   `Agent(subagent_type="deep-research-agent", ...)`.
4. Review `docs/research/engineering/coverage-report.md` when done.

## Re-run policy

- Anthropic engineering blog updates frequently — safe to re-run monthly.
- Foundry SDK docs update with each SDK release — re-run when SDK bumps to a
  new major version.
- Overwrite `docs/research/engineering/raw/` freely; persona + judge require
  human review before overwrite.

---

## PROMPT

```
ROLE
You are a deep-research agent. Your job is to ingest eight engineering corpora:

  A. Microsoft Foundry Python SDK (Azure AI Projects 2.x and related)
     Start: https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/sdk-overview?view=foundry&pivots=programming-language-python

  B. Anthropic Engineering
     Start: https://www.anthropic.com/engineering

  C. GitHub Spec Kit (Specify CLI — spec-driven development toolkit)
     Start: https://github.com/github/spec-kit
     Specifically: README, CLI reference section, all /docs/* pages, all /spec/* samples,
     and the template used by `specify init`. Clone or read raw files via
     https://raw.githubusercontent.com/github/spec-kit/main/... when needed.

  D. Microsoft Azure Skills (Claude Code / agent skill catalog for Azure services)
     Start: https://github.com/microsoft/azure-skills
     Specifically: README, every SKILL.md under skills/*/, skill manifest files,
     and any Azure-service-specific skill docs. Catalog which Azure surfaces
     already have skills (Cosmos DB, Container Apps, Key Vault, Foundry, etc.)
     and flag gaps relevant to IPAI (Odoo on ACA, Postgres Flexible, Foundry
     agent wiring, Front Door, Databricks/Fabric).

Then produce a governed engineering knowledge base + reusable skill +
Principal Engineer persona + engineering-decision judge that helps the
IPAI / Pulser stack (Azure-native, Odoo CE 18 + OCA, multi-agent, policy-gated)
build production-grade agents without reinventing what Microsoft, Anthropic,
GitHub, or Azure Skills has already solved.

Do not summarize in chat. Produce files.

---

SCOPE (recursive, depth >= 5 per corpus)

Corpus A — Microsoft Foundry Python SDK:
  - Follow every internal Microsoft Learn link under /azure/foundry/, /azure/ai-foundry/,
    /azure/ai-services/, and /python/api/azure-ai-projects/
  - Include linked SDK reference pages (azure-ai-projects, azure-ai-inference,
    azure-identity, azure-ai-agents, azure-ai-evaluation)
  - Include the Foundry Agent Service and Responses API docs
  - Include authentication pages (DefaultAzureCredential, managed identity,
    keyless patterns)

Corpus B — Anthropic Engineering:
  - Crawl every blog post under anthropic.com/engineering
  - Include linked Anthropic docs pages that posts reference
    (docs.anthropic.com for tool use, prompt caching, context management,
    computer use, Claude Code Agent SDK)
  - Include Anthropic's published Claude Code documentation at
    code.claude.com/docs where it extends engineering posts

Corpus C — GitHub Spec Kit (Specify CLI):
  - Fetch https://github.com/github/spec-kit README and the full Specify CLI
    reference anchor (#-specify-cli-reference)
  - Fetch raw files under the repo's /docs, /spec, /templates, /memory, /scripts
    via https://raw.githubusercontent.com/github/spec-kit/main/<path> as needed
    to ground the commands (specify init, specify plan, specify tasks, etc.)
  - Include linked issue templates and example spec bundles
  - Goal: understand how Spec Kit structures specs, plans, tasks, and how the
    CLI wires them — so IPAI's existing `.claude/skills/speckit.*` stay aligned
    with upstream evolution

Corpus D — Microsoft Azure Skills:
  - Fetch https://github.com/microsoft/azure-skills README and repo tree
  - For every directory under skills/, fetch SKILL.md and any referenced docs
  - Fetch raw files via https://raw.githubusercontent.com/microsoft/azure-skills/main/<path>
  - Build a catalog of what's covered (Cosmos DB, Container Apps, Key Vault,
    Foundry, etc.) and flag IPAI-relevant gaps (Odoo on ACA, Postgres Flexible
    Server with Fabric mirroring, Front Door preserve-hostname, Databricks
    Unity Catalog, Pulser MCP wiring)
  - Mark which skills IPAI should adopt as-is, adapt, or leave

Corpus H — Microsoft Teams Toolkit (delivery-channel authoring):
  - Start: https://learn.microsoft.com/microsoftteams/platform/toolkit/
  - Also fetch https://github.com/OfficeDev/TeamsFx README + /docs/ tree
  - Follow linked Microsoft Learn pages under /microsoftteams/platform/
    relevant to: Copilot agent manifests, bot framework handoff, SSO with
    Entra, app packaging (teamsApp/manifest.json), AppSource submission
  - Scope focus per IPAI doctrine:
    Teams is a DELIVERY CHANNEL, not the Pulser runtime
    (per CLAUDE.md: "M365 Agents SDK is a channel layer ... does NOT
    replace the canonical agent-platform runtime")
  - Extract: Teams app manifest schema, Copilot agent manifest schema,
    dev tunnel setup, SSO patterns for Entra-backed Teams apps,
    submission requirements for Teams Store / AppSource, how Teams
    Toolkit interacts with Azure Functions vs ACA backends
  - IPAI application: when IPAI ships Pulser as a Teams app, this corpus
    tells us the wire format + submission path. Pulser's agents stay on
    Foundry; Teams app is a thin packaging + auth layer.
  - Mark what IPAI adopts: manifest schemas, SSO pattern, dev tunnel.
    Mark what IPAI rejects: Teams-specific hosted bot services (use ACA),
    Teams sample SDK choices (use Foundry + Anthropic via the Pulser
    runtime, not bot-framework + OpenAI-direct examples from samples)

Corpus G — Anthropic Cookbooks (runnable recipes, companion to Corpus B):
  - Start: https://github.com/anthropics/claude-cookbooks/tree/main/anthropic_cookbook
  - Walk every subdirectory (tool_use/, agents/, multimodal/, misc/, etc.)
  - For every .ipynb notebook and .md recipe, fetch via
    https://raw.githubusercontent.com/anthropics/claude-cookbooks/main/<path>
  - Extract per recipe:
      * recipe name + file path
      * problem it solves in one line
      * minimal runnable code block (pasteable)
      * external dependencies (SDK, MCP server, external API)
      * prompt-caching / tool-use / extended-thinking flags if used
      * token-cost / latency notes if mentioned
  - IPAI substitution rule: every recipe targeting the direct Anthropic API
    must be paired with its Foundry-endpoint equivalent
    (base_url -> https://ipai-copilot-resource.services.ai.azure.com/anthropic
     + DefaultAzureCredential bearer token, not ANTHROPIC_API_KEY)
  - Relationship to Corpus B:
    Corpus B = principles / blog posts
    Corpus G = runnable confirmation of those principles
    Every pattern in B should have at least one G recipe cited where one exists.

Corpus F — Microsoft Agent Factory (Foundry Agent Service positioning):
  - Start: https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-microsoft-agent-factory/4470732
  - Follow linked TechCommunity posts under /blog/azure-ai-foundry-blog/ that
    elaborate Agent Factory components (Agent Service, Agent Builder,
    Connected Agents, Agent ID, Agent Catalog)
  - Follow linked Microsoft Learn pages (learn.microsoft.com/azure/ai-foundry/
    agents/*) that are authoritative references for the blog claims
  - Extract: what Microsoft calls the "Agent Factory" building blocks,
    the positioning vs. Copilot Studio / Copilot Agents / M365 Copilot,
    the developer ladder (pro-code -> low-code -> no-code), the Agent ID
    and governance story (tie to existing IPAI memory on Agent ID surface),
    and the roadmap signals (preview vs GA status by feature)
  - IPAI application: Pulser IS an Agent Factory instance on `ipai-copilot-resource`.
    Map every Microsoft Agent Factory building block to the IPAI equivalent:
    Agent Service -> Foundry project `ipai-copilot`;
    Agent Builder -> Foundry portal + Pulser's manifest-first authoring;
    Connected Agents -> Pulser planner/router + specialists;
    Agent ID -> Entra Agent ID (P2, already visible on IPAI tenant);
    Agent Catalog -> IPAI-internal agents/ directory of personas/judges/skills
  - Gaps to flag: features announced but not yet deployable on
    `ipai-copilot-resource` (e.g., Connected Agents GA region, Agent ID
    creation vs visibility, Agent Catalog publishing path)

Corpus E — Google 5-Day AI Agents Intensive (Nov 2025, self-paced on Kaggle):
  - Start: https://www.kaggle.com/learn-guide/5-day-genai-agents
  - Fetch all 5 whitepapers (Day 1 Intro / Day 2 Tools+MCP / Day 3 Context
    Engineering / Day 4 Agent Quality / Day 5 Prototype-to-Production)
  - If Kaggle page blocks direct fetch, capture the curriculum structure
    and topic coverage from the public description, then extract patterns
    from the corresponding publicly-linked whitepaper PDFs or blog
    companions where available
  - Scope focus: patterns and frameworks, NOT SDK choices
    * ADOPT: agent taxonomy, Agent Ops discipline, tool-design best practices,
      MCP interoperability, session vs memory distinction, observability
      pillars (Logs/Traces/Metrics), LLM-as-Judge, HITL evaluation,
      A2A Protocol, agent identity/policy patterns
    * REJECT (IPAI is Azure-native): Google ADK, Gemini models, Vertex AI
      Agent Engine deployment, google-cloud-aiplatform SDK
    * TRANSLATE: for each Google pattern, record the IPAI-native equivalent
      (ADK agent -> Foundry PromptAgentDefinition; Gemini -> Claude via
      Foundry Anthropic endpoint; Vertex Agent Engine -> Foundry Agent
      Service on ACA; Agent Builder -> Foundry project + MCP tool binds)
  - Explicit mandate: any code sample captured from Corpus E must be paired
    with its Foundry + Anthropic equivalent before landing in Artifact 1

Stop conditions per corpus: depth 5, OR URL leaves the host allowlist
(A: learn.microsoft.com + python.microsoft.com;
 B: anthropic.com + docs.anthropic.com + code.claude.com;
 C: github.com/github/spec-kit + raw.githubusercontent.com/github/spec-kit;
 D: github.com/microsoft/azure-skills + raw.githubusercontent.com/microsoft/azure-skills;
 E: kaggle.com/learn-guide/5-day-genai-agents + any publicly-linked whitepaper hosts;
 F: techcommunity.microsoft.com/blog/azure-ai-foundry-blog + learn.microsoft.com/azure/ai-foundry/agents;
 G: github.com/anthropics/claude-cookbooks + raw.githubusercontent.com/anthropics/claude-cookbooks;
 H: learn.microsoft.com/microsoftteams/platform + github.com/OfficeDev/TeamsFx + raw.githubusercontent.com/OfficeDev/TeamsFx),
OR page already fetched.

Fetch method: WebFetch. Maintain a visited-URL set.
Respect robots.txt. No auth-walled content.

---

EXTRACTION — for every page, capture

- url, title, last_updated, corpus (A / B / C / D)
- topic category (agent-design, auth, tool-use, context-mgmt, evals,
  caching, orchestration, safety, deployment, observability,
  spec-authoring, cli-command, skill-definition, azure-service-pattern)
- SDK / CLI / skill surface touched
    (A: Foundry SDK class/method names;
     B: Anthropic API endpoints / SDK types / post title;
     C: Specify CLI command + flag + artifact produced;
     D: skill name + Azure service + skill frontmatter fields)
- code examples (verbatim, with language tag)
- claimed invariants (e.g., "agents should be stateless", "tool results
  live in user-role messages", "responses API bills differently",
  "specs precede code", "skills are rigid vs flexible")
- named patterns (e.g., "react loop", "planner-executor", "think tool",
  "contextual retrieval", "Safe Outputs", "spec → plan → tasks → implement",
  "MI-first auth skill")
- deprecations / version gates mentioned
- cost / latency / token implications if stated
- IPAI-adoption flag (for C & D only):
    adopt_as_is | adapt | reference_only | skip_with_reason

Write raw captures to: docs/research/engineering/raw/<corpus>/<slug>.md
  where <corpus> is one of: foundry / anthropic / spec-kit / azure-skills
Include YAML frontmatter with all fields above.

---

SYNTHESIS — produce FOUR artifacts

### Artifact 1: Engineering knowledge base
Path: docs/research/engineering/knowledge-base.md
Structure:
  - Foundry SDK capability matrix (class -> purpose -> when to use -> code snippet)
  - Anthropic pattern catalog (pattern name -> when to use -> example -> trade-offs)
  - Spec Kit command reference (specify init/plan/tasks/implement/analyze/etc.
    with inputs, outputs, and the exact spec-bundle file each command writes)
  - Azure Skills adoption matrix (skill name -> Azure service -> IPAI-relevant?
    -> adopt_as_is | adapt | reference_only | skip | GAP-TO-FILL)
  - Cross-walk table: "If you need X, Foundry says Y, Anthropic says Z,
    Spec Kit says A, Azure Skills says B, IPAI's policy is W"
  - Auth & identity section (DefaultAzureCredential chain, MI, keyless,
    token caching, rotation)
  - Agent lifecycle section (create_version, deployment, evals, promotion)
  - Tool-use section (Anthropic tool spec vs. Foundry tool bindings vs.
    MCP — how they map)
  - Context management section (caching, compaction, handoff, subagents,
    session resume)
  - Safety & policy section (Safe Outputs, Content Safety, prompt injection,
    3-tier defense per IPAI doctrine)
  - Observability section (OpenTelemetry, traces, evals, replay)
  - IPAI-specific application notes: how each capability maps to the Pulser
    architecture (planner/router + specialists + validators + policy gate)
  - Contradictions found across the two corpora (where Microsoft and
    Anthropic recommend different patterns — flag and recommend)
  - Open questions requiring human decision

### Artifact 2: Reusable skill
Path: .claude/skills/pulser-engineering-compass/SKILL.md
Format: standard skill frontmatter + body
Purpose: "Given a proposed engineering change on the Pulser / IPAI stack,
return (a) the nearest Microsoft-canonical pattern, (b) the nearest
Anthropic-canonical pattern, (c) which one applies, (d) the minimal code
spike to validate, (e) the evals to add."
Must include:
  - decision tree: "is this commodity, compositional, or delta?"
    (enforces CLAUDE.md engineering execution doctrine)
  - template code blocks for the common Pulser primitives:
    * create a Foundry agent with MI auth
    * wire a tool to an MCP endpoint
    * add prompt caching on a long-system-prompt
    * run an eval with azure-ai-evaluation
    * set up Safe Outputs middleware
  - anti-patterns it refuses (hardcoded API keys, floating model aliases,
    agent-held credentials, ad-hoc prompt engineering without evals,
    tool explosions > ~15 tools, swallowed errors, unbounded retries)
  - link-out map to canonical source pages (source of truth)

### Artifact 3: Principal Engineer persona
Path: agents/personas/principal-engineer-persona.md
Persona name: "Rafi, Principal Engineer"
Must embody:
  - Ownership: agent architecture, SDK choices, auth & identity, eval
    discipline, observability, cost/latency budgets, release gates,
    incident response, doctrine (CLAUDE.md) enforcement
  - Decision framing: always answers in the layer order —
    (1) does CE 18 / built-in solve it? (2) does OCA / Anthropic /
    Foundry stock pattern solve it? (3) can we compose? (4) minimal
    thinnest delta only if 1-3 fail
  - Voice: direct, evidence-first, never "here's a tutorial",
    always "here's the change + verification + rollback"
  - Anti-patterns refused:
    * starting from scratch when upstream solved it
    * "let me write a helper for this" on first use
    * mocking what should be integration-tested
    * speculative abstractions / future-proofing
    * feature flags for reversible changes
    * 3-hour debugging sessions without reading the error
  - Tools used: Claude Code + Agent SDK, Foundry Python SDK, Azure CLI,
    `gh`, `az`, Docker, PostgreSQL, pytest, playwright, openTelemetry
  - Weekly cadence: incident review (root cause, not symptom),
    eval score review, cost-per-agent-call review, doctrine drift review,
    dependency & CVE sweep
  - First-30-days playbook for IPAI/Pulser:
    * land deterministic CI baseline (Azure Pipelines)
    * land a single production-quality Foundry agent end-to-end with
      auth, evals, Safe Outputs, OTel, and rollback
    * land the pattern as a reusable template other agents copy
  - Escalation rules (when he pulls in CGO, CEO, legal, Microsoft PDM,
    Anthropic TAM)
  - How he disagrees (shows evidence, names the doctrine, proposes the
    cheapest spike to prove himself wrong)

### Artifact 4: Engineering-decision judge
Path: agents/judges/engineering-decision-judge.md
Purpose: Score any proposed engineering change against the knowledge base +
Rafi persona + IPAI doctrine.
Dimensions (0-5 each, with criterion text):
  - Upstream fit (does CE / OCA / Foundry SDK / Anthropic pattern solve this?)
  - Doctrine alignment (CLAUDE.md invariants — Azure-native, CE-only,
    no deprecated items, MI-first, pinned models)
  - Reversibility (how long to roll back? what's the blast radius?)
  - Evidence plan (what eval / test / trace proves it works?)
  - Cost & latency fit (token budget, latency budget, $ per 1k calls)
  - Security posture (secrets handling, Safe Outputs, least-privilege)
  - Simplicity (thinnest delta; no speculative abstractions)
Output format: JSON with per-dimension score + rationale + blocking flag
(blocks if doctrine alignment < 3 OR security < 4 OR upstream fit < 2 and
no justification).
Include 5 worked examples:
  - a clear-pass (thin Pulser tool bridging to Foundry agent with MI auth)
  - a clear-fail (hand-rolled auth with hardcoded API key)
  - a borderline (custom retry loop when Azure SDK already does it)
  - a subtle fail (correct code but wrong doctrine — e.g., using GitHub
    Actions for deploy when Azure Pipelines is canonical)
  - a subtle pass (deviation from upstream with a documented reason
    and rollback plan)

---

GOVERNANCE & CONSTRAINTS

- Every claim must cite at least one raw capture file in
  docs/research/engineering/raw/<corpus>/
- If corpora disagree, record both and recommend based on IPAI doctrine
- No fabrication. Unknown fields = "UNKNOWN — not found in crawled pages"
- Honor CLAUDE.md doctrine:
  * Azure-native only
  * CE 18 + OCA first; thin `ipai_*` last
  * MI / Entra first, API keys fallback
  * Pinned model deployments (no floating aliases)
  * No deprecated items (Supabase, Vercel, Cloudflare, Mailgun, n8n, etc.)
  * Azure Pipelines is sole CI/CD authority
  * 3-tier defense + Safe Outputs for mutating agents
- All code examples must be runnable against `ipai-copilot-resource` /
  project `ipai-copilot` (canonical Foundry) — not synthetic endpoints
- Date format: absolute dates (2026-04-14), never "last week"

---

VERIFICATION (run before declaring done)

1. >= 65 pages fetched total across all 8 corpora.
   Per-corpus minimums: A >= 10, B >= 8, C >= 6, D >= 6, E >= 5, F >= 4, G >= 8, H >= 5.
   If a corpus cannot meet its minimum (e.g., Kaggle gating Corpus E), log
   the gap with exact URLs attempted in open-questions.md and proceed.
2. Every SDK class named in knowledge-base.md has a raw capture citation
3. Every Anthropic pattern named in knowledge-base.md has a raw capture citation
4. Every Specify CLI command named in knowledge-base.md has a Corpus C citation
5. Every Azure Skill named in the adoption matrix has a Corpus D citation
6. Every Agent Factory building block named has a Corpus F citation
6a. Every Anthropic pattern in knowledge-base.md has at least one Corpus G
    recipe citation where one exists in the cookbook repo (principle + proof)
6b. Every Corpus G recipe captured shows its Foundry-endpoint substitution
    (base_url swap + DefaultAzureCredential bearer) — direct-API keys not allowed
6c. Corpus H yields a "Teams delivery channel" section in knowledge-base.md
    with: Teams app manifest schema, Copilot agent manifest schema, SSO-with-Entra
    pattern, dev-tunnel setup, and AppSource submission checklist — each with
    Corpus H citations. Doctrine reminder block inline: "Teams = channel, not
    runtime; Pulser agents stay on Foundry."
7. Skill SKILL.md has valid frontmatter (name, description, type)
8. Persona file passes human read: sounds like a real Principal Engineer,
   not a generic persona
9. Judge file has all 5 worked examples with scores + rationale
10. Cross-walk table has >= 15 rows, at least 5 of which reference 3+ corpora
    (proves genuine cross-corpus synthesis, not just parallel summaries)
11. No broken internal links between artifacts
12. Output a coverage report: docs/research/engineering/coverage-report.md
    listing URLs crawled per corpus, URLs skipped (with reason), and the
    >= 5 most load-bearing patterns discovered in each corpus
13. Agent Factory mapping table (Corpus F) has every Microsoft building block
    mapped to the IPAI / Pulser equivalent with a "what's missing on
    ipai-copilot-resource today" column

---

DELIVERABLE

Reply in CONTEXT/CHANGES/EVIDENCE/VERIFICATION/NEXT format (per
~/.claude/rules/output-format.md). Include the coverage report summary inline.
Do not ask clarifying questions — infer from IPAI's CLAUDE.md and memory.
```

---

## Outputs (expected when the agent finishes)

| Path | Purpose |
|---|---|
| `docs/research/engineering/raw/foundry/*.md` | Per-page captures from Foundry SDK corpus |
| `docs/research/engineering/raw/anthropic/*.md` | Per-page captures from Anthropic engineering corpus |
| `docs/research/engineering/knowledge-base.md` | SDK matrix + pattern catalog + cross-walk |
| `docs/research/engineering/coverage-report.md` | Crawl coverage per corpus |
| `docs/research/engineering/open-questions.md` | Unknown fields + human-decision gaps |
| `.claude/skills/pulser-engineering-compass/SKILL.md` | Reusable skill |
| `agents/personas/principal-engineer-persona.md` | Rafi, Principal Engineer persona |
| `agents/judges/engineering-decision-judge.md` | Engineering decision evaluator |

## Pairs with

- `.claude/prompts/ms-startups-growth-build.md` — companion growth persona (Kira, CGO)

Together they produce the founder's two-hemisphere brain:
- **Kira (CGO)** — grounds growth decisions in Microsoft for Startups programs
- **Rafi (Principal Engineer)** — grounds engineering decisions in Foundry SDK + Anthropic engineering

## Related

- `CLAUDE.md` — engineering execution doctrine, cross-repo invariants
- `docs/runbooks/claude-code-foundry.md` — Foundry activation runbook
- Memory: `reference_foundry_sdk_2x`, `project_foundry_managed_identity`,
  `feedback_foundry_reuse_doctrine`, `feedback_engineering_execution_doctrine`
