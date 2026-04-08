# PRD: Odoo.sh-Equivalent Staging Engine (Platform Lane)

## Vision
A Cloudpepper-style staging lifecycle that operates outside the transactional Odoo runtime, ensuring that production clones are sanitized and release-gated before becoming operational.

## Authority Model
- **Platform Engine**: Sovereign authority over infrastructure (cloning, sanitization, DNS cutover).
- **Odoo UI**: Thin client for status observation and request initiation.

## Core Workflows

### 1. Staging Refresh (Request)
- **Initiator**: Odoo UI (Operator Button).
- **Process**:
  1. Trigger out-of-band Azure Pipeline.
  2. Snapshot Production Postgres.
  3. Create Staging ACA (Azure Container App) instance.
  4. **Sanitize Data**: Mask PII (Partner Emails, VATs) and disable Outbound Email/Connectors.
  5. **Gate Verification**: Run V2 Factory Validator against the new environment.
- **Outcome**: Staging URL and Evidence Pack published.

### 2. Guarded Promotion
- **Gate**: Validator Status == 'PASS'.
- **Result**: Evidence pack is generated and pushed to Odoo `ipai.deployment.status`.

## User Roles
- **Odoo Operator**: Can request refresh and view outcomes.
- **Platform Admin**: Manages sanitization rules and release policies.
