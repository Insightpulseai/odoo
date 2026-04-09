# Skill Pack: Identity, RBAC & Segregation of Duties

## Scope

Role-based access control design, segregation of duties enforcement, record-level
security, identity federation with external IdPs, and audit trail management in
Odoo 18 CE. Targets parity with SAP GRC Access Control, SAP Authorization Concepts
(roles, profiles, SoD matrices), and enterprise IAM patterns using Entra ID federation.

---

## Concepts

| Concept | SAP Equivalent | Odoo 18 CE Surface |
|---------|---------------|---------------------|
| User | SAP User (SU01) | `res.users` |
| Group / Role | SAP Role (PFCG) | `res.groups` |
| Record Rule | Authorization Object | `ir.rule` (domain-based) |
| Model Access (ACL) | Transaction Auth | `ir.model.access` (CRUD per model per group) |
| Menu Visibility | Menu Authorization | `ir.ui.menu` `groups_id` field |
| Field Access | Field-level Auth | `ir.model.fields` `groups` attribute in XML |
| Multi-Company | Company Code isolation | `ir.rule` with `company_ids` domain |
| Audit Log | SAP Security Audit Log (SM20) | `mail.tracking.value` + OCA `audit_log` |
| Identity Federation | SAP IAS / Entra SAML | OCA `auth_oidc` + Entra ID |
| User Role (composite) | Composite Role | OCA `base_user_role` |

---

## Must-Know Vocabulary

- **ACL (Access Control List)**: `ir.model.access` records granting CRUD on a model
  to a group. If no ACL exists for a model, only admin can access it.
- **Record Rule**: `ir.rule` records filtering which records a group can see/edit.
  Uses Odoo domain expressions evaluated per-record.
- **Global Rule**: An `ir.rule` with no group assigned. Applies to ALL non-superuser
  users. Multiple global rules are AND-ed. Used for multi-company isolation.
- **Group Rule**: An `ir.rule` assigned to a specific group. Multiple group rules
  for the same user are OR-ed. Grants additional access beyond global rules.
- **Segregation of Duties (SoD)**: Principle that no single user should control all
  phases of a critical transaction (e.g., cannot both create and approve a PO).
- **Implied Group**: Group inheritance via `implied_ids`. If user has Group A which
  implies Group B, user effectively has both. Maps to SAP composite roles.
- **Superuser Bypass**: `res.users` with `id=1` (OdooBot, SUPERUSER_ID) or `sudo()` bypasses
  all ACL and record rules. `id=2` is the human admin user. Never use for regular operations.
- **OIDC (OpenID Connect)**: Protocol for identity federation. Entra ID acts as IdP;
  Odoo acts as relying party via `auth_oidc`.
- **SCIM**: System for Cross-domain Identity Management. Protocol for automated
  user provisioning/deprovisioning from Entra ID to Odoo.

---

## Core Workflows

### 1. Group Architecture Design

Odoo groups form a DAG (directed acyclic graph) via `implied_ids`:

```
                    base.group_user (Internal User)
                         |
            +------------+------------+
            |            |            |
      account.group_   sale.group_  project.group_
      account_invoice  sale_salesman  project_user
            |            |            |
      account.group_   sale.group_  project.group_
      account_manager  sale_manager  project_manager
```

Design principle: Start with the least privilege. Each functional area has User
and Manager tiers. Manager implies User. Custom `ipai_*` groups extend this tree.

### 2. ACL Configuration

File: `security/ir.model.access.csv`
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_invoice_user,account.move.user,account.model_account_move,account.group_account_invoice,1,1,1,0
access_invoice_manager,account.move.manager,account.model_account_move,account.group_account_manager,1,1,1,1
```

Rules:
- Every model must have at least one ACL or it is invisible to non-admin.
- Read-only access: `perm_read=1`, all others 0.
- Delete is the most dangerous permission; reserve for Manager groups.

### 3. Record Rules for Multi-Company and SoD

Multi-company isolation (global rule, ships with Odoo):
```xml
<record id="account_move_comp_rule" model="ir.rule">
    <field name="name">Account Move: multi-company</field>
    <field name="model_id" ref="account.model_account_move"/>
    <field name="domain_force">[('company_id','in',company_ids)]</field>
</record>
```

Custom SoD rule -- prevent invoice creator from approving their own:
```xml
<record id="rule_invoice_sod_approve" model="ir.rule">
    <field name="name">Invoice: cannot approve own</field>
    <field name="model_id" ref="account.model_account_move"/>
    <field name="groups" eval="[(4, ref('account.group_account_manager'))]"/>
    <field name="domain_force">[('create_uid','!=',user.id)]</field>
    <field name="perm_write">True</field>
    <field name="perm_read">False</field>
</record>
```

This rule means managers can only write (approve/post) invoices they did not create.

### 4. Role-Based User Assignment (OCA base_user_role)

Instead of assigning 15 individual groups, define composite roles:
```xml
<record id="role_ap_clerk" model="res.users.role">
    <field name="name">AP Clerk</field>
    <field name="line_ids" eval="[
        (0, 0, {'group_id': ref('account.group_account_invoice')}),
        (0, 0, {'group_id': ref('purchase.group_purchase_user')}),
        (0, 0, {'group_id': ref('base.group_partner_manager')}),
    ]"/>
</record>
```

Assign role to user: `res.users.role.line` links `user_id` to `role_id`.
When role membership changes, all group assignments update atomically.

### 5. Identity Federation with Entra ID

OCA `auth_oidc` configuration:
```
Provider: Microsoft Entra ID
Client ID: <from App Registration>
Client Secret: <in env var OIDC_CLIENT_SECRET>
Authorization URL: https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize
Token URL: https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token
JWKS URL: https://login.microsoftonline.com/{tenant}/discovery/v2.0/keys
Scope: openid email profile
User mapping: email -> res.users.login
```

Flow: User clicks "Login with Microsoft" -> Entra authenticates -> OIDC callback
creates/matches `res.users` by email -> Odoo session established.

### 6. Audit Trail

Native: `mail.tracking.value` records field changes on models inheriting `mail.thread`.
Every `account.move`, `sale.order`, `purchase.order` tracks who changed what and when.

Enhanced: OCA `auditlog` (`auditlog.rule`) enables field-level audit on any model
without requiring `mail.thread` inheritance. Captures old value, new value, user, timestamp.

---

## Edge Cases

1. **Group rule OR vs. global rule AND**: A user in multiple groups gets the UNION
   of all group rules but the INTERSECTION of all global rules. Misunderstanding
   this causes either over-permissive or locked-out scenarios.
2. **sudo() in custom code**: `self.sudo().write(vals)` bypasses all security.
   Audit all `sudo()` calls in `ipai_*` modules. Each must have a justifying comment.
3. **Portal users and record rules**: Portal users (`base.group_portal`) have separate
   rule sets. They must never see internal records. Test portal access independently.
4. **Deactivated users with active sessions**: Deactivating `res.users.active=False`
   does not kill existing sessions. Implement session invalidation via cron or middleware.
5. **OIDC token expiry**: If Entra token expires mid-session, Odoo does not refresh
   it automatically. Configure Odoo session timeout <= Entra token lifetime.

---

## Controls & Compliance

| Control | Implementation |
|---------|---------------|
| SoD: Create vs. Approve PO | `ir.rule` restricting `button_confirm` to non-creator |
| SoD: Create vs. Post Invoice | `ir.rule` on write with `state` transition check |
| Quarterly access review | Script: dump `res.users.role.line` + `res.groups.users_ids` to CSV for review |
| Failed login monitoring | `res.users._check_credentials` logging + Azure Monitor alert |
| Privileged access (admin) | Only 1 admin account. All others via roles. Admin actions logged to `auditlog` |
| Password policy | OCA `password_security`: min length 12, complexity, expiry 90 days, no reuse 5 |
| MFA enforcement | Entra ID Conditional Access policy (enforced at IdP, not in Odoo) |

---

## Odoo/OCA Implementation Surfaces

| Module | Source | Purpose |
|--------|--------|---------|
| `base` | Core | `res.users`, `res.groups`, `ir.rule`, `ir.model.access` |
| `mail` | Core | `mail.tracking.value` for field-change audit |
| `auth_oidc` | OCA | OpenID Connect authentication with Entra ID |
| `base_user_role` | OCA | Composite role management |
| `auditlog` | OCA | Field-level audit trail on any model |
| `password_security` | OCA | Password complexity, expiry, history |
| `auth_session_timeout` | OCA | Automatic session expiry after inactivity |
| `auth_totp` | Core | Time-based OTP for local MFA (fallback if no Entra) |
| `ipai_auth_oidc` | Custom | Entra-specific extensions (group sync, SCIM receiver) |
| `ipai_sod_matrix` | Custom | SoD conflict detection and reporting |

---

## Azure/Platform Considerations

- **Entra ID App Registration**: One registration per environment (dev/staging/prod).
  Redirect URIs: `https://<odoo-host>/auth_oauth/signin`.
- **Entra Conditional Access**: Require MFA for all users accessing Odoo. Geo-fence
  to PH + allowed countries. Block legacy authentication.
- **Entra Group Sync**: Map Entra security groups to Odoo roles via `ipai_auth_oidc`.
  When user is removed from Entra group "Finance", their Odoo AP Clerk role is revoked.
- **Azure Monitor**: Ingest Odoo `ir.logging` and `auditlog` records via Diagnostic
  Settings. Create alerts for: admin login, bulk record deletion, SoD violation attempts.
- **Key Vault**: Store OIDC client secret, DB credentials. Odoo reads via env vars
  injected by Azure Container Apps secret references.

---

## Exercises

### Exercise 1: ACL and Record Rule
Create a model `ipai.expense.claim`. Define ACLs: Employee group gets read+create,
Manager group gets full CRUD. Add a record rule: employees can only see their own
claims (`user_id = user.id`). Managers see all. Test with two users.

### Exercise 2: SoD Enforcement
Configure a record rule that prevents the creator of a `purchase.order` from confirming
it. Test: User A creates PO. User A tries to confirm -- blocked. User B (same group)
confirms -- succeeds. Verify via audit log that the attempt was recorded.

### Exercise 3: Role Provisioning
Install `base_user_role`. Create roles: "AR Clerk" (invoice user + sales user),
"AP Clerk" (invoice user + purchase user), "Controller" (account manager + all reports).
Assign a user to "AR Clerk". Verify they can create customer invoices but cannot
access vendor bills. Change role to "AP Clerk". Verify access flips.

### Exercise 4: OIDC Federation
Configure `auth_oidc` with Entra ID (use dev tenant). Create a test user in Entra.
Login to Odoo via "Login with Microsoft". Verify `res.users` record created with
correct email. Disable user in Entra. Verify next login attempt fails.

---

## Test Prompts for Agents

1. "Design the RBAC matrix for a 20-person company with these departments: Finance (5),
   Sales (5), Operations (5), Management (3), IT (2). Define roles, groups, and
   the SoD constraints between them."

2. "A user reports they can see invoices from another company in a multi-company setup.
   Diagnose the record rule configuration. Check `ir.rule` for the account.move model
   and verify the company domain filter."

3. "Implement Entra ID SSO for Odoo. Provide the auth_oidc provider configuration,
   the Entra App Registration settings needed, and the redirect URI. Do not hardcode
   the client secret."

4. "Generate a quarterly access review report: list all users, their roles, last login
   date, and flag any user who has not logged in for 60+ days for deactivation review."

5. "We need to ensure that no single person can create a vendor, create a vendor bill,
   and approve payment. Design the three-way SoD control using Odoo groups and record rules."
