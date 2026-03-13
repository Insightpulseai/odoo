# Organization Invite System

## Overview

Multi-tenant organization invite system with email-based invitations, role-based access control, and Supabase RLS security.

## Architecture

### Database Layer
- **Schema**: `registry.org_invites`
- **Security**: Row Level Security (RLS) enabled
- **Token Storage**: SHA-256 hashed (64 hex characters)
- **Expiration**: 7-day default (configurable)

### RPC Functions (SECURITY DEFINER)
1. `create_org_invite_with_token(p_org_id, p_email, p_role, p_token)`
   - Authorization: User must be org admin (user.id = org_id)
   - Hashes token with SHA-256 before storage
   - Returns invite record

2. `accept_org_invite(p_token, p_user_id)`
   - Validates token hash, checks expiration
   - Updates status to 'accepted'
   - Returns org_id and role

3. `cancel_org_invite(p_invite_id)`
   - Authorization: User must be org admin
   - Updates status to 'cancelled'

4. `cleanup_expired_invites()`
   - Marks expired invites as 'expired'
   - Returns count of updated records

### API Routes

#### POST /api/org/create
Create new organization (user becomes owner).

**Request:**
```json
{
  "name": "Acme Inc.",
  "description": "Optional description"
}
```

**Response:**
```json
{
  "org_id": "uuid",
  "name": "Acme Inc.",
  "description": "...",
  "owner_id": "uuid",
  "owner_email": "user@example.com"
}
```

#### POST /api/invite/send
Send email invitation to join organization.

**Request:**
```json
{
  "org_id": "uuid",
  "email": "colleague@example.com",
  "role": "member",
  "org_name": "Acme Inc."
}
```

**Response:**
```json
{
  "invite": {
    "id": "uuid",
    "email": "colleague@example.com",
    "role": "member",
    "status": "pending",
    "expires_at": "2026-02-19T...",
    "created_at": "2026-02-12T..."
  }
}
```

#### POST /api/invite/accept
Accept invitation and join organization.

**Request:**
```json
{
  "token": "64-char-hex-token"
}
```

**Response:**
```json
{
  "org_id": "uuid",
  "role": "member",
  "message": "Invite accepted successfully"
}
```

**Error Responses:**
- `410`: Invite expired
- `404`: Invalid or already used invite
- `401`: Unauthorized (not logged in)

#### GET /api/invite/list?org_id=uuid
List organization invitations (admin only).

**Response:**
```json
{
  "invites": [
    {
      "id": "uuid",
      "email": "colleague@example.com",
      "role": "member",
      "status": "pending",
      "expires_at": "2026-02-19T...",
      "accepted_at": null,
      "created_at": "2026-02-12T...",
      "updated_at": "2026-02-12T..."
    }
  ]
}
```

#### POST /api/invite/cancel
Cancel pending invitation (admin only).

**Request:**
```json
{
  "invite_id": "uuid"
}
```

**Response:**
```json
{
  "message": "Invite cancelled successfully"
}
```

## Frontend Pages

### /org/new
Create new organization form.

**Features:**
- Organization name (required)
- Description (optional)
- Form validation
- Error handling

### /org/[orgId]
Organization dashboard with invite management.

**Features:**
- Send new invitations
- List pending/accepted invites
- Cancel pending invites
- Role selection (admin/member/viewer)
- Auto-refresh after actions

### /invite/accept?token=...
Accept invitation page.

**Features:**
- Token validation
- Auth check (redirect to login if needed)
- Accept/decline buttons
- Automatic redirect to org dashboard on success
- Suspense boundary for loading state

## Email Integration

**Provider**: Zoho SMTP (smtp.zoho.com:587)

**Email Template:**
- Branded HTML email with gradient design
- Accept invitation button
- Plain text fallback
- Expiration date
- Fallback link for non-working buttons

**Environment Variables:**
```bash
ZOHO_USER=business@insightpulseai.com
ZOHO_PASS=your_zoho_app_password
ZOHO_FROM_NAME=InsightPulse.ai
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

## Security

### Token Security
- 256-bit entropy (32 bytes → 64 hex characters)
- SHA-256 hashing before database storage
- Never store plaintext tokens
- Single-use enforcement (status update)
- 7-day expiration (configurable)

### Database Security
- RLS policies enabled on all tables
- `SECURITY DEFINER` RPC functions
- Authorization checks in RPC functions
- Org-level data isolation via RLS

### API Security
- JWT validation on all protected routes
- Role-based access control (admin-only operations)
- Input validation with token format check
- Error message sanitization

### Email Security
- TLS encryption (port 587)
- Credentials via environment variables
- HTTPS-only accept URLs

## Testing

### Manual Test Flow
1. Create organization: `/org/new`
2. Send invite: `/org/{orgId}` → Invite form
3. Check email (Zoho inbox)
4. Accept invite: Click link in email → `/invite/accept?token=...`
5. Verify membership: Redirects to `/org/{orgId}`

### Database Tests (SQL)
```sql
-- Test RPC: create invite
SELECT * FROM registry.create_org_invite_with_token(
  '<user_id>', 'test@example.com', 'member', 'test-token-abc123'
);

-- Test RPC: accept invite
SELECT * FROM registry.accept_org_invite('test-token-abc123', '<user_id>');

-- Verify token hash (should be 64 hex chars)
SELECT LENGTH(token_hash), token_hash FROM registry.org_invites LIMIT 1;

-- Test RLS policies
SET ROLE authenticated;
SET request.jwt.claims.sub TO '<user_id>';
SELECT * FROM registry.org_invites;
```

### API Tests (cURL)
```bash
# Create org
curl -X POST http://localhost:3000/api/org/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Org","description":"Test"}'

# Send invite
curl -X POST http://localhost:3000/api/invite/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"org_id":"xxx","email":"test@example.com","role":"member","org_name":"Test Org"}'

# Accept invite
curl -X POST http://localhost:3000/api/invite/accept \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"token":"abc123..."}'
```

## Deployment

### Supabase Migration
```bash
# Login
supabase login

# Link project
supabase link --project-ref spdtwktxdalcfigzeqrz

# Push migration
supabase db push

# Or via Dashboard SQL Editor
# Copy/paste: supabase/migrations/20260212_org_invites.sql
```

### Environment Variables (Vercel)
```bash
# Required
NEXT_PUBLIC_SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...
ZOHO_USER=business@insightpulseai.com
ZOHO_PASS=...
ZOHO_FROM_NAME=InsightPulse.ai
NEXT_PUBLIC_APP_URL=https://yourdomain.com
```

### Build Verification
```bash
pnpm build
# ✓ All pages should build successfully
# ✓ No TypeScript errors
# ✓ API routes compiled
```

## Troubleshooting

### Email Not Sending
- Check ZOHO_USER and ZOHO_PASS are set
- Verify Zoho SMTP allows app passwords
- Check server logs for email errors

### Invite Not Accepting
- Verify token is valid 64-hex format
- Check invite not expired (7 days)
- Ensure user is authenticated
- Check RLS policies in Supabase

### Build Errors
- Install missing dependencies: `@radix-ui/react-label`, `@radix-ui/react-select`
- Wrap `useSearchParams()` in Suspense boundary
- Check all API routes compile

## Future Enhancements

### Organization Features
- [ ] Separate `organizations` table (not just user.id)
- [ ] Organization metadata (logo, settings)
- [ ] Multi-role support per user (multiple orgs)

### Invite Features
- [ ] Custom expiration periods
- [ ] Invite link preview
- [ ] Batch invites
- [ ] Invite templates

### Security
- [ ] Rate limiting on invite sending
- [ ] CAPTCHA on accept page
- [ ] Audit log for invite actions
- [ ] Email verification before invite send

### UI/UX
- [ ] Invite status filters
- [ ] Search invites by email
- [ ] Resend expired invites
- [ ] Invite analytics dashboard

## Files Changed

### New Files
- `supabase/migrations/20260212_org_invites.sql`
- `lib/supabase/client.ts`
- `lib/supabase/server.ts`
- `lib/email/zoho.ts`
- `lib/auth/invite-token.ts`
- `app/api/org/create/route.ts`
- `app/api/invite/send/route.ts`
- `app/api/invite/accept/route.ts`
- `app/api/invite/list/route.ts`
- `app/api/invite/cancel/route.ts`
- `app/org/new/page.tsx`
- `app/org/[orgId]/page.tsx`
- `app/invite/accept/page.tsx`
- `docs/ORG_INVITES.md`

### Modified Files
- `.env.example` (added Zoho SMTP config)
- `package.json` (added dependencies)

### Dependencies Added
- `@supabase/supabase-js@^2.47.14`
- `nodemailer@^6.9.16`
- `@types/nodemailer@^6.4.16`
- `@radix-ui/react-label@2.1.1`
- `@radix-ui/react-select@2.1.4`
