#!/bin/bash
# Helper script to migrate secrets to Supabase Vault

PROJECT_REF="spdtwktxdalcfigzeqrz"

echo "🔐 Migrating secrets to Supabase Vault..."

# Example: Set a secret
# supabase secrets set SECRET_NAME="secret_value" --project-ref $PROJECT_REF

echo "
Usage:
  supabase secrets set DB_PASSWORD=\"your_password\" --project-ref $PROJECT_REF
  supabase secrets set OPENAI_API_KEY=\"sk-...\" --project-ref $PROJECT_REF

View secrets:
  supabase secrets list --project-ref $PROJECT_REF

Delete secret:
  supabase secrets unset SECRET_NAME --project-ref $PROJECT_REF
"
