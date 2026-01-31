# Supabase SSOT Doctrine – Implementation Plan

## Phase 1: Documentation & Agent Configuration

### 1.1 Create Doctrine Documentation
- [x] Create spec bundle with constitution, prd, plan, tasks
- [x] Create copy-paste agent prompt
- [x] Update docs/architecture/SOURCE_OF_TRUTH.md
- [x] Add .claude/commands/ssot-doctrine.md

### 1.2 Update CLAUDE.md
- [ ] Add SSOT/SoR section to CLAUDE.md
- [ ] Reference spec bundle

## Phase 2: Secret Migration

### 2.1 Audit Current Secrets
- [ ] Identify all secrets in environment files
- [ ] Identify any secrets in Odoo models
- [ ] Identify secrets in Git history

### 2.2 Migrate to Supabase Vault
- [ ] Create Vault entries for all platform secrets
- [ ] Update Edge Functions to use Vault
- [ ] Update n8n to use Vault-based credentials
- [ ] Remove secrets from other locations

## Phase 3: Data Ownership Enforcement

### 3.1 Schema Organization
- [ ] Create Supabase schemas: ops, ai, audit, analytics
- [ ] Tag all replicated tables as shadow/mirror
- [ ] Implement RLS policies

### 3.2 Sync Pipeline
- [ ] Document Odoo→Supabase sync process
- [ ] Ensure read-only replication
- [ ] Add sync status tracking

## Phase 4: Orchestration Migration

### 4.1 Move Scheduled Jobs
- [ ] Audit any Odoo-based cron jobs
- [ ] Migrate to pg_cron or n8n
- [ ] Verify job execution

### 4.2 Edge Function Setup
- [ ] Document Edge Function patterns
- [ ] Implement standard job queue
- [ ] Add monitoring

## Phase 5: AI Agent Configuration

### 5.1 Access Controls
- [ ] Define agent access scopes
- [ ] Implement Supabase-first read patterns
- [ ] Document Odoo access exceptions

### 5.2 Output Storage
- [ ] Configure AI output schemas
- [ ] Implement agent memory tables
- [ ] Add audit logging

## Verification

Each phase requires:
1. Evidence documentation in docs/evidence/
2. CI gate validation
3. Manual verification checklist
