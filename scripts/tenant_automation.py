#!/usr/bin/env python3
"""
InsightPulse AI - Multi-Tenant ERP SaaS Automation System
=========================================================

This module provides:
1. Tenant provisioning (create/clone databases)
2. Database introspection (schema analysis)
3. Auto-documentation (DBML, ERD, Markdown)
4. Superset workspace automation

Architecture:
- Control Plane DB: insightpulse_master (manages all tenants)
- Template DB: insightpulse_template (cloned for new tenants)
- Tenant DBs: insightpulse_{tenant_code} (isolated per tenant)

Usage:
    from tenant_automation import TenantManager, SchemaIntrospector
    
    # Create new tenant
    manager = TenantManager()
    tenant = await manager.create_tenant("acme-corp", "Acme Corporation")
    
    # Introspect and document
    introspector = SchemaIntrospector(tenant.db_connection_string)
    dbml = await introspector.generate_dbml()
    docs = await introspector.generate_documentation()
"""

import os
import json
import asyncio
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path

import asyncpg
from cryptography.fernet import Fernet
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class Config:
    """Platform configuration from environment variables"""
    
    # Control Plane Database
    master_db_host: str = field(default_factory=lambda: os.getenv("MASTER_DB_HOST", "localhost"))
    master_db_port: int = field(default_factory=lambda: int(os.getenv("MASTER_DB_PORT", "5432")))
    master_db_name: str = field(default_factory=lambda: os.getenv("MASTER_DB_NAME", "insightpulse_master"))
    master_db_user: str = field(default_factory=lambda: os.getenv("MASTER_DB_USER", "postgres"))
    master_db_password: str = field(default_factory=lambda: os.getenv("MASTER_DB_PASSWORD", ""))
    
    # Template Database
    template_db_name: str = field(default_factory=lambda: os.getenv("TEMPLATE_DB_NAME", "insightpulse_template"))
    
    # Encryption
    encryption_key: str = field(default_factory=lambda: os.getenv("ENCRYPTION_KEY", Fernet.generate_key().decode()))
    
    # Superset
    superset_url: str = field(default_factory=lambda: os.getenv("SUPERSET_URL", "http://localhost:8088"))
    superset_username: str = field(default_factory=lambda: os.getenv("SUPERSET_USERNAME", "admin"))
    superset_password: str = field(default_factory=lambda: os.getenv("SUPERSET_PASSWORD", "admin"))
    
    # Defaults
    default_tenant_db_prefix: str = "insightpulse_"
    trial_days: int = 14
    
    @property
    def master_dsn(self) -> str:
        return f"postgresql://{self.master_db_user}:{self.master_db_password}@{self.master_db_host}:{self.master_db_port}/{self.master_db_name}"
    
    @property
    def template_dsn(self) -> str:
        return f"postgresql://{self.master_db_user}:{self.master_db_password}@{self.master_db_host}:{self.master_db_port}/{self.template_db_name}"


config = Config()


# =============================================================================
# ENUMS & DATA CLASSES
# =============================================================================

class TenantType(str, Enum):
    PLATFORM_OWNER = "platform_owner"
    PROVIDER = "provider"  # Can create sub-tenants
    CLIENT = "client"
    INTERNAL = "internal"


class TenantStatus(str, Enum):
    PROVISIONING = "provisioning"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"
    DELETED = "deleted"


class SubscriptionStatus(str, Enum):
    TRIAL = "trial"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class JobType(str, Enum):
    CREATE_DATABASE = "create_database"
    CLONE_DATABASE = "clone_database"
    MIGRATE_SCHEMA = "migrate_schema"
    SEED_DATA = "seed_data"
    BACKUP = "backup"
    RESTORE = "restore"
    SETUP_SUPERSET = "setup_superset"
    SYNC_ODOO = "sync_odoo"


class JobStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Tenant:
    """Tenant entity"""
    id: str
    code: str
    name: str
    legal_name: Optional[str] = None
    tenant_type: TenantType = TenantType.CLIENT
    parent_tenant_id: Optional[str] = None
    
    # Database
    db_host: str = ""
    db_port: int = 5432
    db_name: str = ""
    db_user: str = ""
    db_password_encrypted: str = ""
    
    # Status
    status: TenantStatus = TenantStatus.PROVISIONING
    provisioned_at: Optional[datetime] = None
    
    # Subscription
    plan_id: Optional[str] = None
    subscription_status: SubscriptionStatus = SubscriptionStatus.TRIAL
    trial_ends_at: Optional[datetime] = None
    
    # Features & Branding
    features: Dict[str, Any] = field(default_factory=dict)
    branding: Dict[str, Any] = field(default_factory=dict)
    custom_domain: Optional[str] = None
    
    # Metadata
    settings: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @property
    def db_connection_string(self) -> str:
        """Decrypted connection string"""
        password = Encryption.decrypt(self.db_password_encrypted)
        return f"postgresql://{self.db_user}:{password}@{self.db_host}:{self.db_port}/{self.db_name}"


@dataclass
class ProvisioningJob:
    """Background job for tenant operations"""
    id: str
    tenant_id: str
    job_type: JobType
    status: JobStatus = JobStatus.PENDING
    config: Dict[str, Any] = field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress_pct: int = 0
    current_step: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0


@dataclass
class TableSchema:
    """Database table schema information"""
    name: str
    schema: str = "public"
    columns: List[Dict[str, Any]] = field(default_factory=list)
    primary_key: List[str] = field(default_factory=list)
    foreign_keys: List[Dict[str, Any]] = field(default_factory=list)
    indexes: List[Dict[str, Any]] = field(default_factory=list)
    row_count: int = 0
    comment: Optional[str] = None


@dataclass
class DatabaseSchema:
    """Complete database schema"""
    database_name: str
    tables: List[TableSchema] = field(default_factory=list)
    enums: Dict[str, List[str]] = field(default_factory=dict)
    views: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    extensions: List[str] = field(default_factory=list)
    introspected_at: datetime = field(default_factory=datetime.utcnow)


# =============================================================================
# ENCRYPTION
# =============================================================================

class Encryption:
    """Handle sensitive data encryption"""
    
    _fernet: Optional[Fernet] = None
    
    @classmethod
    def _get_fernet(cls) -> Fernet:
        if cls._fernet is None:
            cls._fernet = Fernet(config.encryption_key.encode())
        return cls._fernet
    
    @classmethod
    def encrypt(cls, plaintext: str) -> str:
        """Encrypt a string"""
        return cls._get_fernet().encrypt(plaintext.encode()).decode()
    
    @classmethod
    def decrypt(cls, ciphertext: str) -> str:
        """Decrypt a string"""
        return cls._get_fernet().decrypt(ciphertext.encode()).decode()


# =============================================================================
# TENANT MANAGER
# =============================================================================

class TenantManager:
    """
    Manages tenant lifecycle:
    - Create tenant (provision database)
    - Clone tenant (copy from existing)
    - Suspend/Archive/Delete tenant
    - Upgrade tenant to Provider
    """
    
    def __init__(self, pool: Optional[asyncpg.Pool] = None):
        self.pool = pool
        self._own_pool = False
    
    async def __aenter__(self):
        if self.pool is None:
            self.pool = await asyncpg.create_pool(config.master_dsn)
            self._own_pool = True
        return self
    
    async def __aexit__(self, *args):
        if self._own_pool and self.pool:
            await self.pool.close()
    
    async def create_tenant(
        self,
        code: str,
        name: str,
        tenant_type: TenantType = TenantType.CLIENT,
        parent_tenant_id: Optional[str] = None,
        plan_id: Optional[str] = None,
        features: Optional[Dict] = None,
        clone_from_tenant_id: Optional[str] = None
    ) -> Tenant:
        """
        Create a new tenant with its own database.
        
        Args:
            code: URL-safe tenant identifier (e.g., 'acme-corp')
            name: Display name
            tenant_type: Type of tenant (client, provider, etc.)
            parent_tenant_id: Parent tenant for white-label scenarios
            plan_id: Subscription plan
            features: Feature flags
            clone_from_tenant_id: Clone data from existing tenant
        
        Returns:
            Tenant: The created tenant
        """
        import uuid
        
        tenant_id = str(uuid.uuid4())
        db_name = f"{config.default_tenant_db_prefix}{code.replace('-', '_')}"
        db_user = f"tenant_{code.replace('-', '_')}"
        db_password = self._generate_password()
        
        tenant = Tenant(
            id=tenant_id,
            code=code,
            name=name,
            tenant_type=tenant_type,
            parent_tenant_id=parent_tenant_id,
            db_host=config.master_db_host,
            db_port=config.master_db_port,
            db_name=db_name,
            db_user=db_user,
            db_password_encrypted=Encryption.encrypt(db_password),
            status=TenantStatus.PROVISIONING,
            plan_id=plan_id,
            subscription_status=SubscriptionStatus.TRIAL,
            trial_ends_at=datetime.utcnow() + timedelta(days=config.trial_days),
            features=features or {},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Insert tenant record
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO tenants (
                    id, code, name, tenant_type, parent_tenant_id,
                    db_host, db_port, db_name, db_user, db_password_encrypted,
                    status, plan_id, subscription_status, trial_ends_at,
                    features, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
            """, tenant.id, tenant.code, tenant.name, tenant.tenant_type.value,
                tenant.parent_tenant_id, tenant.db_host, tenant.db_port,
                tenant.db_name, tenant.db_user, tenant.db_password_encrypted,
                tenant.status.value, tenant.plan_id, tenant.subscription_status.value,
                tenant.trial_ends_at, json.dumps(tenant.features),
                tenant.created_at, tenant.updated_at)
        
        # Create provisioning job
        job_type = JobType.CLONE_DATABASE if clone_from_tenant_id else JobType.CREATE_DATABASE
        job = await self._create_provisioning_job(
            tenant_id=tenant_id,
            job_type=job_type,
            config={
                "db_name": db_name,
                "db_user": db_user,
                "db_password": db_password,
                "clone_from_tenant_id": clone_from_tenant_id
            }
        )
        
        # Execute provisioning (could be async via queue)
        await self._execute_provisioning_job(job)
        
        return tenant
    
    async def clone_tenant(
        self,
        source_tenant_id: str,
        new_code: str,
        new_name: str,
        include_data: bool = False
    ) -> Tenant:
        """
        Clone an existing tenant's database structure (optionally with data).
        
        Useful for:
        - Creating demo environments
        - Setting up test tenants
        - White-label deployments
        """
        return await self.create_tenant(
            code=new_code,
            name=new_name,
            clone_from_tenant_id=source_tenant_id if include_data else None
        )
    
    async def upgrade_to_provider(self, tenant_id: str) -> Tenant:
        """
        Upgrade a client tenant to provider status.
        Providers can create and manage their own sub-tenants.
        """
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE tenants 
                SET tenant_type = $1, 
                    features = features || '{"can_create_tenants": true}'::jsonb,
                    updated_at = $2
                WHERE id = $3
            """, TenantType.PROVIDER.value, datetime.utcnow(), tenant_id)
            
            row = await conn.fetchrow("SELECT * FROM tenants WHERE id = $1", tenant_id)
            return self._row_to_tenant(row)
    
    async def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM tenants WHERE id = $1", tenant_id)
            return self._row_to_tenant(row) if row else None
    
    async def get_tenant_by_code(self, code: str) -> Optional[Tenant]:
        """Get tenant by code"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM tenants WHERE code = $1", code)
            return self._row_to_tenant(row) if row else None
    
    async def list_tenants(
        self,
        tenant_type: Optional[TenantType] = None,
        status: Optional[TenantStatus] = None,
        parent_tenant_id: Optional[str] = None
    ) -> List[Tenant]:
        """List tenants with optional filters"""
        query = "SELECT * FROM tenants WHERE deleted_at IS NULL"
        params = []
        
        if tenant_type:
            params.append(tenant_type.value)
            query += f" AND tenant_type = ${len(params)}"
        
        if status:
            params.append(status.value)
            query += f" AND status = ${len(params)}"
        
        if parent_tenant_id:
            params.append(parent_tenant_id)
            query += f" AND parent_tenant_id = ${len(params)}"
        
        query += " ORDER BY created_at DESC"
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [self._row_to_tenant(row) for row in rows]
    
    async def suspend_tenant(self, tenant_id: str, reason: str = "") -> Tenant:
        """Suspend a tenant (e.g., payment failure)"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE tenants 
                SET status = $1, 
                    settings = settings || jsonb_build_object('suspension_reason', $2),
                    updated_at = $3
                WHERE id = $4
            """, TenantStatus.SUSPENDED.value, reason, datetime.utcnow(), tenant_id)
            
            row = await conn.fetchrow("SELECT * FROM tenants WHERE id = $1", tenant_id)
            return self._row_to_tenant(row)
    
    async def archive_tenant(self, tenant_id: str) -> Tenant:
        """Archive a tenant (soft delete, data retained)"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE tenants 
                SET status = $1, deleted_at = $2, updated_at = $2
                WHERE id = $3
            """, TenantStatus.ARCHIVED.value, datetime.utcnow(), tenant_id)
            
            row = await conn.fetchrow("SELECT * FROM tenants WHERE id = $1", tenant_id)
            return self._row_to_tenant(row)
    
    # -------------------------------------------------------------------------
    # Private Methods
    # -------------------------------------------------------------------------
    
    def _generate_password(self, length: int = 32) -> str:
        """Generate a secure random password"""
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def _row_to_tenant(self, row: asyncpg.Record) -> Tenant:
        """Convert database row to Tenant object"""
        return Tenant(
            id=str(row['id']),
            code=row['code'],
            name=row['name'],
            legal_name=row.get('legal_name'),
            tenant_type=TenantType(row['tenant_type']),
            parent_tenant_id=str(row['parent_tenant_id']) if row.get('parent_tenant_id') else None,
            db_host=row['db_host'],
            db_port=row['db_port'],
            db_name=row['db_name'],
            db_user=row['db_user'],
            db_password_encrypted=row['db_password_encrypted'],
            status=TenantStatus(row['status']),
            provisioned_at=row.get('provisioned_at'),
            plan_id=str(row['plan_id']) if row.get('plan_id') else None,
            subscription_status=SubscriptionStatus(row['subscription_status']) if row.get('subscription_status') else SubscriptionStatus.TRIAL,
            trial_ends_at=row.get('trial_ends_at'),
            features=json.loads(row['features']) if row.get('features') else {},
            branding=json.loads(row['branding']) if row.get('branding') else {},
            custom_domain=row.get('custom_domain'),
            settings=json.loads(row['settings']) if row.get('settings') else {},
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
    
    async def _create_provisioning_job(
        self,
        tenant_id: str,
        job_type: JobType,
        config: Dict[str, Any]
    ) -> ProvisioningJob:
        """Create a provisioning job record"""
        import uuid
        
        job_id = str(uuid.uuid4())
        job = ProvisioningJob(
            id=job_id,
            tenant_id=tenant_id,
            job_type=job_type,
            config=config
        )
        
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO provisioning_jobs (id, tenant_id, job_type, status, config, created_at)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, job.id, job.tenant_id, job.job_type.value, job.status.value,
                json.dumps(job.config), datetime.utcnow())
        
        return job
    
    async def _execute_provisioning_job(self, job: ProvisioningJob) -> None:
        """Execute a provisioning job"""
        try:
            # Update job status
            await self._update_job_status(job.id, JobStatus.RUNNING, "Starting provisioning")
            
            if job.job_type == JobType.CREATE_DATABASE:
                await self._provision_new_database(job)
            elif job.job_type == JobType.CLONE_DATABASE:
                await self._clone_database(job)
            
            # Mark complete
            await self._update_job_status(job.id, JobStatus.COMPLETED, "Provisioning complete")
            
            # Update tenant status
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE tenants SET status = $1, provisioned_at = $2, updated_at = $2
                    WHERE id = $3
                """, TenantStatus.ACTIVE.value, datetime.utcnow(), job.tenant_id)
                
        except Exception as e:
            logger.error(f"Provisioning failed: {e}")
            await self._update_job_status(job.id, JobStatus.FAILED, str(e))
            raise
    
    async def _provision_new_database(self, job: ProvisioningJob) -> None:
        """Create a new database from template"""
        db_name = job.config['db_name']
        db_user = job.config['db_user']
        db_password = job.config['db_password']
        
        # Connect to postgres database (not master) to create new DB
        conn = await asyncpg.connect(
            host=config.master_db_host,
            port=config.master_db_port,
            user=config.master_db_user,
            password=config.master_db_password,
            database='postgres'
        )
        
        try:
            await self._update_job_status(job.id, JobStatus.RUNNING, "Creating database user", 10)
            
            # Create user
            await conn.execute(f"""
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '{db_user}') THEN
                        CREATE ROLE {db_user} WITH LOGIN PASSWORD '{db_password}';
                    END IF;
                END
                $$;
            """)
            
            await self._update_job_status(job.id, JobStatus.RUNNING, "Creating database from template", 30)
            
            # Create database from template
            # Note: Template database must have no active connections
            await conn.execute(f"""
                CREATE DATABASE {db_name} 
                WITH TEMPLATE {config.template_db_name}
                OWNER {db_user};
            """)
            
            await self._update_job_status(job.id, JobStatus.RUNNING, "Granting permissions", 70)
            
            # Grant permissions
            await conn.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};")
            
            await self._update_job_status(job.id, JobStatus.RUNNING, "Finalizing", 90)
            
        finally:
            await conn.close()
    
    async def _clone_database(self, job: ProvisioningJob) -> None:
        """Clone an existing tenant's database"""
        # First create the database structure
        await self._provision_new_database(job)
        
        source_tenant_id = job.config.get('clone_from_tenant_id')
        if source_tenant_id:
            # Get source tenant connection
            source_tenant = await self.get_tenant(source_tenant_id)
            if source_tenant:
                await self._update_job_status(job.id, JobStatus.RUNNING, "Copying data", 80)
                # Use pg_dump/pg_restore for data copy
                # This is simplified - in production use subprocess with pg_dump
                logger.info(f"Would copy data from {source_tenant.db_name} to {job.config['db_name']}")
    
    async def _update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        step: str,
        progress: int = 0
    ) -> None:
        """Update job status in database"""
        async with self.pool.acquire() as conn:
            if status == JobStatus.RUNNING:
                await conn.execute("""
                    UPDATE provisioning_jobs 
                    SET status = $1, current_step = $2, progress_pct = $3,
                        started_at = COALESCE(started_at, $4)
                    WHERE id = $5
                """, status.value, step, progress, datetime.utcnow(), job_id)
            elif status in (JobStatus.COMPLETED, JobStatus.FAILED):
                await conn.execute("""
                    UPDATE provisioning_jobs 
                    SET status = $1, current_step = $2, progress_pct = 100,
                        completed_at = $3, error_message = $4
                    WHERE id = $5
                """, status.value, step, datetime.utcnow(),
                    step if status == JobStatus.FAILED else None, job_id)


# =============================================================================
# SCHEMA INTROSPECTOR
# =============================================================================

class SchemaIntrospector:
    """
    Introspect PostgreSQL database schema and generate documentation.
    
    Features:
    - Extract table/column definitions
    - Map foreign key relationships
    - Generate DBML output
    - Generate Markdown documentation
    - Generate ERD data for visualization
    """
    
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool: Optional[asyncpg.Pool] = None
    
    async def __aenter__(self):
        self.pool = await asyncpg.create_pool(self.dsn)
        return self
    
    async def __aexit__(self, *args):
        if self.pool:
            await self.pool.close()
    
    async def introspect(self) -> DatabaseSchema:
        """
        Full database introspection.
        
        Returns:
            DatabaseSchema: Complete schema information
        """
        async with self.pool.acquire() as conn:
            # Get database name
            db_name = await conn.fetchval("SELECT current_database()")
            
            schema = DatabaseSchema(database_name=db_name)
            
            # Get tables
            schema.tables = await self._get_tables(conn)
            
            # Get enums
            schema.enums = await self._get_enums(conn)
            
            # Get views
            schema.views = await self._get_views(conn)
            
            # Get extensions
            schema.extensions = await self._get_extensions(conn)
            
            return schema
    
    async def _get_tables(self, conn: asyncpg.Connection) -> List[TableSchema]:
        """Get all tables with columns, keys, and indexes"""
        tables = []
        
        # Get table list
        table_rows = await conn.fetch("""
            SELECT 
                t.table_schema,
                t.table_name,
                obj_description((t.table_schema || '.' || t.table_name)::regclass) as comment,
                (SELECT reltuples::bigint FROM pg_class WHERE relname = t.table_name) as row_estimate
            FROM information_schema.tables t
            WHERE t.table_schema NOT IN ('pg_catalog', 'information_schema')
              AND t.table_type = 'BASE TABLE'
            ORDER BY t.table_schema, t.table_name
        """)
        
        for table_row in table_rows:
            table = TableSchema(
                name=table_row['table_name'],
                schema=table_row['table_schema'],
                comment=table_row['comment'],
                row_count=table_row['row_estimate'] or 0
            )
            
            # Get columns
            table.columns = await self._get_columns(conn, table.schema, table.name)
            
            # Get primary key
            table.primary_key = await self._get_primary_key(conn, table.schema, table.name)
            
            # Get foreign keys
            table.foreign_keys = await self._get_foreign_keys(conn, table.schema, table.name)
            
            # Get indexes
            table.indexes = await self._get_indexes(conn, table.schema, table.name)
            
            tables.append(table)
        
        return tables
    
    async def _get_columns(self, conn: asyncpg.Connection, schema: str, table: str) -> List[Dict]:
        """Get column definitions for a table"""
        rows = await conn.fetch("""
            SELECT 
                c.column_name,
                c.data_type,
                c.udt_name,
                c.is_nullable,
                c.column_default,
                c.character_maximum_length,
                c.numeric_precision,
                c.numeric_scale,
                col_description((c.table_schema || '.' || c.table_name)::regclass, c.ordinal_position) as comment
            FROM information_schema.columns c
            WHERE c.table_schema = $1 AND c.table_name = $2
            ORDER BY c.ordinal_position
        """, schema, table)
        
        return [dict(row) for row in rows]
    
    async def _get_primary_key(self, conn: asyncpg.Connection, schema: str, table: str) -> List[str]:
        """Get primary key columns"""
        rows = await conn.fetch("""
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = ($1 || '.' || $2)::regclass
              AND i.indisprimary
        """, schema, table)
        
        return [row['attname'] for row in rows]
    
    async def _get_foreign_keys(self, conn: asyncpg.Connection, schema: str, table: str) -> List[Dict]:
        """Get foreign key relationships"""
        rows = await conn.fetch("""
            SELECT
                tc.constraint_name,
                kcu.column_name,
                ccu.table_schema AS foreign_table_schema,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_schema = $1
              AND tc.table_name = $2
        """, schema, table)
        
        return [dict(row) for row in rows]
    
    async def _get_indexes(self, conn: asyncpg.Connection, schema: str, table: str) -> List[Dict]:
        """Get index definitions"""
        rows = await conn.fetch("""
            SELECT
                i.relname as index_name,
                a.attname as column_name,
                ix.indisunique as is_unique,
                ix.indisprimary as is_primary,
                am.amname as index_type
            FROM pg_class t
            JOIN pg_index ix ON t.oid = ix.indrelid
            JOIN pg_class i ON i.oid = ix.indexrelid
            JOIN pg_am am ON i.relam = am.oid
            JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
            WHERE t.relkind = 'r'
              AND t.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = $1)
              AND t.relname = $2
            ORDER BY i.relname
        """, schema, table)
        
        return [dict(row) for row in rows]
    
    async def _get_enums(self, conn: asyncpg.Connection) -> Dict[str, List[str]]:
        """Get enum type definitions"""
        rows = await conn.fetch("""
            SELECT 
                t.typname as enum_name,
                array_agg(e.enumlabel ORDER BY e.enumsortorder) as enum_values
            FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
            WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
            GROUP BY t.typname
        """)
        
        return {row['enum_name']: list(row['enum_values']) for row in rows}
    
    async def _get_views(self, conn: asyncpg.Connection) -> List[str]:
        """Get view names"""
        rows = await conn.fetch("""
            SELECT table_name
            FROM information_schema.views
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
        """)
        
        return [row['table_name'] for row in rows]
    
    async def _get_extensions(self, conn: asyncpg.Connection) -> List[str]:
        """Get installed extensions"""
        rows = await conn.fetch("SELECT extname FROM pg_extension")
        return [row['extname'] for row in rows]
    
    # -------------------------------------------------------------------------
    # Output Generators
    # -------------------------------------------------------------------------
    
    async def generate_dbml(self) -> str:
        """
        Generate DBML (Database Markup Language) from schema.
        
        Returns:
            str: DBML document
        """
        schema = await self.introspect()
        lines = []
        
        # Header
        lines.append(f"// Generated from {schema.database_name}")
        lines.append(f"// Introspected at {schema.introspected_at.isoformat()}")
        lines.append("")
        lines.append(f"Project {schema.database_name} {{")
        lines.append("  database_type: 'PostgreSQL'")
        lines.append("}")
        lines.append("")
        
        # Enums
        for enum_name, values in schema.enums.items():
            lines.append(f"Enum {enum_name} {{")
            for value in values:
                lines.append(f"  {value}")
            lines.append("}")
            lines.append("")
        
        # Tables
        for table in schema.tables:
            lines.append(f"Table {table.schema}.{table.name} {{")
            
            for col in table.columns:
                col_def = self._format_column_dbml(col, table.primary_key)
                lines.append(f"  {col_def}")
            
            # Indexes
            if table.indexes:
                lines.append("")
                lines.append("  indexes {")
                seen_indexes = set()
                for idx in table.indexes:
                    idx_name = idx['index_name']
                    if idx_name not in seen_indexes and not idx['is_primary']:
                        unique = " [unique]" if idx['is_unique'] else ""
                        lines.append(f"    {idx['column_name']}{unique}")
                        seen_indexes.add(idx_name)
                lines.append("  }")
            
            if table.comment:
                lines.append("")
                lines.append(f"  Note: '{table.comment}'")
            
            lines.append("}")
            lines.append("")
        
        # Foreign Key References
        lines.append("// Foreign Key Relationships")
        for table in schema.tables:
            for fk in table.foreign_keys:
                ref = f"Ref: {table.schema}.{table.name}.{fk['column_name']} > "
                ref += f"{fk['foreign_table_schema']}.{fk['foreign_table_name']}.{fk['foreign_column_name']}"
                lines.append(ref)
        
        return "\n".join(lines)
    
    def _format_column_dbml(self, col: Dict, primary_keys: List[str]) -> str:
        """Format a column for DBML output"""
        name = col['column_name']
        
        # Map PostgreSQL types to DBML types
        pg_type = col['udt_name']
        type_map = {
            'int4': 'integer',
            'int8': 'bigint',
            'int2': 'smallint',
            'float4': 'real',
            'float8': 'double',
            'bool': 'boolean',
            'varchar': 'varchar',
            'text': 'text',
            'uuid': 'uuid',
            'timestamptz': 'timestamptz',
            'timestamp': 'timestamp',
            'date': 'date',
            'jsonb': 'jsonb',
            'json': 'json',
            '_text': 'text[]',
        }
        
        dbml_type = type_map.get(pg_type, pg_type)
        
        # Add length for varchar
        if pg_type == 'varchar' and col.get('character_maximum_length'):
            dbml_type = f"varchar({col['character_maximum_length']})"
        
        # Build attributes
        attrs = []
        if name in primary_keys:
            attrs.append("pk")
        if col['column_default']:
            default = col['column_default']
            if 'nextval' in str(default):
                attrs.append("increment")
            elif 'gen_random_uuid' in str(default) or 'uuid_generate' in str(default):
                attrs.append("default: `gen_random_uuid()`")
            elif 'now()' in str(default) or 'CURRENT_TIMESTAMP' in str(default):
                attrs.append("default: `now()`")
            else:
                attrs.append(f"default: {default}")
        if col['is_nullable'] == 'NO' and name not in primary_keys:
            attrs.append("not null")
        if col.get('comment'):
            attrs.append(f"note: '{col['comment']}'")
        
        attr_str = f" [{', '.join(attrs)}]" if attrs else ""
        
        return f"{name} {dbml_type}{attr_str}"
    
    async def generate_markdown(self) -> str:
        """
        Generate Markdown documentation from schema.
        
        Returns:
            str: Markdown document
        """
        schema = await self.introspect()
        lines = []
        
        # Header
        lines.append(f"# Database Schema: {schema.database_name}")
        lines.append("")
        lines.append(f"*Generated: {schema.introspected_at.strftime('%Y-%m-%d %H:%M:%S UTC')}*")
        lines.append("")
        
        # Summary
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- **Tables**: {len(schema.tables)}")
        lines.append(f"- **Views**: {len(schema.views)}")
        lines.append(f"- **Enums**: {len(schema.enums)}")
        lines.append(f"- **Extensions**: {', '.join(schema.extensions)}")
        lines.append("")
        
        # Table of Contents
        lines.append("## Tables")
        lines.append("")
        for table in schema.tables:
            lines.append(f"- [{table.schema}.{table.name}](#{table.schema}{table.name})")
        lines.append("")
        
        # Enums
        if schema.enums:
            lines.append("## Enum Types")
            lines.append("")
            for enum_name, values in schema.enums.items():
                lines.append(f"### {enum_name}")
                lines.append("")
                lines.append("| Value |")
                lines.append("|-------|")
                for value in values:
                    lines.append(f"| `{value}` |")
                lines.append("")
        
        # Table Details
        lines.append("## Table Details")
        lines.append("")
        
        for table in schema.tables:
            lines.append(f"### {table.schema}.{table.name}")
            lines.append("")
            
            if table.comment:
                lines.append(f"*{table.comment}*")
                lines.append("")
            
            lines.append(f"**Estimated Rows**: {table.row_count:,}")
            lines.append("")
            
            # Columns table
            lines.append("#### Columns")
            lines.append("")
            lines.append("| Column | Type | Nullable | Default | Description |")
            lines.append("|--------|------|----------|---------|-------------|")
            
            for col in table.columns:
                name = col['column_name']
                if name in table.primary_key:
                    name = f"**{name}** 🔑"
                
                col_type = col['udt_name']
                if col.get('character_maximum_length'):
                    col_type = f"{col_type}({col['character_maximum_length']})"
                
                nullable = "✓" if col['is_nullable'] == 'YES' else ""
                default = col.get('column_default') or ""
                if len(default) > 30:
                    default = default[:27] + "..."
                comment = col.get('comment') or ""
                
                lines.append(f"| {name} | `{col_type}` | {nullable} | {default} | {comment} |")
            
            lines.append("")
            
            # Foreign Keys
            if table.foreign_keys:
                lines.append("#### Foreign Keys")
                lines.append("")
                for fk in table.foreign_keys:
                    lines.append(f"- `{fk['column_name']}` → `{fk['foreign_table_schema']}.{fk['foreign_table_name']}.{fk['foreign_column_name']}`")
                lines.append("")
            
            # Indexes
            if table.indexes:
                lines.append("#### Indexes")
                lines.append("")
                seen = set()
                for idx in table.indexes:
                    if idx['index_name'] not in seen:
                        unique = " (UNIQUE)" if idx['is_unique'] else ""
                        primary = " (PRIMARY)" if idx['is_primary'] else ""
                        lines.append(f"- `{idx['index_name']}`: {idx['column_name']}{unique}{primary}")
                        seen.add(idx['index_name'])
                lines.append("")
        
        return "\n".join(lines)
    
    async def generate_erd_json(self) -> Dict[str, Any]:
        """
        Generate ERD data as JSON for visualization tools.
        
        Returns:
            Dict: ERD structure for rendering
        """
        schema = await self.introspect()
        
        nodes = []
        edges = []
        
        for table in schema.tables:
            node = {
                "id": f"{table.schema}.{table.name}",
                "type": "table",
                "label": table.name,
                "schema": table.schema,
                "columns": [
                    {
                        "name": col['column_name'],
                        "type": col['udt_name'],
                        "isPrimaryKey": col['column_name'] in table.primary_key,
                        "isNullable": col['is_nullable'] == 'YES'
                    }
                    for col in table.columns
                ],
                "rowCount": table.row_count
            }
            nodes.append(node)
            
            for fk in table.foreign_keys:
                edge = {
                    "id": fk['constraint_name'],
                    "source": f"{table.schema}.{table.name}",
                    "sourceColumn": fk['column_name'],
                    "target": f"{fk['foreign_table_schema']}.{fk['foreign_table_name']}",
                    "targetColumn": fk['foreign_column_name'],
                    "type": "foreignKey"
                }
                edges.append(edge)
        
        return {
            "database": schema.database_name,
            "introspectedAt": schema.introspected_at.isoformat(),
            "nodes": nodes,
            "edges": edges,
            "enums": schema.enums,
            "extensions": schema.extensions
        }


# =============================================================================
# SUPERSET INTEGRATION
# =============================================================================

class SupersetManager:
    """
    Manage Superset workspaces and datasets for tenants.
    
    Features:
    - Create database connection per tenant
    - Auto-generate datasets from introspected schema
    - Configure default dashboards
    """
    
    def __init__(self, superset_url: str = None, username: str = None, password: str = None):
        self.superset_url = superset_url or config.superset_url
        self.username = username or config.superset_username
        self.password = password or config.superset_password
        self._access_token: Optional[str] = None
        self._csrf_token: Optional[str] = None
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=30.0)
        await self._authenticate()
        return self
    
    async def __aexit__(self, *args):
        if self._client:
            await self._client.aclose()
    
    async def _authenticate(self) -> None:
        """Authenticate with Superset and get tokens"""
        # Get access token
        response = await self._client.post(
            f"{self.superset_url}/api/v1/security/login",
            json={
                "username": self.username,
                "password": self.password,
                "provider": "db"
            }
        )
        response.raise_for_status()
        self._access_token = response.json()["access_token"]
        
        # Get CSRF token
        response = await self._client.get(
            f"{self.superset_url}/api/v1/security/csrf_token/",
            headers={"Authorization": f"Bearer {self._access_token}"}
        )
        response.raise_for_status()
        self._csrf_token = response.json()["result"]
    
    def _headers(self) -> Dict[str, str]:
        """Get authenticated headers"""
        return {
            "Authorization": f"Bearer {self._access_token}",
            "X-CSRFToken": self._csrf_token,
            "Content-Type": "application/json"
        }
    
    async def create_database_connection(
        self,
        tenant: Tenant,
        database_name: Optional[str] = None
    ) -> int:
        """
        Create a Superset database connection for a tenant.
        
        Args:
            tenant: Tenant to create connection for
            database_name: Display name in Superset
        
        Returns:
            int: Superset database ID
        """
        password = Encryption.decrypt(tenant.db_password_encrypted)
        sqlalchemy_uri = f"postgresql://{tenant.db_user}:{password}@{tenant.db_host}:{tenant.db_port}/{tenant.db_name}"
        
        response = await self._client.post(
            f"{self.superset_url}/api/v1/database/",
            headers=self._headers(),
            json={
                "database_name": database_name or f"Tenant: {tenant.name}",
                "engine": "postgresql",
                "sqlalchemy_uri": sqlalchemy_uri,
                "expose_in_sqllab": True,
                "allow_ctas": False,
                "allow_cvas": False,
                "allow_dml": False,
                "allow_run_async": True,
                "extra": json.dumps({
                    "metadata_params": {},
                    "engine_params": {},
                    "metadata_cache_timeout": {},
                    "schemas_allowed_for_csv_upload": []
                })
            }
        )
        response.raise_for_status()
        return response.json()["id"]
    
    async def create_datasets_from_schema(
        self,
        database_id: int,
        schema: DatabaseSchema,
        include_tables: Optional[List[str]] = None,
        exclude_tables: Optional[List[str]] = None
    ) -> List[int]:
        """
        Create Superset datasets from introspected schema.
        
        Args:
            database_id: Superset database ID
            schema: Introspected schema
            include_tables: Only create datasets for these tables
            exclude_tables: Skip these tables
        
        Returns:
            List[int]: Created dataset IDs
        """
        dataset_ids = []
        exclude_tables = exclude_tables or []
        
        for table in schema.tables:
            table_full_name = f"{table.schema}.{table.name}"
            
            if include_tables and table_full_name not in include_tables:
                continue
            if table_full_name in exclude_tables:
                continue
            
            response = await self._client.post(
                f"{self.superset_url}/api/v1/dataset/",
                headers=self._headers(),
                json={
                    "database": database_id,
                    "schema": table.schema,
                    "table_name": table.name
                }
            )
            
            if response.status_code == 201:
                dataset_ids.append(response.json()["id"])
            else:
                logger.warning(f"Failed to create dataset for {table_full_name}: {response.text}")
        
        return dataset_ids
    
    async def sync_table_columns(self, dataset_id: int) -> None:
        """Refresh dataset columns from database"""
        await self._client.put(
            f"{self.superset_url}/api/v1/dataset/{dataset_id}/refresh",
            headers=self._headers()
        )
    
    async def setup_tenant_workspace(self, tenant: Tenant) -> Dict[str, Any]:
        """
        Complete tenant workspace setup:
        1. Create database connection
        2. Introspect schema
        3. Create datasets
        4. Return workspace info
        """
        # Create database connection
        db_id = await self.create_database_connection(tenant)
        
        # Introspect tenant database
        async with SchemaIntrospector(tenant.db_connection_string) as introspector:
            schema = await introspector.introspect()
        
        # Create datasets (exclude system tables)
        exclude = [
            "public.ir_model", "public.ir_model_fields",  # Odoo system
            "public.audit_log"  # Don't expose audit
        ]
        dataset_ids = await self.create_datasets_from_schema(db_id, schema, exclude_tables=exclude)
        
        return {
            "database_id": db_id,
            "dataset_ids": dataset_ids,
            "table_count": len(schema.tables),
            "superset_url": self.superset_url
        }


# =============================================================================
# DOCUMENTATION GENERATOR
# =============================================================================

class DocumentationGenerator:
    """
    Generate comprehensive documentation for tenant databases.
    
    Outputs:
    - DBML file (for dbdiagram.io)
    - Markdown documentation
    - ERD JSON (for React Flow, Mermaid)
    - SQL DDL export
    """
    
    def __init__(self, output_dir: str = "./docs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def generate_all(
        self,
        dsn: str,
        tenant_code: str,
        formats: Optional[List[str]] = None
    ) -> Dict[str, Path]:
        """
        Generate all documentation formats.
        
        Args:
            dsn: Database connection string
            tenant_code: Tenant identifier for filenames
            formats: List of formats to generate (dbml, markdown, json, sql)
        
        Returns:
            Dict[str, Path]: Generated file paths
        """
        formats = formats or ["dbml", "markdown", "json"]
        outputs = {}
        
        async with SchemaIntrospector(dsn) as introspector:
            if "dbml" in formats:
                dbml = await introspector.generate_dbml()
                path = self.output_dir / f"{tenant_code}_schema.dbml"
                path.write_text(dbml)
                outputs["dbml"] = path
                logger.info(f"Generated DBML: {path}")
            
            if "markdown" in formats:
                md = await introspector.generate_markdown()
                path = self.output_dir / f"{tenant_code}_schema.md"
                path.write_text(md)
                outputs["markdown"] = path
                logger.info(f"Generated Markdown: {path}")
            
            if "json" in formats:
                erd = await introspector.generate_erd_json()
                path = self.output_dir / f"{tenant_code}_erd.json"
                path.write_text(json.dumps(erd, indent=2, default=str))
                outputs["json"] = path
                logger.info(f"Generated ERD JSON: {path}")
        
        return outputs


# =============================================================================
# CLI INTERFACE
# =============================================================================

async def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="InsightPulse Tenant Management")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Create tenant
    create_parser = subparsers.add_parser("create", help="Create a new tenant")
    create_parser.add_argument("code", help="Tenant code (URL-safe)")
    create_parser.add_argument("name", help="Tenant display name")
    create_parser.add_argument("--type", choices=["client", "provider"], default="client")
    create_parser.add_argument("--clone-from", help="Clone from existing tenant ID")
    
    # List tenants
    list_parser = subparsers.add_parser("list", help="List tenants")
    list_parser.add_argument("--type", choices=["client", "provider", "all"], default="all")
    list_parser.add_argument("--status", choices=["active", "suspended", "all"], default="all")
    
    # Introspect
    introspect_parser = subparsers.add_parser("introspect", help="Introspect database schema")
    introspect_parser.add_argument("tenant_code", help="Tenant code")
    introspect_parser.add_argument("--format", choices=["dbml", "markdown", "json", "all"], default="all")
    introspect_parser.add_argument("--output", default="./docs", help="Output directory")
    
    # Superset setup
    superset_parser = subparsers.add_parser("superset", help="Setup Superset workspace")
    superset_parser.add_argument("tenant_code", help="Tenant code")
    
    args = parser.parse_args()
    
    if args.command == "create":
        async with TenantManager() as manager:
            tenant_type = TenantType.PROVIDER if args.type == "provider" else TenantType.CLIENT
            tenant = await manager.create_tenant(
                code=args.code,
                name=args.name,
                tenant_type=tenant_type,
                clone_from_tenant_id=args.clone_from
            )
            print(f"Created tenant: {tenant.id} ({tenant.code})")
            print(f"Database: {tenant.db_name}")
            print(f"Status: {tenant.status.value}")
    
    elif args.command == "list":
        async with TenantManager() as manager:
            tenant_type = None if args.type == "all" else TenantType(args.type)
            status = None if args.status == "all" else TenantStatus(args.status)
            tenants = await manager.list_tenants(tenant_type=tenant_type, status=status)
            
            print(f"{'Code':<20} {'Name':<30} {'Type':<12} {'Status':<12}")
            print("-" * 74)
            for t in tenants:
                print(f"{t.code:<20} {t.name:<30} {t.tenant_type.value:<12} {t.status.value:<12}")
    
    elif args.command == "introspect":
        async with TenantManager() as manager:
            tenant = await manager.get_tenant_by_code(args.tenant_code)
            if not tenant:
                print(f"Tenant not found: {args.tenant_code}")
                return
            
            formats = ["dbml", "markdown", "json"] if args.format == "all" else [args.format]
            generator = DocumentationGenerator(args.output)
            outputs = await generator.generate_all(tenant.db_connection_string, tenant.code, formats)
            
            print("Generated documentation:")
            for fmt, path in outputs.items():
                print(f"  {fmt}: {path}")
    
    elif args.command == "superset":
        async with TenantManager() as manager:
            tenant = await manager.get_tenant_by_code(args.tenant_code)
            if not tenant:
                print(f"Tenant not found: {args.tenant_code}")
                return
            
            async with SupersetManager() as superset:
                result = await superset.setup_tenant_workspace(tenant)
                print(f"Superset workspace created:")
                print(f"  Database ID: {result['database_id']}")
                print(f"  Datasets: {len(result['dataset_ids'])}")
                print(f"  Tables: {result['table_count']}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
