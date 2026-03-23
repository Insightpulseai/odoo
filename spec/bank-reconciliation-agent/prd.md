# PRD: Bank Reconciliation Agent

## Problem Statement
Bank reconciliation in Odoo is often a bottleneck for finance teams, requiring manual matching of bank statement lines against internal invoices and payments. Current AI solutions often lack the "deterministic trust" required to handle financial mutations safely.

## Goals
1.  **Automate 80%+ of high-confidence matches** with zero human intervention.
2.  **Reduce exception handling time** by providing grounded "candidate suggestions" with evidence.
3.  **Enforce fail-closed safety** to prevent incorrect General Ledger postings.

## User Personas
*   **Accountant**: Reviews ambiguous matches and validates automated proposals.
*   **Finance Manager**: Monitors reconciliation health and sets confidence policy.

## Key Features

### 1. Statement Ingestion & Analysis
- Parse bank statement files (CSV, OFX) or fetch via Odoo bank sync.
- Normalize statement descriptions and metadata.

### 2. Candidate Matching Engine
- Multi-vector search: Reference number, Amount (exact/delta), Date proximity, and Vendor/Customer name.
- Cross-reference with `ipai_bir_tax_compliance` classification (VAT/EWT interaction).

### 3. Evidence-Based Logic
- Link every match to a specific Odoo `account.move` or `account.payment`.
- Emit an `evidence_pack` for every suggestion.

### 4. Exception Orchestration
- Workflow states: `ingested` -> `matched` -> `ambiguous` -> `exception` -> `quarantined`.
- Integration with Odoo Chatter for human-in-the-loop clarifications.

## Constraints
- **Odoo 19.0** runtime compatibility.
- Must follow the **3-Agent Topology** (Advisory/Ops/Actions).
- Bounded by the **Bank Reconciliation Constitution**.
