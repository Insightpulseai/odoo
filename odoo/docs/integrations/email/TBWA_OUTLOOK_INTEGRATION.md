# TBWA Outlook/365 Email Integration

**Status**: Active
**Created**: 2026-02-12
**Portfolio Initiative**: PORT-2026-011
**Evidence**: EVID-20260212-006

---

## Overview

This document defines email integration patterns for TBWA agency workflows with Odoo, covering authentication, SMTP configuration, formatting, routing, and automation.

**Integration Stack**:
- **Email Platform**: Microsoft 365 (Outlook/Exchange Online)
- **SMTP Provider**: Zoho Mail (`smtp.zoho.com:587`) - See ADR-001
- **ERP**: Odoo 19 CE (`mail.activity`, `mail.message`, `mail.thread`)
- **Automation**: n8n workflows for email triggers

---

## Section 1: Authentication

### OAuth 2.0 Setup for Exchange/365

**Microsoft 365 App Registration**:

1. **Azure AD Portal** (https://portal.azure.com)
   - Navigate to: Azure Active Directory → App Registrations → New Registration
   - Name: `Odoo Email Integration - TBWA`
   - Supported account types: Single tenant (TBWA organization only)
   - Redirect URI: `https://erp.insightpulseai.com/auth/oauth2/callback`

2. **API Permissions**:
   - Microsoft Graph API:
     - `Mail.Read` (Delegated) - Read user mailboxes
     - `Mail.ReadWrite` (Delegated) - Manage user mailboxes
     - `Mail.Send` (Delegated) - Send email as user
     - `User.Read` (Delegated) - Read user profile
   - Grant admin consent for TBWA organization

3. **Certificates & Secrets**:
   - Create client secret: `Odoo-Email-Integration-Secret`
   - Copy secret value (only shown once)
   - Store in Supabase Vault: `vault.tbwa_outlook_client_secret`

4. **Authentication Flow** (Delegated Permissions):
   ```
   User → Odoo Login → Redirect to Microsoft OAuth
   → User Consents → Microsoft Returns Auth Code
   → Odoo Exchanges Code for Access Token
   → Access Token Stored in Odoo User Preferences
   ```

**OAuth 2.0 Endpoints**:
```
Authorization URL: https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize
Token URL: https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token
Scope: https://graph.microsoft.com/Mail.ReadWrite https://graph.microsoft.com/Mail.Send
```

**Odoo Configuration** (`Settings → General Settings → Integrations`):
- Email Provider: Microsoft 365 (OAuth 2.0)
- Client ID: `{app_registration_client_id}`
- Client Secret: (from Supabase Vault)
- Tenant ID: `{tbwa_tenant_id}`

---

## Section 2: SMTP Configuration

### Zoho Mail SMTP vs. Exchange SMTP Comparison

**Decision**: Use **Zoho Mail SMTP** for outbound email (see `docs/evidence/decisions/ADR-001-zoho-mail.md`)

| Feature | Zoho Mail SMTP | Exchange SMTP | Decision |
|---------|----------------|---------------|----------|
| **Server** | `smtp.zoho.com:587` | `smtp.office365.com:587` | Zoho ✅ |
| **Authentication** | App-specific password | OAuth 2.0 or app password | Zoho simpler |
| **Deliverability** | High (dedicated IP) | High (shared IP) | Zoho ✅ |
| **Rate Limits** | 300/day (free), 5000/day (paid) | 10,000/day | Exchange higher limit |
| **DKIM/SPF** | Automatic | Requires manual DNS | Zoho easier ✅ |
| **Cost** | $1/user/month | $6/user/month (M365 Business Basic) | Zoho cheaper ✅ |
| **Integration** | SMTP only | OAuth 2.0 + Graph API | Depends on use case |

**Zoho Mail SMTP Configuration** (Odoo):
```python
# Odoo Settings → Technical → Outgoing Mail Servers
Host: smtp.zoho.com
Port: 587
Security: TLS (STARTTLS)
Username: noreply@insightpulseai.com
Password: (app-specific password from Zoho)
```

**Verification**:
```bash
# Test SMTP connection
python3 -c "import smtplib; \
server = smtplib.SMTP('smtp.zoho.com', 587); \
server.starttls(); \
server.login('noreply@insightpulseai.com', 'APP_PASSWORD'); \
server.quit(); \
print('SMTP connection successful')"
```

---

## Section 3: Email Formatting

### Agency-Specific HTML Templates

**TBWA Email Signature Block**:
```html
<!-- Odoo email template: TBWA Signature -->
<table style="font-family: Arial, sans-serif; font-size: 12px; color: #333;">
  <tr>
    <td style="padding-right: 20px;">
      <img src="https://insightpulseai.com/assets/tbwa-logo.png" alt="TBWA Logo" width="120" />
    </td>
    <td>
      <strong style="font-size: 14px;">${object.user_id.name}</strong><br/>
      ${object.user_id.function or ''}<br/>
      TBWA\\Santiago Mangada Puno<br/>
      <a href="mailto:${object.user_id.email}" style="color: #0066cc;">${object.user_id.email}</a><br/>
      +63 2 8888 8888
    </td>
  </tr>
  <tr>
    <td colspan="2" style="padding-top: 10px; border-top: 2px solid #e74c3c; margin-top: 10px;">
      <small style="color: #999;">
        This email and any attachments are confidential and intended solely for the addressee.
        If you are not the intended recipient, please delete this email and notify the sender immediately.
      </small>
    </td>
  </tr>
</table>
```

**Project Update Email Template**:
```html
<!-- Odoo email template: TBWA Project Update -->
<div style="font-family: Arial, sans-serif; max-width: 600px;">
  <h2 style="color: #e74c3c;">Project Update: ${object.name}</h2>

  <table style="width: 100%; border-collapse: collapse;">
    <tr>
      <td style="padding: 10px; background: #f5f5f5; font-weight: bold;">Project</td>
      <td style="padding: 10px;">${object.name}</td>
    </tr>
    <tr>
      <td style="padding: 10px; background: #f5f5f5; font-weight: bold;">Status</td>
      <td style="padding: 10px;">
        <span style="background: #27ae60; color: white; padding: 3px 10px; border-radius: 3px;">
          ${object.stage_id.name}
        </span>
      </td>
    </tr>
    <tr>
      <td style="padding: 10px; background: #f5f5f5; font-weight: bold;">Progress</td>
      <td style="padding: 10px;">
        <div style="background: #ecf0f1; height: 20px; border-radius: 10px;">
          <div style="background: #3498db; width: ${object.progress}%; height: 20px; border-radius: 10px;">
            <span style="color: white; padding-left: 10px; line-height: 20px;">
              ${object.progress}%
            </span>
          </div>
        </div>
      </td>
    </tr>
    <tr>
      <td style="padding: 10px; background: #f5f5f5; font-weight: bold;">Next Milestone</td>
      <td style="padding: 10px;">${object.next_milestone or 'TBD'}</td>
    </tr>
  </table>

  <p style="margin-top: 20px;">
    ${object.description or 'No additional details.'}
  </p>

  <p style="margin-top: 20px;">
    <a href="https://erp.insightpulseai.com/web#id=${object.id}&model=project.project"
       style="background: #e74c3c; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
      View Project in Odoo
    </a>
  </p>
</div>
```

**Attachment Naming Convention**:
- `TBWA_ProjectName_YYYYMMDD_v01.pdf` (client deliverables)
- `TBWA_Internal_Topic_YYYYMMDD.xlsx` (internal reports)
- `TBWA_Invoice_ClientCode_InvNumber.pdf` (invoices)

---

## Section 4: Routing Rules

### Folder Organization

**Outlook Folder Structure** (synced to Odoo):
```
Inbox/
├── TBWA-Clients/
│   ├── Client-Jollibee/        → project.project (Jollibee campaign)
│   ├── Client-SanMiguel/       → project.project (San Miguel campaign)
│   └── Client-Ayala/           → project.project (Ayala campaign)
├── TBWA-Internal/
│   ├── HR-Notices/             → hr.department (HR)
│   ├── Finance-Invoices/       → account.move (Invoices)
│   └── IT-Requests/            → helpdesk.ticket (IT support)
└── TBWA-Procurement/
    ├── Vendor-Quotes/          → purchase.order (RFQ)
    └── PO-Approvals/           → purchase.order (Approval workflow)
```

**Autoforwarding Rules** (Outlook → Odoo):
- **Sender**: `*@jollibee.com.ph` → Forward to `projects+jollibee@insightpulseai.com`
- **Subject**: `[INVOICE]` → Forward to `accounting+invoices@insightpulseai.com`
- **Attachment**: `.pdf` + Subject contains `PO` → Forward to `procurement+po@insightpulseai.com`

---

## Section 5: n8n Workflows

### Email Trigger Workflows

**Workflow 1: Client Email to Odoo Task**

**Trigger**: Email received in `Inbox/TBWA-Clients/{ClientName}/`

**n8n Workflow** (`supabase/functions/n8n-email-client-task/index.ts`):
```typescript
// Workflow Steps:
// 1. IMAP trigger (Outlook mailbox)
// 2. Extract email metadata (sender, subject, body, attachments)
// 3. Identify client project (sender domain → project mapping)
// 4. Create Odoo task (project.task)
// 5. Attach email thread to task (mail.message)
// 6. Notify project manager (Slack message)

// Step 3: Identify client project
const senderDomain = email.from.split('@')[1];
const projectMapping = {
  'jollibee.com.ph': { project_id: 42, assign_to: 'user_5' },
  'sanmiguel.com': { project_id: 43, assign_to: 'user_6' },
  'ayala.com.ph': { project_id: 44, assign_to: 'user_7' }
};

const project = projectMapping[senderDomain];

// Step 4: Create Odoo task
const task = await odoo.create('project.task', {
  name: email.subject,
  project_id: project.project_id,
  user_ids: [project.assign_to],
  description: email.body_html,
  email_from: email.from,
  partner_id: await getPartnerByEmail(email.from)
});

// Step 5: Attach email thread
await odoo.create('mail.message', {
  res_id: task.id,
  model: 'project.task',
  message_type: 'email',
  subject: email.subject,
  body: email.body_html,
  author_id: await getPartnerByEmail(email.from),
  email_from: email.from,
  attachment_ids: await uploadAttachments(email.attachments)
});
```

**Workflow 2: Invoice Email to Odoo Accounting**

**Trigger**: Email received with `[INVOICE]` in subject or `.pdf` attachment

**n8n Workflow** (`supabase/functions/n8n-email-invoice/index.ts`):
```typescript
// Workflow Steps:
// 1. IMAP trigger (Inbox/TBWA-Procurement/)
// 2. Extract invoice PDF attachment
// 3. OCR invoice (PaddleOCR-VL) → extract vendor, amount, date
// 4. Create draft invoice (account.move)
// 5. Attach PDF to invoice
// 6. Notify accounting team (email + Slack)

// Step 3: OCR invoice
const ocrResult = await fetch('https://ocr.insightpulseai.com/api/v1/invoice', {
  method: 'POST',
  body: email.attachments[0].content
});

const invoiceData = await ocrResult.json();

// Step 4: Create draft invoice
const invoice = await odoo.create('account.move', {
  move_type: 'in_invoice',
  partner_id: await getPartnerByName(invoiceData.vendor_name),
  invoice_date: invoiceData.invoice_date,
  invoice_line_ids: [
    [0, 0, {
      name: invoiceData.line_items[0].description,
      price_unit: invoiceData.line_items[0].amount,
      quantity: 1
    }]
  ],
  state: 'draft'
});
```

**Workflow 3: Attachment Extraction to Shared Drive**

**Trigger**: Email with PDF/Excel attachments to `projects+*@insightpulseai.com`

**n8n Workflow** (`supabase/functions/n8n-email-attachment-archive/index.ts`):
```typescript
// Workflow Steps:
// 1. IMAP trigger (email aliases)
// 2. Extract attachments
// 3. Classify by type (Invoice, RFQ, Deliverable, Report)
// 4. Upload to Supabase Storage (or MinIO)
// 5. Create file record in Odoo (ir.attachment)
// 6. Link to relevant record (project.task, purchase.order, etc.)

// Step 4: Upload to storage
const filePath = `tbwa/${emailAlias}/${date}/${attachment.filename}`;
const { data, error } = await supabase.storage
  .from('email-attachments')
  .upload(filePath, attachment.content);

// Step 5: Create Odoo attachment
await odoo.create('ir.attachment', {
  name: attachment.filename,
  type: 'url',
  url: data.publicUrl,
  res_model: 'project.task',
  res_id: taskId
});
```

---

## Section 6: Odoo Integration

### `mail.activity` Model Usage

**Create Email Follow-up Activity**:
```python
# Odoo: Create activity for client response
self.env['mail.activity'].create({
    'res_id': task.id,
    'res_model_id': self.env['ir.model']._get('project.task').id,
    'activity_type_id': self.env.ref('mail.mail_activity_data_email').id,
    'summary': f'Follow-up: {email.subject}',
    'note': email.body_html,
    'user_id': project.user_id.id,
    'date_deadline': fields.Date.today() + timedelta(days=3)
})
```

### `mail.message` Model Usage

**Attach Email Thread to Task**:
```python
# Odoo: Create message linked to task
self.env['mail.message'].create({
    'res_id': task.id,
    'model': 'project.task',
    'message_type': 'email',
    'subject': email.subject,
    'body': email.body_html,
    'author_id': partner.id,
    'email_from': email.from_address,
    'attachment_ids': [(6, 0, attachment_ids)]
})
```

### `mail.thread` Mixin

**Enable Email Tracking on Custom Models**:
```python
# addons/ipai/ipai_tbwa_client/models/client_project.py
from odoo import models, fields

class ClientProject(models.Model):
    _name = 'tbwa.client.project'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'TBWA Client Project'

    name = fields.Char(string='Project Name', required=True, tracking=True)
    client_id = fields.Many2one('res.partner', string='Client', tracking=True)
    stage_id = fields.Many2one('project.stage', string='Stage', tracking=True)

    # Email alias for automatic tracking
    _mail_post_access = 'read'

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        """Override to create project from email"""
        defaults = {
            'name': msg_dict.get('subject', 'New Project'),
            'client_id': self._get_partner_from_email(msg_dict.get('from')),
        }
        return super().message_new(msg_dict, custom_values=defaults)
```

---

## Section 7: Security

### App Passwords

**Microsoft 365 App Password** (if not using OAuth 2.0):
1. Go to: Microsoft 365 Security → My Account → Security Info
2. Add new sign-in method: App Password
3. Name: `Odoo Email Integration`
4. Copy 16-character password
5. Store in Supabase Vault: `vault.tbwa_m365_app_password`

**Zoho Mail App Password**:
1. Go to: Zoho Mail → Settings → Security → App Passwords
2. Create new: `Odoo SMTP`
3. Copy password
4. Store in Supabase Vault: `vault.zoho_smtp_password`

### MFA Requirements

**Enforce MFA for Email-Linked Accounts**:
- All Odoo users with email integration must enable MFA
- Microsoft 365: Enforce MFA via Conditional Access policies
- Zoho Mail: Enforce MFA via account settings

### Encryption

**TLS/STARTTLS**:
- All SMTP connections use TLS (port 587)
- IMAP connections use TLS (port 993)
- No plaintext email transmission

**Supabase Vault Storage**:
```sql
-- Store email credentials in Vault
INSERT INTO vault.secrets (name, secret)
VALUES
  ('tbwa_outlook_client_secret', 'encrypted_value'),
  ('zoho_smtp_password', 'encrypted_value'),
  ('tbwa_m365_app_password', 'encrypted_value');

-- Retrieve in Odoo via RPC
SELECT decrypted_secret FROM vault.decrypted_secrets
WHERE name = 'zoho_smtp_password';
```

---

## Email Routing Matrix

See companion file: `docs/integration/email/EMAIL_ROUTING_MATRIX.yaml`

**Summary**:
- Client domains → Odoo projects
- Invoice patterns → Accounting workflows
- Procurement patterns → Purchase orders
- Internal departments → Team assignments

---

## Verification

### Test Email Creation

**Send test email**:
```bash
# Send test email from TBWA account
echo "Test email body" | mail -s "Test: Project Update" \
  -a "From: user@tbwa.com" \
  projects+jollibee@insightpulseai.com
```

**Verify Odoo activity creation**:
```python
# Odoo shell
activities = self.env['mail.activity'].search([
    ('create_date', '>', datetime.now() - timedelta(hours=1)),
    ('summary', 'ilike', 'Test: Project Update')
])
print(f"Found {len(activities)} activities")
for activity in activities:
    print(f"- {activity.summary} (Project: {activity.res_id})")
```

### Test Routing

**Verify sender → project mapping**:
```python
# Odoo: Check email routing
routing = {
    'jollibee.com.ph': 42,  # Project ID
    'sanmiguel.com': 43,
    'ayala.com.ph': 44
}

sender = 'marketing@jollibee.com.ph'
domain = sender.split('@')[1]
project_id = routing.get(domain)
print(f"Sender {sender} → Project ID {project_id}")
```

---

## Related Documentation

- `docs/evidence/decisions/ADR-001-zoho-mail.md` - SMTP provider decision
- `addons/ipai/ipai_slack_connector/` - Messaging integration patterns
- `supabase/functions/email-processor/` - Email parsing Edge Functions
- `docs/integration/email/EMAIL_ROUTING_MATRIX.yaml` - Sender → Project mapping

---

*Documentation created: 2026-02-12*
*Status: Active*
*Portfolio Initiative: PORT-2026-011*
