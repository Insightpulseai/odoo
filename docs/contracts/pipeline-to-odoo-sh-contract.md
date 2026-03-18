# Pipeline-to-Odoo Runtime Contract

## Purpose

Define how a governed pipeline hands off a validated delivery unit to an Odoo runtime target.

## Supported runtime targets

- `azure_runtime` (default for this platform)
- `odoo_sh`

## Runtime selection rule

The release path must declare one runtime target explicitly. Do not mix both in one promotion flow unless there is a documented mirror/rehearsal requirement.

## Common requirements for both targets

Before handoff to runtime, the pipeline must provide:

- build/package artifact
- module/app version
- migration/install notes
- smoke-check definition
- rollback path
- release metadata
- linked work item and spec slug

## Azure runtime handoff

Use this path when the real Odoo runtime is Azure-hosted.

Required:

- target environment identified
- release artifact/image identified
- config/secret references resolved
- smoke/health checks defined
- rollback method defined
- progressive exposure policy documented if applicable

Exit gate: staging deploy passed, production approvals passed, runtime evidence captured.

## Odoo.sh handoff

Use this path only when Odoo.sh is the actual deployment platform.

Required:

- branch/build target identified
- module dependencies declared
- install/update path declared
- staging branch/build used before production
- production promotion through the production branch path
- post-deploy validation defined

Exit gate: Odoo.sh staging build green, production merge/promotion approved, production validation complete.

## Staging rules

### Azure runtime

Staging must be production-like enough to validate module install/update, integration behavior, smoke checks, and operational dependencies.

### Odoo.sh

Staging must use the platform's staging semantics and validate against the staging build before production branch promotion.

## Required runtime evidence

The runtime handoff must preserve: deployment timestamp, release version, environment, linked work item, spec slug, validation status, rollback reference, approver (if applicable).

---

*Last updated: 2026-03-17*
