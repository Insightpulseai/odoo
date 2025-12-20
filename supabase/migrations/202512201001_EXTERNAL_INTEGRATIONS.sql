-- =============================================================================
-- External Integrations: SAP Concur, SAP Ariba, Checkroom PPM, Notion
-- =============================================================================
-- Implements:
--   * Unified integration framework with credential vending
--   * SAP Concur expense sync with OCR receipt processing
--   * SAP Ariba procurement integration
--   * Checkroom PPM equipment/asset management
--   * Notion workspace sync with AI capabilities
--   * AI/OCR document processing layer
-- =============================================================================

BEGIN;

-- Ensure integrations schema exists
CREATE SCHEMA IF NOT EXISTS integrations;
CREATE SCHEMA IF NOT EXISTS ocr;

-- =============================================================================
-- 1. INTEGRATION PROVIDERS - Base Configuration
-- =============================================================================

CREATE TABLE IF NOT EXISTS integrations.providers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL UNIQUE, -- sap_concur, sap_ariba, checkroom, notion
    name TEXT NOT NULL,
    provider_type TEXT NOT NULL CHECK (provider_type IN ('expense', 'procurement', 'asset', 'workspace', 'ocr', 'ai')),

    -- API configuration
    base_url TEXT NOT NULL,
    auth_type TEXT NOT NULL CHECK (auth_type IN ('oauth2', 'api_key', 'basic', 'jwt', 'saml')),
    oauth_config JSONB, -- {authorize_url, token_url, scopes}
    api_version TEXT,

    -- Rate limiting
    rate_limit_rpm INT DEFAULT 60,
    rate_limit_daily INT,

    -- Status
    is_active BOOLEAN DEFAULT true,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

COMMENT ON TABLE integrations.providers IS 'External integration provider definitions';

-- =============================================================================
-- 2. TENANT CONNECTIONS - Per-Tenant Integration Setup
-- =============================================================================

CREATE TABLE IF NOT EXISTS integrations.connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id) ON DELETE CASCADE,
    provider_id UUID NOT NULL REFERENCES integrations.providers(id),

    -- Connection identity
    connection_name TEXT NOT NULL,
    external_account_id TEXT, -- Account ID in external system

    -- Credentials (encrypted, managed via vault)
    vault_credential_id UUID REFERENCES vault.principals(id),
    access_token_encrypted TEXT,
    refresh_token_encrypted TEXT,
    token_expires_at TIMESTAMPTZ,

    -- Sync configuration
    sync_enabled BOOLEAN DEFAULT true,
    sync_direction TEXT DEFAULT 'bidirectional' CHECK (sync_direction IN ('inbound', 'outbound', 'bidirectional')),
    sync_interval_minutes INT DEFAULT 60,
    last_sync_at TIMESTAMPTZ,
    last_sync_status TEXT,

    -- Field mappings
    field_mappings JSONB DEFAULT '{}'::jsonb,
    custom_config JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE (tenant_id, provider_id, connection_name)
);

CREATE INDEX idx_connections_tenant ON integrations.connections(tenant_id);
CREATE INDEX idx_connections_provider ON integrations.connections(provider_id);
CREATE INDEX idx_connections_sync ON integrations.connections(sync_enabled, last_sync_at);

COMMENT ON TABLE integrations.connections IS 'Tenant-specific integration connections with credentials';

-- =============================================================================
-- 3. SAP CONCUR INTEGRATION
-- =============================================================================

-- Expense reports synced from Concur
CREATE TABLE IF NOT EXISTS integrations.concur_expense_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),
    connection_id UUID NOT NULL REFERENCES integrations.connections(id),

    -- Concur identifiers
    concur_report_id TEXT NOT NULL,
    concur_report_key TEXT,
    concur_user_id TEXT NOT NULL,

    -- Report details
    report_name TEXT NOT NULL,
    report_number TEXT,
    purpose TEXT,
    report_date DATE NOT NULL,
    submit_date TIMESTAMPTZ,
    approval_status TEXT NOT NULL, -- NOT_SUBMITTED, SUBMITTED, APPROVED, REJECTED, etc.

    -- Financial
    total_amount DECIMAL(15,2),
    currency_code TEXT DEFAULT 'USD',
    reimbursement_amount DECIMAL(15,2),

    -- Workflow
    approver_user_id TEXT,
    approved_at TIMESTAMPTZ,
    paid_at TIMESTAMPTZ,
    payment_type TEXT,

    -- Policy
    policy_id TEXT,
    policy_name TEXT,
    has_policy_exceptions BOOLEAN DEFAULT false,

    -- Sync metadata
    raw_data JSONB,
    synced_at TIMESTAMPTZ DEFAULT now(),
    sync_version INT DEFAULT 1,

    -- Link to Odoo
    odoo_expense_report_id INT,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE (tenant_id, concur_report_id)
);

CREATE INDEX idx_concur_reports_tenant ON integrations.concur_expense_reports(tenant_id, report_date DESC);
CREATE INDEX idx_concur_reports_status ON integrations.concur_expense_reports(approval_status);
CREATE INDEX idx_concur_reports_user ON integrations.concur_expense_reports(concur_user_id);

-- Expense line items
CREATE TABLE IF NOT EXISTS integrations.concur_expense_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),
    report_id UUID NOT NULL REFERENCES integrations.concur_expense_reports(id) ON DELETE CASCADE,

    -- Concur identifiers
    concur_entry_id TEXT NOT NULL,

    -- Entry details
    expense_type_code TEXT NOT NULL,
    expense_type_name TEXT,
    transaction_date DATE NOT NULL,
    vendor_name TEXT,
    vendor_description TEXT,

    -- Financial
    transaction_amount DECIMAL(15,2) NOT NULL,
    transaction_currency TEXT,
    posted_amount DECIMAL(15,2),
    posted_currency TEXT DEFAULT 'USD',
    exchange_rate DECIMAL(15,6),

    -- Location
    location_name TEXT,
    location_country TEXT,

    -- Payment
    payment_type TEXT, -- CASH, CORPORATE_CARD, PERSONAL_CARD
    is_personal_expense BOOLEAN DEFAULT false,

    -- Receipt
    has_receipt BOOLEAN DEFAULT false,
    receipt_required BOOLEAN DEFAULT true,
    receipt_status TEXT, -- MISSING, ATTACHED, VERIFIED
    receipt_image_url TEXT,

    -- OCR processing
    ocr_processed BOOLEAN DEFAULT false,
    ocr_document_id UUID,
    ocr_confidence DECIMAL(5,4),

    -- Accounting
    allocation_json JSONB, -- Cost center, project, GL account allocations
    custom_fields JSONB,

    -- Sync metadata
    raw_data JSONB,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE (tenant_id, concur_entry_id)
);

CREATE INDEX idx_concur_entries_report ON integrations.concur_expense_entries(report_id);
CREATE INDEX idx_concur_entries_date ON integrations.concur_expense_entries(tenant_id, transaction_date DESC);
CREATE INDEX idx_concur_entries_vendor ON integrations.concur_expense_entries(vendor_name);

-- =============================================================================
-- 4. SAP ARIBA INTEGRATION
-- =============================================================================

-- Procurement requisitions
CREATE TABLE IF NOT EXISTS integrations.ariba_requisitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),
    connection_id UUID NOT NULL REFERENCES integrations.connections(id),

    -- Ariba identifiers
    ariba_req_id TEXT NOT NULL,
    ariba_req_number TEXT,

    -- Requisition details
    title TEXT NOT NULL,
    description TEXT,
    requester_id TEXT NOT NULL,
    requester_name TEXT,
    submit_date TIMESTAMPTZ,
    need_by_date DATE,

    -- Status
    status TEXT NOT NULL, -- DRAFT, SUBMITTED, APPROVED, ORDERED, RECEIVED, CLOSED
    approval_status TEXT,

    -- Financial
    total_amount DECIMAL(15,2),
    currency_code TEXT DEFAULT 'USD',
    budget_period TEXT,

    -- Supplier
    preferred_supplier_id TEXT,
    preferred_supplier_name TEXT,

    -- Contract reference
    contract_id TEXT,
    contract_number TEXT,

    -- Sync metadata
    raw_data JSONB,
    synced_at TIMESTAMPTZ DEFAULT now(),

    -- Link to Odoo
    odoo_purchase_order_id INT,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE (tenant_id, ariba_req_id)
);

CREATE INDEX idx_ariba_reqs_tenant ON integrations.ariba_requisitions(tenant_id, submit_date DESC);
CREATE INDEX idx_ariba_reqs_status ON integrations.ariba_requisitions(status);

-- Requisition line items
CREATE TABLE IF NOT EXISTS integrations.ariba_requisition_lines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),
    requisition_id UUID NOT NULL REFERENCES integrations.ariba_requisitions(id) ON DELETE CASCADE,

    -- Ariba identifiers
    ariba_line_id TEXT NOT NULL,
    line_number INT NOT NULL,

    -- Item details
    item_description TEXT NOT NULL,
    commodity_code TEXT,
    unit_of_measure TEXT,
    quantity DECIMAL(15,4) NOT NULL,
    unit_price DECIMAL(15,4),
    extended_price DECIMAL(15,2),

    -- Supplier/Catalog
    supplier_part_number TEXT,
    catalog_item_id TEXT,
    manufacturer TEXT,
    manufacturer_part_number TEXT,

    -- Delivery
    deliver_to_location TEXT,
    deliver_to_address JSONB,

    -- Accounting
    cost_center TEXT,
    project_code TEXT,
    gl_account TEXT,
    wbs_element TEXT,

    raw_data JSONB,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE (tenant_id, ariba_line_id)
);

CREATE INDEX idx_ariba_lines_req ON integrations.ariba_requisition_lines(requisition_id);

-- Purchase orders from Ariba
CREATE TABLE IF NOT EXISTS integrations.ariba_purchase_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),
    connection_id UUID NOT NULL REFERENCES integrations.connections(id),

    -- Ariba identifiers
    ariba_po_id TEXT NOT NULL,
    ariba_po_number TEXT NOT NULL,
    requisition_id UUID REFERENCES integrations.ariba_requisitions(id),

    -- PO details
    supplier_id TEXT NOT NULL,
    supplier_name TEXT NOT NULL,
    order_date DATE NOT NULL,
    delivery_date DATE,

    -- Status
    status TEXT NOT NULL, -- DRAFT, SENT, CONFIRMED, PARTIALLY_RECEIVED, RECEIVED, INVOICED, CLOSED
    acknowledgment_status TEXT,

    -- Financial
    total_amount DECIMAL(15,2) NOT NULL,
    currency_code TEXT DEFAULT 'USD',
    payment_terms TEXT,

    -- Contract
    contract_id TEXT,
    contract_number TEXT,

    raw_data JSONB,
    synced_at TIMESTAMPTZ DEFAULT now(),

    odoo_purchase_order_id INT,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE (tenant_id, ariba_po_id)
);

CREATE INDEX idx_ariba_po_tenant ON integrations.ariba_purchase_orders(tenant_id, order_date DESC);
CREATE INDEX idx_ariba_po_supplier ON integrations.ariba_purchase_orders(supplier_id);

-- Invoices from Ariba
CREATE TABLE IF NOT EXISTS integrations.ariba_invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),
    connection_id UUID NOT NULL REFERENCES integrations.connections(id),

    -- Ariba identifiers
    ariba_invoice_id TEXT NOT NULL,
    ariba_invoice_number TEXT NOT NULL,
    purchase_order_id UUID REFERENCES integrations.ariba_purchase_orders(id),

    -- Invoice details
    supplier_id TEXT NOT NULL,
    supplier_name TEXT NOT NULL,
    invoice_date DATE NOT NULL,
    due_date DATE,
    received_date TIMESTAMPTZ,

    -- Status
    status TEXT NOT NULL, -- RECEIVED, MATCHED, APPROVED, PAID, REJECTED, DISPUTED
    matching_status TEXT, -- FULL_MATCH, PARTIAL_MATCH, NO_MATCH, EXCEPTION

    -- Financial
    subtotal_amount DECIMAL(15,2),
    tax_amount DECIMAL(15,2),
    total_amount DECIMAL(15,2) NOT NULL,
    currency_code TEXT DEFAULT 'USD',

    -- OCR/AI processing
    ocr_processed BOOLEAN DEFAULT false,
    ocr_document_id UUID,
    ai_extracted_data JSONB,

    raw_data JSONB,
    synced_at TIMESTAMPTZ DEFAULT now(),

    odoo_invoice_id INT,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE (tenant_id, ariba_invoice_id)
);

CREATE INDEX idx_ariba_invoices_tenant ON integrations.ariba_invoices(tenant_id, invoice_date DESC);
CREATE INDEX idx_ariba_invoices_status ON integrations.ariba_invoices(status);

-- =============================================================================
-- 5. CHECKROOM PPM INTEGRATION (Equipment/Asset Management)
-- =============================================================================

-- Equipment catalog synced from Checkroom
CREATE TABLE IF NOT EXISTS integrations.checkroom_equipment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),
    connection_id UUID NOT NULL REFERENCES integrations.connections(id),

    -- Checkroom identifiers
    checkroom_item_id TEXT NOT NULL,
    checkroom_qr_code TEXT,
    checkroom_barcode TEXT,

    -- Equipment details
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,
    subcategory TEXT,
    brand TEXT,
    model TEXT,
    serial_number TEXT,

    -- Status
    status TEXT NOT NULL, -- AVAILABLE, CHECKED_OUT, MAINTENANCE, RETIRED, LOST
    condition TEXT, -- EXCELLENT, GOOD, FAIR, POOR

    -- Location
    current_location TEXT,
    home_location TEXT,
    gps_coordinates JSONB,

    -- Custody
    current_custodian_id TEXT,
    current_custodian_name TEXT,
    checked_out_at TIMESTAMPTZ,
    due_back_at TIMESTAMPTZ,
    is_overdue BOOLEAN DEFAULT false,

    -- Financial
    purchase_price DECIMAL(15,2),
    current_value DECIMAL(15,2),
    purchase_date DATE,
    warranty_expiry DATE,
    depreciation_rate DECIMAL(5,4),

    -- Maintenance
    last_maintenance_date DATE,
    next_maintenance_date DATE,
    maintenance_interval_days INT,

    -- Custom fields
    custom_fields JSONB DEFAULT '{}'::jsonb,
    tags TEXT[],

    -- Images
    image_urls TEXT[],
    thumbnail_url TEXT,

    raw_data JSONB,
    synced_at TIMESTAMPTZ DEFAULT now(),

    -- Link to Odoo
    odoo_equipment_id INT,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE (tenant_id, checkroom_item_id)
);

CREATE INDEX idx_checkroom_equipment_tenant ON integrations.checkroom_equipment(tenant_id);
CREATE INDEX idx_checkroom_equipment_status ON integrations.checkroom_equipment(status);
CREATE INDEX idx_checkroom_equipment_category ON integrations.checkroom_equipment(category);
CREATE INDEX idx_checkroom_equipment_custodian ON integrations.checkroom_equipment(current_custodian_id);
CREATE INDEX idx_checkroom_equipment_serial ON integrations.checkroom_equipment(serial_number);

-- Equipment bookings/reservations
CREATE TABLE IF NOT EXISTS integrations.checkroom_bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),
    equipment_id UUID NOT NULL REFERENCES integrations.checkroom_equipment(id) ON DELETE CASCADE,

    -- Checkroom identifiers
    checkroom_booking_id TEXT NOT NULL,

    -- Booking details
    booker_id TEXT NOT NULL,
    booker_name TEXT,
    booking_purpose TEXT,
    project_reference TEXT,

    -- Schedule
    start_datetime TIMESTAMPTZ NOT NULL,
    end_datetime TIMESTAMPTZ NOT NULL,
    actual_checkout_at TIMESTAMPTZ,
    actual_checkin_at TIMESTAMPTZ,

    -- Status
    status TEXT NOT NULL, -- PENDING, CONFIRMED, CHECKED_OUT, RETURNED, CANCELLED, OVERDUE

    -- Condition tracking
    checkout_condition TEXT,
    checkin_condition TEXT,
    damage_reported BOOLEAN DEFAULT false,
    damage_notes TEXT,

    raw_data JSONB,
    synced_at TIMESTAMPTZ DEFAULT now(),

    odoo_booking_id INT,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE (tenant_id, checkroom_booking_id)
);

CREATE INDEX idx_checkroom_bookings_equipment ON integrations.checkroom_bookings(equipment_id);
CREATE INDEX idx_checkroom_bookings_dates ON integrations.checkroom_bookings(start_datetime, end_datetime);
CREATE INDEX idx_checkroom_bookings_status ON integrations.checkroom_bookings(status);

-- Equipment incidents/damages
CREATE TABLE IF NOT EXISTS integrations.checkroom_incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),
    equipment_id UUID NOT NULL REFERENCES integrations.checkroom_equipment(id) ON DELETE CASCADE,
    booking_id UUID REFERENCES integrations.checkroom_bookings(id),

    -- Checkroom identifiers
    checkroom_incident_id TEXT,

    -- Incident details
    incident_type TEXT NOT NULL, -- DAMAGE, LOSS, THEFT, MALFUNCTION
    severity TEXT NOT NULL, -- LOW, MEDIUM, HIGH, CRITICAL
    description TEXT NOT NULL,
    reported_by_id TEXT,
    reported_by_name TEXT,
    reported_at TIMESTAMPTZ DEFAULT now(),

    -- Resolution
    status TEXT NOT NULL DEFAULT 'OPEN', -- OPEN, INVESTIGATING, RESOLVED, CLOSED
    resolution_notes TEXT,
    resolved_at TIMESTAMPTZ,
    resolved_by_id TEXT,

    -- Financial impact
    repair_cost DECIMAL(15,2),
    replacement_cost DECIMAL(15,2),
    insurance_claim_id TEXT,

    -- Evidence
    photo_urls TEXT[],
    document_urls TEXT[],

    raw_data JSONB,
    synced_at TIMESTAMPTZ DEFAULT now(),

    odoo_incident_id INT,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_checkroom_incidents_equipment ON integrations.checkroom_incidents(equipment_id);
CREATE INDEX idx_checkroom_incidents_status ON integrations.checkroom_incidents(status);
CREATE INDEX idx_checkroom_incidents_type ON integrations.checkroom_incidents(incident_type);

-- =============================================================================
-- 6. NOTION INTEGRATION
-- =============================================================================

-- Notion workspaces connected
CREATE TABLE IF NOT EXISTS integrations.notion_workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),
    connection_id UUID NOT NULL REFERENCES integrations.connections(id),

    -- Notion identifiers
    notion_workspace_id TEXT NOT NULL,
    notion_bot_id TEXT,

    -- Workspace details
    name TEXT NOT NULL,
    icon_url TEXT,

    -- Permissions
    can_read_content BOOLEAN DEFAULT true,
    can_update_content BOOLEAN DEFAULT false,
    can_insert_content BOOLEAN DEFAULT false,

    -- AI settings
    ai_indexing_enabled BOOLEAN DEFAULT true,
    ai_last_indexed_at TIMESTAMPTZ,
    rag_document_count INT DEFAULT 0,

    raw_data JSONB,
    synced_at TIMESTAMPTZ DEFAULT now(),

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE (tenant_id, notion_workspace_id)
);

CREATE INDEX idx_notion_workspaces_tenant ON integrations.notion_workspaces(tenant_id);

-- Notion databases synced
CREATE TABLE IF NOT EXISTS integrations.notion_databases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),
    workspace_id UUID NOT NULL REFERENCES integrations.notion_workspaces(id) ON DELETE CASCADE,

    -- Notion identifiers
    notion_database_id TEXT NOT NULL,
    notion_parent_id TEXT,
    notion_parent_type TEXT, -- workspace, page, database

    -- Database details
    title TEXT NOT NULL,
    description TEXT,
    icon_type TEXT, -- emoji, file, external
    icon_value TEXT,
    cover_url TEXT,

    -- Schema
    properties_schema JSONB NOT NULL, -- Full Notion properties definition
    property_names TEXT[], -- Extracted for quick lookup

    -- Sync configuration
    sync_enabled BOOLEAN DEFAULT true,
    sync_filter JSONB, -- Notion filter for partial sync
    last_edited_time TIMESTAMPTZ,

    -- Mapping to Odoo
    odoo_model TEXT, -- e.g., 'project.task', 'account.move'
    field_mappings JSONB, -- {notion_prop: odoo_field}

    -- AI/RAG integration
    ai_indexing_enabled BOOLEAN DEFAULT true,
    embedding_field TEXT, -- Which property to use for embeddings

    raw_data JSONB,
    synced_at TIMESTAMPTZ DEFAULT now(),

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE (tenant_id, notion_database_id)
);

CREATE INDEX idx_notion_databases_workspace ON integrations.notion_databases(workspace_id);
CREATE INDEX idx_notion_databases_odoo ON integrations.notion_databases(odoo_model) WHERE odoo_model IS NOT NULL;

-- Notion pages/records
CREATE TABLE IF NOT EXISTS integrations.notion_pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),
    database_id UUID REFERENCES integrations.notion_databases(id) ON DELETE CASCADE,
    workspace_id UUID NOT NULL REFERENCES integrations.notion_workspaces(id) ON DELETE CASCADE,

    -- Notion identifiers
    notion_page_id TEXT NOT NULL,
    notion_parent_id TEXT,
    notion_parent_type TEXT, -- workspace, page, database

    -- Page type
    is_database_page BOOLEAN DEFAULT false, -- True if this is a row in a database

    -- Page details
    title TEXT,
    icon_type TEXT,
    icon_value TEXT,
    cover_url TEXT,
    url TEXT,

    -- Properties (for database pages)
    properties JSONB,

    -- Content (markdown)
    content_markdown TEXT,
    content_blocks JSONB, -- Notion block structure

    -- Timestamps from Notion
    notion_created_time TIMESTAMPTZ,
    notion_last_edited_time TIMESTAMPTZ,
    notion_created_by TEXT,
    notion_last_edited_by TEXT,

    -- AI/RAG
    ai_indexed BOOLEAN DEFAULT false,
    ai_indexed_at TIMESTAMPTZ,
    embedding_vector vector(1536),
    rag_chunk_ids UUID[], -- Links to rag.chunks

    -- Odoo sync
    odoo_model TEXT,
    odoo_record_id INT,
    odoo_synced_at TIMESTAMPTZ,

    raw_data JSONB,
    synced_at TIMESTAMPTZ DEFAULT now(),

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE (tenant_id, notion_page_id)
);

CREATE INDEX idx_notion_pages_database ON integrations.notion_pages(database_id);
CREATE INDEX idx_notion_pages_workspace ON integrations.notion_pages(workspace_id);
CREATE INDEX idx_notion_pages_odoo ON integrations.notion_pages(odoo_model, odoo_record_id);
CREATE INDEX idx_notion_pages_edited ON integrations.notion_pages(notion_last_edited_time DESC);

-- =============================================================================
-- 7. OCR/AI DOCUMENT PROCESSING
-- =============================================================================

-- OCR processing queue
CREATE TABLE IF NOT EXISTS ocr.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),

    -- Source reference
    source_type TEXT NOT NULL, -- expense_receipt, invoice, contract, id_card, etc.
    source_integration TEXT, -- concur, ariba, notion, upload
    source_record_id UUID, -- FK to the source table

    -- Document details
    original_filename TEXT,
    file_url TEXT NOT NULL,
    file_size_bytes BIGINT,
    mime_type TEXT,
    page_count INT DEFAULT 1,

    -- Processing status
    status TEXT NOT NULL DEFAULT 'PENDING' CHECK (status IN (
        'PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'NEEDS_REVIEW'
    )),
    processing_started_at TIMESTAMPTZ,
    processing_completed_at TIMESTAMPTZ,
    retry_count INT DEFAULT 0,
    error_message TEXT,

    -- OCR results
    ocr_engine TEXT, -- paddleocr, tesseract, aws_textract, google_vision, azure_di
    ocr_raw_text TEXT,
    ocr_confidence DECIMAL(5,4),
    ocr_structured_data JSONB, -- Extracted key-value pairs

    -- AI extraction
    ai_model TEXT, -- gpt-4o-mini, claude-3, etc.
    ai_extracted_fields JSONB, -- {vendor: "...", amount: 123.45, date: "..."}
    ai_confidence JSONB, -- Confidence per field
    ai_suggestions JSONB, -- Suggested corrections

    -- Verification
    human_verified BOOLEAN DEFAULT false,
    verified_by UUID,
    verified_at TIMESTAMPTZ,
    corrections JSONB, -- Human corrections applied

    -- Final extracted data (merged OCR + AI + human corrections)
    final_data JSONB NOT NULL DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_ocr_documents_tenant ON ocr.documents(tenant_id, created_at DESC);
CREATE INDEX idx_ocr_documents_status ON ocr.documents(status) WHERE status IN ('PENDING', 'PROCESSING');
CREATE INDEX idx_ocr_documents_source ON ocr.documents(source_type, source_record_id);

COMMENT ON TABLE ocr.documents IS 'OCR document processing queue with AI extraction';

-- OCR extraction templates (for structured document types)
CREATE TABLE IF NOT EXISTS ocr.extraction_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES core.tenants(id), -- NULL = global template

    -- Template identity
    name TEXT NOT NULL,
    document_type TEXT NOT NULL, -- receipt, invoice, po, contract, etc.
    vendor_pattern TEXT, -- Regex to match vendor names

    -- Fields to extract
    fields JSONB NOT NULL, -- [{name, type, required, validation_regex, ai_prompt}]

    -- OCR regions (for form-based documents)
    regions JSONB, -- [{name, x, y, width, height}]

    -- AI instructions
    system_prompt TEXT,
    extraction_prompt_template TEXT,

    -- Validation rules
    validation_rules JSONB, -- Cross-field validations

    is_active BOOLEAN DEFAULT true,
    priority INT DEFAULT 100, -- Higher = preferred when multiple match

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE NULLS NOT DISTINCT (tenant_id, name)
);

CREATE INDEX idx_extraction_templates_type ON ocr.extraction_templates(document_type);

-- Vendor patterns learned from corrections (active learning)
CREATE TABLE IF NOT EXISTS ocr.vendor_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),

    -- Pattern details
    vendor_name_normalized TEXT NOT NULL,
    patterns TEXT[] NOT NULL, -- Array of regex patterns
    common_categories TEXT[], -- Common expense categories

    -- Expected fields
    expected_fields JSONB, -- {amount_position: "bottom_right", date_format: "MM/DD/YYYY"}

    -- Learning stats
    occurrence_count INT DEFAULT 1,
    correction_count INT DEFAULT 0,
    last_seen_at TIMESTAMPTZ DEFAULT now(),

    -- Confidence (increases with successful extractions)
    confidence_score DECIMAL(5,4) DEFAULT 0.5,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE (tenant_id, vendor_name_normalized)
);

CREATE INDEX idx_vendor_patterns_tenant ON ocr.vendor_patterns(tenant_id);
CREATE INDEX idx_vendor_patterns_confidence ON ocr.vendor_patterns(confidence_score DESC);

-- =============================================================================
-- 8. SYNC JOBS AND AUDIT
-- =============================================================================

-- Integration sync job history
CREATE TABLE IF NOT EXISTS integrations.sync_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),
    connection_id UUID NOT NULL REFERENCES integrations.connections(id),

    -- Job details
    job_type TEXT NOT NULL, -- full_sync, incremental, push, pull
    started_at TIMESTAMPTZ DEFAULT now(),
    completed_at TIMESTAMPTZ,

    -- Status
    status TEXT NOT NULL DEFAULT 'RUNNING' CHECK (status IN ('RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED')),
    error_message TEXT,

    -- Metrics
    records_fetched INT DEFAULT 0,
    records_created INT DEFAULT 0,
    records_updated INT DEFAULT 0,
    records_failed INT DEFAULT 0,

    -- Details
    sync_metadata JSONB DEFAULT '{}'::jsonb,
    failed_records JSONB DEFAULT '[]'::jsonb
);

CREATE INDEX idx_sync_jobs_connection ON integrations.sync_jobs(connection_id, started_at DESC);
CREATE INDEX idx_sync_jobs_status ON integrations.sync_jobs(status) WHERE status = 'RUNNING';

-- Webhook events from integrations
CREATE TABLE IF NOT EXISTS integrations.webhook_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),
    connection_id UUID NOT NULL REFERENCES integrations.connections(id),

    -- Webhook details
    event_type TEXT NOT NULL,
    event_id TEXT, -- External event ID
    received_at TIMESTAMPTZ DEFAULT now(),

    -- Payload
    headers JSONB,
    payload JSONB NOT NULL,
    signature TEXT,
    signature_valid BOOLEAN,

    -- Processing
    processed BOOLEAN DEFAULT false,
    processed_at TIMESTAMPTZ,
    processing_result JSONB
);

CREATE INDEX idx_webhook_events_connection ON integrations.webhook_events(connection_id, received_at DESC);
CREATE INDEX idx_webhook_events_pending ON integrations.webhook_events(received_at) WHERE NOT processed;

-- =============================================================================
-- 9. SEED INTEGRATION PROVIDERS
-- =============================================================================

INSERT INTO integrations.providers (code, name, provider_type, base_url, auth_type, oauth_config, api_version) VALUES
    ('sap_concur', 'SAP Concur', 'expense',
     'https://us.api.concursolutions.com',
     'oauth2',
     '{"authorize_url": "https://us-impl.api.concursolutions.com/oauth2/v0/authorize",
       "token_url": "https://us-impl.api.concursolutions.com/oauth2/v0/token",
       "scopes": ["openid", "user_read", "receipts.read", "expense.report.read", "expense.report.readwrite"]}'::jsonb,
     'v4.0'),

    ('sap_ariba', 'SAP Ariba', 'procurement',
     'https://api.ariba.com',
     'oauth2',
     '{"authorize_url": "https://api.ariba.com/v2/oauth/authorize",
       "token_url": "https://api.ariba.com/v2/oauth/token",
       "scopes": ["ProcurementRequisitionRead", "PurchaseOrderRead", "InvoiceRead"]}'::jsonb,
     'v2'),

    ('checkroom', 'Cheqroom', 'asset',
     'https://api.cheqroom.com/v2.5',
     'api_key',
     NULL,
     'v2.5'),

    ('notion', 'Notion', 'workspace',
     'https://api.notion.com',
     'oauth2',
     '{"authorize_url": "https://api.notion.com/v1/oauth/authorize",
       "token_url": "https://api.notion.com/v1/oauth/token",
       "scopes": []}'::jsonb,
     '2022-06-28'),

    ('paddleocr', 'PaddleOCR', 'ocr',
     'http://ocr.insightpulseai.net:8090',
     'api_key',
     NULL,
     'v1'),

    ('openai', 'OpenAI', 'ai',
     'https://api.openai.com/v1',
     'api_key',
     NULL,
     'v1')
ON CONFLICT (code) DO NOTHING;

-- =============================================================================
-- 10. OCR EXTRACTION TEMPLATES
-- =============================================================================

INSERT INTO ocr.extraction_templates (name, document_type, fields, system_prompt, extraction_prompt_template) VALUES
    ('Standard Receipt', 'receipt',
     '[
       {"name": "vendor_name", "type": "string", "required": true},
       {"name": "transaction_date", "type": "date", "required": true},
       {"name": "total_amount", "type": "decimal", "required": true},
       {"name": "tax_amount", "type": "decimal", "required": false},
       {"name": "payment_method", "type": "string", "required": false},
       {"name": "items", "type": "array", "required": false}
     ]'::jsonb,
     'You are an expert receipt OCR extraction system. Extract structured data from receipt images.',
     'Extract the following from this receipt:\n1. Vendor/merchant name\n2. Transaction date\n3. Total amount\n4. Tax amount (if shown)\n5. Payment method\n6. List of items (if readable)\n\nReturn as JSON.'),

    ('Standard Invoice', 'invoice',
     '[
       {"name": "vendor_name", "type": "string", "required": true},
       {"name": "vendor_address", "type": "string", "required": false},
       {"name": "invoice_number", "type": "string", "required": true},
       {"name": "invoice_date", "type": "date", "required": true},
       {"name": "due_date", "type": "date", "required": false},
       {"name": "subtotal", "type": "decimal", "required": false},
       {"name": "tax_amount", "type": "decimal", "required": false},
       {"name": "total_amount", "type": "decimal", "required": true},
       {"name": "currency", "type": "string", "required": false},
       {"name": "line_items", "type": "array", "required": false},
       {"name": "po_reference", "type": "string", "required": false}
     ]'::jsonb,
     'You are an expert invoice OCR extraction system. Extract structured data from invoice documents.',
     'Extract the following from this invoice:\n1. Vendor/supplier name and address\n2. Invoice number\n3. Invoice date and due date\n4. Subtotal, tax, and total amount\n5. Currency\n6. Line items (description, quantity, unit price, amount)\n7. PO reference if present\n\nReturn as JSON.')
ON CONFLICT DO NOTHING;

-- =============================================================================
-- 11. HELPER FUNCTIONS
-- =============================================================================

-- Get active connection for a tenant and provider
CREATE OR REPLACE FUNCTION integrations.get_connection(
    p_tenant_id UUID,
    p_provider_code TEXT
)
RETURNS integrations.connections
LANGUAGE sql STABLE
AS $func$
    SELECT c.*
    FROM integrations.connections c
    JOIN integrations.providers p ON p.id = c.provider_id
    WHERE c.tenant_id = p_tenant_id
      AND p.code = p_provider_code
      AND c.sync_enabled = true
    LIMIT 1;
$func$;

-- Queue document for OCR processing
CREATE OR REPLACE FUNCTION ocr.queue_document(
    p_tenant_id UUID,
    p_source_type TEXT,
    p_source_integration TEXT,
    p_source_record_id UUID,
    p_file_url TEXT,
    p_filename TEXT DEFAULT NULL,
    p_mime_type TEXT DEFAULT NULL
)
RETURNS UUID
LANGUAGE plpgsql
AS $func$
DECLARE
    v_doc_id UUID;
BEGIN
    INSERT INTO ocr.documents (
        tenant_id, source_type, source_integration, source_record_id,
        file_url, original_filename, mime_type, status
    ) VALUES (
        p_tenant_id, p_source_type, p_source_integration, p_source_record_id,
        p_file_url, p_filename, p_mime_type, 'PENDING'
    ) RETURNING id INTO v_doc_id;

    RETURN v_doc_id;
END;
$func$;

-- Sync Notion page to RAG
CREATE OR REPLACE FUNCTION integrations.sync_notion_to_rag(
    p_page_id UUID
)
RETURNS UUID
LANGUAGE plpgsql
AS $func$
DECLARE
    v_page integrations.notion_pages%ROWTYPE;
    v_doc_id UUID;
    v_chunk_id UUID;
BEGIN
    SELECT * INTO v_page FROM integrations.notion_pages WHERE id = p_page_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Notion page not found: %', p_page_id;
    END IF;

    -- Create or update RAG document
    INSERT INTO rag.documents (
        tenant_id, source_type, source_url, title, canonical_url
    ) VALUES (
        v_page.tenant_id,
        'notion',
        v_page.url,
        v_page.title,
        v_page.url
    )
    ON CONFLICT (tenant_id, source_type, source_url)
    DO UPDATE SET
        title = EXCLUDED.title,
        updated_at = now()
    RETURNING id INTO v_doc_id;

    -- Create chunk from content
    IF v_page.content_markdown IS NOT NULL AND length(v_page.content_markdown) > 0 THEN
        INSERT INTO rag.chunks (
            tenant_id, document_id, content, section_path
        ) VALUES (
            v_page.tenant_id,
            v_doc_id,
            v_page.content_markdown,
            v_page.title
        )
        ON CONFLICT DO NOTHING
        RETURNING id INTO v_chunk_id;

        -- Update page with chunk reference
        UPDATE integrations.notion_pages
        SET rag_chunk_ids = array_append(COALESCE(rag_chunk_ids, '{}'), v_chunk_id),
            ai_indexed = false,
            updated_at = now()
        WHERE id = p_page_id;
    END IF;

    RETURN v_doc_id;
END;
$func$;

COMMENT ON FUNCTION integrations.sync_notion_to_rag IS 'Sync a Notion page to the RAG document store';

COMMIT;
