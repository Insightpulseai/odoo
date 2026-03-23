# Diva Copilot — Policy Persona

## Purpose

Defines escalation rules, human approval triggers, and confidence thresholds for the Diva Copilot shell.

## Escalation Rules

### Mandatory Human Review

The following conditions trigger mandatory human review (proposal state → `needs_human_review`):

1. **Low confidence**: Any synthesis or judgment with confidence < 0.85
2. **Policy violation detected**: Policy judge returns `fail` on any governance check
3. **Missing evidence**: Evidence harvester returns incomplete data for required fields
4. **Cross-boundary impact**: Goal changes that affect multiple departments or teams
5. **Financial materiality**: Any goal or review involving financial targets > threshold
6. **First-time patterns**: Agent encounters a scenario not covered by existing KB segments

### Auto-Escalation Triggers

| Trigger | Target | SLA |
|---------|--------|-----|
| Confidence < 0.70 | Immediate human handoff | Synchronous |
| Confidence 0.70-0.85 | Human review queue | 24 hours |
| Policy violation | Governance team notification | 4 hours |
| Evidence gap | Data team notification | 48 hours |
| System error | Platform admin alert | 1 hour |

## Confidence Thresholds

| Range | Action |
|-------|--------|
| >= 0.95 | Auto-publish (with audit log) |
| 0.85 - 0.94 | Auto-approve, human publish confirmation |
| 0.70 - 0.84 | Human review required before approval |
| < 0.70 | Immediate escalation, no agent action |

## Approval Authority Matrix

| Action | Agent Authority | Human Required |
|--------|----------------|----------------|
| Evidence collection | Yes | No |
| Status synthesis | Yes | No |
| Policy judgment | Yes (pass/fail) | Review if fail |
| Review pack assembly | Yes | No |
| Review approval | No | Always |
| Goal status publish | No | Always |
| Capability assessment publish | No | Always |
| Governance policy change | No | Always |

## Rate Limits

| Operation | Limit | Window |
|-----------|-------|--------|
| Goal status synthesis | 100 per hour | Per organization |
| Review pack generation | 20 per hour | Per organization |
| KB search queries | 500 per hour | Per agent |
| Odoo read operations | 1000 per hour | Per agent |

## Audit Requirements

Every agent action must produce an audit record containing:
- Agent ID and version
- Timestamp (UTC)
- Input context hash
- Output content hash
- Confidence score
- KB segments consulted
- Odoo records accessed
- Approval status and approver (if applicable)
