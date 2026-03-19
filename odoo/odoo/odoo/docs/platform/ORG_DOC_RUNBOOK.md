# Org Doc Platform Runbook

> Operational procedures for the org-wide documentation platform.

---

## 1. Trigger Manual Refresh

**When**: After a significant doc update, new source added, or emergency fix.

```bash
# Trigger via GitHub Actions
gh workflow run org-docs-refresh.yml

# Trigger with specific mode
gh workflow run org-docs-refresh.yml --field mode=incremental
gh workflow run org-docs-refresh.yml --field mode=full

# Monitor the run
gh run list --workflow=org-docs-refresh.yml --limit=5
gh run watch <run-id>
```

**Verification**:
```bash
# Check refresh workflow output for stats
gh run view <run-id> --log | grep -E "(added|updated|unchanged|errors)"

# Verify health after refresh
curl -s https://ipai-org-docs-kb.thankfulbush-191bdcb0.southeastasia.azurecontainerapps.io/health | python3 -m json.tool
```

---

## 2. Add a New Doc Source

**When**: A new documentation area needs to be searchable.

1. Verify the source meets admission policy (`docs/platform/ORG_DOC_ADMISSION_POLICY.md`)

2. Add entry to `source_inventory.yaml`:
```yaml
- path: "docs/new-area/"
  owner: "Your Team"
  doc_type: engineering
  sensitivity: internal
  format: markdown
  refresh_cadence: weekly
  added_date: "YYYY-MM-DD"
  notes: "What this source covers"
```

3. Commit the inventory change:
```bash
git add source_inventory.yaml
git commit -m "chore(org-docs): add docs/new-area/ to source inventory"
git push
```

4. Trigger a manual refresh to index the new source:
```bash
gh workflow run org-docs-refresh.yml --field mode=incremental
```

5. Verify the new docs appear in search:
```bash
curl -s "https://<endpoint>/search?q=<term-from-new-source>&doc_type=engineering" | python3 -m json.tool
```

---

## 3. Investigate Search Quality Issues

**When**: Users report that search returns irrelevant or missing results.

### Step 1: Check index health
```bash
curl -s https://<endpoint>/health | python3 -m json.tool
```

### Step 2: Run the eval suite
```bash
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo
python agents/evals/score_org_doc_platform.py
# Review artifacts/evals/org_doc_platform_eval.md
```

### Step 3: Test the specific failing query
```bash
curl -s "https://<endpoint>/search?q=<failing-query>" | python3 -m json.tool
```

### Step 4: Check if the expected source doc exists and is indexed
- Verify the doc exists in the repo
- Verify the doc is listed in `source_inventory.yaml`
- Verify the doc was included in the last refresh (check workflow logs)

### Step 5: Check embedding quality
- If the doc exists but is not returned, the embedding may not capture the query intent
- Consider adding the query to the eval suite for tracking
- Consider whether the doc needs better headings or structure

### Step 6: Document findings
```bash
mkdir -p docs/evidence/$(date +%Y%m%d-%H%M)/org-docs-kb
# Write findings to docs/evidence/<stamp>/org-docs-kb/search_quality_investigation.md
```

---

## 4. Rebuild the Index from Scratch

**When**: Quarterly maintenance, schema change, embedding model change, or data corruption.

```bash
# 1. Trigger full rebuild
gh workflow run org-docs-refresh.yml --field mode=full

# 2. Monitor progress
gh run watch <run-id>

# 3. Verify index health
curl -s https://<endpoint>/health | python3 -m json.tool

# 4. Run eval suite to compare against previous scores
python agents/evals/score_org_doc_platform.py

# 5. Compare with previous eval
diff artifacts/evals/org_doc_platform_eval.md <previous-eval>
```

**Warning**: Full rebuild deletes and recreates the index. Search will be unavailable during the rebuild (typically 5-15 minutes depending on corpus size).

---

## 5. Rotate Search API Keys

**When**: Key compromised, scheduled rotation (quarterly recommended).

1. Generate new API key in Azure Portal (Azure AI Search > Keys)

2. Update the secret in Azure Key Vault:
```bash
az keyvault secret set \
  --vault-name kv-ipai-dev \
  --name azure-search-api-key \
  --value "<new-key>"
```

3. Restart the container app to pick up the new key:
```bash
az containerapp revision restart \
  --name ipai-org-docs-kb \
  --resource-group rg-ipai-dev \
  --revision <active-revision>
```

4. Verify health:
```bash
curl -s https://<endpoint>/health | python3 -m json.tool
```

5. Revoke the old key in Azure Portal

6. Update the refresh workflow secret if it uses a separate key:
```bash
gh secret set AZURE_SEARCH_API_KEY --body "<new-key>"
```

---

## 6. Check Platform Health

**When**: Routine check, after deployment, after refresh, or when issues reported.

```bash
# Quick health check
curl -s https://ipai-org-docs-kb.thankfulbush-191bdcb0.southeastasia.azurecontainerapps.io/health

# Container app status
az containerapp show \
  --name ipai-org-docs-kb \
  --resource-group rg-ipai-dev \
  --query "{status:properties.runningStatus, replicas:properties.template.scale}" \
  --output table

# Recent logs
az containerapp logs show \
  --name ipai-org-docs-kb \
  --resource-group rg-ipai-dev \
  --tail 50

# Recent revisions
az containerapp revision list \
  --name ipai-org-docs-kb \
  --resource-group rg-ipai-dev \
  --output table
```

---

## 7. Run Capability Eval

**When**: Weekly (automated), monthly (manual review), quarterly (full re-assessment).

```bash
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo

# Run scorer
python agents/evals/score_org_doc_platform.py

# Review outputs
cat artifacts/evals/org_doc_platform_eval.md

# Check for blockers
python -c "
import json
with open('artifacts/evals/org_doc_platform_eval.json') as f:
    data = json.load(f)
print('Overall:', data['summary']['overall_score'])
print('Blocked:', data['summary']['release_blocked'])
for b in data['blockers']:
    print('  -', b)
"
```

---

## 8. Handle Stale Doc Alerts

**When**: Monthly stale doc report shows >10% stale docs in a source family.

1. Identify stale docs from the refresh report or eval output

2. For each stale doc, determine action:
   - **Still current**: Touch the file with a no-op commit to reset staleness
   - **Needs update**: Assign to source owner for update
   - **Should be deprecated**: Mark in `source_inventory.yaml` with `deprecated: true`

3. Track resolution:
```bash
# If doc is still current but hasn't changed
git commit --allow-empty -m "docs: confirm <path> is current (staleness reset)"

# If deprecating
# Edit source_inventory.yaml to add deprecated: true
git add source_inventory.yaml
git commit -m "chore(org-docs): deprecate <path>"
```

4. After changes, trigger refresh:
```bash
gh workflow run org-docs-refresh.yml --field mode=incremental
```

---

## Troubleshooting Quick Reference

| Symptom | Likely Cause | Action |
|---------|-------------|--------|
| Health check returns 503 | Container not running | Check ACA revision status, restart |
| Health check returns 200 but search fails | Search service key expired | Rotate key (section 5) |
| Refresh workflow fails | Git auth or Azure auth issue | Check workflow secrets |
| Search returns no results | Index empty or not populated | Run full rebuild (section 4) |
| Search returns stale results | Refresh not running | Check workflow schedule, trigger manual |
| Eval score dropped | Source removed or quality regression | Compare eval reports, investigate |

---

*Created: 2026-03-15*
*Owner: Platform Engineering*
