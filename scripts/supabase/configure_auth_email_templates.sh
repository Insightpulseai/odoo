#!/usr/bin/env bash
set -euo pipefail

# ========================================
# Configure Supabase Auth Email Templates
# ========================================
# Sets up Magic Link, OTP, Confirmation, Recovery email templates

echo "📧 Configuring Auth Email Templates..."

# Verify prerequisites
: "${SUPABASE_PROJECT_REF:?Error: SUPABASE_PROJECT_REF not set}"
: "${SUPABASE_ACCESS_TOKEN:?Error: SUPABASE_ACCESS_TOKEN not set}"

# Construct payload with all email templates
payload="$(python3 - <<'PY'
import json

templates = {
  # Magic Link (user clicks link)
  "mailer_subjects_magic_link": "Sign in to InsightPulseAI",
  "mailer_templates_magic_link_content": """
<h2>Sign in to InsightPulseAI</h2>
<p>Click the link below to sign in to your account:</p>
<p><a href="{{ .ConfirmationURL }}">Sign in now</a></p>
<p>If you didn't request this, you can safely ignore this email.</p>
<p>This link expires in 24 hours.</p>
""",

  # Email OTP (user types code)
  "mailer_subjects_reauthentication": "Your InsightPulseAI verification code",
  "mailer_templates_reauthentication_content": """
<h2>Your verification code</h2>
<p>Enter this code to sign in to InsightPulseAI:</p>
<h1 style="font-size: 32px; letter-spacing: 8px;">{{ .Token }}</h1>
<p>This code expires in 5 minutes.</p>
<p>If you didn't request this, you can safely ignore this email.</p>
""",

  # Account confirmation
  "mailer_subjects_confirmation": "Confirm your InsightPulseAI account",
  "mailer_templates_confirmation_content": """
<h2>Confirm your account</h2>
<p>Click the link below to confirm your email address:</p>
<p><a href="{{ .ConfirmationURL }}">Confirm email</a></p>
<p>If you didn't create an account, you can safely ignore this email.</p>
""",

  # Password recovery
  "mailer_subjects_recovery": "Reset your InsightPulseAI password",
  "mailer_templates_recovery_content": """
<h2>Reset your password</h2>
<p>Click the link below to reset your password:</p>
<p><a href="{{ .ConfirmationURL }}">Reset password</a></p>
<p>If you didn't request this, you can safely ignore this email.</p>
<p>This link expires in 1 hour.</p>
""",

  # User invitation
  "mailer_subjects_invite": "You've been invited to InsightPulseAI",
  "mailer_templates_invite_content": """
<h2>Welcome to InsightPulseAI</h2>
<p>You've been invited to join InsightPulseAI.</p>
<p>Click the link below to accept the invitation:</p>
<p><a href="{{ .ConfirmationURL }}">Accept invitation</a></p>
"""
}

print(json.dumps(templates))
PY
)"

# PATCH via Management API
echo "→ Applying email templates via Management API..."
curl -fsS -X PATCH "https://api.supabase.com/v1/projects/${SUPABASE_PROJECT_REF}/config/auth" \
  -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "$payload" >/dev/null

echo "✅ Email templates configured successfully"
echo ""
echo "Templates configured:"
echo "  ✓ Magic Link (clickable URL)"
echo "  ✓ Email OTP (6-digit code)"
echo "  ✓ Account Confirmation"
echo "  ✓ Password Recovery"
echo "  ✓ User Invitation"
