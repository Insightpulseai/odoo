# Directory Authority Matrix

Canonical source: [`platform/ssot/identity/directory-authority-matrix.yaml`](../../platform/ssot/identity/directory-authority-matrix.yaml)

## Core split

- `insightpulseai.com` mailboxes -> Zoho Mail
- `w9studio.net` mailboxes -> Google Workspace
- workforce / admin / guest / app / managed identity / agent identity -> Microsoft Entra
- TBWA/SMP workbook -> external contact directory / guest candidate source

## Key rule

Mailbox systems are not the primary identity authority.

## ERP rule

- Entra determines identity
- Odoo determines ERP authorization
- Odoo multi-company determines company / branch / trade-name context

## External collaborator rule

TBWA/SMP contacts should remain external contacts by default and only be promoted to Entra Guests or Odoo users when collaboration or ERP access is explicitly required.

## Related

- Entra target state: [`ssot/identity/entra_target_state.yaml`](../../ssot/identity/entra_target_state.yaml)
- 5-plane identity matrix: [`ssot/identity/entra-identity-matrix.yaml`](../../ssot/identity/entra-identity-matrix.yaml)
- Mailbox authority SSOT: [`ssot/identity/mailbox-authority.yaml`](../../ssot/identity/mailbox-authority.yaml)
- Guest invite registry: [`ssot/identity/guest-invite-registry.yaml`](../../ssot/identity/guest-invite-registry.yaml)
- Guest onboarding runbook: [`docs/runbooks/entra-guest-onboarding.md`](../runbooks/entra-guest-onboarding.md)
