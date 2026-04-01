# Odoo Connector

Wrapper for Odoo XML-RPC/JSON-RPC interactions used by automation jobs.

## Scope

- Record CRUD via XML-RPC (`/xmlrpc/2/object`)
- Authentication via `/xmlrpc/2/common`
- Report generation triggers
- Module state queries

## Auth

Uses API key or session token. Credentials resolved from Azure Key Vault.
Target: `erp.insightpulseai.com` (production) or local dev endpoint.

<!-- TODO: Implement base connector with connection pooling and retry -->
