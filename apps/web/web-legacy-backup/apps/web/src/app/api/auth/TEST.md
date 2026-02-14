# Auth API Testing Guide

Production-grade authentication routes for Magic Link and Email OTP flows.

---

## Available Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/api/auth/magic-link` | POST | Send passwordless email link |
| `/api/auth/otp/start` | POST | Send 6-digit email code |
| `/api/auth/otp/verify` | POST | Verify OTP code and create session |
| `/api/auth/callback` | GET | OAuth callback (shared by Magic Link) |
| `/api/auth/health` | GET | Health check endpoint |

---

## Testing Flows

### Prerequisites

```bash
# Local dev server
cd ~/Documents/GitHub/Insightpulseai/odoo/web/web
pnpm dev

# Or use production URL after deployment
BASE_URL="${BASE_URL:-http://localhost:3002}"
```

### 1. Magic Link Flow

**Step 1: Request magic link**
```bash
curl -sS -X POST "${BASE_URL}/api/auth/magic-link" \
  -H "Content-Type: application/json" \
  -d '{"email":"business@insightpulseai.com"}' | jq .
```

**Expected Response:**
```json
{"ok":true}
```

**Step 2: Check email**
- Email subject: "Confirm your signup"
- Click link (redirects to `/api/auth/callback`)
- Callback exchanges code for session
- Sets secure httpOnly cookies

**Step 3: Verify session**
```bash
# After clicking link, cookies are set
curl -sS "${BASE_URL}/api/auth/health" \
  --cookie-jar /tmp/cookies.txt \
  --cookie /tmp/cookies.txt | jq .
```

---

### 2. Email OTP Flow

**Step 1: Request OTP code**
```bash
curl -sS -X POST "${BASE_URL}/api/auth/otp/start" \
  -H "Content-Type: application/json" \
  -d '{"email":"business@insightpulseai.com"}' | jq .
```

**Expected Response:**
```json
{"ok":true}
```

**Step 2: Check email for 6-digit code**
- Email subject: "Your verification code"
- Copy the 6-digit code

**Step 3: Verify OTP**
```bash
OTP_CODE="123456"  # Replace with actual code
curl -sS -X POST "${BASE_URL}/api/auth/otp/verify" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"business@insightpulseai.com\",\"token\":\"${OTP_CODE}\"}" \
  --cookie-jar /tmp/cookies.txt | jq .
```

**Expected Response:**
```json
{
  "ok": true,
  "user": {
    "id": "uuid...",
    "email": "business@insightpulseai.com",
    ...
  }
}
```

**Step 4: Verify session**
```bash
curl -sS "${BASE_URL}/api/auth/health" \
  --cookie /tmp/cookies.txt | jq .
```

---

## Rate Limiting

**Supabase Email Rate Limits:**
- Magic Link: 3 emails per hour per email address
- OTP: 3 emails per hour per email address

**Expected 429 Response:**
```json
{
  "error": "Email rate limit exceeded"
}
```

**Backoff Strategy:**
```bash
# Wait 60 seconds between requests
for i in {1..3}; do
  curl -sS -X POST "${BASE_URL}/api/auth/otp/start" \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com"}'
  sleep 60
done
```

---

## Production Testing

### After Vercel Deployment

```bash
PROD_URL="https://insightpulseai.com"

# Test Magic Link
curl -sS -X POST "${PROD_URL}/api/auth/magic-link" \
  -H "Content-Type: application/json" \
  -d '{"email":"business@insightpulseai.com"}' | jq .

# Test OTP Start
curl -sS -X POST "${PROD_URL}/api/auth/otp/start" \
  -H "Content-Type: application/json" \
  -d '{"email":"business@insightpulseai.com"}' | jq .

# Test Health
curl -sS "${PROD_URL}/api/auth/health" | jq .
```

---

## Cookie Configuration

**Set by `/api/auth/callback` and `/api/auth/otp/verify`:**

| Cookie Name | HttpOnly | Secure | SameSite | MaxAge | Purpose |
|-------------|----------|--------|----------|--------|---------|
| `sb-access-token` | ✅ | Prod only | lax | session.expires_in | Access token |
| `sb-refresh-token` | ✅ | Prod only | lax | 30 days | Refresh token |

**Alignment Note:** Cookie names match Supabase auth convention. Adjust in both routes if changing.

---

## Troubleshooting

### Error: "email required"
- **Cause:** Missing email in request body
- **Fix:** Include `{"email":"user@example.com"}` in POST body

### Error: "email and token required"
- **Cause:** Missing OTP verification fields
- **Fix:** Include both `email` and `token` in verify request

### Error: "Email rate limit exceeded"
- **Cause:** Too many auth requests in short time
- **Fix:** Wait 60 minutes before retrying same email

### Error: "Invalid token"
- **Cause:** OTP code expired (10 minutes) or incorrect
- **Fix:** Request new OTP code, verify within 10 minutes

### Cookies Not Set
- **Cause:** Session not created or CORS issue
- **Fix:** Check `data.session` is present in API response

### Production 404 on Auth Routes
- **Cause:** Vercel build from wrong directory
- **Fix:** Set `rootDirectory: web/web` via `./scripts/vercel/fix_root_directory.sh`

---

## Security Notes

1. **httpOnly Cookies:** Prevents XSS access to tokens
2. **Secure Flag:** HTTPS-only in production (NODE_ENV=production)
3. **SameSite=lax:** CSRF protection while allowing navigation
4. **No Client-Side Storage:** Tokens never exposed to JavaScript
5. **Rate Limiting:** Supabase enforces email rate limits

---

## Next Steps

After successful testing:
1. ✅ Magic Link flow verified
2. ✅ OTP flow verified
3. ✅ Session cookies validated
4. → Add frontend UI components
5. → Implement session refresh logic
6. → Add protected route middleware
