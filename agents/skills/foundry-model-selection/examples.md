# Examples — foundry-model-selection

## Example 1: Customer support agent — low latency, moderate quality

**Input**: Agent handles customer support chat. Latency SLA: p95 < 2s. Budget: $500/mo. Safety: high (customer-facing).

**Output**:
- Workload: customer support chat, latency-sensitive, customer-facing safety requirements
- Candidate 1: GPT-4o-mini — quality: good for support tasks, safety: high, cost: low ($0.15/1M input), throughput: fast (p95 ~800ms) — RECOMMENDED
- Candidate 2: GPT-4o — quality: excellent, safety: high, cost: moderate ($2.50/1M input), throughput: moderate (p95 ~1.5s) — CONDITIONAL (over budget at scale)
- Rejected: GPT-4 Turbo — throughput: p95 ~3s exceeds latency SLA
- Rejected: o1-preview — cost prohibitive for chat volume, latency too high
- Safety assessment: both candidates meet content safety threshold
- Cost assessment: GPT-4o-mini stays within $500/mo at projected volume; GPT-4o exceeds at >200k requests/mo

## Example 2: Code generation agent — high quality, cost secondary

**Input**: Agent generates Odoo module code. Latency SLA: p95 < 30s (batch OK). Budget: $2000/mo. Safety: moderate (internal use).

**Output**:
- Workload: code generation, quality-critical, internal use, batch latency acceptable
- Candidate 1: GPT-4o — quality: excellent for code gen, safety: adequate, cost: moderate, throughput: sufficient for batch — RECOMMENDED
- Candidate 2: Claude Sonnet 4 — quality: excellent, safety: high, cost: comparable, throughput: sufficient — RECOMMENDED (alternative)
- Rejected: GPT-4o-mini — quality insufficient for complex code generation tasks
- Rejected: o1 — cost exceeds budget at projected volume
- Safety assessment: internal use reduces safety bar; both candidates meet threshold
- Cost assessment: both within budget at projected 50k requests/mo

## Example 3: Model selection rejected — missing safety evaluation

**Input**: Request to select "fastest model" for a public-facing summarization agent. No safety requirements specified.

**Output**:
- BLOCKED: safety requirements not specified for a public-facing agent
- Missing: content safety threshold, jailbreak resistance requirement, harmful content filtering needs
- Action: define safety requirements before model selection can proceed
- Rationale: safety dimension is mandatory — cannot skip for public-facing workloads
