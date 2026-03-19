# Org Doc Platform Operating Model

> Defines ownership, cadences, and operational procedures for the
> org-wide documentation platform.

---

## Ownership

### Platform Owner

**Role**: Platform Engineering
**Responsibility**: Infrastructure, deployment, search quality, index health

### Source Family Owners

| Source Family | Owner | Scope |
|---------------|-------|-------|
| `docs/architecture/` | Platform Engineering | Architecture decision records, platform diagrams |
| `docs/contracts/` | Platform Engineering | Cross-domain contracts, eval contracts |
| `docs/operations/` | Platform Engineering | Operational runbooks, incident response |
| `docs/platform/` | Platform Engineering | Platform-specific docs (this file) |
| `spec/` | Product/Engineering | Spec bundles (PRD, constitution, plan, tasks) |
| `addons/ipai/` | Module Owners | Module-level documentation and manifests |
| `.claude/rules/` | Platform Engineering | Agent behavior rules, coding conventions |
| `CLAUDE.md` | Platform Engineering | Root project instructions |
| `infra/` | Platform Engineering | Infrastructure configs and SSOT files |
| `scripts/` | Platform Engineering | Automation scripts and CI tooling |
| External docs | Designated per source | Azure docs, OCA wiki, vendor docs |

### Ownership Transfer

When an owner leaves or role changes:
1. Update the source family table above
2. Update `source_inventory.yaml` owner fields
3. Notify the new owner of staleness obligations
4. Record transfer in commit message

---

## Refresh Cadence

| Refresh Type | Frequency | Trigger | Scope |
|-------------|-----------|---------|-------|
| Incremental | Weekly (Monday 07:00 UTC) | Scheduled workflow | Changed files since last run |
| Manual | On-demand | `workflow_dispatch` | Specified sources or all |
| Full rebuild | Quarterly | Manual trigger | Delete and recreate entire index |
| Emergency | As needed | Manual | Specific source after critical update |

### Incremental Refresh

The weekly refresh:
1. Uses `git log --since` to detect changed files
2. Re-embeds only changed documents
3. Updates search index via upsert
4. Reports stats: added, updated, unchanged, errors

### Full Rebuild

Quarterly full rebuild ensures index consistency:
1. Delete existing index
2. Recreate index with current schema
3. Load and embed all documents from all sources
4. Validate with eval query suite
5. Report total doc count, source distribution

---

## Eval Cadence

| Eval Activity | Frequency | Owner |
|---------------|-----------|-------|
| Automated score calculation | Weekly (after refresh) | CI pipeline |
| Blocker review | Monthly | Platform Engineering |
| Full re-assessment | Quarterly | Platform Engineering |
| Eval query update | Quarterly | All source owners |

### Monthly Blocker Review

1. Run `python agents/evals/score_org_doc_platform.py`
2. Review blockers list
3. Prioritize next-highest-value actions
4. Update capability scores with new evidence
5. Record decisions in `docs/evidence/<stamp>/org-docs-kb/eval_review.md`

---

## Index Rebuild Policy

### Triggers for Full Rebuild

- Schema change (new fields, changed analyzers)
- Embedding model change (new deployment, different dimensions)
- Quarterly scheduled maintenance
- Corruption or data loss detected

### Rebuild Procedure

```bash
# 1. Notify stakeholders
# 2. Run full rebuild workflow
gh workflow run org-docs-refresh.yml --field mode=full

# 3. Validate with eval queries
python agents/evals/score_org_doc_platform.py

# 4. Compare scores with previous eval
# 5. If regression, investigate and fix before marking complete
```

---

## Stale Doc Handling

### Definition

A document is **stale** if its source file has not been modified in 90 days.

### Automated Handling

1. During each refresh, compute days-since-last-modified for each doc
2. Flag docs where `days_since_modified > 90` as stale
3. Stale docs remain in index but with `is_stale: true` metadata
4. Stale docs are deprioritized in search results (lower boost)

### Owner Notification

- Monthly: Generate stale doc report per source family
- Notify source family owner via standard channels
- Owner must either:
  - Update the doc (resets staleness)
  - Confirm the doc is still current (touch with no-op commit)
  - Mark for deprecation in `source_inventory.yaml`

### Escalation

If a source family has >50% stale docs for 2 consecutive months:
1. Escalate to platform owner
2. Consider removing source family from index
3. Document decision in monthly eval review

---

## Deprecation

### Marking a Doc as Deprecated

1. Add `deprecated: true` and `deprecated_date` to `source_inventory.yaml` entry
2. Optionally add `replacement` path pointing to the successor
3. On next refresh, deprecated docs are excluded from indexing
4. After 30-day grace period, deprecated docs are removed from index

### Marking a Source Family as Deprecated

1. Update source family entry in `source_inventory.yaml`
2. Remove from refresh workflow scope
3. Notify all consumers of the source family
4. After 90-day grace period, remove all docs from index

---

## Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Source coverage | >90% of known sources indexed | Source inventory completeness |
| Freshness | <10% stale docs | Stale doc count / total doc count |
| Retrieval quality | >70% recall on eval queries | Eval suite results |
| Citation accuracy | >80% on eval queries | Manual spot-check quarterly |
| Index health | 0 failed refreshes per month | Workflow success rate |
| Platform uptime | >99% | Health check success rate |

---

*Created: 2026-03-15*
*Owner: Platform Engineering*
