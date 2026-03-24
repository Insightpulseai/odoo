# InsightPulseAI Landing Site

> Build/deploy authority for the public marketing site at `insightpulseai.com`.
> Deployed to Azure Container Apps (`ipai-website-dev`) via ACR cloud build.

---

## Local Development

**Prerequisites:** Node.js >= 18

```bash
npm install
npm run dev        # Vite dev server with HMR on http://localhost:3100
```

Production mode (serves from `dist/`):

```bash
npm run build
NODE_ENV=production npx tsx server.ts    # http://localhost:3000
```

## Build

```bash
npx vite build
```

Output: `dist/` (static assets + `index.html`)

## Deploy

### 1. Build image via ACR (cloud build)

```bash
az acr build --registry acripaiodoo \
  --image ipai-website:latest \
  --image ipai-website:$(date +%Y%m%d-%H%M) \
  --file Dockerfile . \
  --platform linux/amd64
```

### 2. Deploy to Azure Container Apps

```bash
az containerapp update \
  --name ipai-website-dev \
  --resource-group rg-ipai-dev-odoo-runtime \
  --image acripaiodoo.azurecr.io/ipai-website:latest
```

### 3. Purge CDN cache

```bash
az afd endpoint purge \
  --resource-group rg-ipai-dev-platform \
  --profile-name ipai-fd-dev \
  --endpoint-name ipai-fd-dev-ep \
  --content-paths '/*' \
  --domains www.insightpulseai.com insightpulseai.com
```

### 4. Verify

```bash
# Title check (origin)
curl -s https://ipai-website-dev.salmontree-b7d27e19.southeastasia.azurecontainerapps.io/ \
  | grep -o '<title>[^<]*</title>'

# Pulser API check
curl -s -X POST https://www.insightpulseai.com/api/pulser/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What is Pulser?","sessionId":"test","context":{"surface":"landing_page"}}' \
  | python3 -m json.tool | head -20
```

## Post-Deploy Verification Checklist

- [ ] Title: `InsightPulseAI — AI-native operations for marketing, media, retail, and financial services`
- [ ] Pulser API returns structured `ctas[]`
- [ ] CSS MIME: `text/css` (not `text/html`)
- [ ] No `Get Started` on public surface
- [ ] No `Request a Demo` (canonical: `Book Demo`)
- [ ] No `Trust & Readiness` (canonical: `Trust Center`)
- [ ] No `Analytics` alone (canonical: `Analytics & Dashboards`)
- [ ] No `Odoo Copilot` remaining
- [ ] Marquee rail animates continuously

## Architecture

- **Runtime:** Express + Vite (production serves static `dist/`)
- **Container:** `node:22-alpine`, port 3000
- **Registry:** `acripaiodoo.azurecr.io/ipai-website`
- **ACA:** `ipai-website-dev` in `rg-ipai-dev-odoo-runtime`
- **Edge:** Azure Front Door (`ipai-fd-dev`)
- **Domains:** `insightpulseai.com`, `www.insightpulseai.com`

## Governance

See `docs/governance/DOCTRINE_PRECEDENCE.md` for the 20-file governance chain.

3 mandatory docs before any Ask Pulser change:
1. `docs/architecture/MARKETING_ASSISTANT_DOCTRINE.md`
2. `docs/brand/PULSER_NAMING_DOCTRINE.md`
3. `docs/audits/WEBSITE_BRANDING_ROUTE_AUDIT.md`
