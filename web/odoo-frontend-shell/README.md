# Odoo Frontend Shell

Decoupled Next.js 15 frontend for Odoo CE 18 with TBWA branding.

## Features

- ✅ **Decoupled Architecture**: Standalone React/Next.js app connecting to Odoo backend via JSON-RPC
- ✅ **Authentication**: Session-based auth with Odoo backend
- ✅ **TBWA Branding**: Custom UI with TBWA design tokens (black/yellow palette)
- ✅ **TypeScript**: Full type safety
- ✅ **State Management**: Zustand for auth, TanStack Query for data fetching
- ✅ **Tailwind CSS**: Utility-first styling

## Architecture

```
Next.js Frontend (Port 3001)
    ↓ JSON-RPC API
Odoo CE 18 Backend (Port 8069)
    ↓
PostgreSQL Database
```

## Getting Started

### Option 1: Vercel Sandbox (Recommended)

**Instant deployment with zero setup:**

```bash
# From project root
cd apps/odoo-frontend-shell
vercel deploy --sandbox
```

Or use Vercel CLI:
```bash
vercel link
vercel deploy --sandbox
```

**Vercel Sandbox URL**: Auto-generated shareable preview URL

### Option 2: Local Development

#### 1. Install Dependencies

```bash
cd apps/odoo-frontend-shell
pnpm install
```

#### 2. Configure Environment

```bash
cp .env.example .env.local
```

Edit `.env.local`:

```env
# Local development
NEXT_PUBLIC_ODOO_URL=http://localhost:8069
NEXT_PUBLIC_ODOO_DB=odoo_dev

# Production
# NEXT_PUBLIC_ODOO_URL=https://erp.insightpulseai.com
# NEXT_PUBLIC_ODOO_DB=odoo
```

#### 3. Start Development Server

```bash
pnpm dev
```

Open http://localhost:3001

### Login Credentials

Use your Odoo backend credentials:
- **Username**: admin (or your Odoo username)
- **Password**: Your Odoo password

## Project Structure

```
apps/odoo-frontend-shell/
├── src/
│   ├── app/               # Next.js App Router
│   │   ├── page.tsx       # Login page
│   │   ├── layout.tsx     # Root layout
│   │   └── globals.css    # Global styles
│   ├── components/        # React components
│   │   └── LoginForm.tsx  # Login form component
│   └── lib/               # Utilities and clients
│       ├── odoo-client.ts # Odoo JSON-RPC client
│       └── auth-store.ts  # Auth state management
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.ts
```

## Odoo Client API

### Authentication

```typescript
import { getOdooClient } from '@/lib/odoo-client';

const client = getOdooClient();
const session = await client.authenticate('admin', 'password');
```

### CRUD Operations

```typescript
// Search and read records
const partners = await client.searchRead(
  'res.partner',
  [['is_company', '=', true]],
  ['name', 'email', 'phone'],
  { limit: 10 }
);

// Create record
const partnerId = await client.create('res.partner', {
  name: 'New Partner',
  email: 'partner@example.com',
});

// Update record
await client.write('res.partner', [partnerId], {
  phone: '+1234567890',
});

// Delete record
await client.unlink('res.partner', [partnerId]);
```

### Search Domains

```typescript
// Simple search
await client.search('res.partner', [['country_id.code', '=', 'PH']]);

// Complex search with operators
await client.search('res.partner', [
  '|',
  ['name', 'ilike', 'TBWA'],
  ['email', 'ilike', '@tbwa-smp.com'],
]);
```

## Auth Store (Zustand)

```typescript
import { useAuthStore } from '@/lib/auth-store';

function MyComponent() {
  const { session, isAuthenticated, login, logout } = useAuthStore();

  const handleLogin = async () => {
    await login('admin', 'password');
  };

  return (
    <div>
      {isAuthenticated ? (
        <p>Logged in as: {session?.username}</p>
      ) : (
        <button onClick={handleLogin}>Login</button>
      )}
    </div>
  );
}
```

## TBWA Design Tokens

### Tailwind Classes

```tsx
// TBWA Black (Primary)
<button className="bg-tbwa-black text-white">Button</button>

// TBWA Yellow (Accent)
<div className="bg-tbwa-yellow text-black">Highlight</div>

// TBWA Gray (Background)
<div className="bg-tbwa-gray">Container</div>
```

### CSS Variables

```css
:root {
  --tbwa-black: #000000;
  --tbwa-yellow: #FFED00;
  --tbwa-gray: #f8f9fa;
}
```

## Deployment Options

### Vercel Sandbox (Quick Preview)

**Best for**: Testing, demos, stakeholder review

```bash
# One-time sandbox deployment
vercel deploy --sandbox

# View deployment
vercel ls
```

Features:
- ✅ Instant shareable URL
- ✅ Automatic HTTPS
- ✅ No infrastructure setup
- ✅ Preview environment variables
- ⚠️ Temporary (30 days, extendable)

### Vercel Production

**Best for**: Production use

```bash
# Link project
vercel link

# Deploy to production
vercel --prod
```

Environment variables (set via Vercel dashboard):
```env
NEXT_PUBLIC_ODOO_URL=https://erp.insightpulseai.com
NEXT_PUBLIC_ODOO_DB=odoo
```

### Docker Deployment

**Best for**: Self-hosted, on-premise

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --production
COPY . .
RUN npm run build
EXPOSE 3001
CMD ["npm", "start"]
```

```bash
docker build -t odoo-frontend-shell .
docker run -p 3001:3001 \
  -e NEXT_PUBLIC_ODOO_URL=https://erp.insightpulseai.com \
  -e NEXT_PUBLIC_ODOO_DB=odoo \
  odoo-frontend-shell
```

## CORS Configuration (Odoo Backend)

Add to Odoo `odoo.conf`:

```ini
[options]
# Allow CORS for frontend shell
xmlrpc_interface = 0.0.0.0
longpolling_port = 8072
proxy_mode = True

# CORS headers
# Configure via nginx reverse proxy
```

**Nginx CORS config** (`/etc/nginx/sites-available/odoo`):

```nginx
location / {
    proxy_pass http://localhost:8069;

    # CORS headers
    add_header 'Access-Control-Allow-Origin' 'http://localhost:3001' always;
    add_header 'Access-Control-Allow-Credentials' 'true' always;
    add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
    add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization' always;

    if ($request_method = 'OPTIONS') {
        return 204;
    }
}
```

## Next Steps

1. **Dashboard Page**: Create `/dashboard` route with Odoo data
2. **Protected Routes**: Add authentication middleware
3. **Data Hooks**: Create custom hooks for common Odoo models
4. **UI Components**: Build reusable components (DataGrid, Form, etc.)
5. **Offline Support**: Add PWA capabilities with service workers

## Troubleshooting

### CORS Errors

Ensure Odoo backend allows CORS requests:
- Configure nginx reverse proxy with CORS headers
- Set `proxy_mode = True` in `odoo.conf`

### Session Expires

Sessions are cookie-based. Ensure:
- `withCredentials: true` in axios config
- Same domain or proper CORS credentials

### Connection Refused

Check:
- Odoo backend is running on configured port
- `NEXT_PUBLIC_ODOO_URL` matches backend URL
- No firewall blocking connections

## License

LGPL-3.0 (aligned with Odoo CE)
