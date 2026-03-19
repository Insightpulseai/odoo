# Contracts

Every cross-boundary integration in InsightPulse AI requires a **contract document**. Contracts define data ownership, allowed flows, prohibited operations, and failure handling.

The master registry lives at `docs/contracts/PLATFORM_CONTRACTS_INDEX.md`. SSOT YAML definitions are in `ssot/integrations/`.

## Pages in this section

| Page | Description |
|------|-------------|
| [Data authority](data-authority.md) | Entity-level ownership matrix across all systems |
| [Reverse ETL guardrails](reverse-etl.md) | Classification, approved flows, prohibited writebacks |
| [SAP contract](sap-contract.md) | SAP Concur and Joule integration rules |

## Contract principles

1. **Explicit ownership.** Every entity has exactly one authoritative system.
2. **No silent writes.** All writes to external systems go through classified, audited flows.
3. **Drafts first.** Inbound records from external systems arrive as drafts for human review.
4. **Idempotency required.** Every integration flow handles duplicates gracefully.
5. **Failure is handled, not ignored.** Every flow defines failure modes and responses.

## Contract file locations

| Type | Location |
|------|----------|
| Contract documents | `docs/contracts/*.md` |
| SSOT YAML definitions | `ssot/integrations/*.yaml` |
| Master registry | `docs/contracts/PLATFORM_CONTRACTS_INDEX.md` |
| Spec bundles (with contract sections) | `spec/<feature>/constitution.md` |
