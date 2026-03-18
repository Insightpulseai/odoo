# Checklist — azure-migration-ops

- [ ] Source resource confirmed as deprecated in CLAUDE.md or infrastructure.md
- [ ] Target Azure resource provisioned and healthy
- [ ] DNS records updated to point to Azure target (Cloudflare CNAME to Front Door)
- [ ] TLS certificate valid on new endpoint
- [ ] Secrets migrated from old provider to Azure Key Vault
- [ ] Old resource no longer receiving traffic (zero request count or equivalent)
- [ ] Codebase scanned for residual references to deprecated resource
- [ ] CI workflows updated to use new resource
- [ ] Rollback path documented before source teardown
- [ ] Migration evidence captured with before/after comparison
- [ ] Deprecated items table updated with completion date
- [ ] Evidence saved to `docs/evidence/{stamp}/azure-ops/migration/`
