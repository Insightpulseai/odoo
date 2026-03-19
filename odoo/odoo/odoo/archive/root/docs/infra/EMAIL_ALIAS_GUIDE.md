# InsightPulseAI Email Alias Usage Guide (SSOT)

**Status**: CANONICAL
**Last Updated**: 2026-02-17
**Owner**: DevOps

**Primary principle:**
Each alias maps to **one intent + one automation surface**.
No alias should be "general purpose" except `info@`.

---

## 🧠 Human / Executive

### `business@insightpulseai.com` **(PRIMARY IDENTITY)**

**Use when:**
- External-facing professional communication
- Partnerships, clients, vendors
- Contracts, proposals, negotiations
- Anything you'd put on a business card

**Automation:**
- CRM ingestion
- Slack/Teams executive channel
- Supabase `contacts` / `leads` table

**Never use for:**
- System notifications
- Support tickets
- Automated receipts

---

### `ceo@insightpulseai.com`

**Use when:**
- Board-level or investor correspondence
- Legal / strategic escalation
- Formal executive authority is required

**Automation:**
- Minimal (manual triage only)
- High-priority alert routing

**Rule:** Low-volume by design. Not for daily ops.

---

### `jake.tolentino@insightpulseai.com`

**Use when:**
- Named individual accountability is required
- Sign-offs, approvals, formal acknowledgements
- Situations where "Jake" (not the company) must respond

**Automation:**
- None (human-only inbox)

---

## 🧾 Finance & Compliance

### `billing@insightpulseai.com`

**Use when:**
- Client invoices
- Subscription billing
- Payment confirmations
- Vendor billing correspondence

**Automation:**
- Accounting system ingestion
- Odoo / Supabase finance pipeline
- n8n → finance workflows

**Rule:** All invoices MUST come **from** or **to** this alias.

---

### `expenses@insightpulseai.com`

**Use when:**
- Receipts
- Expense claims
- Reimbursements
- OCR / DocFlow ingestion

**Automation:**
- OCR pipelines
- Odoo expense modules
- Supabase `expenses_raw` → `expenses_clean`

**Rule:** Never mix with billing or support.

---

## 🛠 Operations & Engineering

### `devops@insightpulseai.com` ⭐ **SYSTEM OWNER**

**Use when:**
- Infrastructure alerts
- CI/CD notifications
- Cloudflare, Vercel, Supabase, GitHub alerts
- Security advisories
- **System admin/owner accounts** (n8n, Odoo, Supabase, etc.)

**Automation:**
- n8n alerting
- PagerDuty / Opsgenie style routing
- Slack `#ops-alerts`
- MCP observability tools

**System Ownership**:
```yaml
n8n: devops@insightpulseai.com          # Admin account
Odoo: devops@insightpulseai.com         # Server admin
Supabase: devops@insightpulseai.com     # Project owner
Vercel: devops@insightpulseai.com       # Team owner
Cloudflare: devops@insightpulseai.com   # Zone owner
GitHub: devops@insightpulseai.com       # Org alerts
Monitoring: devops@insightpulseai.com   # Netdata, Sentry
```

**Rule:** Machine-first inbox. Humans respond only when alerted.

---

## 🎧 Support & External Requests

### `support@insightpulseai.com`

**Use when:**
- Customer support
- Bug reports
- Product questions
- User-facing help

**Automation:**
- Ticketing system
- Supabase `support_tickets`
- AI triage / auto-responder

**Rule:** No internal traffic. External users only.

---

### `info@insightpulseai.com`

**Use when:**
- General inquiries
- Website contact forms
- Non-specific questions

**Automation:**
- Auto-classification
- Routing to `support`, `business`, or `sales` logic

**Rule:** This is the **only true catch-all**.

---

## 📣 Communications & Automation

### `no-reply@insightpulseai.com`

**Use when:**
- System-generated emails
- Auth flows (Supabase, n8n)
- Notifications
- Reports
- Cron / scheduled messages

**Automation:**
- Supabase Auth
- n8n workflows
- CI/CD reports
- Odoo transactional emails

**Rule:** Never monitored. Never replied to.

---

### `team@insightpulseai.com`

**Use when:**
- Group communications
- Internal announcements
- Hiring or collaboration threads
- Multi-recipient replies

**Automation:**
- Distribution list
- Slack mirror (read-only)

**Rule:** Not for external customers.

---

## 🌐 External / Legacy

### `jgtolentino.rn@gmail.com`

**Use when:**
- Personal fallback
- Third-party tools that *cannot* use custom domains
- Emergency recovery only

**Rule:** Not part of the official system. Do not publish.

---

## ✅ Quick Decision Table

| Scenario | Alias |
|----------|-------|
| Client proposal | `business@` |
| Invoice / payment | `billing@` |
| Expense receipt | `expenses@` |
| Infra alert | `devops@` |
| System admin account | `devops@` ⭐ |
| Customer issue | `support@` |
| Website contact | `info@` |
| System email | `no-reply@` |
| Exec / investor | `ceo@` |
| Named approval | `jake.tolentino@` |
| Internal broadcast | `team@` |

---

## 🔐 Governance Rules

1. **One alias = one automation pipeline**
2. **No alias does double duty**
3. **All system emails originate from `no-reply@`**
4. **All money touches `billing@` or `expenses@`**
5. **All infra alerts go to `devops@`**
6. **All system admin accounts use `devops@`** ⭐

---

## 🧩 Golden Rule

> **Humans use named emails.
> Systems use role emails.
> Automation never uses personal identity.**

---

## System Admin Email Policy

### ✅ **Primary admin/service owner: `devops@insightpulseai.com`**

**This is the DEFAULT admin email for:**
- n8n instance
- Odoo (server + modules + cron)
- Supabase project owner (preferred)
- Vercel projects
- Cloudflare zone
- GitHub org alerts
- CI/CD systems
- Monitoring (Netdata, Sentry, etc.)

**Why:**
- Role-based, not person-based
- Safe for automation
- Can fan out to Slack / PagerDuty
- Survives org changes

✅ **Use this unless there is a strong reason not to**

---

### ⚙️ System-generated outbound email: `no-reply@insightpulseai.com`

**Use for:**
- Odoo transactional emails
- Supabase Auth (magic links, resets)
- n8n notifications to users
- Reports, digests, cron output

❌ Never use as an admin/owner
❌ Never monitored

---

### 🧾 Financial systems (special case): `billing@insightpulseai.com`

**Use as admin email ONLY for:**
- Payment processors (Stripe, PayPal, etc.)
- Invoicing systems
- Subscription billing platforms

⚠️ Not for infra, CI, or automation tools.

---

### 🧠 Human fallback / escalation: `jake.tolentino@insightpulseai.com`

**Use only when a platform REQUIRES a human owner**, e.g.:
- Legacy SaaS with no role accounts
- Legal verification flows
- One-time identity confirmation

🔁 After setup, always:
- Add `devops@` as secondary owner
- Remove personal dependency where possible

---

## ❌ What NOT to use for admin

| Alias | Why |
|-------|-----|
| `business@` | External-facing, noisy |
| `info@` | Catch-all, low signal |
| `support@` | User-facing |
| `team@` | Distribution only |
| Gmail | Not org-governed |

---

## 🔐 Recommended Default Mapping

| System | Admin Email |
|--------|-------------|
| **n8n** | `devops@insightpulseai.com` |
| **Odoo** | `devops@insightpulseai.com` |
| **Supabase** | `devops@insightpulseai.com` |
| **Vercel** | `devops@insightpulseai.com` |
| **Cloudflare** | `devops@insightpulseai.com` |
| **GitHub Org** | `devops@insightpulseai.com` |
| **Monitoring (Netdata/Sentry)** | `devops@insightpulseai.com` |
| **Emails sent by systems** | `no-reply@insightpulseai.com` |

---

## Implementation

### YAML SSOT

See: `infra/identity/email-roles.yaml` (to be created)

### CI Policy

See: `.github/workflows/email-policy-check.yml` (to be created)

### MCP Integration

See: `spec/mcp-provider-system/` - Vault secrets use role emails

### n8n + Supabase Mapping

See: `docs/N8N_CREDENTIALS_BOOTSTRAP.md` - Credentials wired to role emails

---

## Related Documents

- `docs/N8N_CREDENTIALS_BOOTSTRAP.md` - n8n credential setup
- `docs/evidence/20260216-1546/n8n-admin-setup/ACCOUNT_CREATION.md` - n8n admin setup
- `infra/identity/email-roles.yaml` - Machine-readable SSOT (to be created)
- `spec/mcp-provider-system/constitution.md` - Vault secret naming

---

**Next Actions**:
1. ✅ Apply to n8n admin account (`devops@`)
2. 🔲 Create `infra/identity/email-roles.yaml` (machine-readable)
3. 🔲 Add CI policy check for personal emails in config
4. 🔲 Map to n8n + Supabase secrets
5. 🔲 Audit current systems for violations
