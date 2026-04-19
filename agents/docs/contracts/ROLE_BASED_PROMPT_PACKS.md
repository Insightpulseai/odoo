# Role-Based Prompt Packs — Contract

Canonical source: [`agents/registries/skills/canonical/prompt-packs.yaml`](../../registries/skills/canonical/prompt-packs.yaml)

Authority: [`ssot/ai/external-reference-authorities.yaml`](../../../ssot/ai/external-reference-authorities.yaml)

## Purpose

Define how role-based prompt assets (OpenAI Academy Prompt Packs and equivalents) enter the IPAI repo. Prompt packs are operator enablement assets, not agent runtime definitions.

## Rules

- Every prompt from an external pack becomes a **skill** under `agents/skills/<pack>/<skill_id>/`.
- Each skill has a `skill.manifest.yaml` with input schema, output schema, evaluators, safe-outputs policy, and approval band.
- No freeform prompt text outside a skill wrapper.
- No prompts that access secrets or Key Vault directly.
- Model preference is resolved through the provider adapter, never inline.

## Role mapping

| Role | Target pack | Example skills |
|---|---|---|
| Sales | `agents/shared/sales` | pitch_draft, discovery_question_generation, objection_handling |
| Customer Success | `agents/shared/support` | ticket_triage, qbr_summary_draft, renewal_risk_briefing |
| Product | `agents/shared/product` | prd_section_draft, user_story_expansion, release_note_draft |
| Engineers | `agents/shared/engineering` | code_review_summary, test_case_draft, incident_timeline_draft |
| Managers / Executives | `agents/shared/strategy` | status_report_draft, okr_review_summary, exec_briefing |
| Finance | `agents/domain/finance` | variance_commentary, forecast_assumption_draft, reconciliation_summary |
| Marketing | `agents/shared/marketing` | campaign_copy_draft, landing_page_outline, seo_meta_draft |
| HR | `agents/shared/people_ops` (optional) | jd_draft, interview_question_set |
| IT | `agents/shared/it_ops` (optional) | runbook_draft, sop_compile |

## Required skill manifest fields

- `skill_id`
- `owner_pack`
- `input_schema` (JSON schema)
- `output_schema` (JSON schema)
- `evaluators` (required if mutating)
- `safe_outputs_policy` (reference to middleware stage set)
- `model_preference` (resolved via provider adapter)
- `approval_band`: `read_only` | `assisted` | `mutating`

## Example

```yaml
skill_id: finance.variance_commentary
owner_pack: agents/domain/finance
approval_band: assisted
input_schema:
  period: string
  dimensions: array
  thresholds: object
output_schema:
  commentary: string
  variance_table: array
evaluators:
  - evals/finance/variance_commentary_rubric.yaml
model_preference: foundry_default
```

> [!IMPORTANT]
> Prompt pack ingestion is additive. Raw pack text must not replace the wrapper contract, and raw prompts must never bypass Safe Outputs middleware.

## Non-goals

- Not importing raw prompt text into the repo.
- Not creating runtime agents for every role automatically.
- Not using prompt packs as evaluator substitutes.
- Not blending sales/marketing personas with finance/IT skills.

## Related

- [Cookbook pattern adoption rules](COOKBOOK_PATTERN_ADOPTION_RULES.md)
- [External reference authorities](../../../ssot/ai/external-reference-authorities.yaml)
- [Pulser pack matrix](../../../platform/ssot/agents/pulser-pack-matrix.yaml)
