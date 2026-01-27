# Deployment Runbook

## Prerequisites

- Node.js >= 18
- pnpm >= 8
- Supabase CLI
- Vercel CLI (optional, for manual deploys)

## Environment Setup

```bash
# Copy environment template
cp .env.example .env.local

# Edit with your credentials
# Required:
#   NEXT_PUBLIC_SUPABASE_URL
#   NEXT_PUBLIC_SUPABASE_ANON_KEY
#   SUPABASE_SERVICE_ROLE_KEY
#   NEXT_PUBLIC_PADDLE_CLIENT_TOKEN
#   PADDLE_WEBHOOK_SECRET
```

## Local Development

```bash
# Install dependencies
pnpm install

# Run development server
pnpm dev

# Run tests
pnpm test

# Type check
pnpm typecheck

# Lint
pnpm lint
```

## Database Migrations

### Apply migrations to Supabase

```bash
# Login to Supabase
supabase login

# Link to project
supabase link --project-ref <project-id>

# Push migrations
supabase db push

# Verify migration status
supabase db diff
```

### Rollback migration (if needed)

```bash
# Create rollback migration
supabase migration new rollback_billing_schema

# Edit the migration with DROP statements
# Then push
supabase db push
```

## Vercel Deployment

### Automatic (via GitHub)

Push to `main` branch triggers automatic deployment via GitHub Actions.

### Manual Deployment

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy preview
vercel

# Deploy production
vercel --prod
```

### Environment Variables in Vercel

Set via Vercel dashboard or CLI:

```bash
vercel env add NEXT_PUBLIC_SUPABASE_URL
vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY
vercel env add SUPABASE_SERVICE_ROLE_KEY
vercel env add NEXT_PUBLIC_PADDLE_CLIENT_TOKEN
vercel env add PADDLE_WEBHOOK_SECRET
vercel env add PADDLE_API_KEY
vercel env add ODOO_BASE_URL
vercel env add ODOO_DB
vercel env add ODOO_USER
vercel env add ODOO_PASSWORD
```

## Paddle Configuration

### Set up webhook endpoint

1. Go to Paddle Dashboard → Developers → Webhooks
2. Add new webhook:
   - URL: `https://your-domain.vercel.app/api/webhooks/paddle`
   - Events: All subscription and transaction events
3. Copy the webhook secret to `PADDLE_WEBHOOK_SECRET`

### Create products and prices

1. Products → Create Product (Starter, Pro, Enterprise)
2. For each product, create prices:
   - Monthly price
   - Annual price (discounted)
3. Copy price IDs to environment variables

## Odoo Configuration

### Create API user

```bash
# SSH into Odoo server
ssh root@your-odoo-server

# Create API user via odoo shell
docker compose exec odoo-core odoo shell -d odoo_core <<EOF
user = env['res.users'].create({
    'name': 'API User',
    'login': 'api@insightpulseai.com',
    'password': 'secure-password',
    'groups_id': [(4, env.ref('base.group_user').id)],
})
print(f"Created user ID: {user.id}")
EOF
```

### Add custom fields to res.partner

```python
# In ipai_billing_connector module (or via Studio)
class ResPartner(models.Model):
    _inherit = 'res.partner'

    x_paddle_customer_id = fields.Char('Paddle Customer ID', index=True)
    x_supabase_org_id = fields.Char('Supabase Org ID', index=True)
```

## Verification

### Health checks

```bash
# Check site is up
curl -s -o /dev/null -w "%{http_code}" https://your-domain.vercel.app

# Check API routes
curl -X POST https://your-domain.vercel.app/api/webhooks/paddle \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
# Expected: 401 (no signature)
```

### Odoo connectivity

```bash
# Run smoke test
ODOO_BASE_URL=https://erp.insightpulseai.net \
ODOO_DB=odoo_core \
ODOO_USER=api@insightpulseai.com \
ODOO_PASSWORD=your-password \
node scripts/smoke_odoo_partner_create.mjs
```

## Rollback

### Vercel rollback

```bash
# List deployments
vercel ls

# Rollback to previous deployment
vercel rollback <deployment-url>
```

### Database rollback

```bash
# Create point-in-time restore from Supabase dashboard
# Or apply rollback migration
supabase db push
```

## Troubleshooting

### Webhook failures

1. Check `billing.webhook_events` for error messages
2. Verify `PADDLE_WEBHOOK_SECRET` is correct
3. Check Vercel function logs

### Odoo provisioning failures

1. Check Vercel function logs for JSON-RPC errors
2. Verify Odoo credentials in environment
3. Check Odoo server logs: `docker compose logs odoo-core`

### Database connection issues

1. Verify Supabase project status
2. Check RLS policies if queries return empty
3. Verify service role key for webhook handlers
