# Magic Link 500 Error: Complete Analysis & Fix

## 🔴 Error: FUNCTION_INVOCATION_FAILED

**Error Message**: "This Serverless Function has crashed. 500: INTERNAL_SERVER_ERROR"

**Where it appears**: After clicking magic link in email

**Platform**: Supabase Edge Functions (NOT Vercel - you have no Vercel deployment yet)

---

## 1. THE FIX

### Immediate Solution: Configure Redirect URL

The magic link is trying to redirect to a URL that doesn't exist. You need to configure a **temporary local redirect** for testing:

**Step 1: Go to Supabase Dashboard**
```
https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz/auth/url-configuration
```

**Step 2: Add Redirect URL**

In "Redirect URLs" section, add:
```
http://localhost:3000/*
http://localhost:3000/auth/callback
```

**Step 3: Test Magic Link Locally**

Set up a simple local server to catch the redirect:

```bash
# Create a simple auth callback handler
cat > /tmp/auth-test.html << 'EOF'
<!DOCTYPE html>
<html>
<head><title>Auth Callback Test</title></head>
<body>
<h1>Magic Link Callback</h1>
<pre id="output">Loading...</pre>
<script type="module">
  import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

  const supabase = createClient(
    'https://spdtwktxdalcfigzeqrz.supabase.co',
    'YOUR_ANON_KEY_HERE'
  )

  // Handle auth callback
  const { data: { session }, error } = await supabase.auth.getSession()

  const output = document.getElementById('output')
  if (error) {
    output.textContent = 'Error: ' + JSON.stringify(error, null, 2)
  } else if (session) {
    output.textContent = 'Success!\n\n' +
      'User: ' + session.user.email + '\n' +
      'Tenant ID: ' + session.user.user_metadata.tenant_id + '\n' +
      'Role: ' + session.user.user_metadata.role + '\n\n' +
      'Full JWT Claims:\n' + JSON.stringify(session.user.user_metadata, null, 2)
  } else {
    output.textContent = 'No session found'
  }
</script>
</body>
</html>
EOF

# Serve it locally
python3 -m http.server 3000 --directory /tmp
```

---

## 2. ROOT CAUSE ANALYSIS

### What the Code Was Doing

```
User clicks magic link
    ↓
Supabase Auth validates token
    ↓
Custom Access Token Hook runs (adds tenant_id to JWT)
    ↓
Supabase tries to redirect to configured URL
    ↓
ERROR: URL doesn't exist / not in allowed list
    ↓
500 FUNCTION_INVOCATION_FAILED
```

### What It Needed

1. **Valid redirect URL** in Supabase Auth URL Configuration
2. **That URL must be in the allowed list**
3. **That URL must respond with valid HTML** (not crash)

### The Misconception

**What you thought**: Magic links work automatically without configuration

**Reality**: Magic links need explicit redirect URL configuration:
- Supabase doesn't know where to send the user after auth
- Default redirect (`/`) might be blocked by security policy
- Each environment (local/staging/prod) needs separate redirect URLs

### Conditions That Triggered This

1. **No redirect URL configured** in Supabase Auth settings
2. **OR configured URL points to non-existent Vercel deployment**
3. **Custom Access Token Hook enabled** (adds complexity to auth flow)
4. **No local development server** running to catch the redirect

---

## 3. UNDERLYING PRINCIPLE: Auth Flow Redirects

### Why This Error Exists

Magic link authentication is a **multi-step redirect flow**:

```
┌─────────────┐         ┌──────────────┐         ┌──────────────┐
│  Email      │ click   │  Supabase    │ 302     │  Your App    │
│  Magic Link │────────>│  Auth Server │────────>│  /auth/      │
│             │         │  (validates) │         │  callback    │
└─────────────┘         └──────────────┘         └──────────────┘
                              ↓
                        Custom Hook Runs
                        (adds tenant_id)
                              ↓
                        Issues JWT + redirect
```

**The error protects you from**:
- Open redirect vulnerabilities (attackers can't redirect to evil.com)
- CSRF attacks (only whitelisted URLs allowed)
- Broken auth flows (crashes if redirect target doesn't exist)

### Correct Mental Model

Think of magic links as **OAuth callback URLs**:

1. **Initiation**: User requests magic link → Supabase sends email
2. **Validation**: User clicks link → Supabase validates token
3. **Hook Execution**: Custom hook adds claims to JWT
4. **Redirect**: Supabase redirects to **YOUR configured URL**
5. **Session Establishment**: Your app reads JWT from URL hash/query params

**Critical**: Step 4 fails if:
- No redirect URL configured
- URL not in whitelist
- Target URL returns 500 error
- Network can't reach target (firewall, DNS, etc.)

### How This Fits Into Supabase Design

Supabase Auth is designed to be **framework-agnostic**:
- It doesn't assume you use Vercel, Netlify, or any specific platform
- It doesn't auto-detect your frontend URL
- **YOU must explicitly configure** where users go after auth

This is intentional for security:
```
Default behavior: FAIL CLOSED (reject unknown URLs)
NOT: FAIL OPEN (allow any URL and risk security)
```

---

## 4. WARNING SIGNS FOR FUTURE

### Red Flags That Indicate This Pattern

1. **"It works in Supabase Dashboard but not my app"**
   - Dashboard has built-in redirect handling
   - Your app needs explicit configuration

2. **"Magic link works once, then fails"**
   - Token already used (they expire after one use)
   - Session cookie conflicts between environments

3. **"Auth works locally but fails in production"**
   - Redirect URL configured for localhost only
   - Production URL not in whitelist

4. **"500 error only on auth, rest of app works"**
   - Auth redirect target doesn't exist
   - OR target exists but crashes on auth callback

### Code Smells

```typescript
// ❌ BAD: No error handling for auth callback
const { data } = await supabase.auth.getSession()
// What if session is null? What if error occurred?

// ✅ GOOD: Explicit error handling
const { data: { session }, error } = await supabase.auth.getSession()
if (error) {
  console.error('Auth callback failed:', error)
  // Redirect to login with error message
}
if (!session) {
  console.warn('No session after auth callback')
  // Redirect to login
}
```

```typescript
// ❌ BAD: Hardcoded redirect URL
const REDIRECT_URL = 'http://localhost:3000/auth/callback'

// ✅ GOOD: Environment-specific redirect
const REDIRECT_URL = process.env.NEXT_PUBLIC_SITE_URL + '/auth/callback'
// .env.local: NEXT_PUBLIC_SITE_URL=http://localhost:3000
// .env.production: NEXT_PUBLIC_SITE_URL=https://app.insightpulseai.com
```

### Similar Mistakes You Might Make

1. **OAuth integrations** (Google, GitHub login)
   - Same redirect URL configuration required
   - Must whitelist each OAuth provider's callback URL

2. **Password reset links**
   - Also requires redirect URL configuration
   - Separate from magic link configuration

3. **Email confirmation links**
   - Yep, also needs redirect URL
   - Can use same URL as magic links

4. **Webhook endpoints**
   - Similar concept: Supabase calls YOUR URL
   - Must be publicly accessible (can't be localhost in prod)

---

## 5. ALTERNATIVE APPROACHES & TRADE-OFFS

### Approach 1: Magic Links (Current)

**Pros:**
- No password to remember
- More secure (token expires after use)
- Better UX for mobile users

**Cons:**
- Requires email delivery (can fail)
- Requires redirect URL configuration
- User must have access to email

**Best for**: B2B SaaS, internal tools, mobile apps

### Approach 2: Password Authentication

**Pros:**
- No redirect configuration needed
- Works offline (after initial login)
- Simpler auth flow

**Cons:**
- Users forget passwords
- Password reset also needs email
- More vulnerable to credential stuffing

**Best for**: Consumer apps, high-traffic sites

```typescript
// Password auth (simpler)
const { data, error } = await supabase.auth.signInWithPassword({
  email,
  password,
})
// No redirect needed - session established immediately
```

### Approach 3: OAuth (Google, GitHub, etc.)

**Pros:**
- User doesn't need new account
- Provider handles security
- Fast signup flow

**Cons:**
- Requires OAuth app registration
- Redirect URL configuration (same issue!)
- Provider dependency (if Google is down, you're down)

**Best for**: Developer tools, apps targeting specific audiences

### Approach 4: Passwordless OTP (SMS/Email code)

**Pros:**
- No redirect needed
- Works in-app (no email click)
- Good UX on mobile

**Cons:**
- SMS costs money
- Can be intercepted (SIM swapping)
- Requires phone number (privacy concern)

**Best for**: Mobile-first apps, e-commerce

```typescript
// OTP auth (no redirect)
await supabase.auth.signInWithOtp({ phone })
// User enters code in-app
await supabase.auth.verifyOtp({ phone, token: userEnteredCode })
```

### Recommended Pattern (What You Should Use)

**Hybrid: Password + Magic Link + OAuth**

```typescript
// Offer multiple options
const loginOptions = {
  password: await supabase.auth.signInWithPassword({ email, password }),
  magicLink: await supabase.auth.signInWithOtp({
    email,
    options: { emailRedirectTo: redirectUrl }
  }),
  google: await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: { redirectTo: redirectUrl }
  })
}
```

**Why this works**:
- Power users use passwords (fast)
- Casual users use magic links (secure)
- Lazy users use OAuth (easiest)
- You configure redirect URL **once** for all methods

---

## 6. PREVENTION CHECKLIST

### Before Enabling Auth in Production

- [ ] Configure redirect URLs for all environments
  - [ ] Development: `http://localhost:3000/*`
  - [ ] Staging: `https://staging.yourapp.com/*`
  - [ ] Production: `https://app.yourapp.com/*`

- [ ] Test auth callback handler
  - [ ] Handles success case (session exists)
  - [ ] Handles error case (displays error message)
  - [ ] Handles no-session case (redirects to login)

- [ ] Verify custom access token hook
  - [ ] Test with valid user (returns claims)
  - [ ] Test with invalid user (handles gracefully)
  - [ ] Check hook execution time (<5s)

- [ ] Monitor auth errors
  - [ ] Set up error tracking (Sentry, LogRocket, etc.)
  - [ ] Alert on >5% auth failure rate
  - [ ] Log hook errors to separate table

### Development Workflow

```bash
# 1. Start local dev server FIRST
npm run dev  # or: python -m http.server 3000

# 2. Configure redirect URL in Supabase Dashboard
# http://localhost:3000/auth/callback

# 3. Request magic link
curl -X POST "$SUPABASE_URL/auth/v1/magiclink" \
  -H "apikey: $SUPABASE_ANON_KEY" \
  -d '{"email": "test@example.com"}'

# 4. Click link in email → should redirect to localhost

# 5. Check session in browser console
await supabase.auth.getSession()
```

---

## 7. DEBUGGING COMMANDS

### Check Current Auth Configuration

```sql
-- What redirect URLs are configured?
SELECT * FROM auth.config WHERE name = 'site_url';
SELECT * FROM auth.config WHERE name = 'additional_redirect_urls';
```

### Test Hook Locally

```sql
-- Simulate what happens when user clicks magic link
SELECT public.custom_access_token_hook(
  jsonb_build_object(
    'user_id', 'f0304ff6-60bd-439e-be9c-ea36c29a3464',
    'claims', '{}'::jsonb
  )
);
```

### Check Recent Auth Attempts

```sql
SELECT
  created_at,
  user_id,
  email,
  event_type,
  ip_address
FROM auth.audit_log_entries
WHERE created_at > now() - interval '1 hour'
ORDER BY created_at DESC
LIMIT 10;
```

---

## 8. NEXT STEPS FOR YOUR SETUP

1. **Configure redirect URL** in Supabase Dashboard:
   ```
   https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz/auth/url-configuration

   Add: http://localhost:3000/*
   ```

2. **Create simple auth callback page** to test:
   ```html
   <!-- /tmp/auth-callback.html -->
   <script type="module">
     import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
     const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)
     const { data: { session } } = await supabase.auth.getSession()
     console.log('Session:', session?.user.user_metadata)
   </script>
   ```

3. **Test magic link flow**:
   - Request magic link
   - Click link in email
   - Should redirect to localhost:3000
   - Should see JWT claims in console

4. **When ready for production**:
   - Deploy frontend to Vercel
   - Add production URL to Supabase redirect URLs
   - Update NEXT_PUBLIC_SITE_URL environment variable

---

**Last Updated**: 2026-01-09
**Related Docs**: `AUTH_MODEL.md`, `verify_auth_setup.sh`
