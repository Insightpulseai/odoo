# AFC RAG Deployment Checklist

**Module**: ipai_ask_ai v18.0.1.0.0
**Integration**: AFC Close Manager RAG System
**Date**: 2026-01-01
**Status**: ✅ Code Complete | ⏳ Awaiting Deployment

---

## Pre-Deployment Checklist

### ✅ Code Complete
- [x] AFC RAG service implemented (`models/afc_rag_service.py`)
- [x] AI assistant integration (`models/ask_ai_service.py`)
- [x] System parameters configured (`data/afc_config_params.xml`)
- [x] Module manifest updated (`__manifest__.py`)
- [x] Model imports updated (`models/__init__.py`)
- [x] Documentation created (README, DEPLOYMENT_STATUS, CHANGES)
- [x] Deployment scripts created (setup, test, deploy)

### ✅ Testing Complete
- [x] Database connection test (PostgreSQL 17.6)
- [x] Seed data verification (tax brackets, SoD roles, conflicts)
- [x] Schema validation (document_chunks, chunk_embeddings, pgvector)
- [x] Health check functionality
- [x] Semantic search placeholder validation

### ⏳ Prerequisites
- [x] psycopg2-binary installed
- [ ] Docker/Colima running
- [ ] Odoo CE 18.0 instance accessible
- [x] Supabase database accessible
- [x] Environment variables set (POSTGRES_PASSWORD, etc.)

---

## Deployment Steps

### Option 1: Automated Deployment (Preferred)

**Prerequisites**:
- Docker/Colima running
- Odoo stack defined in `docker-compose.yml`

**Commands**:
```bash
# 1. Start Docker (if using Colima)
colima start

# 2. Run automated deployment
./scripts/deploy_afc_rag.sh

# 3. Follow on-screen instructions for System Parameters
```

**Script Actions**:
1. ✅ Checks psycopg2 installation
2. ✅ Validates environment variables
3. ✅ Starts Odoo Docker stack
4. ✅ Upgrades ipai_ask_ai module
5. ✅ Restarts Odoo
6. ⚠️  Prompts for manual System Parameters configuration
7. ✅ Runs test suite
8. ✅ Verifies module installation

### Option 2: Manual Deployment

**Step 1: Copy Module to Odoo**
```bash
# If using Docker
docker cp addons/ipai_ask_ai <odoo_container>:/mnt/extra-addons/

# If using local Odoo installation
cp -r addons/ipai_ask_ai /path/to/odoo/addons/
```

**Step 2: Restart Odoo**
```bash
# Docker
docker compose restart web

# Systemd
sudo systemctl restart odoo

# Direct command
odoo -c /etc/odoo/odoo.conf --stop-after-init
```

**Step 3: Update Apps List**
1. Login to Odoo
2. Navigate to Apps
3. Click "Update Apps List"
4. Wait for list refresh

**Step 4: Install Module**
1. In Apps, search for "IPAI Ask AI"
2. Click "Install" or "Upgrade"
3. Wait for installation to complete

**Step 5: Configure System Parameters**
1. Navigate to: Settings → Technical → Parameters → System Parameters
2. Locate and update the following parameters:

| Parameter | Value | Required |
|-----------|-------|----------|
| `afc.supabase.db_host` | db.spdtwktxdalcfigzeqrz.supabase.co | ✅ Yes |
| `afc.supabase.db_name` | postgres | ✅ Yes |
| `afc.supabase.db_user` | postgres | ✅ Yes |
| `afc.supabase.db_password` | [from $POSTGRES_PASSWORD] | ✅ Yes |
| `afc.supabase.db_port` | 5432 | ✅ Yes |
| `openai.api_key` | [your OpenAI API key] | ⚠️ Optional |
| `openai.embedding_model` | text-embedding-3-large | ⚠️ Optional |

3. Save changes
4. Restart Odoo (if required by your setup)

**Step 6: Verify Installation**
```bash
# Run test suite
python3 scripts/test_afc_rag.py

# Check Odoo logs
docker compose logs web | tail -100
# or
tail -f /var/log/odoo/odoo-server.log
```

---

## Post-Deployment Verification

### Test 1: Module Installation ✅
**Action**: Check Apps list in Odoo UI
**Expected**: "IPAI Ask AI Assistant" shows as "Installed"

### Test 2: AI Assistant Widget 🧪
**Action**:
1. Login to Odoo
2. Look for chat bubble icon in top-right header
3. Click to open AI assistant

**Expected**: Chat widget opens with welcome message

### Test 3: AFC Query Routing 🧪
**Action**: Submit query in AI assistant
```
Test query: "What is the BIR 1601-C filing deadline?"
```

**Expected Response Format**:
```
[AI-Generated Answer based on knowledge base]

📚 Sources:
• [Source 1] (similarity: XX%)
• [Source 2] (similarity: XX%)
• [Source 3] (similarity: XX%)

✅ Confidence: XX%
```

**If Knowledge Base Empty**:
```
I don't have enough information about that topic in my knowledge base.

📚 Sources:

❓ Confidence: 0%
```

### Test 4: Non-AFC Query Fallback 🧪
**Action**: Submit non-AFC query
```
Test query: "How many customers do I have?"
```

**Expected**: Pattern-based response (original AI assistant behavior)
```
You have X customers in the system.
```

### Test 5: Health Check 🧪
**Action**: Run health check from Python shell
```python
# Access Odoo shell
docker compose exec web odoo shell -d production

# Or via xmlrpc
import xmlrpc.client
# ... authenticate ...
models.execute_kw(db, uid, password,
    'afc.rag.service', 'health_check', [])
```

**Expected Output**:
```python
{
    'status': 'ok' | 'error',
    'chunk_count': 0,  # Until knowledge base ingested
    'embedding_count': 0,
    'message': 'AFC RAG service healthy. 0 chunks with 0 embeddings available.'
}
```

### Test 6: Semantic Search 🧪
**Action**: Test semantic search from Python shell
```python
env = odoo.api.Environment(cr, uid, {})
AfcRag = env['afc.rag.service']

results = AfcRag.semantic_search(
    "What is the BIR 1601-C deadline?",
    top_k=3
)

print(f"Found {len(results)} results")
for r in results:
    print(f"- {r['source']} (similarity: {r['similarity']:.2f})")
```

**Expected** (with empty knowledge base):
```
Found 0 results
```

**Expected** (with populated knowledge base):
```
Found 3 results
- BIR 1601-C Documentation (similarity: 0.12)
- Philippine Tax Code 2024 (similarity: 0.15)
- AFC Compliance Checklist (similarity: 0.18)
```

---

## Troubleshooting

### Issue 1: Module Not Found in Apps List
**Symptoms**: "IPAI Ask AI" not visible in Apps
**Solution**:
1. Verify module copied to addons path: `ls /path/to/odoo/addons/ipai_ask_ai`
2. Check Odoo addons path config: `grep addons_path /etc/odoo/odoo.conf`
3. Update Apps List: Apps → Update Apps List
4. Check Odoo logs for errors: `docker compose logs web | grep ipai_ask_ai`

### Issue 2: Installation Fails
**Symptoms**: Module installation error
**Solution**:
1. Check dependencies: `pip list | grep psycopg2`
2. Check Odoo logs: `docker compose logs web | tail -50`
3. Verify manifest syntax: `python3 -m py_compile addons/ipai_ask_ai/__manifest__.py`
4. Check file permissions: `ls -la addons/ipai_ask_ai/`

### Issue 3: AFC RAG Service Not Configured
**Symptoms**: "AFC RAG service not configured" error
**Solution**:
1. Check System Parameters: Settings → Technical → Parameters → System Parameters
2. Verify `afc.supabase.db_password` is set
3. Check environment variables: `env | grep POSTGRES`
4. Test connection: `python3 scripts/test_afc_rag.py`

### Issue 4: AI Assistant Widget Not Visible
**Symptoms**: No chat bubble icon in header
**Solution**:
1. Clear browser cache and reload
2. Check if module installed: Apps → Search "IPAI Ask AI"
3. Check JavaScript errors: Browser console (F12)
4. Verify assets loaded: Check browser Network tab for `ask_ai_*.js`

### Issue 5: Queries Return "Not Enough Information"
**Symptoms**: All AFC queries return empty knowledge base message
**Solution**:
1. This is **expected** until knowledge base is ingested
2. Check chunk count: `psql "$POSTGRES_URL_NON_POOLING" -c "SELECT COUNT(*) FROM afc.document_chunks;"`
3. Expected: 0 rows until documents ingested
4. See "Knowledge Base Ingestion" section below

### Issue 6: Permission Denied on Database Tables
**Symptoms**: PostgreSQL permission errors
**Solution**:
1. Check RLS policies: `psql "$POSTGRES_URL_NON_POOLING" -c "SELECT * FROM pg_policies WHERE tablename LIKE 'document_chunks';"`
2. Set session variables (see README_AFC_RAG.md "Set Session Variables for RLS")
3. Or use service role: `self.env.cr.execute("SET ROLE service_role")`

---

## Knowledge Base Ingestion

### Current Status: 📦 Empty
- `afc.document_chunks`: 0 rows
- `afc.chunk_embeddings`: 0 rows

### Ingestion Roadmap

**Phase 1: Document Preparation (Week 1)**
- [ ] Gather BIR form instructions (1601-C, 1700, 2550Q)
- [ ] Collect AFC Close Manager documentation
- [ ] Compile SOX 404 compliance guidelines
- [ ] Assemble Four-Eyes principle documentation

**Phase 2: Chunking (Week 1)**
- [ ] Implement document chunking script (500-1000 tokens per chunk)
- [ ] Maintain source attribution and metadata
- [ ] Insert chunks into `afc.document_chunks` table
- [ ] Target: ≥100 chunks for MVP, ≥1000 for production

**Phase 3: Embedding Generation (Week 1-2)**
- [ ] Configure OpenAI API key in System Parameters
- [ ] Implement actual `_generate_embedding()` method
- [ ] Batch process all chunks (rate limit: 3000 req/min)
- [ ] Insert embeddings into `afc.chunk_embeddings` table

**Phase 4: Validation (Week 2)**
- [ ] Run health check (should return "ok" status)
- [ ] Test semantic search with 10+ queries
- [ ] Measure Top-5 hit rate (target: ≥70% for MVP, ≥85% for production)
- [ ] Validate response quality and source citations

**Ingestion Script Template**:
See `addons/ipai_ask_ai/DEPLOYMENT_STATUS.md` for complete script

---

## Success Criteria

### MVP (Minimum Viable Product)
- [ ] Module installed and visible in Odoo Apps
- [ ] AI assistant widget accessible in UI
- [ ] AFC query routing functional (keyword detection)
- [ ] Non-AFC queries fallback to pattern-based logic
- [ ] System Parameters configured correctly
- [ ] Health check returns valid status
- [ ] Knowledge base ≥100 document chunks (optional for code testing)

### Production-Ready
- [ ] All MVP criteria met
- [ ] Knowledge base ≥1000 document chunks covering all BIR forms
- [ ] OpenAI embeddings configured and generating
- [ ] Claude 3.5 Sonnet or GPT-4 answer generation (future phase)
- [ ] Semantic search Top-5 hit rate ≥85%
- [ ] Response accuracy ≥92% on benchmark queries
- [ ] Hallucination rate <5%
- [ ] RLS policies tested and validated
- [ ] User feedback collection implemented
- [ ] Performance monitoring enabled

---

## Deployment Completion Checklist

**Before Marking Complete**:
- [ ] All deployment steps executed successfully
- [ ] Post-deployment verification tests passed
- [ ] System Parameters configured
- [ ] Module visible and installed in Odoo
- [ ] AI assistant widget functional
- [ ] AFC query routing tested
- [ ] Non-AFC fallback tested
- [ ] Health check passed
- [ ] Documentation reviewed
- [ ] Team trained on new functionality

**Sign-Off**:
- Date: ____________
- Deployed By: ____________
- Verified By: ____________
- Notes: ____________

---

## Rollback Procedure

**If Deployment Fails**:

1. **Uninstall Module**:
   ```bash
   # Via Odoo UI
   Apps → Search "IPAI Ask AI" → Uninstall

   # Via CLI
   docker compose exec web odoo -d production -u ipai_ask_ai --uninstall --stop-after-init
   ```

2. **Remove Files** (if needed):
   ```bash
   docker compose exec web rm -rf /mnt/extra-addons/ipai_ask_ai
   # or
   rm -rf /path/to/odoo/addons/ipai_ask_ai
   ```

3. **Restart Odoo**:
   ```bash
   docker compose restart web
   # or
   sudo systemctl restart odoo
   ```

4. **Verify Removal**:
   - Check Apps list (should not show "IPAI Ask AI")
   - Check AI assistant widget (should not be visible)
   - Check logs for errors

---

## Support Resources

**Documentation**:
- `README_AFC_RAG.md` - Comprehensive deployment guide (485 lines)
- `DEPLOYMENT_STATUS.md` - Real-time deployment status (325 lines)
- `CHANGES.md` - Complete change summary (389 lines)
- `DEPLOYMENT_CHECKLIST.md` - This file

**Scripts**:
- `scripts/deploy_afc_rag.sh` - Automated deployment
- `scripts/setup_afc_rag.sh` - Setup validation
- `scripts/test_afc_rag.py` - Test suite

**External Resources**:
- Supabase Dashboard: https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz
- AFC Schema Docs: `supabase/migrations/AFC_DEPLOYMENT_SUMMARY.md`
- Odoo CE 18 Docs: https://www.odoo.com/documentation/18.0/
- pgvector Docs: https://github.com/pgvector/pgvector

---

**Last Updated**: 2026-01-01
**Next Review**: After Docker/Colima startup and module installation
**Status**: ⏳ Awaiting Docker startup for deployment
