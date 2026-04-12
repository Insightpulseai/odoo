# Microsoft Solutions Partner — Canonical Copy

> Source of truth for all Microsoft partnership language across the website,
> sales collateral, email signatures, and badge usage. Microsoft's Partner
> Brand Guide requires qualifying the designation by **solution area** —
> never shorten to "Microsoft Solutions Partner" alone.

**Designation:** Microsoft Solutions Partner for Business Applications

---

## The one-line compliance rule

```text
Always use "Microsoft Solutions Partner for Business Applications," never just "Microsoft Solutions Partner."
```

## ✅ Use

```text
InsightPulseAI is a Microsoft Solutions Partner for Business Applications.
```

## ❌ Do not use

```text
InsightPulseAI is a Microsoft Solutions Partner.
InsightPulseAI is a Microsoft MSP.
InsightPulseAI is an MSP for Microsoft.
```

---

## Paste-ready blocks

### Homepage trust block (minimal)

```html
<section aria-labelledby="microsoft-partner-heading">
  <h3 id="microsoft-partner-heading">Microsoft partnership</h3>
  <p>InsightPulseAI is a Microsoft Solutions Partner for Business Applications.</p>
</section>
```

### Homepage trust block (richer — used on `/`)

```html
<section aria-labelledby="microsoft-partner-heading">
  <h3 id="microsoft-partner-heading">Microsoft partnership</h3>
  <p>
    InsightPulseAI is a Microsoft Solutions Partner for Business Applications.
    We help organizations modernize business applications, operations, and ERP workflows using Microsoft technologies.
  </p>
</section>
```

### Footer copy

```html
<p>InsightPulseAI is a Microsoft Solutions Partner for Business Applications.</p>
```

### About / credibility section

```html
<p>
  InsightPulseAI is a Microsoft Solutions Partner for Business Applications.
  Our work focuses on business-application modernization, AI-enabled operations, and connected enterprise workflows.
</p>
```

### Contact / CTA support line

```html
<p>
  Work with a Microsoft Solutions Partner for Business Applications on ERP, AI, and business-process transformation.
</p>
```

### Email signature line

```text
InsightPulseAI is a Microsoft Solutions Partner for Business Applications.
```

### Badge alt text

```text
Microsoft Solutions Partner for Business Applications badge
```

### Caption under the official badge

```html
<p>InsightPulseAI is a Microsoft Solutions Partner for Business Applications.</p>
```

---

## Badge usage rules

1. **Generate only from Logo Builder** in Partner Center. Do not manufacture or copy from third parties.
2. **Full-color by default.** Use the monochrome variant only where contrast requires it.
3. **Never stretch, recolor, crop, or rebuild** the badge.
4. **Clean background** — no photos, busy patterns, gradients conflicting with the badge.
5. **Preserve clear space** around the badge per the Logo Builder output.
6. **Small-logo lockup** only if the full badge doesn't fit.
7. **Preferred digital placement:** lower left of the page, top-right, or bottom-right.

## Current placements on insightpulseai.com

| Location | Variant | Status |
|---|---|---|
| Homepage Trust & Governance section | Homepage trust block (richer) | ✓ landed [web/ipai-landing/src/App.tsx](../../web/ipai-landing/src/App.tsx) |
| Footer (bottom-left, under company address) | Footer copy | ✓ landed |
| `/features` placeholder page | — | **Blocked** — page shows template text "This is the space to describe the product" on the live site (not served from this repo). Unpublish, redirect, or rewrite before leaning harder into Microsoft-partner branding. |
| About / credibility | About section | Pending — apply when About page is added |
| Contact / CTA | CTA support line | Pending |

## Known blockers

1. **Live `/features` page shows placeholder copy** — source is not in this repo (likely a stale Wix or other off-repo host). Owner action: unpublish, redirect to `/products`, or rewrite the page. Weakens trust if reachable from navigation or search alongside Microsoft-partner branding.
2. **Official badge asset not yet downloaded** — Owner must visit Partner Center → Logo Builder, generate the badge, save to `web/ipai-landing/public/microsoft-partner-badge.png`, then embed via the caption block above.

---

## References

- Microsoft Partner Brand Guide — https://partner.microsoft.com/en-us/marketing/partnerbrandguide (must be logged in)
- Partner Center Logo Builder — https://partner.microsoft.com/en-us/dashboard/ → Benefits → Logos

*Last updated: 2026-04-13*
