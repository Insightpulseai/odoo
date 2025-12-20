-- =============================================================================
-- CAPABILITY REGISTRY: Full SAP → Odoo CE/OCA 18 + Supabase Gap Handlers
-- =============================================================================
-- Canonical rule: SAP product ≠ 1:1 module
-- Map into normalized capability registry, then bind to:
--   1. Odoo CE core module(s)
--   2. OCA addon(s)
--   3. Supabase gap handlers
--
-- Source: config/capability_map.yaml
-- =============================================================================

-- Enhanced capability_map schema (add missing columns if needed)
ALTER TABLE gold.capability_map
    ADD COLUMN IF NOT EXISTS source_suite text,
    ADD COLUMN IF NOT EXISTS gap_severity text,
    ADD COLUMN IF NOT EXISTS oca_addons jsonb DEFAULT '[]'::jsonb,
    ADD COLUMN IF NOT EXISTS supabase_handlers jsonb DEFAULT '[]'::jsonb;

-- Create gap_handlers registry table
CREATE TABLE IF NOT EXISTS gold.gap_handlers (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

    function_key text NOT NULL UNIQUE,
    title text NOT NULL,
    description text,

    handler_type text NOT NULL DEFAULT 'edge_function',
    endpoint text,
    tables jsonb DEFAULT '[]'::jsonb,
    n8n_workflow text,

    config jsonb DEFAULT '{}'::jsonb,

    enabled boolean DEFAULT true,

    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT valid_handler_type CHECK (
        handler_type IN ('edge_function', 'table', 'n8n_workflow', 'hybrid')
    )
);

CREATE INDEX IF NOT EXISTS ix_gap_handlers_type ON gold.gap_handlers (handler_type);

-- =============================================================================
-- SEED: Gap Handlers Registry
-- =============================================================================

INSERT INTO gold.gap_handlers (function_key, title, description, handler_type, endpoint, tables, n8n_workflow)
VALUES
-- OCR Handlers
('ocr.receipt_extract', 'Receipt OCR Extraction', 'PaddleOCR-VL + OpenAI for receipt line extraction', 'edge_function', '/functions/v1/ocr-receipt', NULL, NULL),
('ocr.invoice_extract', 'Invoice OCR Extraction', 'Invoice OCR with vendor matching', 'edge_function', '/functions/v1/ocr-invoice', NULL, NULL),

-- Policy Handlers
('policy.expense_rules', 'Expense Policy Rules', 'Per diem, category limits, receipt requirements engine', 'edge_function', '/functions/v1/expense-policy-check', NULL, NULL),
('policy.po_gating', 'PO Policy Gating', 'PO approval policy gating', 'edge_function', '/functions/v1/po-policy-check', NULL, NULL),
('policy.threshold_validate', 'Threshold Validation', 'Amount threshold validation', 'edge_function', '/functions/v1/threshold-check', NULL, NULL),

-- Rules Handlers
('rules.approval_routing', 'Approval Routing', 'Dynamic approval chain based on amount thresholds', 'edge_function', '/functions/v1/approval-route', NULL, NULL),
('rules.invoice_routing', 'Invoice Routing', 'Dynamic routing based on invoice attributes', 'edge_function', '/functions/v1/invoice-route', NULL, NULL),

-- Budget Handlers
('budget.check', 'Budget Check', 'Budget availability check against GL', 'edge_function', '/functions/v1/budget-check', NULL, NULL),

-- Matching Handlers
('matching.vendor_lookup', 'Vendor Lookup', 'Fuzzy vendor name matching to res.partner', 'edge_function', '/functions/v1/vendor-match', NULL, NULL),
('assertions.three_way_match', '3-Way Match Assertions', 'Assertion store (PO/GR/INV) + tolerance checks', 'edge_function', '/functions/v1/three-way-match', NULL, NULL),

-- Vendor Handlers
('vendor.scoring', 'Vendor Scoring', 'Supplier risk scoring and performance tracking', 'edge_function', '/functions/v1/vendor-score', NULL, NULL),
('kyc.document_check', 'Vendor KYC Check', 'Document KYC validation', 'edge_function', '/functions/v1/vendor-kyc', NULL, NULL),

-- Catalog Handlers
('catalog.normalize', 'Catalog Normalize', 'Catalog normalization + price compliance', 'edge_function', '/functions/v1/catalog-normalize', NULL, NULL),
('price.compliance', 'Price Compliance', 'Price compliance validation', 'edge_function', '/functions/v1/price-compliance', NULL, NULL),

-- Ticket Handlers
('classify.ticket', 'Ticket Classification', 'AI-powered ticket classification', 'edge_function', '/functions/v1/ticket-classify', NULL, NULL),
('route.ticket', 'Ticket Routing', 'Auto-routing to appropriate queue', 'edge_function', '/functions/v1/ticket-route', NULL, NULL),
('rag.ticket_suggest', 'KB Article Suggestions', 'RAG-powered article suggestions for tickets', 'edge_function', '/functions/v1/ticket-kb-suggest', NULL, NULL),

-- Workflow Handlers (hybrid: table + n8n)
('workflow.onboarding', 'Onboarding Workflow', 'Cross-dept orchestration state machine', 'hybrid', NULL, '["process.definitions", "run.instances", "run.work_items"]'::jsonb, 'onboard_offboard'),
('workflow.offboarding', 'Offboarding Workflow', 'Offboarding state machine with asset recovery', 'hybrid', NULL, '["process.definitions", "run.instances", "run.work_items"]'::jsonb, 'onboard_offboard'),
('workflow.doc_approval', 'Document Approval Workflow', 'Multi-step approval workflow', 'table', NULL, '["qms.approval_routes", "qms.approvals"]'::jsonb, NULL),
('workflow.vendor_qualification', 'Vendor Qualification Workflow', 'Multi-step qualification workflow', 'hybrid', NULL, '["run.instances"]'::jsonb, NULL),
('workflow.change_control', 'Change Control Workflow', 'Change control workflow', 'table', NULL, '["qms.change_controls"]'::jsonb, NULL),

-- SLA Handlers
('sla.monitor', 'SLA Monitor', 'SLA timers with escalation', 'hybrid', NULL, '["run.sla_timers"]'::jsonb, 'sla_monitor'),
('sla.ticket_timer', 'Ticket SLA Timer', 'SLA timer with warning/breach thresholds', 'table', NULL, '["run.sla_timers"]'::jsonb, NULL),
('escalation.auto', 'Auto Escalation', 'Auto-escalation on SLA breach', 'table', NULL, '["run.escalations"]'::jsonb, NULL),

-- Audit Handlers
('audit.provenance', 'Audit Provenance', 'Immutable audit trail for expense lifecycle', 'table', NULL, '["runtime.audit_log"]'::jsonb, NULL),
('audit.payment_trail', 'Payment Audit Trail', 'Payment audit trail + exceptions', 'table', NULL, '["runtime.audit_log"]'::jsonb, NULL),
('audit.immutable', 'Immutable Audit', 'Immutable audit trail', 'table', NULL, '["runtime.audit_log"]'::jsonb, NULL),
('audit.training', 'Training Audit', 'Training completion audit trail', 'table', NULL, '["qms.audit_events"]'::jsonb, NULL),

-- Alert Handlers
('alerts.policy_violation', 'Policy Violation Alert', 'Real-time violation notifications', 'edge_function', '/functions/v1/policy-violation-alert', NULL, NULL),
('alerts.mismatch', 'Mismatch Alert', 'Real-time mismatch notifications', 'edge_function', '/functions/v1/mismatch-alert', NULL, NULL),
('alerts.risk_flags', 'Risk Flags Alert', 'Supplier risk flag notifications', 'edge_function', '/functions/v1/vendor-risk-alert', NULL, NULL),
('alerts.quantity_mismatch', 'Quantity Mismatch Alert', 'Quantity mismatch notifications', 'edge_function', '/functions/v1/quantity-alert', NULL, NULL),

-- Exception Handlers
('exceptions.receiving', 'Receiving Exceptions', 'Exception detection + mismatch alerts', 'edge_function', '/functions/v1/receiving-exceptions', NULL, NULL),
('disputes.ticketing', 'Dispute Ticketing', 'Auto-create work items for mismatches', 'table', NULL, '["run.work_items"]'::jsonb, NULL),

-- Document Handlers
('doc.version_control', 'Document Version Control', 'Immutable version snapshots', 'table', NULL, '["qms.doc_versions"]'::jsonb, NULL),
('training.read_receipt', 'Training Read Receipt', '"I have read and understood" acknowledgments', 'table', NULL, '["qms.read_receipts"]'::jsonb, NULL),
('evidence.pack', 'Evidence Pack', 'Evidence pack for audits', 'table', NULL, '["qms.evidence_packs"]'::jsonb, NULL),
('link.resolution', 'Resolution Link', 'Link resolution to KB article', 'table', NULL, '["rag.documents"]'::jsonb, NULL),

-- Calculation Handlers
('calc.reimburse_amount', 'Reimburse Calculation', 'Net reimbursement calculation with deductions', 'edge_function', '/functions/v1/reimburse-calc', NULL, NULL),

-- Checklist Handlers
('checklist.vendor_docs', 'Vendor Documents Checklist', 'Required document checklist', 'table', NULL, '["control.checklists"]'::jsonb, NULL),
('checklist.offboarding', 'Offboarding Checklist', 'Offboarding checklist (equipment, access, final pay)', 'table', NULL, '["control.checklists"]'::jsonb, NULL),

-- Integration Handlers (n8n)
('routing.message', 'Message Routing', 'n8n workflows + Edge Functions + retry/DLQ', 'n8n_workflow', NULL, NULL, 'message_router'),
('bpmn.engine', 'BPMN Engine', 'BPMN engine + run logs + step replay', 'table', NULL, '["process.definitions", "process.nodes", "run.instances", "run.events"]'::jsonb, NULL),
('connectors.pack', 'Connector Packs', 'HTTP/SFTP/IMAP/Drive/Notion/GitHub connector packs', 'n8n_workflow', NULL, NULL, 'connector_hub'),
('monitoring.runs', 'Run Monitoring', 'Run inspector UI + OpenLineage events', 'table', NULL, '["runtime.pipeline_runs", "runtime.pipeline_run_steps"]'::jsonb, NULL)

ON CONFLICT (function_key) DO UPDATE SET
    title = EXCLUDED.title,
    description = EXCLUDED.description,
    handler_type = EXCLUDED.handler_type,
    endpoint = EXCLUDED.endpoint,
    tables = EXCLUDED.tables,
    n8n_workflow = EXCLUDED.n8n_workflow,
    updated_at = now();

-- =============================================================================
-- SEED: Full Capability Map (SAP Concur + SRM + Integration + ITSM)
-- =============================================================================

DO $$
DECLARE
    v_tenant_id uuid;
BEGIN
    -- Get default tenant
    SELECT id INTO v_tenant_id FROM core.tenants LIMIT 1;

    IF v_tenant_id IS NULL THEN
        RAISE NOTICE 'No tenant found, skipping capability map seeding';
        RETURN;
    END IF;

    -- Clear existing and re-seed (idempotent via ON CONFLICT)

    -- =========================================================================
    -- SAP CONCUR: Expense Management
    -- =========================================================================

    INSERT INTO gold.capability_map (
        tenant_id, source_framework, source_suite, capability_key, title, description,
        target_modules, oca_addons, supabase_handlers, gap_severity, status
    ) VALUES
    -- Expense Capture
    (v_tenant_id, 'sap_concur', 'concur_expense', 'travel.expense.capture',
     'Expense Capture + Receipt Processing',
     'Employee photo capture of receipts, OCR extraction, line-item data validation',
     '["hr_expense", "documents"]'::jsonb,
     '[{"repo": "OCA/hr-expense", "modules": ["hr_expense_sequence", "hr_expense_invoice"]}]'::jsonb,
     '["ocr.receipt_extract", "policy.expense_rules", "audit.provenance"]'::jsonb,
     'critical', 'mapped'),

    -- Expense Approvals
    (v_tenant_id, 'sap_concur', 'concur_expense', 'travel.expense.approvals',
     'Expense Approval Workflow',
     'Multi-tier approval with configurable rules based on amount, category, policy',
     '["hr_expense"]'::jsonb,
     '[{"repo": "OCA/hr-expense", "modules": ["hr_expense_tier_validation"]}, {"repo": "OCA/server-ux", "modules": ["base_tier_validation"]}]'::jsonb,
     '["rules.approval_routing"]'::jsonb,
     'minor', 'mapped'),

    -- Expense Policy
    (v_tenant_id, 'sap_concur', 'concur_expense', 'travel.expense.policy',
     'Expense Policy Rule Engine',
     'Define and enforce expense policies with complex conditions',
     '["hr_expense"]'::jsonb,
     '[]'::jsonb,
     '["policy.expense_rules", "alerts.policy_violation"]'::jsonb,
     'critical', 'draft'),

    -- Reimbursement
    (v_tenant_id, 'sap_concur', 'concur_expense', 'travel.expense.reimburse',
     'Expense Reimbursement',
     'Process employee expense reimbursements via payroll or direct payment',
     '["hr_expense", "account_payment"]'::jsonb,
     '[{"repo": "OCA/account-payment", "modules": ["account_payment_order", "account_payment_partner"]}]'::jsonb,
     '["calc.reimburse_amount", "audit.payment_trail"]'::jsonb,
     'minor', 'mapped'),

    -- Invoice Capture
    (v_tenant_id, 'sap_concur', 'concur_invoice', 'ap.invoice.capture',
     'Invoice Capture + OCR',
     'Vendor invoice scan/upload, OCR extraction, data validation',
     '["account", "purchase"]'::jsonb,
     '[{"repo": "OCA/account-invoicing", "modules": ["account_invoice_import"]}]'::jsonb,
     '["ocr.invoice_extract", "matching.vendor_lookup"]'::jsonb,
     'critical', 'draft'),

    -- Invoice Routing
    (v_tenant_id, 'sap_concur', 'concur_invoice', 'ap.invoice.routing',
     'Invoice Approval Routing',
     'Multi-step invoice approval based on amount, GL code, vendor',
     '["account", "purchase"]'::jsonb,
     '[{"repo": "OCA/account-invoicing", "modules": ["account_invoice_tier_validation"]}, {"repo": "OCA/purchase-workflow", "modules": ["purchase_tier_validation"]}]'::jsonb,
     '["rules.invoice_routing"]'::jsonb,
     'minor', 'mapped'),

    -- 3-Way Match
    (v_tenant_id, 'sap_concur', 'concur_invoice', 'ap.invoice.three_way_match',
     '3-Way Match (PO/GR/Invoice)',
     'Automated matching of purchase order, goods receipt, and invoice',
     '["purchase", "stock", "account"]'::jsonb,
     '[{"repo": "OCA/purchase-workflow", "modules": ["purchase_order_line_invoice_status"]}, {"repo": "OCA/account-invoicing", "modules": ["account_invoice_check_total"]}]'::jsonb,
     '["assertions.three_way_match", "disputes.ticketing", "alerts.mismatch"]'::jsonb,
     'moderate', 'draft'),

    -- Pre-Approval
    (v_tenant_id, 'sap_concur', 'concur_request', 'spend.request.preapproval',
     'Spend Pre-Approval Request',
     'Pre-trip approval with budget checks and threshold validation',
     '["hr_expense"]'::jsonb,
     '[{"repo": "OCA/hr-expense", "modules": ["hr_expense_advance_clearing"]}]'::jsonb,
     '["budget.check", "policy.threshold_validate"]'::jsonb,
     'moderate', 'draft')

    ON CONFLICT (tenant_id, source_framework, capability_key) DO UPDATE SET
        source_suite = EXCLUDED.source_suite,
        title = EXCLUDED.title,
        description = EXCLUDED.description,
        target_modules = EXCLUDED.target_modules,
        oca_addons = EXCLUDED.oca_addons,
        supabase_handlers = EXCLUDED.supabase_handlers,
        gap_severity = EXCLUDED.gap_severity,
        status = EXCLUDED.status,
        updated_at = now();

    -- =========================================================================
    -- SAP SRM/ARIBA: Procurement
    -- =========================================================================

    INSERT INTO gold.capability_map (
        tenant_id, source_framework, source_suite, capability_key, title, description,
        target_modules, oca_addons, supabase_handlers, gap_severity, status
    ) VALUES
    -- Supplier Master
    (v_tenant_id, 'sap_srm', 'ariba', 'procurement.supplier.master',
     'Supplier Master Data',
     'Vendor onboarding, qualification, and profile management',
     '["contacts", "purchase"]'::jsonb,
     '[{"repo": "OCA/partner-contact", "modules": ["partner_contact_department", "partner_contact_birthdate"]}, {"repo": "OCA/purchase-workflow", "modules": ["purchase_commercial_partner"]}]'::jsonb,
     '["vendor.scoring", "kyc.document_check", "alerts.risk_flags"]'::jsonb,
     'moderate', 'draft'),

    -- Supplier Qualification
    (v_tenant_id, 'sap_srm', 'ariba', 'procurement.supplier.qualification',
     'Supplier Qualification',
     'Vendor qualification workflow with document requirements',
     '["purchase", "documents"]'::jsonb,
     '[{"repo": "OCA/purchase-workflow", "modules": ["purchase_request"]}]'::jsonb,
     '["workflow.vendor_qualification", "checklist.vendor_docs"]'::jsonb,
     'critical', 'draft'),

    -- RFQ to PO
    (v_tenant_id, 'sap_srm', 'ariba', 'procurement.rfq.po',
     'RFQ to Purchase Order',
     'Request for quotation workflow to PO creation',
     '["purchase"]'::jsonb,
     '[{"repo": "OCA/purchase-workflow", "modules": ["purchase_request", "purchase_request_tier_validation", "purchase_order_approval_block"]}]'::jsonb,
     '["policy.po_gating", "audit.po_trail"]'::jsonb,
     'closed', 'implemented'),

    -- Requisition
    (v_tenant_id, 'sap_srm', 'ariba', 'procurement.requisition',
     'Purchase Requisition',
     'Employee-initiated purchase requests with approval workflow',
     '["purchase"]'::jsonb,
     '[{"repo": "OCA/purchase-workflow", "modules": ["purchase_request", "purchase_request_tier_validation"]}]'::jsonb,
     '[]'::jsonb,
     'closed', 'implemented'),

    -- Receiving
    (v_tenant_id, 'sap_srm', 'ariba', 'procurement.receiving',
     'Goods Receipt',
     'Receiving workflow with quantity validation and exception handling',
     '["stock", "purchase"]'::jsonb,
     '[{"repo": "OCA/stock-logistics-workflow", "modules": ["stock_picking_tier_validation"]}]'::jsonb,
     '["exceptions.receiving", "alerts.quantity_mismatch"]'::jsonb,
     'minor', 'mapped'),

    -- Contracts/Catalogs
    (v_tenant_id, 'sap_srm', 'ariba', 'procurement.contracts.catalog',
     'Contracts and Catalogs',
     'Vendor contracts with catalog item management',
     '["purchase", "product"]'::jsonb,
     '[{"repo": "OCA/contract", "modules": ["contract", "contract_sale_invoicing"]}, {"repo": "OCA/purchase-workflow", "modules": ["purchase_blanket_order"]}]'::jsonb,
     '["catalog.normalize", "price.compliance"]'::jsonb,
     'moderate', 'draft')

    ON CONFLICT (tenant_id, source_framework, capability_key) DO UPDATE SET
        source_suite = EXCLUDED.source_suite,
        title = EXCLUDED.title,
        description = EXCLUDED.description,
        target_modules = EXCLUDED.target_modules,
        oca_addons = EXCLUDED.oca_addons,
        supabase_handlers = EXCLUDED.supabase_handlers,
        gap_severity = EXCLUDED.gap_severity,
        status = EXCLUDED.status,
        updated_at = now();

    -- =========================================================================
    -- SAP INTEGRATION / PROCESS ORCHESTRATION
    -- =========================================================================

    INSERT INTO gold.capability_map (
        tenant_id, source_framework, source_suite, capability_key, title, description,
        target_modules, oca_addons, supabase_handlers, gap_severity, status, config_notes
    ) VALUES
    -- iFlows
    (v_tenant_id, 'sap_integration', 'pi_po', 'integration.iflow.routing',
     'Message Routing (iFlows)',
     'Message-based integration routing between systems',
     '[]'::jsonb,
     '[{"repo": "OCA/queue", "modules": ["queue_job"]}]'::jsonb,
     '["routing.message"]'::jsonb,
     'n/a', 'mapped', 'Handled entirely by n8n + Supabase, not Odoo'),

    -- BPMN
    (v_tenant_id, 'sap_integration', 'pi_po', 'integration.bpmn.orchestrate',
     'BPMN Orchestration',
     'Business process orchestration with step tracking',
     '[]'::jsonb,
     '[]'::jsonb,
     '["bpmn.engine"]'::jsonb,
     'n/a', 'implemented', 'Uses process runtime tables'),

    -- Adapters
    (v_tenant_id, 'sap_integration', 'pi_po', 'integration.adapters',
     'Adapter Ecosystem',
     'Connectors for external systems',
     '[]'::jsonb,
     '[{"repo": "OCA/connector", "modules": ["connector"]}]'::jsonb,
     '["connectors.pack"]'::jsonb,
     'n/a', 'mapped', NULL),

    -- Monitoring
    (v_tenant_id, 'sap_integration', 'pi_po', 'integration.run.monitoring',
     'Pipeline Run Monitoring',
     'Execution monitoring with logs and alerts',
     '[]'::jsonb,
     '[]'::jsonb,
     '["monitoring.runs"]'::jsonb,
     'n/a', 'implemented', NULL)

    ON CONFLICT (tenant_id, source_framework, capability_key) DO UPDATE SET
        source_suite = EXCLUDED.source_suite,
        title = EXCLUDED.title,
        description = EXCLUDED.description,
        target_modules = EXCLUDED.target_modules,
        oca_addons = EXCLUDED.oca_addons,
        supabase_handlers = EXCLUDED.supabase_handlers,
        gap_severity = EXCLUDED.gap_severity,
        status = EXCLUDED.status,
        config_notes = EXCLUDED.config_notes,
        updated_at = now();

    -- =========================================================================
    -- HR/ITSM: Onboarding, Offboarding, Ticketing
    -- =========================================================================

    INSERT INTO gold.capability_map (
        tenant_id, source_framework, source_suite, capability_key, title, description,
        target_modules, oca_addons, supabase_handlers, gap_severity, status, config_notes
    ) VALUES
    -- Onboarding
    (v_tenant_id, 'sap_successfactors', 'sf_onboarding', 'hr.onboarding.case',
     'Employee Onboarding Case',
     'New hire onboarding workflow with task automation',
     '["hr", "project"]'::jsonb,
     '[{"repo": "OCA/hr", "modules": ["hr_contract_types"]}, {"repo": "OCA/project", "modules": ["project_task_default_stage"]}]'::jsonb,
     '["workflow.onboarding", "sla.monitor", "audit.immutable"]'::jsonb,
     'moderate', 'implemented', 'Uses Hire-to-Retire process'),

    -- Offboarding
    (v_tenant_id, 'sap_successfactors', 'sf_onboarding', 'hr.offboarding.case',
     'Employee Offboarding Case',
     'Termination/resignation workflow with checklist',
     '["hr", "project"]'::jsonb,
     '[{"repo": "OCA/hr", "modules": ["hr_contract_types"]}]'::jsonb,
     '["workflow.offboarding", "checklist.offboarding"]'::jsonb,
     'moderate', 'implemented', NULL),

    -- Ticket Intake
    (v_tenant_id, 'sap_service_cloud', 'service_cloud', 'itsm.ticket.intake',
     'IT Ticket Intake',
     'IT service request submission and categorization',
     '["helpdesk", "project"]'::jsonb,
     '[{"repo": "OCA/helpdesk", "modules": ["helpdesk_mgmt"]}]'::jsonb,
     '["classify.ticket", "route.ticket"]'::jsonb,
     'minor', 'mapped', NULL),

    -- Ticket SLA
    (v_tenant_id, 'sap_service_cloud', 'service_cloud', 'itsm.ticket.sla',
     'IT Ticket SLA Management',
     'SLA tracking with escalation rules',
     '["helpdesk"]'::jsonb,
     '[{"repo": "OCA/helpdesk", "modules": ["helpdesk_mgmt"]}]'::jsonb,
     '["sla.ticket_timer", "escalation.auto"]'::jsonb,
     'minor', 'mapped', NULL),

    -- KB-Linked Tickets
    (v_tenant_id, 'sap_service_cloud', 'service_cloud', 'itsm.ticket.knowledge_linked',
     'Knowledge-Linked Tickets',
     'Link tickets to knowledge base articles for resolution',
     '["helpdesk", "knowledge"]'::jsonb,
     '[{"repo": "OCA/helpdesk", "modules": ["helpdesk_mgmt"]}]'::jsonb,
     '["rag.ticket_suggest", "link.resolution"]'::jsonb,
     'moderate', 'draft', NULL)

    ON CONFLICT (tenant_id, source_framework, capability_key) DO UPDATE SET
        source_suite = EXCLUDED.source_suite,
        title = EXCLUDED.title,
        description = EXCLUDED.description,
        target_modules = EXCLUDED.target_modules,
        oca_addons = EXCLUDED.oca_addons,
        supabase_handlers = EXCLUDED.supabase_handlers,
        gap_severity = EXCLUDED.gap_severity,
        status = EXCLUDED.status,
        config_notes = EXCLUDED.config_notes,
        updated_at = now();

    -- =========================================================================
    -- QMS-LITE: Document Control
    -- =========================================================================

    INSERT INTO gold.capability_map (
        tenant_id, source_framework, source_suite, capability_key, title, description,
        target_modules, oca_addons, supabase_handlers, gap_severity, status, config_notes
    ) VALUES
    -- Document Control
    (v_tenant_id, 'mastercontrol', 'qms', 'qms.document.control',
     'Controlled Document Management',
     'Document versioning with approval workflow',
     '["documents"]'::jsonb,
     '[{"repo": "OCA/knowledge", "modules": ["document_page", "document_page_approval"]}]'::jsonb,
     '["doc.version_control", "workflow.doc_approval"]'::jsonb,
     'moderate', 'implemented', 'Uses QMS-lite schema'),

    -- Training Records
    (v_tenant_id, 'mastercontrol', 'qms', 'qms.training.records',
     'Training Records',
     'Read receipts and training acknowledgments',
     '["hr"]'::jsonb,
     '[]'::jsonb,
     '["training.read_receipt", "audit.training"]'::jsonb,
     'moderate', 'implemented', NULL),

    -- Change Control
    (v_tenant_id, 'mastercontrol', 'qms', 'qms.change.control',
     'Change Control Records',
     'Change control workflow with impact assessment',
     '[]'::jsonb,
     '[]'::jsonb,
     '["workflow.change_control", "evidence.pack"]'::jsonb,
     'critical', 'draft', 'Minimal implementation; full CAPA requires GAP_DELTA')

    ON CONFLICT (tenant_id, source_framework, capability_key) DO UPDATE SET
        source_suite = EXCLUDED.source_suite,
        title = EXCLUDED.title,
        description = EXCLUDED.description,
        target_modules = EXCLUDED.target_modules,
        oca_addons = EXCLUDED.oca_addons,
        supabase_handlers = EXCLUDED.supabase_handlers,
        gap_severity = EXCLUDED.gap_severity,
        status = EXCLUDED.status,
        config_notes = EXCLUDED.config_notes,
        updated_at = now();

    RAISE NOTICE 'Seeded capability maps for tenant %', v_tenant_id;
END;
$$;

-- =============================================================================
-- VIEWS: Capability Registry API Surface
-- =============================================================================

-- View: Capabilities with gap handler details
CREATE OR REPLACE VIEW gold.v_capabilities_full AS
SELECT
    cm.id,
    cm.tenant_id,
    cm.source_framework,
    cm.source_suite,
    cm.capability_key,
    cm.title,
    cm.description,
    cm.target_modules,
    cm.oca_addons,
    cm.supabase_handlers,
    cm.gap_severity,
    cm.status,
    cm.config_notes,
    -- Expand gap handlers
    (
        SELECT jsonb_agg(
            jsonb_build_object(
                'function_key', gh.function_key,
                'title', gh.title,
                'handler_type', gh.handler_type,
                'endpoint', gh.endpoint,
                'tables', gh.tables,
                'n8n_workflow', gh.n8n_workflow
            )
        )
        FROM gold.gap_handlers gh
        WHERE gh.function_key = ANY(
            SELECT jsonb_array_elements_text(cm.supabase_handlers)
        )
    ) AS gap_handler_details
FROM gold.capability_map cm;

-- View: Gap handler usage (which capabilities use each handler)
CREATE OR REPLACE VIEW gold.v_gap_handler_usage AS
SELECT
    gh.function_key,
    gh.title,
    gh.handler_type,
    gh.endpoint,
    COUNT(DISTINCT cm.id) AS capability_count,
    jsonb_agg(DISTINCT cm.capability_key) AS capabilities
FROM gold.gap_handlers gh
LEFT JOIN gold.capability_map cm
    ON gh.function_key = ANY(
        SELECT jsonb_array_elements_text(cm.supabase_handlers)
    )
GROUP BY gh.function_key, gh.title, gh.handler_type, gh.endpoint;

-- =============================================================================
-- RPC: Capability Registry Functions
-- =============================================================================

-- Find capabilities by gap handler
CREATE OR REPLACE FUNCTION gold.capabilities_by_handler(
    p_tenant_id uuid,
    p_handler_key text
)
RETURNS TABLE (
    capability_key text,
    title text,
    source_framework text,
    status text
)
LANGUAGE sql STABLE
AS $func$
SELECT
    cm.capability_key,
    cm.title,
    cm.source_framework,
    cm.status
FROM gold.capability_map cm
WHERE cm.tenant_id = p_tenant_id
  AND cm.supabase_handlers ? p_handler_key
ORDER BY cm.source_framework, cm.capability_key;
$func$;

-- Get gap handler implementation status
CREATE OR REPLACE FUNCTION gold.gap_handler_status()
RETURNS TABLE (
    function_key text,
    title text,
    handler_type text,
    has_endpoint boolean,
    has_tables boolean,
    has_n8n_workflow boolean
)
LANGUAGE sql STABLE
AS $func$
SELECT
    gh.function_key,
    gh.title,
    gh.handler_type,
    gh.endpoint IS NOT NULL AS has_endpoint,
    gh.tables IS NOT NULL AND jsonb_array_length(gh.tables) > 0 AS has_tables,
    gh.n8n_workflow IS NOT NULL AS has_n8n_workflow
FROM gold.gap_handlers gh
ORDER BY gh.handler_type, gh.function_key;
$func$;

-- =============================================================================
-- VERIFICATION
-- =============================================================================

DO $verify$
DECLARE
    handler_count int;
    cap_count int;
BEGIN
    SELECT COUNT(*) INTO handler_count FROM gold.gap_handlers;
    SELECT COUNT(*) INTO cap_count FROM gold.capability_map;

    RAISE NOTICE 'Capability Registry: % gap handlers, % capabilities', handler_count, cap_count;

    -- Verify handler types distribution
    RAISE NOTICE 'Handler types:';
    FOR handler_count, cap_count IN
        SELECT handler_type, COUNT(*)
        FROM gold.gap_handlers
        GROUP BY handler_type
        ORDER BY handler_type
    LOOP
        RAISE NOTICE '  %: %', cap_count, handler_count;
    END LOOP;
END;
$verify$;
