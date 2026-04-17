# Reference adaptation — `microsoft/CDM`

> **Mode:** `clone-reference` (per `ssot/governance/upstream-adoption-register.yaml`)
> **Upstream:** https://github.com/Microsoft/CDM
> **Do NOT fork. Do NOT vendor. Do NOT treat as runtime authority.**
> Locked 2026-04-15.

---

## What this repo is

A **schema / specification repository** — standardized collection of schemas (entities, attributes, relationships) that represents business concepts. Key folders on upstream:
- `schemaDocuments/` — canonical CDM entity definitions
- `objectModel/` — programmatic access SDK (language bindings)
- `samples/` — reference usage examples

**Important upstream notice:** Microsoft shut down the old CDM Schema Store dependency path; newer SDKs bundle only foundational definitions, not all application schemas. This means many apps that used to auto-resolve full CDM schemas now need to bundle what they need locally.

## Why IPAI references it

IPAI has already committed to CDM as a **projection target** for Fabric / Power BI / M365 Copilot interop per `docs/architecture/cdm-odoo-mapping.md`. The canonical IPAI contract is `platform/contracts/cdm-entity-map.yaml` — NOT upstream CDM schemas.

We reference upstream CDM for:

| Aspect | How we use it |
|---|---|
| Entity definitions + naming | Match upstream entity names (Account, Contact, Invoice, Payment, …) in our YAML SSOT for maximum Fabric/PBI interop |
| Attribute/relationship reference | Validate our attribute names map to CDM's canonical when possible |
| Schema extension patterns | For `IPAI_*` entities (PH BIR extensions), we use CDM's extension pattern (`extends:` parent entity) rather than inventing our own |
| Additive-versioning mindset | Never break attribute contracts; add new attributes, don't rename or remove |

## What IPAI explicitly does NOT adopt from upstream

| Upstream construct | Why we skip |
|---|---|
| Old CDM Schema Store assumptions | Shut down per Microsoft; bundle foundational defs locally instead |
| Dataverse-first posture | IPAI's SOR is Odoo, not Dataverse — CDM is interop, not truth |
| CDM-as-transaction-truth | IPAI writes to Odoo, projects to CDM Gold in Fabric; never reverses |
| Full `schemaDocuments/` tree | Too many entities irrelevant to IPAI verticals; IPAI-canonical set lives in `platform/contracts/cdm-entity-map.yaml` |

## File placement convention

When patterns from upstream CDM are harvested, they land here (`docs/architecture/reference-adaptations/cdm/`) as reference notes — never in repo root, never in runtime paths.

Canonical IPAI CDM artifact: `platform/contracts/cdm-entity-map.yaml` (SSOT — authoritative for Fabric DLT export per `data-intelligence/pipelines/odoo_cdm_export/`).

## Reading path

1. `platform/contracts/cdm-entity-map.yaml` — IPAI SSOT (read this first)
2. `docs/architecture/cdm-odoo-mapping.md` — full mapping narrative
3. `docs/architecture/data-model-erd.md §11` — CDM positioning in the architecture
4. Upstream `microsoft/CDM` `schemaDocuments/core/applicationCommon/` — reference for CDM-standard entity names (Account, Contact, Invoice, etc.) when extending our YAML

## Update trigger

Revisit this adaptation when:
- Microsoft ships a new CDM schema version we want to align to
- Fabric / Power BI / Copilot ecosystem adds a consumer that requires richer CDM metadata than our YAML currently encodes
- A new IPAI entity needs a CDM extension we haven't captured yet

---

*Reference-adapt note locked 2026-04-15. Register entry in `ssot/governance/upstream-adoption-register.yaml` under "Added 2026-04-15 — CDM + agentic-app-with-fabric".*
