# Identity Governance — Canonical Model

## Overview

The ERP-on-Azure platform uses Microsoft Entra governance principles as the benchmark
identity-control model. Governance spans people, guests, applications, and AI agents.

---

## Core controls

- **Lifecycle workflows** for joiner / mover / leaver events
- **Entitlement management** for access assignment with approval policies
- **Access reviews** for recurring recertification of sensitive access
- **Privileged Identity Management (PIM)** for JIT administrative access
- **Least-privilege role selection** as the default administrative model

---

## Governed identities

| Identity type | Governance approach |
|---------------|-------------------|
| Employees | Lifecycle workflows, entitlement packages, access reviews |
| Guests / partners | Entitlement packages with expiration, access reviews |
| Service / application identities | Managed identities preferred, Key Vault for secrets |
| AI agent identities | Governed agent identities with human sponsor/owner |

---

## Agent identity policy

AI agents (Pulser, platform agents) are first-class governed identities.

Requirements:

- A **distinct identity model** — not shared application credentials
- **Scoped permissions** — minimum access for the agent's function
- A **human sponsor / owner** — named accountability for agent access
- **Reviewable and removable access** — lifecycle review and decommission
- **Access-package based assignment** where the Entra platform supports it

Where Microsoft Foundry provisions agent identities automatically (Entra Agent ID),
those identities inherit the governance controls of the platform.

---

## Privileged access model

- Standing privilege is minimized
- Administrative roles use **eligible assignment** with time-bound activation
- Activation requires justification and optional approval
- All privileged actions are audited

---

## Access review cadence

| Scope | Review frequency |
|-------|-----------------|
| Production admin roles | Quarterly |
| Guest / partner access | Quarterly |
| Agent identity access | Quarterly |
| Application service connections | Semi-annually |
| Developer access to staging | Semi-annually |

---

## SAP positioning

SAP is an **optional governed integration surface** — one of many external systems whose
access can be managed through Entra entitlement packages and access reviews. SAP is not
the benchmark architecture for the identity governance model.

---

*Last updated: 2026-04-10*
