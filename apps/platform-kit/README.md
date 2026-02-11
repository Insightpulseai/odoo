# Platform Kit AI

*Automatically synced with your [v0.app](https://v0.app) deployments*

[![Deployed on Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-black?style=for-the-badge&logo=vercel)](https://vercel.com/tbwa/v0-fix-script-error)
[![Built with v0](https://img.shields.io/badge/Built%20with-v0.app-black?style=for-the-badge)](https://v0.app/chat/Wqls9Agiefs)

## Overview

This repository will stay in sync with your deployed chats on [v0.app](https://v0.app).
Any changes you make to your deployed app will be automatically pushed to this repository from [v0.app](https://v0.app).

## Deployment

Your project is live at:

**[https://vercel.com/tbwa/v0-fix-script-error](https://vercel.com/tbwa/v0-fix-script-error)**

## Build your app

Continue building your app on:

**[https://v0.app/chat/Wqls9Agiefs](https://v0.app/chat/Wqls9Agiefs)**

## How It Works

1. Create and modify your project using [v0.app](https://v0.app)
2. Deploy your chats from the v0 interface
3. Changes are automatically pushed to this repository
4. Vercel deploys the latest version from this repository

## Content Management

This project includes a functional [Supabase CMS](https://www.supabase-cms.com) for managing content.

### Quick Setup

**Automatic deployment** (recommended):
```bash
cd apps/platform-kit
./scripts/deploy-cms.sh
```

This will:
- Link to Supabase project `spdtwktxdalcfigzeqrz`
- Create CMS database schema (posts, categories, tags)
- Deploy `posts-api` Edge Function
- Configure environment variables

**Manual setup**:
```bash
# 1. Run migrations
supabase db push

# 2. Deploy Edge Function
supabase functions deploy posts-api --no-verify-jwt

# 3. Configure .env (already set to correct project)
SUPABASE_CMS_URL=https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/posts-api
SUPABASE_CMS_API_KEY=${SUPABASE_SERVICE_ROLE_KEY}
```

2. Use the CMS client in your code:
```typescript
import { cms } from '@/lib/supabase-cms'

// Get all posts
const { data: posts } = await cms.getPosts()

// Get posts by category
const { data: newsPosts } = await cms.getPostsByCategory('news')

// Search posts
const { data: results } = await cms.searchPosts('Next.js')
```

3. Or use the API route:
```typescript
// GET /api/cms?category=news&page=1&perPage=10
const response = await fetch('/api/cms?category=news')
const { data: posts } = await response.json()
```

### Features

- ✅ REST API client (`lib/supabase-cms.ts`)
- ✅ API route (`app/api/cms/route.ts`)
- ✅ Example component (`components/cms-example.tsx`)
- ✅ TypeScript types for posts and responses
- ✅ SEO metadata support
- ✅ Category and tag filtering
- ✅ Pagination
- ✅ Full CRUD operations

### Resources

- **[Supabase CMS Documentation](https://www.supabase-cms.com/docs)** - Complete API reference
- **[Supabase CMS](https://www.supabase-cms.com)** - Open-source CMS powered by Supabase and AI
