# Skills Coverage Runbook

## Purpose

Ensure every Odoo 19 documentation section and external skill pack has a corresponding
skill stub directory in `skills/`. CI fails a PR if any expected stub is missing.

## SSOT file

```
ssot/skills/odoo19_docs_coverage.yaml
```

### Schema

| Key | Purpose |
|-----|---------|
| `odoo_version` | Odoo version this mapping covers |
| `docs.*` | Odoo documentation section URLs |
| `external_skill_packs.*` | External skill pack repository URLs |
| `expected.*` | Skill slug → `skills/<path>` mapping; this is what the validator enforces |

## Validator

```bash
python scripts/skills/validate_odoo19_skills_coverage.py
```

Exits 0 if all expected stubs exist, 1 if any are missing.

**Structured JSON output** (stdout):

```json
{
  "coverage": {
    "odoo19_docs":          { "total": 63, "found": 63, "missing": 0, "pct": 100.0 },
    "vercel_agent_skills":  { "total": 6,  "found": 6,  "missing": 0, "pct": 100.0 },
    "supabase_agent_skills":{ "total": 1,  "found": 1,  "missing": 0, "pct": 100.0 }
  },
  "overall":       { "total": 70, "found": 70, "missing": 0, "pct": 100.0 },
  "missing_skills": []
}
```

## CI gate

`.github/workflows/skill-coverage-gate.yml` — triggers on push/PR to `main` when any of
these paths change:

```
skills/**
ssot/skills/**
scripts/skills/**
```

## Adding a new expected skill

1. Add the entry to `ssot/skills/odoo19_docs_coverage.yaml` under `expected:`.
2. Create the stub directory (at minimum a `README.md`):
   ```bash
   mkdir -p skills/<slug>
   echo "# Skill: <slug>\n\n**Status:** STUB\n\n**Source:** <url>" > skills/<slug>/README.md
   ```
3. Run the validator locally to confirm it passes.
4. Commit both the SSOT change and the new stub in the same commit.

## Evidence

Evidence logs from CI runs are stored at:

```
runtime/evidence/<YYYYMMDD-HHMMSSZ>-skills-coverage/validate.stdout.txt
```
