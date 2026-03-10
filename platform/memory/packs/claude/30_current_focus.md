# Current Focus (Claude)

## Active Priorities

### 1. Marketplace Integrations (High)
**Status**: Implementation complete, testing phase
**Components**:
- Supabase `marketplace` schema (6 tables, 8 functions, 3 views)
- Edge Function `marketplace-webhook` (GitHub, Google, S3 handlers)
- n8n workflows (artifact mirror, workspace events)

**Next Steps**:
- Configure webhook endpoints in GitHub/Google
- Test end-to-end artifact sync flow
- Monitor quota usage

### 2. Memory Architecture (High)
**Status**: Structure defined, distillation pipeline needed
**Components**:
- `memory/packs/` - LLM-optimized context bundles
- `memory/sources/` - Raw input files
- `memory/snapshots/` - Point-in-time captures

**Separation Contract**:
- Supabase = operational memory (logs, runs, artifacts)
- Git packs = guidance memory (runbooks, patterns, policy)

### 3. Finance PPM (Medium)
**Status**: Core modules deployed, BIR integration pending
**Components**:
- `ipai_finance_ppm` - Month-end close
- `ipai_finance_bir_compliance` - Tax filing
- n8n finance-handler workflow

## Known Blockers

| Issue | Workaround |
|-------|------------|
| GitHub iterations API missing | Use UI for Quarter/Sprint setup |
| Vault beta limitations | Fallback to env vars for OAuth tokens |
| Odoo Enterprise parity | Use OCA equivalents where available |

## Error Recovery

If marketplace sync fails:
```sql
-- Check failed syncs
SELECT * FROM marketplace.artifact_syncs WHERE status = 'failed';

-- Retry failed sync
UPDATE marketplace.artifact_syncs SET status = 'pending' WHERE id = '<sync_id>';
```

If webhook verification fails:
```bash
# Check Edge Function logs
supabase functions logs marketplace-webhook --tail
```
