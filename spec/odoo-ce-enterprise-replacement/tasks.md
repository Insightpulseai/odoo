# Tasks: Odoo CE Enterprise Replacement

## 1. Odoo Configuration & Architecture

- [ ] Inventory all General Settings sections (Companies, Multi-company, Email, IoT, Integrations, Developer Tools)
- [ ] Identify EE-only and IAP-backed capabilities in those sections
- [ ] Map replacements using Odoo 18 CE core
- [ ] Map replacements using OCA modules (18.0)
- [ ] Map replacements using `ipai_*` modules
- [ ] Define `ipai_enterprise_bridge` scope for EE/IAP replacements
- [ ] Define programmatic configuration strategy (`odoo.conf`, env vars, `ir.config_parameter`)
- [ ] Create XML/CSV seed files for configuration
- [ ] Configure OAuth providers (Google/Outlook)
- [ ] Configure SMTP/mail routing (Mailgun)
- [ ] Define CI/CD commands for applying configuration idempotently
- [ ] Define automated validation (email, OAuth, DNS, IoT status)
- [ ] Produce fallback strategy for unavailable EE/IAP capabilities

## 2. Mail / Email Integration (Non-IAP)

- [ ] Configure programmatic outbound email using Mailgun SMTP
- [ ] Configure Mailgun API for transactional email
- [ ] Configure inbound email routing (Fetchmail)
- [ ] Replace Mailjet/IAP/Enterprise email features
- [ ] Configure SMTP via `ir.mail_server` seeds
- [ ] Configure `fetchmail` for inbound
- [ ] Set `mail.catchall.domain` parameter
- [ ] Configure mail alias routing
- [ ] Configure OAuth for Gmail (outbound auth)
- [ ] Configure OAuth for Outlook (outbound auth)
- [ ] Document DNS setup (MX, SPF, DKIM, DMARC)
- [ ] Create tracking domain configuration
- [ ] Define CLI health checks for MX/DKIM/SPF validation
- [ ] Create email delivery test script

## 3. Authentication & OAuth

- [ ] Research Azure OAuth for Outlook 365 connection (non-IAP)
- [ ] Research Google OAuth for Gmail connection (non-IAP)
- [ ] Create `auth_oauth_provider` records for Google
- [ ] Create `auth_oauth_provider` records for Azure AD
- [ ] Define key/secret storage pattern (env vars)
- [ ] Configure redirect URIs for OAuth
- [ ] Define CI env variable handling
- [ ] Implement CE+OCA email OAuth without EE dependency
- [ ] Test OAuth login flow (Google)
- [ ] Test OAuth login flow (Azure AD)
- [ ] Document Keycloak OIDC integration (optional)

## 4. IoT Replacement Strategy

- [ ] Inventory IoT Box & Windows Virtual IoT settings
- [ ] Identify EE/IAP dependencies in IoT flow
- [ ] Design `ipai_iot_bridge` architecture
- [ ] Create device registry model
- [ ] Implement MQTT bridge
- [ ] Implement WebSocket bridge (alternative)
- [ ] Create Odoo controller endpoints for IoT
- [ ] Implement security/token handling
- [ ] Define Dev test scenarios for IoT validation
- [ ] Define Prod test scenarios for IoT validation
- [ ] Document supported device types (printer, scale, drawer, display)

## 5. Multi-Company Configuration

- [ ] Seed multi-company structure (TBWA\SMP, InsightPulseAI)
- [ ] Add user invites (jgtolentino_rn@yahoo.com, others)
- [ ] Install OCA multi-company ACL modules
- [ ] Configure shared resources
- [ ] Configure intercompany flows (if needed)
- [ ] Create XML `res.company` seeds
- [ ] Create CSV `res.users` seeds
- [ ] Define ACL & `ir.rule` entries
- [ ] Create CI script for bootstrapping base companies

## 6. Enterprise to CE+OCA Mapping

- [ ] List EE-only modules/features from Odoo docs
- [ ] Map replacements to OCA modules (18.0)
- [ ] Define scope for `ipai_enterprise_bridge` gaps
- [ ] Produce parity matrix (EE vs CE+OCA+IPAI)
- [ ] Mark deprecated features

## 7. IAP Removal & Replacement

- [ ] Identify IAP usage in Email
- [ ] Identify IAP usage in SMS
- [ ] Identify IAP usage in Data enrichment
- [ ] Identify IAP usage in Document digitalization
- [ ] Identify IAP usage in IoT
- [ ] Map Mailgun/SMTP for email
- [ ] Map Twilio for SMS
- [ ] Map OCR services (PaddleOCR, Tesseract)
- [ ] Map IoT gateway alternatives
- [ ] Map AI enrichment (LangChain, local LLM)
- [ ] Document service env variables / secret handling

## 8. Module Development

- [ ] Create `ipai_enterprise_bridge` module scaffold
- [ ] Implement `__manifest__.py` with dependencies
- [ ] Implement `res.config.settings` inheritance
- [ ] Implement email layer (Mailgun integration)
- [ ] Implement OAuth layer (provider configs)
- [ ] Implement IoT layer (MQTT bridge)
- [ ] Implement multi-company layer
- [ ] Create data seeds (XML)
- [ ] Create demo data (CSV)
- [ ] Create security rules (`ir.model.access.csv`)
- [ ] Create menu entries
- [ ] Write unit tests

## 9. Programmatic Configuration Artifacts

- [ ] Generate `odoo.conf` template
- [ ] Generate `.env.example` with all required vars
- [ ] Generate XML seeds for companies
- [ ] Generate XML seeds for users
- [ ] Generate XML seeds for mail servers
- [ ] Generate XML seeds for OAuth providers
- [ ] Create Python seed scripts (optional)
- [ ] Create CI setup YAML workflow
- [ ] Define standardized repository layout
- [ ] Define CI validation scripts

## 10. Automated Test & Validation

- [ ] Create smoke test suite (Odoo shell)
- [ ] Create mail delivery test
- [ ] Create OAuth provider test
- [ ] Create DNS verification test
- [ ] Create CE/EE feature guard tests
- [ ] Create rollback plan for failed config
- [ ] Define logging outputs (structured)
- [ ] Define metrics outputs

## 11. Documentation

- [ ] Document installation procedure
- [ ] Document configuration parameters
- [ ] Document DNS requirements
- [ ] Document OAuth setup (Google, Azure)
- [ ] Document IoT setup
- [ ] Document multi-company setup
- [ ] Create troubleshooting guide
- [ ] Create parity matrix document

## 12. CI/CD Integration

- [ ] Create GitHub workflow for module tests
- [ ] Create GitHub workflow for email validation
- [ ] Create GitHub workflow for OAuth validation
- [ ] Create deployment script
- [ ] Create rollback script
- [ ] Add to `all-green-gates.yml`

---

## Priority Order

1. **P0 - Foundation**: Module scaffold, manifest, base config
2. **P1 - Email**: SMTP, Fetchmail, DNS validation
3. **P2 - Auth**: OAuth Google, OAuth Azure
4. **P3 - Multi-Company**: Seeds, ACLs, intercompany
5. **P4 - IoT**: MQTT bridge, device registry
6. **P5 - AI/OCR**: Document processing, enrichment

## Status Legend

- [ ] Not started
- [~] In progress
- [x] Completed
- [!] Blocked
