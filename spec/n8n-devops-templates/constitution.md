# Constitution — n8n DevOps Templates Integration

Version: 1.0.0 | Status: Active | Last updated: 2026-03-01

## Non-Negotiable Rules

**Rule 1: Every template execution emits ops ledger events.**
All imported n8n templates must write to ops.runs (one row per execution)
and ops.run_events (granular step events). Templates that cannot emit
telemetry are rejected from the catalog.

**Rule 2: Idempotency keys are mandatory and deterministic.**
Every template must declare an idempotency_key_format in its catalog entry.
The key must be deterministic from input parameters (no random UUIDs).
Duplicate executions with the same key must be safe (no-op or update, never duplicate).

**Rule 3: Secrets use credential references, never literals.**
All n8n templates must use `{{ $credentials.<name>.<field> }}` for secrets
and `{{ $env.<VAR_NAME> }}` for environment variables. Literal values in
workflow JSON are rejected at import time. Secret consumers must be
registered in ssot/secrets/registry.yaml.

**Rule 4: External calls are constrained by SSOT allowlists.**
Templates may only call endpoints declared in ssot/integrations/ policies.
No unbounded shell execution, no direct production database writes,
no unregistered external API calls.

**Rule 5: Templates are importable, not bespoke.**
Every template in the catalog must be reproducible from its n8n source
plus SSOT-declared configuration. No manual patching of imported workflows.
Customizations are overlays, not edits.

## Boundaries

- SSOT: ssot/integrations/n8n_devops_templates.yaml (catalog)
- Workflows: automations/n8n/workflows/ (executable JSON)
- Secrets: ssot/secrets/registry.yaml (consumer registration)
- Telemetry: ops.runs + ops.run_events (Supabase)
- Advisor: ops.runs scoring via advisor engine

## Guardrails

- Forbidden: direct_prod_db_write, unbounded_shell_exec, plaintext_secret_in_json
- Allowed triggers: webhook, cron, github, manual
- All templates must pass policy validation before activation
- Advisor can score: automation coverage, failure rate, cost signals, security compliance
