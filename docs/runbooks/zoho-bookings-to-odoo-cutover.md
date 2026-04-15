# Zoho Bookings → Odoo CE 18 Appointment Cutover

**Replaces:** `https://insightpulseai.zohobookings.com/#/insightpulseai`
**Target:** `https://book.insightpulseai.com/appointment`
**Doctrine:** Odoo CE 18 `appointment` module (no custom code) + data XML seed in existing `ipai_web_branding` module.

---

## What I executed (2026-04-15)

| Step | Status | Evidence |
|---|---|---|
| Wrote 4 appointment-type seeds | ✅ Done | `addons/ipai/ipai_web_branding/data/appointment_types.xml` |
| Updated module manifest (depends + version + data list) | ✅ Done | `addons/ipai/ipai_web_branding/__manifest__.py` v18.0.5.0.0 |
| Created Azure DNS CNAME `book.insightpulseai.com` | ✅ Done | Resolves to `ipai-odoo-dev-web.blackstone-0df78186.southeastasia.azurecontainerapps.io` (20.43.154.179) |
| Created TXT `asuid.book.insightpulseai.com` for ownership verification | ✅ Done | Verification ID `16233186F242CF…0746E1A` |
| Pre-created ACA managed cert with required tags (Azure Policy compliance) | ⏳ Background | `mc-book-insightpulseai` |
| Bound `book.insightpulseai.com` hostname to `ipai-odoo-dev-web` | ⏳ Background | Pending cert issuance (≤ 20 min) |

---

## What you must run on the Odoo container

The data XML is staged in git but **not yet loaded into the running Odoo DB**. Run this against the container to install:

```bash
# Option A — devcontainer / docker compose
docker compose exec odoo odoo -d odoo_dev -u ipai_web_branding --stop-after-init

# Option B — Azure Container App exec
az containerapp exec --name ipai-odoo-dev-web --resource-group rg-ipai-dev-odoo-runtime \
  --subscription 536d8cf6-89e1-4815-aef3-d5f2c5f4d070 \
  --command "/opt/odoo/odoo-bin -c /etc/odoo/odoo.conf -d odoo_dev -u ipai_web_branding --stop-after-init"

# Verify install
curl -sI https://book.insightpulseai.com/appointment | head -3
```

Expected after install: 4 appointment types appear at `/appointment`:
1. **Discovery Call** (30 min)
2. **Product Demo — Pulser & Odoo Platform** (45 min)
3. **AI & ERP Advisory Session** (60 min)
4. **Pulser Implementation Scoping** (60 min)

---

## Customization (optional, post-install)

Each appointment type is configurable in the Odoo backend:
- **Settings → Appointments → Types → [type]**
- Edit duration, intro message, staff assignment, calendar resources
- Add Google Workspace calendar sync (already in scope per `feedback_w9_google_workspace_integration.md`):
  - `Settings → Users → [user] → Calendar → Sync with Google Calendar`
- Add Xendit/PayPal payment requirement at booking time (optional):
  - Install `website_sale_appointment` (CE 18) → enable "Pay to confirm"

---

## Zoho Bookings retirement (you do)

After confirming `https://book.insightpulseai.com/appointment` works:

1. **Export existing bookings from Zoho** (one-time):
   - Zoho Bookings → Reports → Export → CSV
   - Save to `docs/migration/zoho-bookings-export-2026-04-15.csv`

2. **Import into Odoo** (one-shot script — can write later):
   - For each row: create `calendar.event` with `appointment_type_id` matched to closest IPAI type
   - Or: send confirmation email to existing customers about new URL, let them rebook

3. **Update marketing references**:
   - `www.insightpulseai.com` → change "Book a meeting" CTA to `book.insightpulseai.com`
   - Email signatures, social profiles, sales decks
   - Zoho CRM (if used) → update calendar invite links

4. **Redirect old Zoho URL**:
   - Zoho Bookings admin → Settings → Custom Domain → set redirect to `https://book.insightpulseai.com`
   - Or: cancel the Zoho Bookings subscription (kills the URL), let 404s tell people to use the new URL (less smooth)

5. **Cancel Zoho Bookings subscription**:
   - Zoho Billing → Bookings → Cancel
   - Confirm no charges next billing cycle

---

## Rollback (if needed)

The Zoho Bookings instance stays live during cutover. To roll back:

```bash
# 1. Revert manifest
cd /workspaces/odoo
git revert <commit-hash-of-this-change>

# 2. Uninstall the appointment module if it conflicts
docker compose exec odoo odoo -d odoo_dev --uninstall=appointment --stop-after-init

# 3. Remove ACA hostname binding (DNS stays)
az containerapp hostname remove --name ipai-odoo-dev-web --resource-group rg-ipai-dev-odoo-runtime \
  --subscription 536d8cf6-89e1-4815-aef3-d5f2c5f4d070 \
  --hostname book.insightpulseai.com

# 4. Point marketing back to zohobookings.com
```

The 4 appointment types are seeded with `noupdate="1"` — they survive module updates without being overwritten by re-running `-u`.

---

## Sub migration note

This binding is on **Azure Sub 1** (the old sub). When the Odoo runtime migrates to sponsored sub, the custom domain + cert + DNS records all migrate with the resources/zone moves. No DNS change for end-users.

---

*Last updated: 2026-04-15 — by Claude (Opus 4.6)*
