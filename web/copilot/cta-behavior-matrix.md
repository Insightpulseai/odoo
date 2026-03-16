# Copilot CTA Behavior Matrix

> Version: 1.0.0
> Last updated: 2026-03-15
> Owner: web repo
> Reference: infra/docs/architecture/PUBLISHABILITY_GATES.md

## Purpose

Defines the correct CTA (Call to Action) behavior for the Copilot product page and embedded widget. Every CTA must route to a real, working endpoint.

## CTA Rules

1. **No fake sign-up links** — Do not link to a sign-up page that doesn't exist
2. **No false "try now" buttons** — If there's no self-serve trial, route to demo request
3. **No pricing pages without pricing** — Route to "contact for pricing" instead
4. **No live demo without live demo** — Route to "request demo" form
5. **Every CTA must have a working destination** — Validated before publish

## CTA Routing Table

| User Intent | Current CTA | Destination | Status |
|-------------|-------------|-------------|--------|
| Try the product | "Request Demo" | /contact?action=demo | Pending validation |
| See pricing | "Contact for Pricing" | /contact?action=pricing | Pending validation |
| Get support | "Contact Support" | /support | Pending validation |
| Learn more | "View Features" | /copilot/features | Pending validation |
| Sign up | "Request Demo" (redirected) | /contact?action=demo | No self-serve yet |

## Unsupported CTAs (Must Not Appear)

- "Sign Up Now" — No self-serve sign-up exists
- "Start Free Trial" — No self-serve trial exists
- "Buy Now" — No self-serve purchase exists
- "Try Live Demo" — No live demo environment exists (yet)
- "Download" — Not a downloadable product

## Validation Required Before Publish

For each CTA:
1. URL exists and returns HTTP 200
2. Form submission works end-to-end
3. Notification reaches sales/support team
4. Thank-you page renders correctly
5. No broken links on mobile
