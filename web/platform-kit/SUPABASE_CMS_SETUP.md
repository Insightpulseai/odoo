# Supabase CMS Implementation

**Project**: platform-kit
**Supabase Project**: spdtwktxdalcfigzeqrz
**Status**: Ready for deployment

## Overview

Complete functional CMS built on Supabase with:
- Full database schema (posts, categories, tags)
- REST API via Edge Functions
- TypeScript client library
- React components
- RLS policies for security
- Sample data for testing

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Next.js App (platform-kit)                     │
│  ├─ lib/supabase-cms.ts (Client)               │
│  ├─ app/api/cms/route.ts (API Routes)          │
│  └─ components/cms-example.tsx (UI)            │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  Supabase Project (spdtwktxdalcfigzeqrz)        │
│  ├─ Edge Function: posts-api                    │
│  │  └─ CRUD operations + filtering              │
│  └─ PostgreSQL Database                         │
│     ├─ cms_posts                                │
│     ├─ cms_categories                           │
│     ├─ cms_tags                                 │
│     ├─ cms_post_categories (many-to-many)      │
│     └─ cms_post_tags (many-to-many)            │
└─────────────────────────────────────────────────┘
```

## Database Schema

### Tables

**cms_posts**
- id (UUID, primary key)
- title, slug (unique), content, excerpt
- author, published_at, status
- seo_title, seo_description
- featured_image
- created_at, updated_at

**cms_categories**
- id (UUID, primary key)
- name (unique), slug (unique)
- description

**cms_tags**
- id (UUID, primary key)
- name (unique), slug (unique)

**cms_post_categories** (many-to-many)
**cms_post_tags** (many-to-many)

### Security (RLS Policies)

- ✅ Public read for published posts
- ✅ Public read for categories/tags
- ✅ Authenticated users manage all content
- ✅ Draft posts hidden from public

## Deployment

### Quick Deploy

```bash
cd apps/platform-kit
./scripts/deploy-cms.sh
```

### Manual Steps

1. **Run Database Migration**
```bash
supabase link --project-ref spdtwktxdalcfigzeqrz
supabase db push
```

2. **Deploy Edge Function**
```bash
supabase functions deploy posts-api --no-verify-jwt
```

3. **Set Function Secrets**
```bash
supabase secrets set \
  SUPABASE_URL="https://spdtwktxdalcfigzeqrz.supabase.co" \
  SUPABASE_ANON_KEY="your_anon_key"
```

4. **Load Sample Data** (optional)
```bash
psql "$SUPABASE_DB_URL" < supabase/seed.sql
```

## API Endpoints

**Base URL**: `https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/posts-api`

### Get All Posts
```bash
GET /posts-api?page=1&perPage=10&category=news&tag=nextjs&search=typescript
```

### Get Single Post
```bash
GET /posts-api/{slug}
```

### Create Post
```bash
POST /posts-api
Content-Type: application/json
Authorization: Bearer {service_role_key}

{
  "title": "My Post",
  "slug": "my-post",
  "content": "Post content...",
  "excerpt": "Short description",
  "author": "Author Name",
  "status": "published"
}
```

### Update Post
```bash
PUT /posts-api/{id}
Content-Type: application/json
Authorization: Bearer {service_role_key}

{
  "title": "Updated Title",
  "content": "Updated content..."
}
```

### Delete Post
```bash
DELETE /posts-api/{id}
Authorization: Bearer {service_role_key}
```

## Client Usage

### TypeScript Client

```typescript
import { cms } from '@/lib/supabase-cms'

// Get all posts
const { data: posts, pagination } = await cms.getPosts({
  page: 1,
  perPage: 10,
  category: 'news',
  tag: 'nextjs'
})

// Get single post
const { data: post } = await cms.getPost('my-post-slug')

// Create post
const { data: newPost } = await cms.createPost({
  title: 'New Post',
  slug: 'new-post',
  content: 'Content here...',
  status: 'published'
})

// Search posts
const { data: results } = await cms.searchPosts('typescript')
```

### React Component

```tsx
import { CMSExample } from '@/components/cms-example'

export default function BlogPage() {
  return <CMSExample category="tutorials" />
}
```

### Next.js API Route

```typescript
// GET /api/cms?category=news
const response = await fetch('/api/cms?category=news')
const { data: posts } = await response.json()
```

## Configuration

### Environment Variables (.env)

```bash
# Supabase CMS (uses canonical project)
SUPABASE_CMS_URL=https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/posts-api
SUPABASE_CMS_API_KEY=${SUPABASE_SERVICE_ROLE_KEY}
```

## Files Created

```
apps/platform-kit/
├── lib/
│   └── supabase-cms.ts              # TypeScript client (138 lines)
├── app/api/cms/
│   └── route.ts                     # Next.js API routes
├── components/
│   └── cms-example.tsx              # Example React component
├── supabase/
│   ├── migrations/
│   │   └── 20260211_cms_schema.sql  # Database schema
│   ├── functions/posts-api/
│   │   └── index.ts                 # Edge Function (265 lines)
│   └── seed.sql                     # Sample data
├── scripts/
│   └── deploy-cms.sh                # Deployment script
├── .env                             # Configuration (updated)
└── README.md                        # Documentation (updated)
```

## Features

✅ **Full CRUD Operations**
- Create, read, update, delete posts
- Category and tag management
- Many-to-many relationships

✅ **Advanced Querying**
- Pagination
- Category filtering
- Tag filtering
- Full-text search
- Sort by publish date

✅ **SEO Optimization**
- SEO title and description
- Slug-based URLs
- Meta information

✅ **Security**
- Row Level Security (RLS)
- Public read for published content
- Auth required for content management
- Draft posts hidden from public

✅ **Developer Experience**
- TypeScript types
- React components
- API routes
- Error handling
- CORS support

## Testing

### Test API Directly

```bash
# List all posts
curl https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/posts-api

# Get specific post
curl https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/posts-api/getting-started-supabase-cms

# Create post (requires service role key)
curl -X POST https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/posts-api \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","slug":"test","content":"Test content","status":"published"}'
```

### Test via Next.js App

```bash
# Start dev server
npm run dev

# Test API route
curl http://localhost:3000/api/cms

# View in browser
open http://localhost:3000
```

## Resources

- **Supabase CMS**: https://www.supabase-cms.com
- **Documentation**: https://www.supabase-cms.com/docs
- **Supabase Docs**: https://supabase.com/docs
- **Edge Functions**: https://supabase.com/docs/guides/functions
- **RLS**: https://supabase.com/docs/guides/auth/row-level-security

## Next Steps

1. ✅ Deploy database schema
2. ✅ Deploy Edge Function
3. ✅ Test API endpoints
4. ⬜ Create admin UI for content management
5. ⬜ Add image upload functionality
6. ⬜ Implement draft/preview mode
7. ⬜ Add comment system (optional)
8. ⬜ Set up webhooks for notifications

## Support

For issues or questions:
- Project: platform-kit
- Supabase Project: spdtwktxdalcfigzeqrz
- Documentation: This file
