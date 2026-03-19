# 🔑 Environment Variables Setup Guide

## Where to Get Your Credentials

### Step 1: Go to Supabase Dashboard

Visit: https://app.supabase.com

### Step 2: Select Your Project

Click on your **"Ops Control Room"** project (or whatever you named it)

### Step 3: Navigate to API Settings

**Left sidebar → Settings → API**

---

## 📋 Copy These Values

### For Frontend (.env file)

Open the `/.env` file in your project and replace the placeholders:

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here
```

**Where to find them on the API page:**

| Variable | Location on Page | Example Value |
|----------|------------------|---------------|
| `VITE_SUPABASE_URL` | **Project URL** section | `https://abcdefg.supabase.co` |
| `VITE_SUPABASE_ANON_KEY` | **Project API keys → anon public** | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |

### For Edge Function (Supabase Dashboard)

After deployment, add these secrets to the Edge Function:

**Supabase Dashboard → Edge Functions → ops-executor → Settings**

| Secret Name | Location on Page | Security Level |
|------------|------------------|----------------|
| `SUPABASE_URL` | Same as VITE_SUPABASE_URL | ⚠️ Server-side only |
| `SUPABASE_SERVICE_ROLE_KEY` | **Project API keys → service_role** | 🔴 CRITICAL - NEVER expose! |

---

## 🎯 Visual Guide

### Screenshot Reference

When you're on the **Settings → API** page, you'll see:

```
┌─────────────────────────────────────────────────┐
│ Project URL                                     │
│ https://abcdefg.supabase.co          [📋 Copy] │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Project API keys                                │
│                                                 │
│ anon public                          [👁️ Show]  │
│ eyJhbGciOiJIUzI1NiIsInR5cCI6Ikp...   [📋 Copy] │
│                                                 │
│ service_role                         [👁️ Show]  │
│ eyJhbGciOiJIUzI1NiIsInR5cCI6Ikp...   [📋 Copy] │
└─────────────────────────────────────────────────┘
```

---

## ✅ Verification Checklist

### After editing .env

- [ ] File exists at `/.env` (not `.env.example`)
- [ ] `VITE_SUPABASE_URL` starts with `https://`
- [ ] `VITE_SUPABASE_URL` ends with `.supabase.co`
- [ ] `VITE_SUPABASE_ANON_KEY` is a long string starting with `eyJ`
- [ ] No placeholder text remains (like "your-project" or "your-anon-key-here")
- [ ] No quotes around the values
- [ ] No extra spaces or line breaks

### Example of CORRECT .env file

```env
VITE_SUPABASE_URL=https://xyzabc123.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh5emFiYzEyMyIsInJvbGUiOiJhbm9uIiwiaWF0IjoxNjQwOTk1MjAwLCJleHAiOjE5NTY1NzEyMDB9.abc123def456
```

### Example of WRONG .env file

```env
# ❌ WRONG - Has placeholder text
VITE_SUPABASE_URL=https://your-project.supabase.co

# ❌ WRONG - Has quotes
VITE_SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1..."

# ❌ WRONG - Missing protocol
VITE_SUPABASE_URL=xyzabc123.supabase.co

# ❌ WRONG - Has comments inline
VITE_SUPABASE_URL=https://xyz.supabase.co  # my project url
```

---

## 🔐 Security Best Practices

### ✅ Safe to Share (Public)
- `VITE_SUPABASE_URL` - Your project URL
- `VITE_SUPABASE_ANON_KEY` - Protected by Row Level Security

**Why it's safe:**
- RLS policies prevent unauthorized access
- Anon key can only do what you've explicitly allowed
- Users can only see their own data

### ⚠️ NEVER Share (Secret)
- `SUPABASE_SERVICE_ROLE_KEY` - **Bypasses ALL security!**
- Any `*_TOKEN` or `*_SECRET` variables

**Why it's dangerous:**
- Service role bypasses Row Level Security
- Can read/write/delete ALL data
- Can access admin functions
- If leaked, attacker has full database access

### 🛡️ What We Do to Protect You

1. **Frontend uses anon key only**
   - Lives in `.env` file
   - Gets bundled into browser code
   - Protected by RLS policies

2. **Backend uses service role**
   - Lives in Supabase Edge Function secrets
   - NEVER sent to browser
   - Only accessible to server-side code

3. **RLS prevents abuse**
   - Users can only see their own runs
   - Users can't fake log entries
   - Users can't modify other users' data

---

## 🧪 Testing Your Configuration

### Test 1: Environment Variables Loaded

After editing `.env`, restart your dev server and check the browser console:

```javascript
// Open browser DevTools → Console
console.log(import.meta.env.VITE_SUPABASE_URL);
// Should print: https://your-project.supabase.co

console.log(import.meta.env.VITE_SUPABASE_ANON_KEY?.substring(0, 20));
// Should print: eyJhbGciOiJIUzI1NiIs...
```

### Test 2: Supabase Connection

Open your app and check the Network tab:

1. Open DevTools → Network tab
2. Filter by "supabase.co"
3. Look for successful requests (status 200)
4. If you see 401/403 errors, your anon key might be wrong

### Test 3: Create a Test Run

Try creating a simple runbook:

1. Type: "check prod status"
2. Click Run
3. Check Supabase Dashboard → Table Editor → ops → runs
4. You should see a new row

---

## 🆘 Troubleshooting

### Error: "Missing Supabase environment variables"

**Problem:** The app can't find your `.env` file or the variables are empty

**Solutions:**
1. Make sure file is named `.env` exactly (not `.env.txt` or `.env.example`)
2. Make sure it's in the **root directory** (same level as `package.json`)
3. Check that values don't have placeholder text
4. Restart your dev server after editing

### Error: "Failed to fetch" or "Network error"

**Problem:** Wrong Supabase URL or project doesn't exist

**Solutions:**
1. Double-check the URL on Supabase Dashboard → Settings → API
2. Make sure URL starts with `https://`
3. Make sure URL ends with `.supabase.co`
4. Check that your Supabase project is active (not paused)

### Error: "Invalid API key" or "JWT expired"

**Problem:** Wrong anon key or using an old key

**Solutions:**
1. Copy the anon key again from Supabase Dashboard
2. Make sure you're copying the **anon public** key, not service_role
3. Check for extra spaces or line breaks in the `.env` file
4. Try clicking the "Regenerate" button on the API page (will require updating .env)

### Error: "Row Level Security policy violation"

**Problem:** RLS policies not set up correctly

**Solutions:**
1. Make sure you ran the migration (`20250103000000_ops_schema.sql`)
2. Check Supabase Dashboard → Authentication → Policies
3. Verify tables have RLS enabled
4. Try the query in SQL Editor with your anon key

---

## 📞 Need Help?

### Quick Links
- **Supabase Dashboard:** https://app.supabase.com
- **API Settings:** Dashboard → Settings → API
- **Project Logs:** Dashboard → Logs
- **SQL Editor:** Dashboard → SQL Editor

### Documentation
- `/QUICKSTART.md` - 3-minute setup
- `/DEPLOY.md` - Full deployment guide
- `/FIXED.md` - Common issues
- `/STATUS.md` - System status

### Still Stuck?

Check the Supabase documentation:
- https://supabase.com/docs/guides/getting-started
- https://supabase.com/docs/guides/api

---

## ✅ Once You're Done

After filling in your `.env` file:

1. **Save the file** 💾
2. **Restart your dev server** 🔄
3. **Refresh your browser** 🌐
4. **You should see NO MORE environment variable errors!** 🎉

Next step: Click **Deploy** in Figma Make to apply the database migration and deploy the Edge Function!

See `/DEPLOY.md` for the complete deployment process.
