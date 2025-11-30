# Superset Production Fix Guide

## Problem
Superset at `https://superset.insightpulseai.net` is returning 500 errors because:
- Using SQLite instead of PostgreSQL
- Missing `SECRET_KEY` environment variable
- Database not initialized (`no such table: logs`)

## Solution (3 Steps)

### Step 1: Add Environment Variables in DigitalOcean

1. Go to: https://cloud.digitalocean.com/apps
2. Click on **superset-analytics** app
3. Go to **Settings** → **Environment Variables**
4. Click **Edit** → **Bulk Editor**
5. Paste these variables:

```bash
SQLALCHEMY_DATABASE_URI=postgresql://postgres.spdtwktxdalcfigzeqrz:vO1OtibFbuqHJX6WDt6Bhu5mwc9bDERzvvRZw9y31TM=@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require
DATABASE_URL=postgresql://postgres.spdtwktxdalcfigzeqrz:vO1OtibFbuqHJX6WDt6Bhu5mwc9bDERzvvRZw9y31TM=@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require
SECRET_KEY=wsRBfW7Sd_q9EdL3sHztC6bTQTVy0gY9fptjsPZmFkQ
SUPERSET_SECRET_KEY=wsRBfW7Sd_q9EdL3sHztC6bTQTVy0gY9fptjsPZmFkQ
PYTHONUNBUFFERED=1
SUPERSET_ENV=production
SUPERSET_LOAD_EXAMPLES=false
```

6. Click **Save**

### Step 2: Redeploy the App

1. In the same app dashboard, click **Actions** → **Force Rebuild and Deploy**
2. Wait for deployment to complete (~5 minutes)

### Step 3: Initialize Database

1. Go to the app dashboard → **Console** tab
2. Click **Launch Console**
3. Run these commands one by one:

```bash
# 1. Initialize Superset metadata tables
superset db upgrade

# 2. Create admin user
superset fab create-admin \
  --username admin \
  --firstname Admin \
  --lastname User \
  --email admin@insightpulseai.net \
  --password AdminPassword123!

# 3. Initialize roles and permissions
superset init
```

### Step 4: Verify It Works

1. Open: https://superset.insightpulseai.net/login/
2. Login with:
   - **Username**: `admin`
   - **Password**: `AdminPassword123!`
3. Change password immediately after first login

## Expected Result

✅ Superset login page loads without 500 error
✅ Can log in with admin credentials
✅ Superset uses PostgreSQL (Supabase) for metadata
✅ Can create dashboards and connect to Supabase data sources

## Troubleshooting

### If login still fails:
```bash
# Check logs in App Platform → Runtime Logs
# Look for SQLAlchemy connection errors

# If you see "role does not exist":
# The password might have special characters that need URL encoding
```

### If "no such table" errors persist:
```bash
# In Console tab, verify database connection:
superset db upgrade --show-sql-only | head -20

# Should show CREATE TABLE statements
```

### To add Supabase as a data source:
1. Go to **Settings** → **Database Connections** → **+ Database**
2. Choose **PostgreSQL**
3. SQLAlchemy URI:
   ```
   postgresql://postgres.spdtwktxdalcfigzeqrz:vO1OtibFbuqHJX6WDt6Bhu5mwc9bDERzvvRZw9y31TM=@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require
   ```
4. Test Connection → Save

## Security Note

⚠️ The passwords in this document are from `.env.production`.
- Change the Superset admin password after first login
- Consider rotating the Supabase password if this file is committed to Git
- Add `.env.production` to `.gitignore` if not already there

---

**Script Generated**: `scripts/fix-superset-production.sh`
**Date**: 2025-11-27
