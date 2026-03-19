# Odoo Documentation Platform - Deployment Guide

> Production deployment guide for the automated Odoo documentation platform

**Status**: Production-ready
**Last Updated**: 2026-03-05
**Components**: GitHub Actions, Supabase Edge Functions, GitHub Pages, Sphinx

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Official Odoo Docs                      │
│           https://github.com/odoo/documentation             │
└────────────────────┬────────────────────────────────────────┘
                     │ Daily sync (3 AM UTC)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 GitHub Actions Workflow                     │
│  - Sync RST files                                          │
│  - Build search index                                      │
│  - Generate Sphinx HTML                                    │
│  - Deploy to GitHub Pages                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┬────────────────────┐
         ▼                       ▼                    ▼
┌─────────────────┐    ┌──────────────────┐   ┌──────────────┐
│  GitHub Pages   │    │  Supabase Edge   │   │   pgvector   │
│  Static Docs    │    │   RAG Endpoint   │   │   Embeddings │
│  (Sphinx HTML)  │    │  (docs-ai-ask)   │   │              │
└─────────────────┘    └──────────────────┘   └──────────────┘
         │                       │                    │
         └───────────┬───────────┴────────────────────┘
                     ▼
           ┌──────────────────┐
           │   AI Chat Widget │
           │   (Real-time)    │
           └──────────────────┘
```

---

## Prerequisites

### 1. GitHub Repository Configuration

**Enable GitHub Pages:**
1. Go to repository **Settings** → **Pages**
2. Source: **GitHub Actions**
3. No custom domain needed (uses `github.io` subdomain)

### 2. GitHub Secrets

Required secrets in repository settings:

```bash
# Optional: Slack notifications
SLACK_BOT_TOKEN=xoxb-your-token-here

# Edge Function will use Supabase environment variables
# (ANTHROPIC_API_KEY, OPENAI_API_KEY)
```

### 3. Supabase Edge Function Deployment

Deploy the enhanced RAG endpoint:

```bash
# From repository root
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo

# Deploy Edge Function
supabase functions deploy docs-ai-enhanced \
  --project-ref spdtwktxdalcfigzeqrz

# Set required secrets
supabase secrets set ANTHROPIC_API_KEY=sk-ant-... \
  --project-ref spdtwktxdalcfigzeqrz

supabase secrets set OPENAI_API_KEY=sk-... \
  --project-ref spdtwktxdalcfigzeqrz
```

### 4. Database Functions

Ensure these RPC functions exist in Supabase:

```sql
-- Hybrid search function
CREATE OR REPLACE FUNCTION docs_ai_hybrid_search(
  match_tenant_id TEXT,
  query_text TEXT,
  query_embedding vector(1536),
  match_count INT DEFAULT 8,
  vector_weight FLOAT DEFAULT 0.7,
  keyword_weight FLOAT DEFAULT 0.3
)
RETURNS TABLE (
  chunk_id TEXT,
  document_id TEXT,
  content TEXT,
  url TEXT,
  title TEXT,
  combined_score FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  WITH vector_search AS (
    SELECT
      id::TEXT as chunk_id,
      document_id::TEXT,
      content,
      url,
      title,
      (1 - (embedding <=> query_embedding)) * vector_weight as vector_score
    FROM docs.chunks
    WHERE tenant_id = match_tenant_id
      AND embedding IS NOT NULL
    ORDER BY embedding <=> query_embedding
    LIMIT match_count
  ),
  keyword_search AS (
    SELECT
      id::TEXT as chunk_id,
      document_id::TEXT,
      content,
      url,
      title,
      ts_rank(search_vector, websearch_to_tsquery('english', query_text)) * keyword_weight as keyword_score
    FROM docs.chunks
    WHERE tenant_id = match_tenant_id
      AND search_vector @@ websearch_to_tsquery('english', query_text)
    ORDER BY keyword_score DESC
    LIMIT match_count
  )
  SELECT DISTINCT ON (v.chunk_id)
    v.chunk_id,
    v.document_id,
    v.content,
    v.url,
    v.title,
    COALESCE(v.vector_score, 0) + COALESCE(k.keyword_score, 0) as combined_score
  FROM vector_search v
  FULL OUTER JOIN keyword_search k USING (chunk_id)
  ORDER BY v.chunk_id, combined_score DESC
  LIMIT match_count;
END;
$$;

-- Question logging
CREATE OR REPLACE FUNCTION docs_ai_log_question(
  p_tenant_id TEXT,
  p_user_id TEXT,
  p_surface TEXT,
  p_question TEXT,
  p_context JSONB
)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
  v_question_id TEXT;
BEGIN
  INSERT INTO docs.questions (tenant_id, user_id, surface, question, context)
  VALUES (p_tenant_id, p_user_id, p_surface, p_question, p_context)
  RETURNING id::TEXT INTO v_question_id;

  RETURN v_question_id;
END;
$$;

-- Answer logging
CREATE OR REPLACE FUNCTION docs_ai_log_answer(
  p_question_id TEXT,
  p_tenant_id TEXT,
  p_answer TEXT,
  p_citations JSONB,
  p_confidence FLOAT,
  p_model TEXT,
  p_surface TEXT
)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
  v_answer_id TEXT;
BEGIN
  INSERT INTO docs.answers (
    question_id,
    tenant_id,
    answer,
    citations,
    confidence,
    model,
    surface
  )
  VALUES (
    p_question_id::UUID,
    p_tenant_id,
    p_answer,
    p_citations,
    p_confidence,
    p_model,
    p_surface
  )
  RETURNING id::TEXT INTO v_answer_id;

  RETURN v_answer_id;
END;
$$;
```

---

## Deployment Steps

### Step 1: Run Initial Sync

Trigger the workflow manually to perform the first sync:

```bash
# Via GitHub CLI
gh workflow run docs-sync-odoo-official.yml

# Or via GitHub UI
# Actions → Sync Official Odoo Documentation → Run workflow
```

**Expected output:**
- Synced RST files in `docs/odoo-official/`
- Generated search index at `docs/odoo-official/search-index.json`
- Deployed static site to GitHub Pages

**Verification:**
```bash
# Check synced files
ls -R docs/odoo-official/

# Check search index
cat docs/odoo-official/search-index.json | jq '.document_count'

# Visit deployed site
open https://insightpulseai.github.io/odoo/
```

### Step 2: Configure Custom Domain (Optional)

If using a custom domain like `docs.insightpulseai.com`:

1. **Add DNS CNAME record:**
   ```
   docs.insightpulseai.com → insightpulseai.github.io
   ```

2. **Configure in GitHub:**
   - Settings → Pages → Custom domain → `docs.insightpulseai.com`
   - Wait for DNS check (may take 24 hours)
   - Enable "Enforce HTTPS" once DNS propagates

3. **Update workflow:**
   Edit `.github/workflows/docs-sync-odoo-official.yml` and uncomment CNAME configuration

### Step 3: Test AI Chat Widget

Visit the deployed documentation site and:

1. Look for the 🤖 button in bottom-right corner
2. Click to open chat panel
3. Ask a test question: "How do I create a computed field in Odoo 19?"
4. Verify:
   - ✅ Answer appears within 3-5 seconds
   - ✅ Citations are included with clickable links
   - ✅ Answer is relevant and accurate

**Troubleshooting AI chat:**
```bash
# Check Edge Function logs
supabase functions logs docs-ai-enhanced \
  --project-ref spdtwktxdalcfigzeqrz

# Test Edge Function directly
curl -X POST \
  https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/docs-ai-enhanced \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I create a model in Odoo?",
    "tenantId": "ipai-odoo-docs",
    "surface": "docs-static"
  }'
```

### Step 4: Enable Automated Daily Sync

The workflow runs automatically at 3 AM UTC daily. No action required.

**Monitor sync status:**
```bash
# View recent workflow runs
gh run list --workflow=docs-sync-odoo-official.yml --limit 10

# View specific run details
gh run view <run-id>

# View run logs
gh run view <run-id> --log
```

---

## Configuration Options

### Sync Frequency

Edit `.github/workflows/docs-sync-odoo-official.yml`:

```yaml
on:
  schedule:
    # Change cron expression
    # Daily at 3 AM UTC (current)
    - cron: '0 3 * * *'

    # Weekly on Monday at 3 AM UTC
    # - cron: '0 3 * * 1'

    # Twice daily (3 AM and 3 PM UTC)
    # - cron: '0 3,15 * * *'
```

### Search Configuration

Adjust hybrid search weights in Edge Function:

```typescript
// supabase/functions/docs-ai-enhanced/index.ts

const VECTOR_WEIGHT = 0.7;    // 70% semantic similarity
const KEYWORD_WEIGHT = 0.3;   // 30% keyword matching
const MAX_CHUNKS = 8;         // Number of context chunks
```

### AI Model Configuration

Change model in Edge Function or via environment variable:

```bash
# Use different Claude model
supabase secrets set DEFAULT_MODEL="claude-opus-4-6" \
  --project-ref spdtwktxdalcfigzeqrz

# Use different embedding model
supabase secrets set DEFAULT_EMBEDDING_MODEL="text-embedding-3-large" \
  --project-ref spdtwktxdalcfigzeqrz
```

### Sphinx Theme Customization

Edit `docs/conf.py` in the workflow to customize appearance:

```python
html_theme_options = {
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': True,
    'navigation_depth': 4,
    'collapse_navigation': False,  # Change to True for auto-collapse
    'sticky_navigation': True,
    'includehidden': True,
    'titles_only': False  # Change to True for compact TOC
}
```

---

## Monitoring & Analytics

### GitHub Actions Monitoring

```bash
# View workflow status
gh run list --workflow=docs-sync-odoo-official.yml

# View failed runs
gh run list --workflow=docs-sync-odoo-official.yml --status failure

# Re-run failed workflow
gh run rerun <run-id>
```

### Edge Function Analytics

Query Supabase for usage stats:

```sql
-- Question volume by day
SELECT
  DATE(created_at) as date,
  COUNT(*) as questions,
  AVG(confidence) as avg_confidence
FROM docs.answers
WHERE tenant_id = 'ipai-odoo-docs'
  AND created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Popular questions
SELECT
  question,
  COUNT(*) as frequency
FROM docs.questions
WHERE tenant_id = 'ipai-odoo-docs'
  AND created_at >= NOW() - INTERVAL '7 days'
GROUP BY question
ORDER BY frequency DESC
LIMIT 20;

-- Low confidence answers (need improvement)
SELECT
  q.question,
  a.confidence,
  a.answer
FROM docs.answers a
JOIN docs.questions q ON a.question_id = q.id
WHERE a.confidence < 0.5
  AND a.created_at >= NOW() - INTERVAL '7 days'
ORDER BY a.confidence ASC
LIMIT 20;
```

### GitHub Pages Traffic

View in GitHub repository:
- **Insights** → **Traffic** → **Popular content**

---

## Troubleshooting

### Workflow Fails at Sync Step

**Symptom**: "fatal: could not read Username" or connection error

**Solution**:
```bash
# Verify official Odoo repo is accessible
git ls-remote https://github.com/odoo/documentation.git 19.0

# Check workflow permissions
# Settings → Actions → General → Workflow permissions → Read and write
```

### Sphinx Build Fails

**Symptom**: "build errors" in build-static-site job

**Solution**:
```bash
# Test locally
pip install sphinx sphinx-rtd-theme myst-parser
sphinx-build -b html docs docs/_build/html

# Check for RST syntax errors
find docs/odoo-official -name '*.rst' -exec rst2html.py --strict {} /dev/null \;
```

### AI Chat Widget Not Appearing

**Symptom**: No 🤖 button on deployed site

**Solution**:
1. Check widget script injection:
   ```bash
   curl https://insightpulseai.github.io/odoo/ | grep "ai-chat-widget.js"
   ```

2. Check browser console for JavaScript errors

3. Verify Edge Function is accessible:
   ```bash
   curl https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/docs-ai-enhanced
   # Should return 405 (Method not allowed) - confirms endpoint exists
   ```

### AI Responses Timeout

**Symptom**: Chat shows "⚠️ Network error: timeout"

**Solution**:
```bash
# Check Edge Function timeout setting (default 300s)
# Increase if needed in Supabase dashboard

# Check API keys are set
supabase secrets list --project-ref spdtwktxdalcfigzeqrz | grep -E "ANTHROPIC|OPENAI"

# Test with smaller question
curl -X POST \
  https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/docs-ai-enhanced \
  -H "Content-Type: application/json" \
  -d '{"question":"What is Odoo?","tenantId":"ipai-odoo-docs"}'
```

---

## Cost Estimation

### GitHub Actions

- **Free tier**: 2,000 minutes/month for private repos, unlimited for public
- **This workflow**: ~10 minutes/run = ~300 minutes/month (daily sync)
- **Cost**: $0 (within free tier)

### GitHub Pages

- **Free tier**: 1 GB storage, 100 GB bandwidth/month
- **This deployment**: ~500 MB storage, ~10 GB bandwidth/month (estimated)
- **Cost**: $0 (within free tier)

### Supabase Edge Functions

- **Free tier**: 500,000 invocations/month, 2 GB-hours compute
- **Estimated usage**: ~5,000 questions/month = ~5,000 invocations
- **Cost**: $0 (within free tier)

### OpenAI API (Embeddings + GPT fallback)

- **Embedding**: text-embedding-3-small @ $0.02 per 1M tokens
- **Estimated**: 500 questions/day × 200 tokens = 100K tokens/day = 3M tokens/month
- **Cost**: ~$0.06/month

### Anthropic API (Primary LLM)

- **Model**: Claude Sonnet 4.6 @ $3/$15 per 1M input/output tokens
- **Estimated**: 500 questions/day × (2K input + 500 output) = ~37.5M tokens/month
- **Cost**: ~$120/month (input: $112.50, output: $7.50)

**Total estimated cost**: ~$120/month (primarily Anthropic API)

**Cost optimization tips:**
1. Use caching for common questions (50% reduction)
2. Lower MAX_CHUNKS from 8 to 5 (30% reduction)
3. Use Claude Haiku for simple questions (80% cost reduction)
4. Implement rate limiting per user

---

## Maintenance

### Monthly Tasks

1. **Review analytics** - Check popular questions and low-confidence answers
2. **Update index** - Force rebuild if official docs had major changes
3. **Check costs** - Monitor API usage in Anthropic/OpenAI dashboards
4. **Test AI quality** - Ask 10 random questions and rate answers

### Quarterly Tasks

1. **Update dependencies** - Bump Sphinx, Supabase client versions
2. **Review search weights** - Adjust VECTOR_WEIGHT/KEYWORD_WEIGHT based on quality
3. **Optimize prompts** - Improve system prompt based on user feedback
4. **Backup logs** - Export docs.questions/answers tables to cold storage

### Annual Tasks

1. **Odoo version upgrade** - Update to Odoo 20.0 when released
2. **Infrastructure review** - Evaluate alternatives to GitHub Pages
3. **Security audit** - Review Edge Function security and rate limiting

---

## Next Steps

1. ✅ Deploy Edge Function: `supabase functions deploy docs-ai-enhanced`
2. ✅ Enable GitHub Pages in repository settings
3. ✅ Run first sync: `gh workflow run docs-sync-odoo-official.yml`
4. ⏳ Configure custom domain (optional): `docs.insightpulseai.com`
5. ⏳ Test AI chat widget with 10 sample questions
6. ⏳ Set up monitoring dashboard in Supabase
7. ⏳ Document internal knowledge base for team

---

**Status**: Production-ready automated documentation platform
**Support**: Internal documentation team
**SLA**: 99.5% uptime for static site, best-effort for AI chat
