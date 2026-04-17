# Product Requirements Document

## Pulser Creative Strategy OS

**Reverse PRD of:** LIONS Marketing Assistant
**Status:** Draft
**Owner:** InsightPulseAI
**Target repo path:** `spec/pulser-creative-strategy-os/prd.md`

## 1. Executive Summary

LIONS Marketing Assistant is positioned as an AI research assistant for creative and strategic marketing work. Publicly, it emphasizes trusted-source retrieval across Cannes Lions, WARC, Contagious, and Effie; three core task modes (`Inspire`, `Research`, `Validate`); source-linked answers; prompt privacy; multilingual response capability; and usage-limited single-user and team plans. It explicitly does **not** position itself as a generative media product.

The improved product should not try to be “LIONS, but cheaper.” It should be a **research-to-action operating system** for agencies and brand teams, especially in emerging and multilingual markets. The core leap is moving from **trusted inspiration retrieval** to a closed loop of **signal ingestion → insight synthesis → brief generation → creative variant planning → activation handoff → performance learning**. This turns the assistant from a knowledge tool into a decision and execution layer. This is the product gap implied by LIONS’ public feature set, which is still centered on research, evidence packs, and strategic validation rather than campaign execution and operating workflows.

Pulser Creative Strategy OS will be the finance-grade/product-grade equivalent for marketing teams: a system that combines trusted external intelligence, first-party commercial context, localized market signals, structured collaboration, and downstream activation hooks. It should win on **local relevance, workflow depth, execution readiness, and memory**, not by copying a source-search UI.

---

## 2. Problem Statement

Marketing strategists, planners, creatives, and client teams still work across disconnected systems:

* external intelligence tools for research
* deck tools for narrative building
* spreadsheets for benchmarks
* messaging docs for refinement
* ad platforms for trafficking
* reporting tools for learning loops

LIONS Marketing Assistant reduces research fragmentation by searching trusted creative and effectiveness sources and returning linked answers. That is valuable, but the publicly disclosed product remains optimized for **finding evidence fast**, not for owning the full downstream operating cycle. It supports inspiration, research, and validation, but the public product messaging does not center execution workflows such as activation, brief orchestration, asset operations, audience handoff, or performance-memory feedback into the next brief.

For PH and APAC teams, there is an additional gap: strategy tools often remain global and English-centric even when they technically support multilingual responses. LIONS states that summaries default to English unless the user prompts another language, while much of the underlying content is still primarily English. That is helpful but insufficient for markets that require mixed-language reasoning, local creator context, local retail/platform conventions, and client-ready outputs for non-Western operating environments.

---

## 3. Product Vision

Build the best **trusted-strategy-to-execution assistant** for agency and in-house marketing teams in multilingual, fast-moving markets.

Pulser Creative Strategy OS should let a team:

1. ask a category, brand, audience, or trend question
2. retrieve trusted proof and local market context
3. synthesize a strategic position
4. generate a client-ready brief and evidence pack
5. turn the brief into channel-ready creative and activation plans
6. feed outcomes back into the system for future recommendations

This preserves LIONS’ strongest idea — trusted-source strategy support — while extending it into actual operating value.

---

## 4. Goals

### 4.1 Primary Goals

1. **Trusted strategy retrieval**
   Return citation-backed answers grounded in premium and first-party sources.

2. **Localized intelligence**
   Make the product materially better than global strategy assistants in PH/APAC contexts.

3. **Decision support, not just search**
   Convert findings into positions, hypotheses, briefs, and recommendations.

4. **Execution handoff**
   Bridge strategy into activation, creative production, and reporting workflows.

5. **Persistent team memory**
   Preserve brand voice, prior recommendations, wins/losses, and approved narratives.

### 4.2 Secondary Goals

1. deck/evidence-pack generation
2. multi-stakeholder collaboration
3. reusable insight templates by category/use case
4. creative and campaign postmortem loops

---

## 5. Non-Goals

1. Build a generic image/video generator as the core product.
2. Replace Adobe, Figma, or a full DAM.
3. Replace Smartly, CM360, Meta Ads Manager, or a full ad-buying suite in v1.
4. Rebuild a full CDP or Dataverse equivalent.
5. Offer uncited freeform hallucinated strategy advice as the primary mode.

LIONS explicitly says it is “proudly not generative” for media creation. Pulser should not copy that exact stance, but it also should not make generative media the center of the product. The winning wedge is **strategy-to-action**, not “another gen-AI canvas.”

---

## 6. Target Users

### 6.1 Primary Users

* strategy directors
* planners
* account leads
* creative leads
* innovation teams
* growth marketers

### 6.2 Secondary Users

* client-side brand managers
* media planners
* research and insights teams
* founders/SMB operators
* production leads

### 6.3 Team Types

* agencies
* brand marketing teams
* retailers / commerce-first operators
* creator-led businesses
* regional strategy teams

---

## 7. Jobs To Be Done

1. “Help me understand this category, competitor set, and audience fast.”
2. “Help me find proof that this creative/platform strategy will work.”
3. “Help me turn the insight into a brief my team or client can use.”
4. “Help me localize the idea for the Philippines or Southeast Asia.”
5. “Help me convert the brief into a content, creator, or activation plan.”
6. “Help me learn from campaign performance and reuse that learning.”

---

## 8. Competitive Diagnosis of LIONS Marketing Assistant

### 8.1 Publicly Disclosed Strengths

* trusted source base from Cannes Lions, WARC, Contagious, and Effie
* source-linked answers
* clear modes for inspiration, research, and validation
* privacy commitment that prompts are not used to train models
* multilingual response support
* simple self-serve pricing entry point
* evidence-pack / narrative-building direction under LIONS Intelligence.

### 8.2 Publicly Disclosed Constraints

* single-user plan only listed in a limited country set, while teams are global
* usage caps per hour/day even on paid plans
* English-default behavior unless prompted otherwise
* explicit avoidance of generative media creation
* public positioning centered on research acceleration more than execution orchestration.

### 8.3 Product Gap To Exploit

Pulser should win by adding:

* local market intelligence
* first-party commercial context
* workflow memory
* execution handoff
* post-campaign learning loops
* stronger structured outputs than chat summaries alone

---

## 9. Product Principles

1. **Cited by default**
2. **Local by design**
3. **Memory over one-off chat**
4. **Decision outputs over generic prose**
5. **Execution-adjacent, not research-only**
6. **Human approval on high-impact recommendations**
7. **Private brand/workspace context stays private**

---

## 10. Functional Requirements

### 10.1 Intelligence Core

**FR-1 — Trusted Source Retrieval**
The system must answer prompts using licensed, curated, and user-connected sources, with visible citations and source links.

**FR-2 — Local Market Signal Layer**
The system must ingest and surface country- and language-specific signals for target markets, starting with the Philippines.

**FR-3 — Hybrid Source Reasoning**
The system must combine:

* premium external sources
* client/workspace files
* prior team decisions
* campaign performance summaries

**FR-4 — Multi-Language Strategy Support**
The system must support English, Filipino/Tagalog, and mixed-language prompting and output in v1.

### 10.2 Strategy Workflows

**FR-5 — Insight Modes**
The system must support at least four structured workflow modes:

* Discover
* Diagnose
* Decide
* Deploy

This replaces the simpler `Inspire / Research / Validate` framing with modes tied to real team outcomes.

**FR-6 — Brief Generator**
The system must generate structured briefs with:

* problem
* audience
* tension
* strategic angle
* reasons to believe
* channel implications
* measurement plan

**FR-7 — Evidence Pack Generator**
The system must generate a client-ready evidence pack with citations, examples, benchmarks, and objections/risks.

**FR-8 — Localization Engine**
The system must adapt strategic recommendations by market, language, media behavior, and retail/platform norms.

### 10.3 Execution Handoff

**FR-9 — Activation Plan Output**
The system must produce channel- and audience-specific activation recommendations.

**FR-10 — Creative Ops Handoff**
The system must hand approved briefs into downstream creative operations, including W9-style asset/variant workflows.

**FR-11 — CRM / Project Handoff**
The system must create structured outputs that can map into CRM/project records for follow-through.

### 10.4 Learning Loop

**FR-12 — Post-Campaign Review**
The system must ingest campaign/reporting summaries and produce:

* what worked
* what failed
* what to repeat
* what to test next

**FR-13 — Workspace Memory**
The system must remember:

* approved claims
* rejected ideas
* client tone
* market assumptions
* prior winning creative patterns

### 10.5 Collaboration

**FR-14 — Team Workspaces**
The system must support team spaces with permissions, shared chats, reusable assets, and saved outputs.

**FR-15 — Approval States**
The system must support Draft → Review → Approved → Activated states for key outputs.

---

## 11. Non-Functional Requirements

**NFR-1 — Citation Integrity**
Every externally grounded answer must include source attribution.

**NFR-2 — Privacy**
Prompts and workspace context must not be used for third-party model training.

**NFR-3 — Response Latency**
Core retrieval workflows should feel materially faster than manual multi-source research.

**NFR-4 — Auditability**
Approved outputs and the source evidence behind them must be recoverable.

**NFR-5 — Geography-Aware Compliance**
Workspace storage, connectors, and exports must support regional privacy and data handling requirements.

**NFR-6 — Structured Output Reliability**
Briefs, evidence packs, and plans must be generated in deterministic schema-backed formats, not just prose.

---

## 12. v1 Scope

### Included

* trusted-source retrieval
* PH-local signal layer
* structured briefs
* evidence packs
* multilingual support
* workspace memory
* execution handoff to downstream systems
* post-campaign review summaries

### Deferred

* native media buying
* full DAM
* full CDP
* autonomous budget allocation
* fully automated creative generation suite
* deep enterprise workflow builder

---

## 13. User Stories

1. As a planner, I want to ask for the strongest strategic angles in a category and get cited evidence plus local market nuance.
2. As an account lead, I want to turn that answer into a client-ready evidence deck quickly.
3. As a strategist, I want the system to adapt the recommendation for PH consumers, creators, and channels.
4. As a creative lead, I want an approved brief handed to a creative ops system, not trapped in chat.
5. As a marketing lead, I want campaign outcomes summarized into reusable strategic learning.
6. As a team, we want shared memory so the system gets smarter about our clients over time.

---

## 14. Success Metrics

### Adoption

* weekly active teams
* repeat workspace usage
* number of briefs/evidence packs generated

### Efficiency

* time from question to first credible brief
* time from brief to approved plan
* reduction in manual source-gathering time

### Quality

* user-rated usefulness
* citation trust score
* approval rate of generated briefs/evidence packs

### Commercial

* paid workspace conversion
* team expansion rate
* retention by agency/brand cohort

### Strategic

* percentage of outputs reused in client work
* percentage of outputs that reach execution handoff
* measurable improvement in campaign-planning cycle time

---

## 15. Packaging and Pricing Hypothesis

LIONS’ current public pricing is:

* Single User: **$30/month** or **$300/year**
* Teams: **$300/user annually**
  with usage caps layered on top.

Pulser should not compete on “cheaper chat.”
It should package as:

1. **Solo Strategy** — capped
2. **Team Strategy OS** — shared memory + collaboration
3. **Strategy + Action** — includes activation and W9 handoff
4. **Enterprise Market Intelligence** — local signal packs, custom workspaces, premium reporting

---

## 16. Rollout Strategy

### Phase 1

* trusted retrieval
* PH market signal layer
* brief generator
* evidence pack generator
* team workspace
* multilingual support

### Phase 2

* execution handoff
* post-campaign reviews
* creator/channel recommendations
* stronger memory and reusable templates

### Phase 3

* deeper audience intelligence
* concept testing
* predictive scoring
* advanced integrations

---

## 17. Risks

1. premium content access and licensing complexity
2. overpromising local coverage before ingest quality is real
3. becoming “another chat tool” without strong structured outputs
4. execution handoff complexity across multiple downstream systems
5. users preferring raw search if structured outputs are weak

---

## 18. Open Questions

1. Which premium source mix is available at launch?
2. What exact PH market datasets are in scope for v1?
3. Which downstream handoffs are first-class at launch?
4. How much of W9 execution should be productized into the same workspace?
5. Should activation export start with Microsoft Advertising, Meta, or reporting-only workflows?

---

## 19. Final Product Statement

Pulser Creative Strategy OS is a trusted, multilingual, market-aware strategy-to-execution assistant for agencies and brand teams. It combines premium research, local market signals, workspace memory, structured strategic outputs, and execution handoff so teams can move from evidence to action faster than research-only assistants.
