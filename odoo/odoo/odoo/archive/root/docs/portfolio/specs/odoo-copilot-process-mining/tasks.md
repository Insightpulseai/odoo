# Tasks: Odoo Copilot – Process Mining

## M1: Schema + P2P Extraction

- [x] Create pm.* schema with tables (case, event, variant, edge, deviation)
- [x] Add indexes for query patterns
- [x] Implement pm.job_state for ETL tracking
- [x] Implement P2P event mapping:
  - [x] purchase.order → PO Created, PO Approved
  - [x] stock.picking → Goods Received
  - [x] account.move → Vendor Bill Posted
  - [x] account.payment → Payment Posted (heuristic)
- [x] Implement backfill job (full history)
- [x] Implement incremental job (idempotent, window-based)

## M2: Discovery + Bottleneck Metrics

- [x] Compute variants from event sequences
- [x] Assign variant_id to cases
- [x] Calculate DFG edges with p50/p95 latency
- [x] Build bottleneck ranking endpoint

## M3: Conformance Rules + Insights

- [x] Implement deviation detection:
  - [x] BILL_BEFORE_RECEIPT rule
  - [x] MISSING_RECEIPT rule
  - [x] MISSING_VENDOR_BILL rule
- [ ] Add APPROVAL_BYPASSED rule
- [ ] Add LATE_PAYMENT rule
- [ ] Implement pm.insight table for recommendations
- [ ] Build deviation summary endpoint

## M4: Copilot NLQ + Action Suggestions

- [ ] Create prompt templates for process mining queries
- [ ] Implement evidence card renderer (case timeline)
- [ ] Build action suggestion engine
- [ ] Integrate with ipai_ai_copilot module
- [ ] Add drill-through for variant analysis

## API Implementation

- [x] `/pm/p2p/summary` - Process-level KPIs
- [x] `/pm/p2p/bottlenecks` - Top edges by latency
- [x] `/pm/p2p/variants` - Top variants by frequency
- [x] `/pm/p2p/cases/{id}` - Case timeline with deviations
- [ ] `/pm/p2p/deviations` - List deviations with filters
- [ ] `/pm/p2p/etl/run` - Trigger incremental ETL

## Security & Privacy

- [ ] Add redaction configuration table
- [ ] Implement PII field masking in event attrs
- [ ] Add retention policy cleanup job
- [ ] Row-level filtering by company_id

## Future: O2C Process

- [ ] Map sale.order → SO Created, SO Confirmed
- [ ] Map stock.picking (outgoing) → Goods Shipped
- [ ] Map account.move (out_invoice) → Invoice Posted
- [ ] Map account.payment → Customer Payment Received

## Future: Strict Payment Reconciliation

- [ ] Replace heuristic payment mapping with account_partial_reconcile join
- [ ] Handle partial payments and overpayments
- [ ] Track reconciliation status in event attrs
