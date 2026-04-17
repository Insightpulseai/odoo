# Pulser Evals

> Behavior-driven eval harness for Pulser specialist agents on
> `ipai-copilot-resource` Foundry.
> Models: `gpt-4.1` (complex) and `gpt-4.1-mini-20260415` (routine).
> Doctrine: evals before prompts before fine-tuning
> (`ssot/foundry/runtime-contract.yaml §activation.fine_tuning_roadmap` Phase 1).

## One eval file per agent

| Agent | File | Primary model | Status |
|---|---|---|---|
| Pulser Finance | `pulser-finance-evals.md` | gpt-4.1 | Phase 1 baseline |
| Pulser Ops | `pulser-ops-evals.md` | gpt-4.1 | Phase 1 baseline |
| Pulser Research | `pulser-research-evals.md` | gpt-4.1 | Phase 1 baseline |

## Eval execution

Run via Foundry Evaluations (built-in tool on `ipai-copilot-resource`)
OR via `azure-ai-evaluation` SDK.

```python
from azure.ai.evaluation import evaluate
from azure.ai.projects import AIProjectClient
from azure.identity import ManagedIdentityCredential

client = AIProjectClient(
    endpoint="https://ipai-copilot-resource.services.ai.azure.com/api/projects/ipai-copilot",
    credential=ManagedIdentityCredential(client_id="<agent-mi-client-id>"),
)
# point at spec/pulser-evals/<agent>-evals.md test cases
```

## Pass criteria (applies to all agents)

- Blocking: security / doctrine violation in output (e.g., hardcoded secret, non-Azure runtime recommendation, Supabase reference) → 0 tolerance
- Accuracy: domain-specific (per agent file)
- Tool-call correctness: agent calls only tools in its declared set (§3 of `docs/runbooks/foundry-connections-and-tools.md`)
- Citation: when agent claims a fact, it cites source (AI Search result, PG MCP query, or user-provided doc)

## Phase progression

1. **Now:** write eval cases, run against current gpt-4.1 + prompts, establish baseline scores
2. **Ongoing:** iterate prompts in `agents/skills/<domain>/SKILL.md` until score plateaus
3. **~1 month:** if plateau below target, trigger Phase 3 (Supervised FT) per SSOT roadmap

## Re-run policy

- Re-run on every SKILL.md change affecting triggers/tools
- Re-run on every base-model version bump (new `gpt-4.1-YYYY-MM-DD` deployment)
- Log score history to `docs/evidence/eval-runs/<yyyymmdd-hhmm>/`
