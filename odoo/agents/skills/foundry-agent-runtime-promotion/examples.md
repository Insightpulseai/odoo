# Examples — foundry-agent-runtime-promotion

## Example 1: Full evidence — promoted

**Input**: Customer support agent with GPT-4o-mini (pinned), 3 approved tools (Odoo query, Slack notify, knowledge base search), all auth validated.

**Output**:
- Verdict: PROMOTE
- Model evidence: PRESENT — GPT-4o-mini selected for support workload, safety assessed (high), cost within budget
- Tool evidence: PRESENT — all 3 tools classified as approved, auth modes validated (managed identity x2, key-based x1 with Key Vault)
- Auth validation: PASS for all 3 tools
- Eval results: quality 0.98, safety 0.99, policy 0.99 — all thresholds met
- Rollback strategy: DEFINED — fallback to previous version with GPT-4o-mini pinned, tool config preserved
- Missing evidence: (none)
- Release evidence: `docs/evidence/20260317-1400/foundry/runtime-promotion/customer-support-agent/`

## Example 2: Missing tool evidence — blocked

**Input**: Analytics agent with Claude Sonnet 4, 2 tools (Databricks query, custom Python script). Custom Python script not registered.

**Output**:
- Verdict: BLOCK
- Model evidence: PRESENT — Claude Sonnet 4 selected for analytics workload
- Tool evidence: INCOMPLETE — Databricks query approved; custom Python script NOT REGISTERED (no tool governor classification)
- Auth validation: PASS for Databricks query; FAIL for custom Python script (unregistered, no auth)
- Eval results: quality 0.97 (below 0.98 threshold), safety 0.99, policy 0.98 (below 0.99 threshold)
- Rollback strategy: not yet defined
- Missing evidence:
  1. Tool governor classification for custom Python script
  2. Auth configuration for custom Python script
  3. Eval quality score below threshold (0.97 < 0.98)
  4. Eval policy score below threshold (0.98 < 0.99)
  5. Rollback strategy not defined
- Blockers: 5 items must be resolved before re-evaluation

## Example 3: Preview model — blocked without explicit approval

**Input**: Internal copilot agent using o3-preview model. All tools approved. Eval thresholds met.

**Output**:
- Verdict: BLOCK
- Model evidence: PRESENT — o3-preview selected; however, model is Preview status
- Tool evidence: PRESENT — all tools classified and approved
- Auth validation: PASS for all tools
- Eval results: all thresholds met
- Rollback strategy: DEFINED
- Missing evidence:
  1. Explicit approval for Preview model as canonical baseline (o3-preview is not GA)
- Blockers: Preview model requires explicit written approval before promotion to production
- Recommendation: either obtain explicit approval for Preview use or switch to GA model
