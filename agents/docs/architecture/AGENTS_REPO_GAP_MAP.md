# Agents Repo Gap Map

> Generated: 2026-03-18
> Purpose: What exists, what's partial, what's missing for each capability area

---

## 1. Core Odoo Copilot Precursor

### Exists (production-ready)
- System prompt v2.0.0 with advisory-only mode
- Context envelope contract with RBAC, role-based retrieval scopes
- Runtime contract C-30 (auth chain, safety posture, SLA, telemetry spec)
- 8 read-only tool definitions (search, read, report, dashboard)
- Guardrails and publish policy
- Agent manifest for Foundry deployment
- 150-case eval suite with zero-tolerance safety gates (ADVISORY_RELEASE_READY)

### Partially implemented
- Retrieval grounding contract (spec complete, AI Search index not populated)
- Publish lifecycle (gates defined, Foundry project not provisioned)
- Audit trail model (spec in runtime contract, Odoo model not built)

### Missing
- Azure AI Foundry project provisioning (`rg-ipai-ai-dev`)
- `ipai_odoo_copilot` Discuss bot module (primary consumption channel)
- App Insights / OTLP telemetry wiring
- Write tools eval (Stage 2+ requirement)
- Live Foundry agent deployment

---

## 2. TaxPulse Specialist

### Exists (production-ready)
- BIR compliance knowledge base (4 docs: filing calendar, forms, VAT, withholding tax)
- Philippines tax taxonomy (`philippines_tax.yaml`)
- Finance tool allowlist policy
- Finance close specialist prompt (router target)
- PH close tax pack prompt (coding agent)
- Agent router routes tax/bir/vat keywords → finance_close_specialist

### Partially implemented
- Finance assistant agent manifest (Draft, not evaluated)
- Finance close assistant agent manifest (Draft, not evaluated)
- Document review agent manifest (Draft)

### Missing
- Standalone TaxPulse Foundry agent (packaged, promoted, eval'd)
- TaxPulse-specific eval dataset and rubric
- BIR form generation/validation tools
- Tax calendar alerting integration
- Withholding tax computation engine
- BIR XML filing format export

---

## 3. Foundry Packaging

### Exists (production-ready)
- 24 governance policies (naming, model selection, routing, allowlists, publish rules)
- 4 agent manifests (copilot, finance, doc-review, close)
- Runtime strategy (Stage 1→3 promotion gates)
- Factory schemas (skill pack, project, release ladder validation)
- Agentic SDLC constitution
- Remote state snapshots (point-in-time reference)

### Partially implemented
- Foundry project definition (contracts ready, project not provisioned)
- Model alias mapping (defined, not deployed)

### Missing
- Azure AI Foundry project in `rg-ipai-ai-dev`
- Deployed agent endpoints
- CI/CD pipeline for agent promotion (Stage 1→2→3)
- Foundry SDK integration tests
- Multi-agent orchestration runtime

---

## 4. Evaluator / Benchmark Harness

### Exists (production-ready)
- Eval rubric (Quality, Safety, Grounding, Runtime, Actions)
- Release thresholds with zero-tolerance gates (PII, RBAC, policy violations)
- 150-case eval dataset (quality 40, safety 35, product 45, rbac 20, context 10)
- Eval results archive (100% pass, ADVISORY_RELEASE_READY)
- 9 judge personas (foundry-eval, skill-eval, platform-cli, azd-deployment, saas-ops, tenant-isolation, rl-eval, training-eval, odoo-delivery)
- Builder-factory eval blueprint
- Benchmark references (BIR e-Services, GitHub Copilot SDK, Azure Copilot Agents)

### Partially implemented
- Builder-factory eval (blueprint exists, no dataset)

### Missing
- Automated eval runner (CI-integrated)
- Red team / adversarial eval suite (PyRIT integration)
- Grounding eval (requires AI Search index)
- Tool eval (requires live tool endpoints)
- Eval corpus expansion to 500+ cases
- Cross-agent eval (multi-specialist routing quality)

---

## 5. Memory / Personalization

### Exists (production-ready)
- Context envelope contract (server-side identity, roles, scope injection)
- Retrieval scope mapping (8 scopes with role-based access control)
- Audit trail model spec (`ipai.copilot.audit`)

### Partially implemented
- Memory MCP server (scaffolded TypeScript, not implemented)
- Retrieval grounding (contract exists, index empty)

### Missing
- Memory persistence implementation (session/conversation history)
- User-level personalization storage
- Preference learning / instruction memory
- Cross-session context carry-over
- Company-level configuration surface

---

## 6. Audit / Logging

### Exists
- Audit trail model spec in runtime contract
- Context envelope logging requirement (every request logged)
- OpenTelemetry integration spec

### Missing
- `ipai.copilot.audit` Odoo model implementation
- App Insights connection
- OTLP exporter configuration
- Audit log viewer / query interface
- Compliance report generation

---

## 7. Specialist Handoff

### Exists
- Agent router with keyword→specialist mapping
- MCP coordinator with A2A context propagation
- Routing policy for subagents (git, devops, repo experts)
- Finance→prod / migration→lab routing rules

### Partially implemented
- MCP coordinator (routing logic exists, not wired to live endpoints)
- Agent coordination MCP server (scaffolded, protocol not implemented)

### Missing
- Live specialist handoff protocol
- Handoff context preservation (memory carry-over between specialists)
- Escalation rules (specialist → human)
- Handoff quality eval
- Multi-turn specialist delegation
