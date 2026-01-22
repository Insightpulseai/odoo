# 🔐 Secrets Setup Guide (Figma Make)

**Important:** Use Figma Make's secret UI, **NOT** the Supabase Dashboard for Edge Function secrets.

---

## 📍 Where to Add Secrets

### ❌ WRONG: Supabase Dashboard → Edge Functions → Settings

Don't add secrets here. Figma Make manages this for you.

### ✅ CORRECT: Figma Make → Settings → Secrets

Add secrets in Figma Make's interface. They'll be automatically injected into your Edge Function.

---

## 🎯 Step-by-Step: Adding Secrets in Figma Make

### Step 1: Open Secrets Panel

In Figma Make:
1. Click the **Settings** icon (gear) in the top-right
2. Navigate to **Secrets** tab
3. You'll see the secrets management interface

### Step 2: Create Each Secret

For each secret, click **"Create a secret"**:

#### Secret 1: SUPABASE_SERVICE_ROLE_KEY (Required)

**Name:** `SUPABASE_SERVICE_ROLE_KEY`

**Value:** Get from Supabase Dashboard:
1. Go to https://app.supabase.com
2. Select your project
3. Navigate to **Settings → API**
4. Find **Project API keys → service_role**
5. Click **👁️ Show** to reveal the key
6. Click **📋 Copy**
7. Paste into Figma Make secret value

**Why needed:** Allows Edge Function to bypass RLS and write logs/artifacts

---

#### Secret 2: VERCEL_TOKEN (Optional)

**Name:** `VERCEL_TOKEN`

**Value:** Get from Vercel:
1. Go to https://vercel.com/account/tokens
2. Click **Create Token**
3. Name: "Ops Control Room"
4. Scope: Full Account
5. Click **Create**
6. Copy the token (starts with `vercel_...`)
7. Paste into Figma Make secret value

**Why needed:** Deploy runbooks need to trigger Vercel builds/deployments

**Skip if:** You're not using deploy runbooks yet

---

#### Secret 3: GITHUB_TOKEN (Optional)

**Name:** `GITHUB_TOKEN`

**Value:** Get from GitHub:
1. Go to https://github.com/settings/tokens
2. Click **Generate new token → Generate new token (classic)**
3. Name: "Ops Control Room"
4. Scopes: Select `repo` (full control of private repositories)
5. Click **Generate token**
6. Copy the token (starts with `ghp_...`)
7. Paste into Figma Make secret value

**Why needed:** Spec and incident runbooks create GitHub PRs

**Skip if:** You're not using spec/incident runbooks yet

---

#### Secret 4: DIGITALOCEAN_TOKEN (Optional)

**Name:** `DIGITALOCEAN_TOKEN`

**Value:** Get from DigitalOcean:
1. Go to https://cloud.digitalocean.com/account/api/tokens
2. Click **Generate New Token**
3. Name: "Ops Control Room"
4. Scopes: Read + Write
5. Click **Generate Token**
6. Copy the token (starts with `dop_...`)
7. Paste into Figma Make secret value

**Why needed:** Health checks need to query droplet status

**Skip if:** You're not using DigitalOcean services

---

## 📋 Quick Reference Table

| Secret Name | Required? | Used For | Where to Get |
|------------|-----------|----------|--------------|
| `SUPABASE_SERVICE_ROLE_KEY` | ✅ Yes | Writing logs/artifacts | Supabase Dashboard → Settings → API |
| `VERCEL_TOKEN` | ⚠️ Optional | Deploy runbooks | https://vercel.com/account/tokens |
| `GITHUB_TOKEN` | ⚠️ Optional | Spec/incident runbooks | https://github.com/settings/tokens |
| `DIGITALOCEAN_TOKEN` | ⚠️ Optional | Health checks | https://cloud.digitalocean.com/account/api |

---

## 🔍 How to Verify Secrets Are Set

### Check in Figma Make

**Figma Make → Settings → Secrets**

You should see:
```
✓ SUPABASE_SERVICE_ROLE_KEY    [Created on: Jan 3, 2026]
✓ VERCEL_TOKEN                 [Created on: Jan 3, 2026]
✓ GITHUB_TOKEN                 [Created on: Jan 3, 2026]
✓ DIGITALOCEAN_TOKEN           [Created on: Jan 3, 2026]
```

### Test in Edge Function

The secrets will be available via:

```typescript
// In /supabase/functions/ops-executor/index.ts
const serviceRoleKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
const vercelToken = Deno.env.get("VERCEL_TOKEN");
const githubToken = Deno.env.get("GITHUB_TOKEN");
const doToken = Deno.env.get("DIGITALOCEAN_TOKEN");

console.log("Service role key exists:", !!serviceRoleKey);
console.log("Vercel token exists:", !!vercelToken);
// etc.
```

Check **Supabase Dashboard → Edge Functions → ops-executor → Logs** to see these console.log outputs.

---

## 🛡️ Security Best Practices

### ✅ DO

- ✅ Use Figma Make's secret UI
- ✅ Rotate tokens periodically
- ✅ Use minimal scopes (e.g., `repo` not `admin:org` for GitHub)
- ✅ Create separate tokens for each environment (dev/staging/prod)
- ✅ Revoke tokens when no longer needed

### ❌ DON'T

- ❌ Put secrets in `.env` file
- ❌ Commit secrets to git
- ❌ Share secrets in chat/email
- ❌ Use your personal tokens in production
- ❌ Grant unnecessary scopes

---

## 🔄 How Secrets Flow

```
┌─────────────────────────────────────────────┐
│  FIGMA MAKE                                 │
│  Settings → Secrets                         │
│  ┌─────────────────────────────────────┐   │
│  │ SUPABASE_SERVICE_ROLE_KEY           │   │
│  │ VERCEL_TOKEN                        │   │
│  │ GITHUB_TOKEN                        │   │
│  │ DIGITALOCEAN_TOKEN                  │   │
│  └─────────────────────────────────────┘   │
└──────────────────┬──────────────────────────┘
                   │
        (Injected at deploy time)
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  SUPABASE EDGE FUNCTION                     │
│  (ops-executor)                             │
│                                             │
│  const key = Deno.env.get("SECRET_NAME")   │
│                                             │
│  ✅ Available at runtime                    │
│  ❌ Never exposed to browser                │
└─────────────────────────────────────────────┘
```

**Key points:**
1. Secrets defined in Figma Make UI
2. Automatically injected into Edge Function at deploy
3. Accessed via `Deno.env.get()` in server code
4. **NEVER** accessible from browser/frontend

---

## 🧪 Testing Secret Access

### Test 1: Check Secrets Exist (Edge Function)

Add temporary logging to `/supabase/functions/ops-executor/index.ts`:

```typescript
serve(async (req) => {
  // Temporary debug logging
  console.log("=== Secret Check ===");
  console.log("SUPABASE_SERVICE_ROLE_KEY:", Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ? "✓ Set" : "✗ Missing");
  console.log("VERCEL_TOKEN:", Deno.env.get("VERCEL_TOKEN") ? "✓ Set" : "✗ Missing");
  console.log("GITHUB_TOKEN:", Deno.env.get("GITHUB_TOKEN") ? "✓ Set" : "✗ Missing");
  console.log("DIGITALOCEAN_TOKEN:", Deno.env.get("DIGITALOCEAN_TOKEN") ? "✓ Set" : "✗ Missing");
  console.log("===================");
  
  // ... rest of function
});
```

Then:
1. Click **Deploy** in Figma Make (to redeploy with logging)
2. Trigger the function manually or wait for cron
3. Check **Supabase Dashboard → Edge Functions → ops-executor → Logs**

Expected output:
```
=== Secret Check ===
SUPABASE_SERVICE_ROLE_KEY: ✓ Set
VERCEL_TOKEN: ✓ Set
GITHUB_TOKEN: ✓ Set
DIGITALOCEAN_TOKEN: ✓ Set
===================
```

### Test 2: Actually Use a Secret

Create a test run and check if it can write to the database:

1. Open your app
2. Type: "check prod status"
3. Click Run
4. Check Supabase Dashboard → Table Editor → ops.run_events

If you see log entries → `SUPABASE_SERVICE_ROLE_KEY` is working! ✅

---

## 🆘 Troubleshooting

### "Secret not found" or undefined

**Problem:** Edge Function can't access secret

**Solutions:**
1. Verify secret exists in **Figma Make → Settings → Secrets**
2. Check spelling (case-sensitive!)
3. Click **Deploy** again to re-inject secrets
4. Check Edge Function logs for exact error message

### "Invalid API key" or "Unauthorized"

**Problem:** Secret value is incorrect

**Solutions:**
1. Re-copy the secret from source (Supabase/Vercel/GitHub)
2. Make sure you copied the **full** key (no truncation)
3. Update the secret in Figma Make
4. Click **Deploy** again

### "Service role key bypasses RLS but still can't write"

**Problem:** Database permissions issue (not secret issue)

**Solutions:**
1. Verify migration applied: Check if `ops` schema exists
2. Verify RLS policies exist: SQL Editor → `\dp ops.*`
3. Check if `service_role` policy exists for `ops.run_events`

---

## 📞 Reference Links

### Get Tokens/Keys

- **Supabase Service Role:** https://app.supabase.com → Your Project → Settings → API
- **Vercel Token:** https://vercel.com/account/tokens
- **GitHub Token:** https://github.com/settings/tokens
- **DigitalOcean Token:** https://cloud.digitalocean.com/account/api/tokens

### Documentation

- **Figma Make Secrets:** [Help Center Article](https://help.figma.com/hc/en-us/articles/32640822050199)
- **Supabase Edge Functions:** https://supabase.com/docs/guides/functions
- **Deno Environment Variables:** https://deno.land/manual/runtime/environment_variables

---

## ✅ Checklist: Secret Setup Complete

After following this guide, verify:

- [ ] Opened Figma Make → Settings → Secrets
- [ ] Created `SUPABASE_SERVICE_ROLE_KEY` secret
- [ ] (Optional) Created `VERCEL_TOKEN` secret
- [ ] (Optional) Created `GITHUB_TOKEN` secret
- [ ] (Optional) Created `DIGITALOCEAN_TOKEN` secret
- [ ] Clicked **Deploy** to apply changes
- [ ] Tested Edge Function logs show secrets exist
- [ ] Tested run creation → logs appear in database

**Once all checked:** Your secrets are properly configured! 🎉

**Next:** Follow `/FIGMA_MAKE_DEPLOY.md` to complete deployment.
