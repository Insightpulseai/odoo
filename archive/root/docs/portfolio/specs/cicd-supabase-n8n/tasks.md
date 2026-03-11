# CI/CD with Supabase + n8n — Tasks

## Status Legend

- [x] Completed
- [ ] Pending
- [~] In Progress

---

## Phase 1: GitHub Actions Workflows

### Supabase CI/CD

- [x] Create `.github/workflows/supabase-deploy.yml`
- [x] Implement change detection for migrations
- [x] Implement change detection for edge functions
- [x] Add PR validation job
- [x] Add deployment job with environment support
- [x] Add n8n webhook notification
- [ ] Configure GitHub Secrets (manual)
- [ ] Test staging deployment
- [ ] Test production deployment

### n8n Orchestrator

- [x] Create `.github/workflows/n8n-orchestrator.yml`
- [x] Implement workflow JSON validation
- [x] Implement API-based sync to n8n
- [x] Add manual trigger capability
- [ ] Configure n8n API credentials (manual)
- [ ] Test workflow sync

### Unified Pipeline

- [x] Create `.github/workflows/insightpulse-cicd.yml`
- [x] Implement multi-component change detection
- [x] Add Supabase deployment job
- [x] Add Odoo deployment job
- [x] Add n8n sync job
- [x] Add unified notification step
- [ ] Test path-based detection
- [ ] Test manual dispatch

---

## Phase 2: n8n Workflows

### Deployment Notifications

- [x] Create `n8n/workflows/deployment-notify.json`
- [x] Implement webhook trigger
- [x] Add event parsing and enrichment
- [x] Add environment routing (prod vs staging)
- [x] Add Supabase logging
- [x] Add Slack notifications
- [x] Add Mattermost alerts for failures
- [ ] Import workflow to n8n instance (manual)
- [ ] Configure Supabase credential in n8n
- [ ] Configure Slack credential in n8n
- [ ] Test notification flow

### GitHub Deploy Trigger

- [x] Create `n8n/workflows/github-deploy-trigger.json`
- [x] Implement authenticated webhook
- [x] Add request validation
- [x] Add production approval flow
- [x] Add GitHub workflow dispatch
- [x] Add deployment logging
- [ ] Import workflow to n8n instance (manual)
- [ ] Configure GitHub token in n8n
- [ ] Test staging trigger
- [ ] Test production approval

---

## Phase 3: Configuration & Infrastructure

### GitHub Secrets

- [ ] Set `SUPABASE_ACCESS_TOKEN`
- [ ] Set `SUPABASE_DB_PASSWORD`
- [ ] Set `SUPABASE_PROJECT_ID`
- [ ] Set `N8N_API_URL`
- [ ] Set `N8N_API_KEY`
- [ ] Set `N8N_WEBHOOK_URL`
- [ ] Verify SSH secrets for Odoo deployment

### n8n Credentials

- [ ] Create Supabase API credential
- [ ] Create Slack OAuth credential
- [ ] Create GitHub Token credential
- [ ] Configure Mattermost webhook URL

### Supabase Schema

- [ ] Create `deployment_logs` table
- [ ] Create `deployment_requests` table
- [ ] Add RLS policies for audit tables
- [ ] Test logging from n8n

---

## Phase 4: Documentation

- [x] Create spec bundle (`spec/cicd-supabase-n8n/`)
- [x] Write constitution.md
- [x] Write prd.md
- [x] Write plan.md
- [x] Write tasks.md (this file)
- [ ] Update CLAUDE.md with CI/CD section
- [ ] Add workflow diagrams

---

## Phase 5: Verification

### Automated Tests

- [ ] Workflow syntax validation (YAML lint)
- [ ] n8n JSON validation
- [ ] Dry-run deployment test

### Manual Tests

- [ ] Supabase migration deployment (staging)
- [ ] Edge function deployment (staging)
- [ ] n8n workflow sync
- [ ] Deployment notification to Slack
- [ ] GitHub trigger from n8n
- [ ] Production approval flow

### Documentation

- [ ] Update README with CI/CD overview
- [ ] Document secret rotation procedure
- [ ] Create runbook for deployment failures

---

## Completion Criteria

- [ ] All GitHub Actions workflows pass on push to develop
- [ ] n8n webhooks receive and process deployment events
- [ ] Slack notifications sent for all deployments
- [ ] Deployment logs visible in Supabase
- [ ] Manual triggers work from n8n
- [ ] Production deployments require approval

---

## Notes

### Secrets Required

| Secret | Where to Get |
|--------|--------------|
| `SUPABASE_ACCESS_TOKEN` | Supabase Dashboard → Settings → API → Generate Token |
| `SUPABASE_DB_PASSWORD` | Supabase Dashboard → Settings → Database → Password |
| `N8N_API_KEY` | n8n → Settings → API → Create API Key |

### Known Limitations

- n8n workflow sync requires API access (not available on all plans)
- Production approval via Slack reactions is manual
- GitHub Actions concurrency may cause delays during high activity
