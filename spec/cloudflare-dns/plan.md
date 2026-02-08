# Plan

1. Terraform module under infra/terraform/cloudflare/insightpulseai.com
2. GitHub Actions workflow:
   - plan on PR
   - apply on main
   - explicit least-privilege permissions
3. Import helper for existing records
4. Verification:
   - dig checks for A/MX/TXT
