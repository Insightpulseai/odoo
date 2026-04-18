# Advertising Agent Skill Map

> Recursive capability model derived from Microsoft Advertising Learning Lab catalog.
> Source taxonomy only — courses and certifications are NOT deployable agent skills.
> Each catalog item is decomposed: catalog → competency → task primitive → skill contract → agent bundle → orchestration.

---

## 1. Search

### Human Competency
Search advertising strategy, keyword management, ad copy creation, bid optimization, and campaign performance analysis.

### Task Primitives

| # | Primitive | Input | Output |
|---|----------|-------|--------|
| 1 | Keyword clustering | Raw keyword list + business goal | Grouped keywords by intent + ad group taxonomy |
| 2 | Negative keyword mining | Search query report | Negative keyword list + savings estimate |
| 3 | Match-type policy suggestion | Keyword list + budget | Match type recommendations per keyword |
| 4 | Ad copy drafting | Product/service description + keywords | 3-5 ad variants (headlines + descriptions) |
| 5 | Ad group structuring | Clustered keywords + landing pages | Ad group hierarchy + naming convention |
| 6 | Search query audit | Query report + conversion data | Wasted spend report + optimization actions |
| 7 | Bid adjustment suggestions | Performance data + goals (CPA/ROAS) | Bid modifiers by device/location/schedule |
| 8 | Landing page alignment check | Ad copy + landing page URL | Relevance score + mismatch flags |
| 9 | Campaign hygiene audit | Full campaign export | Issues list (duplicates, conflicts, orphans) |
| 10 | Performance anomaly detection | Time-series metrics | Alerts for CTR/CPC/conversion anomalies |

### Skill Contracts

**search-keyword-cluster**
- Trigger: New campaign or keyword expansion request
- Inputs: keyword list, business goal, market/language, exclusions
- Procedure: normalize → group by intent → separate branded/non-branded → identify negatives → propose ad-group taxonomy
- Guardrails: do not invent business offerings, flag ambiguous terms, no auto-finalized bids
- Output: grouped keywords, negatives, naming proposal, risk notes
- Escalation: >20% ambiguous terms → human review

**search-query-audit**
- Trigger: Weekly or on-demand query report review
- Inputs: search query report, conversion data, budget
- Procedure: identify wasted spend → flag irrelevant queries → recommend negatives → calculate savings
- Guardrails: do not auto-add negatives, flag branded queries for human decision
- Output: wasted spend report, negative recommendations, projected savings
- Escalation: >15% wasted spend → alert account manager

**search-ad-copy-draft**
- Trigger: New ad group or refresh request
- Inputs: product description, keywords, brand guidelines, character limits
- Procedure: generate 3-5 headline variants → generate descriptions → check policy compliance → score relevance
- Guardrails: do not make claims without source, follow brand voice, respect character limits
- Output: ad variants with relevance scores
- Escalation: regulated industry (pharma, finance) → mandatory human review

**search-campaign-hygiene**
- Trigger: Monthly or pre-launch audit
- Inputs: full campaign export (keywords, ads, settings)
- Procedure: check duplicates → find conflicting negatives → orphan ads → budget distribution → URL validation
- Guardrails: do not modify campaigns directly, report-only
- Output: issues list with severity, recommended fixes
- Escalation: critical issues (broken URLs, budget errors) → immediate alert

**search-performance-anomaly**
- Trigger: Daily automated check
- Inputs: time-series metrics (CTR, CPC, conversions, impressions)
- Procedure: detect statistical anomalies → compare to baseline → classify severity → identify likely cause
- Guardrails: do not auto-pause campaigns, alert only
- Output: anomaly report with severity, likely cause, suggested action
- Escalation: severe anomaly (>50% drop) → immediate alert to account manager

### Specialist Agent: Search Operations Agent

Bundle: `search-keyword-cluster` + `search-query-audit` + `search-ad-copy-draft` + `search-campaign-hygiene` + `search-performance-anomaly`

Eval criteria:
- Keyword clustering accuracy: >90% agreement with human expert
- Negative keyword precision: <5% false negatives (valid keywords incorrectly flagged)
- Ad copy relevance score: >80% by LLM-as-judge
- Hygiene audit completeness: catches >95% of known issue types
- Anomaly detection recall: >90% of real anomalies flagged

---

## 2. Retail

### Human Competency
Product feed management, retail media strategy, catalog-driven advertising, shopping campaigns, and merchant center operations.

### Task Primitives

| # | Primitive | Input | Output |
|---|----------|-------|--------|
| 1 | Feed completeness validation | Product feed CSV/XML | Completeness score + missing field report |
| 2 | Taxonomy normalization | Product categories + platform taxonomy | Mapped categories + unmapped items |
| 3 | Product grouping | Product catalog + performance data | Product group hierarchy for campaigns |
| 4 | Promo/calendar mapping | Promotional calendar + product catalog | Campaign schedule + budget allocation |
| 5 | Stock-aware ad suppression | Inventory data + active campaigns | Out-of-stock suppression list |
| 6 | Retail audience segmentation | Customer data + purchase history | Audience segments for targeting |
| 7 | Budget split by product class | Performance data + business priorities | Budget allocation recommendation |
| 8 | Competitive pricing analysis | Product prices + competitor data | Price positioning report |

### Skill Contracts

**retail-feed-validation**
- Trigger: Feed upload or scheduled check
- Inputs: product feed file, platform requirements
- Procedure: validate required fields → check image quality indicators → verify pricing → flag policy violations
- Guardrails: do not modify feed directly, report-only
- Output: completeness score, field-level issues, rejection risk assessment
- Escalation: >10% rejection risk → alert merchandising team

**retail-taxonomy-mapping**
- Trigger: New product catalog or platform taxonomy update
- Inputs: product categories, target platform taxonomy
- Procedure: auto-map by semantic similarity → flag ambiguous mappings → suggest best-fit categories
- Guardrails: do not auto-assign high-value categories, flag for human review
- Output: mapped taxonomy, confidence scores, unmapped items
- Escalation: >15% unmapped → human categorization needed

**retail-stock-suppression**
- Trigger: Inventory update or daily check
- Inputs: inventory levels, active campaigns, product IDs
- Procedure: identify out-of-stock items → match to active campaigns → generate suppression list → estimate budget recovery
- Guardrails: do not pause campaigns without approval, alert only
- Output: suppression list, affected campaigns, estimated budget savings
- Escalation: >20% of catalog out-of-stock → strategic review

### Specialist Agent: Retail Media Agent

Bundle: `retail-feed-validation` + `retail-taxonomy-mapping` + `retail-stock-suppression` + product-grouping + budget-split + audience-segmentation

Eval criteria:
- Feed validation accuracy: >98% issue detection rate
- Taxonomy mapping precision: >85% correct auto-mappings
- Stock suppression timeliness: within 1 hour of inventory update
- Budget allocation: within 10% of expert recommendation

---

## 3. Display & Video

### Human Competency
Audience-driven media planning, creative strategy, video advertising, connected TV, and upper-funnel measurement.

### Task Primitives

| # | Primitive | Input | Output |
|---|----------|-------|--------|
| 1 | Audience/message matrix | Campaign brief + audience data | Audience × message grid |
| 2 | Placement/channel recommendation | Budget + goals + audience | Channel mix recommendation |
| 3 | Creative variant planning | Brand assets + message strategy | Creative brief with variant spec |
| 4 | Video brief summarization | Video assets + campaign goals | Structured brief for production |
| 5 | Upper-funnel KPI framing | Campaign goals | KPI framework (awareness, consideration, intent) |
| 6 | Frequency capping strategy | Audience size + budget + duration | Frequency cap recommendations |
| 7 | CTV audience sizing | Target demographics + market data | Estimated reach and frequency |

### Skill Contracts

**display-audience-matrix**
- Trigger: Campaign planning phase
- Inputs: campaign brief, audience segments, message themes
- Procedure: cross audience segments with message themes → identify gaps → prioritize by reach × relevance → suggest creative formats per cell
- Guardrails: do not finalize targeting without media planner review
- Output: audience × message matrix with format recommendations
- Escalation: >5 audience segments → recommend prioritization workshop

**display-channel-mix**
- Trigger: Budget allocation phase
- Inputs: budget, campaign goals (awareness/consideration/conversion), audience profile
- Procedure: recommend channel split → estimate reach per channel → project cost efficiency → flag conflicts
- Guardrails: do not commit budget, recommendation only
- Output: channel mix recommendation with reach/cost projections
- Escalation: budget <$10K → simplified plan, >$100K → detailed multi-channel plan

**display-video-brief**
- Trigger: Video production planning
- Inputs: campaign goals, brand guidelines, target audience, available assets
- Procedure: structure brief → define key messages → specify lengths/formats → CTA recommendations
- Guardrails: follow brand guidelines, do not generate video content
- Output: structured video brief document
- Escalation: regulated industry → legal review of claims

### Specialist Agent: Display & Video Planning Agent

Bundle: `display-audience-matrix` + `display-channel-mix` + `display-video-brief` + creative-variant-planning + kpi-framing + frequency-strategy

Eval criteria:
- Channel mix alignment: >80% agreement with senior media planner
- Audience matrix completeness: covers all target segments
- Brief quality: all required fields populated, brand-compliant

---

## 4. Programmatic

### Human Competency
Automated media buying, audience cohort design, supply path optimization, pacing management, and cross-channel planning.

### Task Primitives

| # | Primitive | Input | Output |
|---|----------|-------|--------|
| 1 | Buying strategy recommendation | Campaign goals + budget + audience | Strategy document (approach, tactics, controls) |
| 2 | Audience cohort design | First/third-party data + goals | Audience cohort definitions + sizing |
| 3 | Pacing and budget checks | Campaign settings + spend data | Pacing report + over/under-spend alerts |
| 4 | Supply path summary | Available inventory + SSP data | Recommended supply paths + quality notes |
| 5 | Cross-channel overlap review | Multi-channel campaign data | Overlap report + deduplication recommendations |
| 6 | Deal/PMP evaluation | Available deals + campaign goals | Deal recommendations with CPM/quality trade-offs |

### Skill Contracts

**programmatic-buying-strategy**
- Trigger: Campaign kick-off
- Inputs: campaign goals, budget, audience profile, competitive context
- Procedure: recommend approach (open exchange / PMP / PG) → define tactics → set control parameters → project outcomes
- Guardrails: do not commit spend, flag unknown inventory sources
- Output: strategy document with approach, tactics, KPIs, controls
- Escalation: budget >$50K → senior strategist review

**programmatic-pacing-check**
- Trigger: Daily automated check
- Inputs: campaign settings, daily spend data, total budget, end date
- Procedure: calculate current pacing → project end-of-flight spend → compare to target → flag deviations
- Guardrails: do not auto-adjust budgets, alert only
- Output: pacing report, deviation flags, adjustment recommendations
- Escalation: >20% off-pace → immediate alert

**programmatic-overlap-review**
- Trigger: Multi-channel campaign active
- Inputs: impression/conversion data across channels
- Procedure: identify user overlap between channels → estimate incremental reach → recommend deduplication
- Guardrails: do not modify campaigns, report-only
- Output: overlap matrix, incremental reach estimate, dedup recommendations
- Escalation: >40% overlap → channel consolidation review

### Specialist Agent: Programmatic Planner Agent

Bundle: `programmatic-buying-strategy` + `programmatic-pacing-check` + `programmatic-overlap-review` + audience-cohort-design + supply-path-summary + deal-evaluation

Eval criteria:
- Strategy alignment: >85% agreement with programmatic lead
- Pacing accuracy: detects deviations within 1 business day
- Overlap detection: >90% recall on cross-channel duplicates

---

## 5. Generative AI & Automation

### Human Competency
AI prompt design, workflow automation, SOP generation, approval flow design, and human-in-the-loop review patterns.

### Task Primitives

| # | Primitive | Input | Output |
|---|----------|-------|--------|
| 1 | Prompt template generation | Task description + constraints | Reusable prompt template |
| 2 | SOP codification | Process description + roles | Structured SOP document |
| 3 | Workflow trigger design | Business event + desired action | Trigger-action specification |
| 4 | Approval memo drafting | Decision context + options | Structured approval memo |
| 5 | Exception routing logic | Business rules + edge cases | Exception handling flowchart |
| 6 | Campaign brief expansion | Short brief + context | Full campaign brief document |
| 7 | Compliance/style checking | Content + brand guidelines | Compliance report + fixes |
| 8 | CTA testing recommendations | Current CTAs + performance data | A/B test plan with variants |

### Skill Contracts

**automation-prompt-template**
- Trigger: New recurring task identified
- Inputs: task description, input variables, output format, constraints
- Procedure: analyze task → identify variables → construct template → add guardrails → test with examples
- Guardrails: templates must include safety instructions, no open-ended generation without constraints
- Output: prompt template with variable slots, examples, and guardrails
- Escalation: high-risk tasks (financial, legal) → human template review

**automation-sop-codify**
- Trigger: Process documentation request
- Inputs: process description, roles involved, tools used, exceptions
- Procedure: structure into steps → assign roles → define inputs/outputs per step → add decision points → include escalation paths
- Guardrails: do not invent process steps, document as-is then suggest improvements separately
- Output: structured SOP with roles, steps, decision trees, escalation paths
- Escalation: cross-department SOPs → stakeholder review required

**automation-workflow-trigger**
- Trigger: Automation design phase
- Inputs: business event, desired action, conditions, frequency
- Procedure: define trigger conditions → specify action sequence → add error handling → define success criteria
- Guardrails: all triggers must have a human-reviewable output before destructive actions
- Output: trigger-action specification with error handling
- Escalation: triggers affecting financial transactions → mandatory approval gate

### Specialist Agent: Creative Automation Agent

Bundle: `automation-prompt-template` + `automation-sop-codify` + `automation-workflow-trigger` + brief-expansion + compliance-checking + cta-testing

Eval criteria:
- Prompt template reusability: >80% adoption rate by team
- SOP accuracy: >95% step completeness vs actual process
- Workflow trigger reliability: <2% false triggers in testing

---

## 6. Copilot

### Human Competency
AI assistant usage patterns, intent routing, contextual suggestions, knowledge-grounded responses, and human escalation policies.

### Task Primitives

| # | Primitive | Input | Output |
|---|----------|-------|--------|
| 1 | User intent routing | User query + context | Classified intent + target skill |
| 2 | Contextual suggestion generation | Current task state + history | Ranked next-action suggestions |
| 3 | Action recommendation | User goal + available actions | Recommended action with rationale |
| 4 | Knowledge-grounded response | Query + knowledge base | Grounded answer with citations |
| 5 | Escalation-to-human policy | Confidence score + risk level | Escalate or auto-respond decision |
| 6 | Session summarization | Conversation history | Structured summary + action items |

### Skill Contracts

**copilot-intent-router**
- Trigger: Every user message
- Inputs: user query, conversation context, available skills
- Procedure: classify intent → match to skill → check confidence → route or escalate
- Guardrails: never guess on ambiguous intent — ask clarifying question
- Output: classified intent, target skill, confidence score
- Escalation: confidence <0.7 → ask clarifying question; <0.4 → hand to human

**copilot-knowledge-response**
- Trigger: Informational query classified
- Inputs: query, knowledge base index, conversation context
- Procedure: retrieve relevant documents → generate grounded answer → attach citations → check for hallucination markers
- Guardrails: never answer without source, flag when no relevant source found
- Output: grounded answer with citations, confidence score
- Escalation: no relevant source → "I don't have information on that, let me connect you with a specialist"

**copilot-escalation-policy**
- Trigger: Every agent response before delivery
- Inputs: response, confidence score, risk classification, action type
- Procedure: evaluate risk level → check if action is destructive/financial → apply confidence threshold → decide auto-respond or escalate
- Guardrails: always escalate financial actions, never auto-execute deletions
- Output: escalation decision (auto-respond / review required / human handoff)
- Escalation: any action affecting money, data deletion, or external communication → human approval

### Specialist Agent: Copilot Enablement Agent

Bundle: `copilot-intent-router` + `copilot-knowledge-response` + `copilot-escalation-policy` + suggestion-generation + session-summarization

Eval criteria:
- Intent classification accuracy: >90%
- Knowledge grounding: >95% responses with valid citations
- Escalation precision: <5% unnecessary escalations, 0% missed critical escalations
- User satisfaction: >4.0/5.0 on post-session survey

---

## Certification → Evaluation Benchmark Mapping

Certifications are NOT runtime modules. They are evaluation benchmarks for validating agent capability.

| Certification | Agent Benchmark | Eval Method |
|--------------|----------------|-------------|
| **Search Certification** | Search Operations Agent answers match certified-level knowledge | Benchmark quiz: agent scores >80% on certification-equivalent questions |
| **Retail Certification** | Retail Media Agent produces feed/taxonomy/strategy outputs at certified quality | Expert review: outputs compared to certified practitioner baseline |
| **Display & Video Certification** | Display & Video Agent produces plans at certified planner quality | Blind comparison: agent plan vs certified planner plan, scored by senior strategist |

### How to Use Certifications for Agent Eval

```
1. Extract certification exam questions (or equivalent practice questions)
2. Run agent against questions as a benchmark
3. Score: >80% = agent meets certified-level knowledge
4. Track over time: does agent knowledge degrade with model updates?
5. Re-benchmark after each model version change
```

Certifications validate the agent knows what a certified human knows. They do NOT mean the agent can execute campaigns autonomously.

---

## Orchestration Workflow

```
Campaign brief received
  │
  ├── Copilot Enablement Agent
  │   └── Classifies intent, routes to specialist
  │
  ├── Creative Automation Agent
  │   └── Expands brief, drafts copy, generates variants
  │
  ├── Search Operations Agent
  │   └── Builds keyword plan, structures ad groups
  │
  ├── Retail Media Agent
  │   └── Validates feed, maps taxonomy, checks stock
  │
  ├── Display & Video Planning Agent
  │   └── Plans audience × message matrix, recommends channels
  │
  ├── Programmatic Planner Agent
  │   └── Designs buying strategy, sets pacing controls
  │
  └── All outputs → Human review gate
      └── Account Director approves → Campaign launches
```

---

## Verification Checklist

- [x] Learning paths are NOT treated as skills directly
- [x] Each catalog item maps to task primitives (5-10 per domain)
- [x] Each task primitive has input/output boundaries
- [x] Agents are bundles of skills, not vague personas
- [x] Certifications used as eval benchmarks, not runtime modules
- [x] All skill contracts include guardrails and escalation
- [x] Orchestration workflow shows human-in-the-loop gate

---

*Source taxonomy: Microsoft Advertising Learning Lab catalog*
*Architecture: recursive capability model — catalog → competency → primitive → skill → agent → orchestration*
*Last updated: 2026-04-18*
