# M365 Declarative Agent Manifest — SSOT Workflow

**Status**: Planned
**Integration SSOT**: `ssot/integrations/m365_copilot.yaml`
**Agent SSOT**: `ssot/m365/agents/insightpulseai_ops_advisor/`
**Reviewed**: 2026-03-01

---

## What Is a Declarative Agent Manifest?

A declarative agent manifest is a JSON file that describes an M365 Copilot extension.
Microsoft uses this file to:

1. Register the agent in Copilot Studio / Teams App Catalog.
2. Understand what the agent can do (capabilities and sample prompts for routing).
3. Know which actions the agent exposes and what their parameters are.

The manifest format is defined by Microsoft's app manifest schema for M365 Copilot
declarative agents. IPAI uses version `1.5` of the Copilot extensions schema.

For the `insightpulseai_ops_advisor` agent, the manifest lives at:

```
dist/m365/agents/insightpulseai_ops_advisor/manifest.json
```

**This file is generated. Never edit it directly.** See the SSOT workflow below.

---

## SSOT to Generated Manifest Workflow

```
1. Edit SSOT YAML (the authoritative sources)
   ssot/m365/agents/insightpulseai_ops_advisor/actions.yaml
   ssot/m365/agents/insightpulseai_ops_advisor/capabilities.yaml

2. Run the generator script
   python scripts/m365/generate_actions_manifest.py

3. Review the diff in dist/m365/agents/insightpulseai_ops_advisor/manifest.json

4. Commit both the YAML changes and the updated manifest.json

5. CI drift check (scripts/ci/check_m365_manifest_drift.py) validates they match.
```

The CI workflow runs `check_m365_manifest_drift.py` on every PR. If the committed
`manifest.json` does not match what the generator would produce from the current YAML,
the build fails with `FAIL [drift]`.

---

## How to Run the Generator Script

**Prerequisites**: Python 3.12+, `pyyaml` installed (`pip install pyyaml`).

```
# Generate (or regenerate) the manifest
python scripts/m365/generate_actions_manifest.py

# Validate only — check whether manifest.json is up to date, no file writes
python scripts/m365/generate_actions_manifest.py --validate-only

# Use a non-default repo root
python scripts/m365/generate_actions_manifest.py --repo-root /path/to/odoo
```

The script reads:
- `ssot/m365/agents/insightpulseai_ops_advisor/actions.yaml`
- `ssot/m365/agents/insightpulseai_ops_advisor/capabilities.yaml`

And writes:
- `dist/m365/agents/insightpulseai_ops_advisor/manifest.json`

The `dist/` directory is created automatically if it does not exist.

---

## Manifest Structure (Schema Summary)

The generated `manifest.json` follows Microsoft's declarative agent schema. Key fields:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/copilot/declarative-agent/v1.5/schema.json",
  "manifestVersion": "1.5",
  "version": "1.0.0",
  "id": "insightpulseai_ops_advisor",
  "packageName": "com.insightpulseai.copilot.ops-advisor",
  "developer": {
    "name": "InsightPulse AI",
    "websiteUrl": "https://insightpulseai.com",
    "privacyUrl": "https://insightpulseai.com/privacy",
    "termsOfUseUrl": "https://insightpulseai.com/terms"
  },
  "name": {
    "short": "IPAI Ops Advisor",
    "full": "InsightPulse AI — Ops Advisor"
  },
  "description": {
    "short": "Access IPAI operational data from M365 Copilot",
    "full": "..."
  },
  "actions": [
    {
      "id": "query_advisor_findings",
      "type": "query",
      "displayName": "Get Advisor findings",
      "description": "...",
      "parameters": { ... }
    }
    // ... additional actions from actions.yaml
  ],
  "capabilities": [
    {
      "name": "advisor_findings_query",
      "description": "...",
      "samplePrompts": [ ... ]
    }
    // ... additional capabilities from capabilities.yaml
  ]
}
```

### Field Sources

| Manifest field | Source |
|----------------|--------|
| `actions[]` | `ssot/m365/agents/insightpulseai_ops_advisor/actions.yaml` — `actions` list |
| `capabilities[]` | `ssot/m365/agents/insightpulseai_ops_advisor/capabilities.yaml` — `capabilities` list |
| `id`, `packageName` | Hardcoded in generator (stable identifiers) |
| `version` | Hardcoded in generator (`1.0.0`); bump manually for breaking changes |
| `developer.*` | Hardcoded in generator (company-level constants) |

---

## Drift Check CI Workflow

**Script**: `scripts/ci/check_m365_manifest_drift.py`

The drift check runs in CI (GitHub Actions) on every PR that touches:
- `ssot/m365/agents/insightpulseai_ops_advisor/`
- `dist/m365/agents/insightpulseai_ops_advisor/`
- `scripts/m365/generate_actions_manifest.py`

**What it checks**:
1. Runs the generator with `--validate-only`.
2. Compares the freshly generated manifest against the committed `manifest.json`.
3. Also checks that all action IDs in the manifest are in the `allowed_action_ids`
   list from `actions.yaml`.

**Exit codes**:
- `0` — manifest is current, all action IDs are allowlisted.
- `1` — drift detected or unknown action ID found.

To add the drift check to an existing workflow:

```yaml
- name: Check M365 manifest drift
  run: python scripts/ci/check_m365_manifest_drift.py --repo-root .
```

---

## How to Add a New Action

1. Edit `ssot/m365/agents/insightpulseai_ops_advisor/actions.yaml`:
   - Add a new entry to the `actions` list with a unique `id`.
   - Add the `id` to the `allowed_action_ids` list at the bottom.

2. If the action corresponds to a new user-visible capability, also edit
   `ssot/m365/agents/insightpulseai_ops_advisor/capabilities.yaml`.

3. Run the generator:
   ```
   python scripts/m365/generate_actions_manifest.py
   ```

4. Review `dist/m365/agents/insightpulseai_ops_advisor/manifest.json` for correctness.

5. Implement the new operation in `supabase/functions/m365-copilot-broker/index.ts`.

6. Open a PR with all three changed files: YAML sources, generated manifest, and
   Edge Function changes.

---

## Troubleshooting

### Generator fails with "actions.yaml not found"

The generator expects to be run from the repo root, or with `--repo-root` pointing to
the repo root. Check that `ssot/m365/agents/insightpulseai_ops_advisor/actions.yaml`
exists relative to the path you are running from.

### Drift check fails in CI but manifest looks correct locally

The committed `manifest.json` was generated from a different version of the YAML or
generator script than what is in the current branch. Re-run the generator locally,
commit the updated `manifest.json`, and push again.

### manifest.json contains an action ID not in allowed_action_ids

Either:
- The generator has a bug (action was added to `actions.yaml` but not to
  `allowed_action_ids`). Fix the YAML — both lists must be consistent.
- The manifest was hand-edited (forbidden). Regenerate from YAML.

### Microsoft rejects the manifest on upload

Common causes:
- `$schema` URL is wrong or inaccessible. Verify against current Microsoft docs.
- Required fields missing (`developer.privacyUrl`, `developer.termsOfUseUrl`).
- Action parameter types use non-standard values (only `string`, `integer`, `boolean`
  are supported in declarative agent action parameters).
- `manifestVersion` is not supported by the target tenant's Copilot version.

Check the Microsoft Teams App Validator output for specific error codes.

---

## References

- M365 Copilot declarative agent manifest schema:
  `https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/declarative-agent-manifest`
- Teams App Validator (manifest validation):
  `https://dev.teams.microsoft.com/appvalidation`
- Copilot Studio registration guide:
  `https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/publish`
- IPAI integration overview:
  `docs/architecture/M365_COPILOT_INTEGRATION.md`
- Generator script:
  `scripts/m365/generate_actions_manifest.py`
- Drift check script:
  `scripts/ci/check_m365_manifest_drift.py`
