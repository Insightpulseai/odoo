# Supabase SSOT Doctrine – Tasks

## Documentation Tasks

- [x] Create spec/supabase-ssot-doctrine/constitution.md
- [x] Create spec/supabase-ssot-doctrine/prd.md
- [x] Create spec/supabase-ssot-doctrine/plan.md
- [x] Create spec/supabase-ssot-doctrine/tasks.md
- [x] Create spec/supabase-ssot-doctrine/agent-prompt.md
- [x] Update docs/architecture/SOURCE_OF_TRUTH.md
- [x] Create .claude/commands/ssot-doctrine.md
- [ ] Update CLAUDE.md with SSOT section reference

## Secret Management Tasks

- [ ] Audit environment files for secrets
- [ ] Audit Odoo models for secret storage
- [ ] Create Supabase Vault entries
- [ ] Update Edge Functions for Vault
- [ ] Update n8n credentials
- [ ] Remove deprecated secret locations

## Schema Tasks

- [ ] Create Supabase `ops` schema
- [ ] Create Supabase `ai` schema
- [ ] Create Supabase `audit` schema
- [ ] Create Supabase `analytics` schema
- [ ] Tag mirror/shadow tables
- [ ] Implement RLS policies

## Orchestration Tasks

- [ ] Audit Odoo cron jobs
- [ ] Migrate cron jobs to pg_cron
- [ ] Document n8n workflow patterns
- [ ] Add job monitoring

## AI Agent Tasks

- [ ] Define agent access scopes
- [ ] Implement agent memory tables
- [ ] Configure output storage
- [ ] Add audit logging

## Verification Tasks

- [ ] Create CI gate for SSOT compliance
- [ ] Add evidence collection scripts
- [ ] Document verification procedures
