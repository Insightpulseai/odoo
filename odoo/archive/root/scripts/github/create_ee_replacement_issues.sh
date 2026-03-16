#!/bin/bash
# scripts/github/create_ee_replacement_issues.sh
# Bulk create GitHub issues for Odoo CE Enterprise Replacement project
set -euo pipefail

REPO="jgtolentino/odoo-ce"
LABELS="enterprise-replacement,ipai"

# Create milestones
echo "Creating milestones..."
gh api repos/$REPO/milestones -f title="EE-Replace: Foundation" -f description="Module scaffold, base config" -f state="open" 2>/dev/null || true
gh api repos/$REPO/milestones -f title="EE-Replace: Email" -f description="SMTP, Fetchmail, DNS validation" -f state="open" 2>/dev/null || true
gh api repos/$REPO/milestones -f title="EE-Replace: Auth" -f description="OAuth Google, OAuth Azure" -f state="open" 2>/dev/null || true
gh api repos/$REPO/milestones -f title="EE-Replace: Multi-Company" -f description="Seeds, ACLs, intercompany" -f state="open" 2>/dev/null || true
gh api repos/$REPO/milestones -f title="EE-Replace: IoT" -f description="MQTT bridge, device registry" -f state="open" 2>/dev/null || true

# Foundation issues
echo "Creating Foundation issues..."
gh issue create --repo $REPO --title "[EE-Replace] Create ipai_enterprise_bridge module scaffold" \
  --body "Create the base module structure for ipai_enterprise_bridge with proper OCA conventions." \
  --label "$LABELS,P0-foundation" --milestone "EE-Replace: Foundation"

gh issue create --repo $REPO --title "[EE-Replace] Implement res.config.settings inheritance" \
  --body "Add configuration fields for email, OAuth, IoT to Settings." \
  --label "$LABELS,P0-foundation" --milestone "EE-Replace: Foundation"

gh issue create --repo $REPO --title "[EE-Replace] Map EE-only modules to CE+OCA alternatives" \
  --body "Create parity matrix: EE feature -> CE/OCA/IPAI replacement." \
  --label "$LABELS,P0-foundation,documentation" --milestone "EE-Replace: Foundation"

# Email issues
echo "Creating Email issues..."
gh issue create --repo $REPO --title "[EE-Replace] Configure Mailgun SMTP outbound email" \
  --body "Replace Odoo IAP Email with Mailgun SMTP. Create ir.mail_server XML seeds." \
  --label "$LABELS,P1-email" --milestone "EE-Replace: Email"

gh issue create --repo $REPO --title "[EE-Replace] Configure Fetchmail inbound email" \
  --body "Set up inbound email via Fetchmail. Create fetchmail.server XML seeds." \
  --label "$LABELS,P1-email" --milestone "EE-Replace: Email"

gh issue create --repo $REPO --title "[EE-Replace] Create DNS validation script" \
  --body "Script to verify SPF, DKIM, DMARC records for mail domain." \
  --label "$LABELS,P1-email,ci-cd" --milestone "EE-Replace: Email"

gh issue create --repo $REPO --title "[EE-Replace] Create email delivery test" \
  --body "Automated test that sends email and verifies delivery." \
  --label "$LABELS,P1-email,testing" --milestone "EE-Replace: Email"

# Auth issues
echo "Creating Auth issues..."
gh issue create --repo $REPO --title "[EE-Replace] Configure Google OAuth provider" \
  --body "Create auth.oauth.provider record for Google login." \
  --label "$LABELS,P2-auth" --milestone "EE-Replace: Auth"

gh issue create --repo $REPO --title "[EE-Replace] Configure Azure AD OAuth provider" \
  --body "Create auth.oauth.provider record for Microsoft 365 login." \
  --label "$LABELS,P2-auth" --milestone "EE-Replace: Auth"

gh issue create --repo $REPO --title "[EE-Replace] Create OAuth login test" \
  --body "Automated test for OAuth login flow." \
  --label "$LABELS,P2-auth,testing" --milestone "EE-Replace: Auth"

# Multi-Company issues
echo "Creating Multi-Company issues..."
gh issue create --repo $REPO --title "[EE-Replace] Create multi-company seed data" \
  --body "XML seeds for TBWA\\SMP and InsightPulseAI companies." \
  --label "$LABELS,P3-multi-company" --milestone "EE-Replace: Multi-Company"

gh issue create --repo $REPO --title "[EE-Replace] Configure intercompany flows" \
  --body "Install and configure OCA intercompany modules." \
  --label "$LABELS,P3-multi-company" --milestone "EE-Replace: Multi-Company"

# IoT issues
echo "Creating IoT issues..."
gh issue create --repo $REPO --title "[EE-Replace] Design ipai_iot_bridge architecture" \
  --body "Design MQTT-based IoT bridge to replace Odoo IoT Box." \
  --label "$LABELS,P4-iot" --milestone "EE-Replace: IoT"

gh issue create --repo $REPO --title "[EE-Replace] Implement IoT device registry model" \
  --body "Create ipai.iot.device model for device registration." \
  --label "$LABELS,P4-iot" --milestone "EE-Replace: IoT"

gh issue create --repo $REPO --title "[EE-Replace] Implement MQTT bridge" \
  --body "Implement paho-mqtt based bridge for IoT communication." \
  --label "$LABELS,P4-iot" --milestone "EE-Replace: IoT"

echo "Done! Created issues in $REPO"
echo "View project: https://github.com/$REPO/projects"
