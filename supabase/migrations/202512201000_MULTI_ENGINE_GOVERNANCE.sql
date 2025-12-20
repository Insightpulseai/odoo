-- =============================================================================
-- Multi-Engine Governance: Iceberg REST Catalog + Credential Vending
-- =============================================================================
-- Implements:
--   * Iceberg REST Catalog schema for multi-engine interoperability
--   * Credential vending with short-lived, scoped storage creds
--   * Central policy framework (RBAC/ABAC)
--   * OpenLineage audit and lineage tracking
-- Pattern: Unity Catalog / Databricks credential vending model
-- =============================================================================

BEGIN;

-- =============================================================================
-- SCHEMAS
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS catalog;    -- Iceberg REST Catalog
CREATE SCHEMA IF NOT EXISTS vault;      -- Credential vending
CREATE SCHEMA IF NOT EXISTS policy;     -- RBAC/ABAC policies
CREATE SCHEMA IF NOT EXISTS lineage;    -- OpenLineage compatible
CREATE SCHEMA IF NOT EXISTS integrations; -- External system integrations

COMMENT ON SCHEMA catalog IS 'Iceberg REST Catalog - central metadata for multi-engine governance';
COMMENT ON SCHEMA vault IS 'Credential vending - short-lived scoped storage credentials';
COMMENT ON SCHEMA policy IS 'Central policy framework - RBAC/ABAC at catalog objects';
COMMENT ON SCHEMA lineage IS 'OpenLineage compatible audit and data lineage tracking';
COMMENT ON SCHEMA integrations IS 'External system integrations (SAP, Notion, etc.)';

-- =============================================================================
-- 1. CATALOG SCHEMA - Iceberg REST Catalog Compatible
-- =============================================================================

-- Catalogs (top-level namespace, similar to Unity Catalog)
CREATE TABLE IF NOT EXISTS catalog.catalogs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    catalog_type TEXT NOT NULL DEFAULT 'iceberg' CHECK (catalog_type IN ('iceberg', 'delta', 'hudi', 'hive')),
    storage_root TEXT NOT NULL, -- s3://bucket/path or do://spaces/path
    default_format TEXT DEFAULT 'parquet',
    properties JSONB DEFAULT '{}'::jsonb,
    owner_principal UUID,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

COMMENT ON TABLE catalog.catalogs IS 'Top-level catalogs in the Iceberg REST namespace hierarchy';

-- Namespaces (schemas within a catalog)
CREATE TABLE IF NOT EXISTS catalog.namespaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    catalog_id UUID NOT NULL REFERENCES catalog.catalogs(id) ON DELETE CASCADE,
    namespace TEXT NOT NULL, -- Dot-separated: "finance.expense"
    parent_namespace TEXT, -- For nested namespaces
    location TEXT, -- Override storage location
    properties JSONB DEFAULT '{}'::jsonb,
    owner_principal UUID,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (catalog_id, namespace)
);

CREATE INDEX idx_namespaces_catalog ON catalog.namespaces(catalog_id);
CREATE INDEX idx_namespaces_parent ON catalog.namespaces(parent_namespace);

COMMENT ON TABLE catalog.namespaces IS 'Iceberg namespaces (schemas) within catalogs';

-- Tables (Iceberg table metadata)
CREATE TABLE IF NOT EXISTS catalog.tables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    catalog_id UUID NOT NULL REFERENCES catalog.catalogs(id) ON DELETE CASCADE,
    namespace_id UUID NOT NULL REFERENCES catalog.namespaces(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    table_type TEXT NOT NULL DEFAULT 'MANAGED' CHECK (table_type IN ('MANAGED', 'EXTERNAL')),
    format TEXT NOT NULL DEFAULT 'iceberg' CHECK (format IN ('iceberg', 'delta', 'parquet', 'orc', 'avro')),

    -- Iceberg-specific metadata
    metadata_location TEXT, -- Path to current metadata.json
    current_snapshot_id BIGINT,
    current_schema_id INT,
    last_sequence_number BIGINT DEFAULT 0,

    -- Table properties
    location TEXT NOT NULL, -- Full path: s3://bucket/warehouse/ns/table
    schema_json JSONB, -- Iceberg schema definition
    partition_spec_json JSONB, -- Partition specification
    sort_order_json JSONB, -- Sort order specification
    properties JSONB DEFAULT '{}'::jsonb,

    -- Governance
    owner_principal UUID,
    sensitivity_level TEXT DEFAULT 'internal' CHECK (sensitivity_level IN ('public', 'internal', 'confidential', 'restricted')),
    retention_days INT,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    deleted_at TIMESTAMPTZ,

    UNIQUE (catalog_id, namespace_id, name)
);

CREATE INDEX idx_tables_namespace ON catalog.tables(namespace_id);
CREATE INDEX idx_tables_catalog ON catalog.tables(catalog_id);
CREATE INDEX idx_tables_location ON catalog.tables(location);
CREATE INDEX idx_tables_sensitivity ON catalog.tables(sensitivity_level);

COMMENT ON TABLE catalog.tables IS 'Iceberg table registry with metadata pointers and governance properties';

-- Snapshots (Iceberg table version history)
CREATE TABLE IF NOT EXISTS catalog.snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_id UUID NOT NULL REFERENCES catalog.tables(id) ON DELETE CASCADE,
    snapshot_id BIGINT NOT NULL,
    parent_snapshot_id BIGINT,
    sequence_number BIGINT NOT NULL,

    -- Snapshot metadata
    timestamp_ms BIGINT NOT NULL,
    operation TEXT NOT NULL, -- append, overwrite, replace, delete
    summary JSONB, -- added-records, deleted-records, etc.
    manifest_list TEXT NOT NULL, -- Path to manifest-list file
    schema_id INT,

    created_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE (table_id, snapshot_id)
);

CREATE INDEX idx_snapshots_table ON catalog.snapshots(table_id, sequence_number DESC);
CREATE INDEX idx_snapshots_timestamp ON catalog.snapshots(timestamp_ms DESC);

COMMENT ON TABLE catalog.snapshots IS 'Iceberg snapshot history for time travel and auditing';

-- Views (virtual tables in the catalog)
CREATE TABLE IF NOT EXISTS catalog.views (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    catalog_id UUID NOT NULL REFERENCES catalog.catalogs(id) ON DELETE CASCADE,
    namespace_id UUID NOT NULL REFERENCES catalog.namespaces(id) ON DELETE CASCADE,
    name TEXT NOT NULL,

    -- View definition
    sql_text TEXT NOT NULL,
    dialect TEXT DEFAULT 'trino', -- trino, spark-sql, presto
    schema_json JSONB,

    -- Properties
    properties JSONB DEFAULT '{}'::jsonb,
    owner_principal UUID,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE (catalog_id, namespace_id, name)
);

CREATE INDEX idx_views_namespace ON catalog.views(namespace_id);

COMMENT ON TABLE catalog.views IS 'Virtual views defined in the catalog (engine-agnostic SQL)';

-- =============================================================================
-- 2. VAULT SCHEMA - Credential Vending
-- =============================================================================

-- Service principals (engines, applications, users)
CREATE TABLE IF NOT EXISTS vault.principals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES core.tenants(id),
    principal_type TEXT NOT NULL CHECK (principal_type IN ('engine', 'application', 'user', 'service_account')),
    name TEXT NOT NULL,
    description TEXT,

    -- Identity attributes (for ABAC)
    attributes JSONB DEFAULT '{}'::jsonb, -- {department: "finance", region: "APAC"}

    -- Credentials (encrypted or reference)
    client_id TEXT UNIQUE,
    client_secret_hash TEXT, -- bcrypt hash
    public_key TEXT, -- For JWT/JWKS verification

    -- Status
    is_active BOOLEAN DEFAULT true,
    last_auth_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_principals_tenant ON vault.principals(tenant_id) WHERE tenant_id IS NOT NULL;
CREATE INDEX idx_principals_type ON vault.principals(principal_type);
CREATE INDEX idx_principals_client ON vault.principals(client_id) WHERE client_id IS NOT NULL;

COMMENT ON TABLE vault.principals IS 'Service principals for credential vending and access control';

-- Storage configurations (backends for credential vending)
CREATE TABLE IF NOT EXISTS vault.storage_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    storage_type TEXT NOT NULL CHECK (storage_type IN ('s3', 'azure_blob', 'gcs', 'do_spaces', 'minio')),

    -- Connection details (encrypted)
    endpoint TEXT, -- For non-AWS S3-compatible (DO Spaces, MinIO)
    region TEXT,
    bucket TEXT NOT NULL,
    prefix TEXT,

    -- Master credentials (encrypted, never vended directly)
    access_key_encrypted TEXT,
    secret_key_encrypted TEXT,

    -- Vending configuration
    vending_enabled BOOLEAN DEFAULT true,
    default_ttl_seconds INT DEFAULT 3600, -- 1 hour default
    max_ttl_seconds INT DEFAULT 43200, -- 12 hours max

    properties JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

COMMENT ON TABLE vault.storage_configs IS 'Storage backend configurations for credential vending';

-- Vended credentials (audit log of issued credentials)
CREATE TABLE IF NOT EXISTS vault.vended_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    principal_id UUID NOT NULL REFERENCES vault.principals(id),
    storage_config_id UUID NOT NULL REFERENCES vault.storage_configs(id),

    -- What was vended
    credential_type TEXT NOT NULL CHECK (credential_type IN ('sts_token', 'presigned_url', 'oauth_token')),
    operation TEXT NOT NULL CHECK (operation IN ('READ', 'WRITE', 'READ_WRITE')),

    -- Scope
    table_ids UUID[], -- Tables this credential grants access to
    path_prefixes TEXT[], -- Storage paths this credential is scoped to

    -- Credential lifecycle
    issued_at TIMESTAMPTZ DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,
    revocation_reason TEXT,

    -- Request context
    request_ip INET,
    user_agent TEXT,
    request_metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_vended_creds_principal ON vault.vended_credentials(principal_id);
CREATE INDEX idx_vended_creds_expires ON vault.vended_credentials(expires_at) WHERE revoked_at IS NULL;
CREATE INDEX idx_vended_creds_issued ON vault.vended_credentials(issued_at DESC);

COMMENT ON TABLE vault.vended_credentials IS 'Audit log of all vended credentials for compliance and debugging';

-- =============================================================================
-- 3. POLICY SCHEMA - RBAC/ABAC
-- =============================================================================

-- Roles
CREATE TABLE IF NOT EXISTS policy.roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES core.tenants(id),
    name TEXT NOT NULL,
    description TEXT,
    is_system_role BOOLEAN DEFAULT false,

    -- Role hierarchy
    parent_role_id UUID REFERENCES policy.roles(id),

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE NULLS NOT DISTINCT (tenant_id, name)
);

CREATE INDEX idx_roles_tenant ON policy.roles(tenant_id);
CREATE INDEX idx_roles_parent ON policy.roles(parent_role_id);

COMMENT ON TABLE policy.roles IS 'Role definitions for RBAC';

-- Role assignments (principal -> role)
CREATE TABLE IF NOT EXISTS policy.role_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    principal_id UUID NOT NULL REFERENCES vault.principals(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES policy.roles(id) ON DELETE CASCADE,

    -- Scope (optional - for scoped role grants)
    catalog_id UUID REFERENCES catalog.catalogs(id),
    namespace_id UUID REFERENCES catalog.namespaces(id),
    table_id UUID REFERENCES catalog.tables(id),

    granted_by UUID REFERENCES vault.principals(id),
    granted_at TIMESTAMPTZ DEFAULT now(),
    expires_at TIMESTAMPTZ,

    UNIQUE (principal_id, role_id, catalog_id, namespace_id, table_id)
);

CREATE INDEX idx_role_assignments_principal ON policy.role_assignments(principal_id);
CREATE INDEX idx_role_assignments_role ON policy.role_assignments(role_id);

COMMENT ON TABLE policy.role_assignments IS 'Role assignments to principals with optional scope';

-- Privileges (permissions on catalog objects)
CREATE TABLE IF NOT EXISTS policy.privileges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id UUID NOT NULL REFERENCES policy.roles(id) ON DELETE CASCADE,

    -- Object reference (one of these must be set)
    catalog_id UUID REFERENCES catalog.catalogs(id),
    namespace_id UUID REFERENCES catalog.namespaces(id),
    table_id UUID REFERENCES catalog.tables(id),

    -- Privilege type
    privilege TEXT NOT NULL CHECK (privilege IN (
        'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'TRUNCATE',
        'CREATE_TABLE', 'DROP_TABLE', 'ALTER_TABLE',
        'CREATE_NAMESPACE', 'DROP_NAMESPACE',
        'MANAGE_GRANTS', 'ALL_PRIVILEGES'
    )),

    -- ABAC conditions (optional)
    condition_json JSONB, -- {column: "region", op: "in", values: ["APAC", "EMEA"]}

    with_grant_option BOOLEAN DEFAULT false,

    created_at TIMESTAMPTZ DEFAULT now(),

    -- At least one object must be specified
    CHECK (catalog_id IS NOT NULL OR namespace_id IS NOT NULL OR table_id IS NOT NULL)
);

CREATE INDEX idx_privileges_role ON policy.privileges(role_id);
CREATE INDEX idx_privileges_table ON policy.privileges(table_id) WHERE table_id IS NOT NULL;
CREATE INDEX idx_privileges_namespace ON policy.privileges(namespace_id) WHERE namespace_id IS NOT NULL;

COMMENT ON TABLE policy.privileges IS 'Privilege grants on catalog objects';

-- Row-level policies (fine-grained access control)
CREATE TABLE IF NOT EXISTS policy.row_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_id UUID NOT NULL REFERENCES catalog.tables(id) ON DELETE CASCADE,
    name TEXT NOT NULL,

    -- Policy definition
    filter_expression TEXT NOT NULL, -- SQL WHERE clause: "tenant_id = current_tenant()"
    policy_type TEXT NOT NULL DEFAULT 'FILTER' CHECK (policy_type IN ('FILTER', 'MASK')),

    -- Scope
    apply_to_roles UUID[], -- Empty = applies to all roles
    exclude_roles UUID[], -- Roles exempt from this policy

    is_enabled BOOLEAN DEFAULT true,
    priority INT DEFAULT 100, -- Higher = evaluated first

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE (table_id, name)
);

CREATE INDEX idx_row_policies_table ON policy.row_policies(table_id);

COMMENT ON TABLE policy.row_policies IS 'Row-level security policies applied at query time';

-- Column masks (data masking policies)
CREATE TABLE IF NOT EXISTS policy.column_masks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_id UUID NOT NULL REFERENCES catalog.tables(id) ON DELETE CASCADE,
    column_name TEXT NOT NULL,

    -- Masking function
    mask_function TEXT NOT NULL, -- SHA256, REDACT, PARTIAL, NULLIFY
    mask_parameters JSONB DEFAULT '{}'::jsonb, -- {show_last: 4}

    -- Scope
    apply_to_roles UUID[], -- Roles that see masked data
    exclude_roles UUID[], -- Roles that see original data

    is_enabled BOOLEAN DEFAULT true,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE (table_id, column_name)
);

CREATE INDEX idx_column_masks_table ON policy.column_masks(table_id);

COMMENT ON TABLE policy.column_masks IS 'Column-level data masking policies';

-- =============================================================================
-- 4. LINEAGE SCHEMA - OpenLineage Compatible
-- =============================================================================

-- Datasets (OpenLineage dataset representation)
CREATE TABLE IF NOT EXISTS lineage.datasets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    namespace TEXT NOT NULL, -- e.g., "postgres://localhost/db" or "s3://bucket"
    name TEXT NOT NULL, -- Fully qualified name

    -- Optional link to catalog table
    catalog_table_id UUID REFERENCES catalog.tables(id),

    -- Dataset metadata
    facets JSONB DEFAULT '{}'::jsonb, -- OpenLineage facets (schema, stats, etc.)

    first_seen_at TIMESTAMPTZ DEFAULT now(),
    last_seen_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE (namespace, name)
);

CREATE INDEX idx_datasets_catalog ON lineage.datasets(catalog_table_id) WHERE catalog_table_id IS NOT NULL;
CREATE INDEX idx_datasets_namespace ON lineage.datasets(namespace);

COMMENT ON TABLE lineage.datasets IS 'OpenLineage dataset registry for lineage tracking';

-- Jobs (OpenLineage job representation)
CREATE TABLE IF NOT EXISTS lineage.jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    namespace TEXT NOT NULL, -- e.g., "spark://cluster" or "trino://coordinator"
    name TEXT NOT NULL, -- Job/query name

    -- Job metadata
    job_type TEXT, -- spark, trino, dbt, airflow, etc.
    owner_principal_id UUID REFERENCES vault.principals(id),
    facets JSONB DEFAULT '{}'::jsonb,

    first_seen_at TIMESTAMPTZ DEFAULT now(),
    last_seen_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE (namespace, name)
);

CREATE INDEX idx_jobs_namespace ON lineage.jobs(namespace);
CREATE INDEX idx_jobs_type ON lineage.jobs(job_type);

COMMENT ON TABLE lineage.jobs IS 'OpenLineage job registry';

-- Runs (job executions with input/output lineage)
CREATE TABLE IF NOT EXISTS lineage.runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES lineage.jobs(id),
    run_id UUID NOT NULL UNIQUE, -- OpenLineage run UUID

    -- Execution details
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    state TEXT NOT NULL DEFAULT 'RUNNING' CHECK (state IN ('RUNNING', 'COMPLETE', 'FAILED', 'ABORTED')),

    -- Context
    principal_id UUID REFERENCES vault.principals(id),
    engine TEXT, -- spark-3.4, trino-433, etc.
    query_text TEXT, -- Actual SQL/Spark code (truncated)

    -- Performance
    input_rows BIGINT,
    output_rows BIGINT,
    bytes_read BIGINT,
    bytes_written BIGINT,

    -- Facets
    facets JSONB DEFAULT '{}'::jsonb,
    error_message TEXT,

    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_runs_job ON lineage.runs(job_id, started_at DESC);
CREATE INDEX idx_runs_state ON lineage.runs(state) WHERE state = 'RUNNING';
CREATE INDEX idx_runs_principal ON lineage.runs(principal_id);

COMMENT ON TABLE lineage.runs IS 'OpenLineage run events with execution metadata';

-- Lineage edges (dataset -> run -> dataset relationships)
CREATE TABLE IF NOT EXISTS lineage.edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES lineage.runs(id) ON DELETE CASCADE,

    -- Direction
    direction TEXT NOT NULL CHECK (direction IN ('INPUT', 'OUTPUT')),

    -- Dataset reference
    dataset_id UUID NOT NULL REFERENCES lineage.datasets(id),

    -- Edge metadata
    facets JSONB DEFAULT '{}'::jsonb, -- Column-level lineage, transformations

    created_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE (run_id, direction, dataset_id)
);

CREATE INDEX idx_edges_run ON lineage.edges(run_id);
CREATE INDEX idx_edges_dataset ON lineage.edges(dataset_id, direction);

COMMENT ON TABLE lineage.edges IS 'OpenLineage input/output edges connecting runs to datasets';

-- Audit log (all governance-related events)
CREATE TABLE IF NOT EXISTS lineage.audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_time TIMESTAMPTZ DEFAULT now(),

    -- Actor
    principal_id UUID REFERENCES vault.principals(id),
    principal_name TEXT,

    -- Action
    action TEXT NOT NULL, -- CREATE_TABLE, GRANT_PRIVILEGE, VEND_CREDENTIAL, etc.
    resource_type TEXT, -- catalog, namespace, table, role, credential
    resource_id UUID,
    resource_name TEXT,

    -- Context
    engine TEXT,
    request_ip INET,
    user_agent TEXT,

    -- Details
    before_state JSONB,
    after_state JSONB,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_audit_log_time ON lineage.audit_log(event_time DESC);
CREATE INDEX idx_audit_log_principal ON lineage.audit_log(principal_id);
CREATE INDEX idx_audit_log_resource ON lineage.audit_log(resource_type, resource_id);
CREATE INDEX idx_audit_log_action ON lineage.audit_log(action);

-- Partition by month for efficient retention
-- Note: Implement as partitioned table in production
COMMENT ON TABLE lineage.audit_log IS 'Comprehensive audit log for all governance events';

-- =============================================================================
-- 5. CREDENTIAL VENDING FUNCTIONS
-- =============================================================================

-- Vend temporary table credentials (main entry point)
CREATE OR REPLACE FUNCTION vault.vend_table_credentials(
    p_principal_id UUID,
    p_table_ids UUID[],
    p_operation TEXT DEFAULT 'READ',
    p_ttl_seconds INT DEFAULT 3600,
    p_request_ip INET DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL
)
RETURNS TABLE (
    credential_id UUID,
    storage_type TEXT,
    endpoint TEXT,
    bucket TEXT,
    path_prefixes TEXT[],
    access_key TEXT,
    secret_key TEXT,
    session_token TEXT,
    expires_at TIMESTAMPTZ
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $func$
DECLARE
    v_principal vault.principals%ROWTYPE;
    v_cred_id UUID;
    v_expires TIMESTAMPTZ;
    v_paths TEXT[];
    v_storage vault.storage_configs%ROWTYPE;
BEGIN
    -- Validate principal
    SELECT * INTO v_principal FROM vault.principals WHERE id = p_principal_id AND is_active;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Invalid or inactive principal: %', p_principal_id;
    END IF;

    -- Check privileges for all requested tables
    IF NOT vault.check_table_access(p_principal_id, p_table_ids, p_operation) THEN
        RAISE EXCEPTION 'Access denied: principal % lacks % privilege on requested tables',
            p_principal_id, p_operation;
    END IF;

    -- Get storage paths for tables
    SELECT array_agg(DISTINCT t.location) INTO v_paths
    FROM catalog.tables t
    WHERE t.id = ANY(p_table_ids);

    -- Get storage config from first table's location
    SELECT sc.* INTO v_storage
    FROM vault.storage_configs sc
    JOIN catalog.tables t ON t.location LIKE sc.bucket || '%'
    WHERE t.id = p_table_ids[1]
    LIMIT 1;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'No storage configuration found for requested tables';
    END IF;

    -- Calculate expiration
    v_expires := now() + (LEAST(p_ttl_seconds, v_storage.max_ttl_seconds) * interval '1 second');

    -- Record the vended credential
    INSERT INTO vault.vended_credentials (
        principal_id, storage_config_id, credential_type, operation,
        table_ids, path_prefixes, expires_at, request_ip, user_agent
    ) VALUES (
        p_principal_id, v_storage.id, 'sts_token', p_operation,
        p_table_ids, v_paths, v_expires, p_request_ip, p_user_agent
    ) RETURNING id INTO v_cred_id;

    -- Log audit event
    INSERT INTO lineage.audit_log (
        principal_id, principal_name, action, resource_type,
        resource_id, request_ip, user_agent, metadata
    ) VALUES (
        p_principal_id, v_principal.name, 'VEND_CREDENTIAL', 'table',
        p_table_ids[1], p_request_ip, p_user_agent,
        jsonb_build_object(
            'credential_id', v_cred_id,
            'operation', p_operation,
            'table_count', array_length(p_table_ids, 1),
            'ttl_seconds', p_ttl_seconds
        )
    );

    -- Return credential info
    -- NOTE: In production, generate actual STS tokens via AWS/DO API
    -- This returns placeholders that would be replaced by the vending service
    RETURN QUERY
    SELECT
        v_cred_id,
        v_storage.storage_type,
        v_storage.endpoint,
        v_storage.bucket,
        v_paths,
        '<ACCESS_KEY_PLACEHOLDER>' AS access_key,
        '<SECRET_KEY_PLACEHOLDER>' AS secret_key,
        '<SESSION_TOKEN_PLACEHOLDER>' AS session_token,
        v_expires;
END;
$func$;

COMMENT ON FUNCTION vault.vend_table_credentials IS
'Vend short-lived storage credentials scoped to specific tables - Databricks credential vending pattern';

-- Check table access helper
CREATE OR REPLACE FUNCTION vault.check_table_access(
    p_principal_id UUID,
    p_table_ids UUID[],
    p_operation TEXT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
AS $func$
DECLARE
    v_required_priv TEXT;
    v_missing_count INT;
BEGIN
    -- Map operation to privilege
    v_required_priv := CASE p_operation
        WHEN 'READ' THEN 'SELECT'
        WHEN 'WRITE' THEN 'INSERT'
        WHEN 'READ_WRITE' THEN 'SELECT' -- Will also check INSERT
        ELSE 'SELECT'
    END;

    -- Count tables without required privilege
    SELECT COUNT(*) INTO v_missing_count
    FROM unnest(p_table_ids) t_id
    WHERE NOT EXISTS (
        SELECT 1
        FROM policy.privileges p
        JOIN policy.role_assignments ra ON ra.role_id = p.role_id
        WHERE ra.principal_id = p_principal_id
          AND (p.table_id = t_id OR p.namespace_id = (SELECT namespace_id FROM catalog.tables WHERE id = t_id))
          AND (p.privilege = v_required_priv OR p.privilege = 'ALL_PRIVILEGES')
          AND (ra.expires_at IS NULL OR ra.expires_at > now())
    );

    IF v_missing_count > 0 AND p_operation = 'READ_WRITE' THEN
        -- Also check INSERT for READ_WRITE
        SELECT COUNT(*) INTO v_missing_count
        FROM unnest(p_table_ids) t_id
        WHERE NOT EXISTS (
            SELECT 1
            FROM policy.privileges p
            JOIN policy.role_assignments ra ON ra.role_id = p.role_id
            WHERE ra.principal_id = p_principal_id
              AND (p.table_id = t_id OR p.namespace_id = (SELECT namespace_id FROM catalog.tables WHERE id = t_id))
              AND (p.privilege IN ('SELECT', 'INSERT') OR p.privilege = 'ALL_PRIVILEGES')
              AND (ra.expires_at IS NULL OR ra.expires_at > now())
        );
    END IF;

    RETURN v_missing_count = 0;
END;
$func$;

COMMENT ON FUNCTION vault.check_table_access IS 'Check if principal has required privileges on tables';

-- Revoke credential
CREATE OR REPLACE FUNCTION vault.revoke_credential(
    p_credential_id UUID,
    p_reason TEXT DEFAULT 'Manual revocation'
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $func$
BEGIN
    UPDATE vault.vended_credentials
    SET revoked_at = now(), revocation_reason = p_reason
    WHERE id = p_credential_id AND revoked_at IS NULL;

    RETURN FOUND;
END;
$func$;

-- =============================================================================
-- 6. ICEBERG REST CATALOG API FUNCTIONS
-- =============================================================================

-- List namespaces (GET /v1/namespaces)
CREATE OR REPLACE FUNCTION catalog.list_namespaces(
    p_catalog_name TEXT,
    p_parent TEXT DEFAULT NULL
)
RETURNS TABLE (namespace TEXT[])
LANGUAGE sql STABLE
AS $func$
    SELECT string_to_array(n.namespace, '.')
    FROM catalog.namespaces n
    JOIN catalog.catalogs c ON c.id = n.catalog_id
    WHERE c.name = p_catalog_name
      AND (p_parent IS NULL OR n.parent_namespace = p_parent);
$func$;

-- Get namespace (GET /v1/namespaces/{namespace})
CREATE OR REPLACE FUNCTION catalog.get_namespace(
    p_catalog_name TEXT,
    p_namespace TEXT
)
RETURNS JSONB
LANGUAGE sql STABLE
AS $func$
    SELECT jsonb_build_object(
        'namespace', string_to_array(n.namespace, '.'),
        'properties', n.properties
    )
    FROM catalog.namespaces n
    JOIN catalog.catalogs c ON c.id = n.catalog_id
    WHERE c.name = p_catalog_name AND n.namespace = p_namespace;
$func$;

-- List tables (GET /v1/namespaces/{namespace}/tables)
CREATE OR REPLACE FUNCTION catalog.list_tables(
    p_catalog_name TEXT,
    p_namespace TEXT
)
RETURNS TABLE (
    namespace TEXT[],
    name TEXT
)
LANGUAGE sql STABLE
AS $func$
    SELECT
        string_to_array(n.namespace, '.'),
        t.name
    FROM catalog.tables t
    JOIN catalog.namespaces n ON n.id = t.namespace_id
    JOIN catalog.catalogs c ON c.id = n.catalog_id
    WHERE c.name = p_catalog_name
      AND n.namespace = p_namespace
      AND t.deleted_at IS NULL;
$func$;

-- Load table (GET /v1/namespaces/{namespace}/tables/{table})
CREATE OR REPLACE FUNCTION catalog.load_table(
    p_catalog_name TEXT,
    p_namespace TEXT,
    p_table_name TEXT
)
RETURNS JSONB
LANGUAGE sql STABLE
AS $func$
    SELECT jsonb_build_object(
        'metadata-location', t.metadata_location,
        'metadata', jsonb_build_object(
            'format-version', 2,
            'table-uuid', t.id,
            'location', t.location,
            'last-sequence-number', t.last_sequence_number,
            'last-updated-ms', extract(epoch from t.updated_at) * 1000,
            'last-column-id', (t.schema_json->>'last-column-id')::int,
            'current-schema-id', t.current_schema_id,
            'schemas', COALESCE((t.schema_json->'schemas'), '[]'::jsonb),
            'current-snapshot-id', t.current_snapshot_id,
            'snapshots', (
                SELECT jsonb_agg(jsonb_build_object(
                    'snapshot-id', s.snapshot_id,
                    'parent-snapshot-id', s.parent_snapshot_id,
                    'sequence-number', s.sequence_number,
                    'timestamp-ms', s.timestamp_ms,
                    'summary', s.summary,
                    'manifest-list', s.manifest_list,
                    'schema-id', s.schema_id
                ) ORDER BY s.sequence_number DESC)
                FROM catalog.snapshots s WHERE s.table_id = t.id
            ),
            'partition-specs', COALESCE((t.partition_spec_json->'partition-specs'), '[]'::jsonb),
            'sort-orders', COALESCE((t.sort_order_json->'sort-orders'), '[]'::jsonb),
            'properties', t.properties
        ),
        'config', jsonb_build_object()
    )
    FROM catalog.tables t
    JOIN catalog.namespaces n ON n.id = t.namespace_id
    JOIN catalog.catalogs c ON c.id = n.catalog_id
    WHERE c.name = p_catalog_name
      AND n.namespace = p_namespace
      AND t.name = p_table_name
      AND t.deleted_at IS NULL;
$func$;

COMMENT ON FUNCTION catalog.load_table IS 'Iceberg REST Catalog: Load table metadata';

-- =============================================================================
-- 7. SEED SYSTEM ROLES
-- =============================================================================

INSERT INTO policy.roles (name, description, is_system_role) VALUES
    ('catalog_admin', 'Full access to all catalog operations', true),
    ('data_engineer', 'Create/modify tables and namespaces', true),
    ('data_analyst', 'Read access to tables, create views', true),
    ('data_steward', 'Manage policies and data governance', true),
    ('engine_reader', 'Read-only access for query engines (Trino, Spark)', true),
    ('engine_writer', 'Read-write access for ETL engines', true)
ON CONFLICT DO NOTHING;

-- =============================================================================
-- 8. SEED DEFAULT CATALOG AND ENGINE PRINCIPALS
-- =============================================================================

-- Default catalog for the data lake
INSERT INTO catalog.catalogs (name, catalog_type, storage_root, properties) VALUES
    ('insightpulse', 'iceberg', 's3://insightpulse-lake/',
     '{"description": "InsightPulseAI data lake catalog"}'::jsonb)
ON CONFLICT (name) DO NOTHING;

-- Engine principals
INSERT INTO vault.principals (principal_type, name, description, attributes, client_id) VALUES
    ('engine', 'trino-coordinator', 'Trino query engine', '{"engine": "trino", "version": "433"}'::jsonb, 'trino-engine-001'),
    ('engine', 'spark-etl', 'Spark ETL jobs', '{"engine": "spark", "version": "3.5"}'::jsonb, 'spark-engine-001'),
    ('engine', 'clickhouse-olap', 'ClickHouse OLAP engine', '{"engine": "clickhouse", "version": "24.1"}'::jsonb, 'clickhouse-engine-001'),
    ('engine', 'duckdb-adhoc', 'DuckDB ad-hoc queries', '{"engine": "duckdb", "version": "0.10"}'::jsonb, 'duckdb-engine-001'),
    ('engine', 'flink-streaming', 'Flink streaming jobs', '{"engine": "flink", "version": "1.18"}'::jsonb, 'flink-engine-001'),
    ('application', 'superset-bi', 'Superset BI dashboards', '{"app": "superset"}'::jsonb, 'superset-app-001'),
    ('application', 'n8n-automation', 'n8n workflow automation', '{"app": "n8n"}'::jsonb, 'n8n-app-001')
ON CONFLICT DO NOTHING;

COMMIT;
