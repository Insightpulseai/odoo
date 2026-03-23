# Knowledge Item: IPAI Agent Factory V2 Governance

## 1. Governance as Code Model
The V2 pilot introduced a "Fail-Closed" governance model where transitions between agent states (e.g., `matched` to `posted`) are programmatically blocked until a machine-verifiable evidence pack is generated and validated.

### Key Components
- **V2 Release Gate**: A GitHub Action/Script that blocks promotion to production if evidence is stale (>30 days) or missing.
- **Factory Validator**: An autonomous python agent (`factory_v2_validator.py`) that audits Odoo records against the SSOT policy contract.
- **Promotion Records**: Machine-readable JSON audits that track every maturity transition.

## 2. Evidence Thresholds
Agents are categorized by maturity (L1 to L5).
- **L1 (Autonomous)**: Requires OCR extraction + policy audit pass.
- **L4 (Production-Ready)**: Requires 5 success cycles and a Red-Team sign-off.
- **L5 (Full Autonomy)**: Requires cross-system reconciliation and anomaly resiliency (Red-Team proof).

## 3. Implementation Lessons
- **Idempotency**: Always use a `source_message_id` or `envelope_id` to prevent duplicate ledger entries.
- **Orthogonal States**: Keep business states (8-state) separate from agent metadata (channel/policy states) to maintain ERP stability.
- **Foundry Bridge**: Centralize all AI calls (OCR, LLM) in a single service bridge (`ipai.foundry.connector`) for unified credential management.
