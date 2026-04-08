---
name: entra-mfa-ca-hardening
description: Entra ID MFA enforcement and Conditional Access policy hardening
microsoft_capability_family: "Microsoft Entra / Security"
---

# entra-mfa-ca-hardening

## Microsoft Capability Family

**Microsoft Entra / Security**

## Purpose

Ensure all platform identities enforce MFA via Conditional Access. Validate CA policies cover admin roles and block legacy authentication.

## Required Repo Evidence

- `spec/entra-identity-migration/`
- `infra/ssot/azure/service-matrix.yaml`
- `docs/evidence/<stamp>/entra-mfa-ca/`

## Microsoft Learn MCP Usage

### Search Prompts

1. `microsoft_docs_search` — "Entra ID Conditional Access policy MFA enforcement"
2. `microsoft_docs_search` — "Microsoft Entra block legacy authentication"
3. `microsoft_docs_search` — "Entra ID authentication strength requirements"

## Workflow

1. Classify under Microsoft Entra / Security
2. Inspect repo evidence first
3. Use Learn MCP to validate recommended Microsoft pattern
4. Compare repo vs official pattern
5. Propose minimal patch
6. Require runtime/test/evidence before claiming done

## Completion Criteria

CA policy requiring MFA exists, legacy auth blocked, admin roles have extra constraints, CA export in evidence.
