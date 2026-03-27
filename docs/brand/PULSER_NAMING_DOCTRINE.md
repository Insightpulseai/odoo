# InsightPulseAI — Pulser Naming Doctrine & Brand Architecture

**Version**: 1.1.0
**Date**: 2026-03-25
**Status**: Approved / Canonical
**Owner**: InsightPulseAI Brand & Product
**SSOT**: `ssot/brand/assistant-brand.yaml`

---

## A. Executive Summary

### Recommendation

**Pulser** becomes the owned assistant family brand for all InsightPulseAI intelligent assistant products. It sits one level below the corporate brand and one level above individual product editions.

**Key decisions:**

1. **Pulser is the master assistant brand** — not a sub-brand, not an internal codename. It is the primary customer-facing name for all AI assistant experiences shipped by InsightPulseAI.
2. **"Odoo Copilot" is retired as a product name.** It uses two third-party marks ("Odoo" trademark of Odoo S.A., "Copilot" trademark of Microsoft) as the primary identity. Replace with **Pulser for Odoo** or simply **Pulser** in ERP context.
3. **"Copilot" is demoted to a generic descriptor**, used only in lowercase descriptive phrases ("copilot-style assistance"), never as a proper noun in product names.
4. **"Odoo" is used only as a compatibility descriptor** — "for Odoo," "works with Odoo," "built on Odoo CE" — never as a lead word in product names.
5. **DIVA becomes Pulser Diva** — DIVA is an owned brand with no third-party conflict. It stays as the orchestration/routing edition name.
6. **W9 Studio becomes Pulser Studio** — clean owned name, no conflicts.
7. **The naming formula is**: `Pulser` + `[Edition]` + optional `for [Platform]`.
8. **All five assistant surfaces get Pulser-family names** with distinct edition identifiers.
9. **Genie stays as Pulser Genie** — "Genie" is generic enough and not a dominant tech trademark in this space.
10. **Document Intelligence stays descriptive** — "Pulser Docs" or "Pulser Document Intelligence" depending on context.

### Naming Architecture at a Glance

```
InsightPulseAI                          ← Corporate brand
  └── Pulser                            ← Assistant family brand
        ├── Pulser (ERP context)        ← ERP assistant (was "Odoo Copilot")
        ├── Pulser Diva                 ← Orchestration shell (was "DIVA Copilot")
        ├── Pulser Studio               ← Creative ops (was "W9 Studio Copilot")
        ├── Pulser Genie                ← Analytics assistant
        └── Pulser Docs                 ← Document intelligence
```

### Why Pulser Works

- **Owned**: No third-party trademark dependency
- **Evocative**: Suggests pulse, rhythm, real-time intelligence — aligned with "InsightPulse"
- **Extensible**: `Pulser [Edition]` scales to any domain
- **Distinct**: Does not overlap with Microsoft Copilot, GitHub Copilot, Salesforce Einstein, or other AI assistant brands
- **Pronounceable**: Works in English, Filipino, and international contexts

---

## B. Naming Doctrine

### Purpose

This doctrine governs how InsightPulseAI names AI assistants, agents, copilots, domain products, and intelligent features across all surfaces — public marketing, product UI, documentation, developer tooling, and marketplace listings.

### Principles

1. **Own the name.** Every customer-facing product name must be built from marks owned by InsightPulseAI. Third-party names appear only as descriptive compatibility labels.

2. **One family, distinct editions.** All intelligent assistant experiences ship under the Pulser family. Each edition has a unique name that signals its domain without requiring explanation.

3. **Platform names are descriptors, not identities.** "Odoo," "Azure," "Databricks," "Slack" may appear as platform descriptors ("for Odoo," "on Azure") but never as the leading word in a product name.

4. **Generic terms stay lowercase.** Words like "assistant," "copilot," "agent," "workspace," "studio" are generic descriptors when used by InsightPulseAI. They appear in lowercase in descriptive text, never capitalized as part of a proper product name (exception: "Studio" in "Pulser Studio" where it functions as an edition name, not the generic word).

5. **Internal names diverge from external names.** Technical module names (`ipai_odoo_copilot`), repository slugs, and YAML keys may use legacy or abbreviated forms. Customer-facing surfaces use only the canonical Pulser-family name.

6. **Future products follow the formula.** Any new intelligent assistant, agent, or domain product must be named `Pulser [Edition]` before launch. No exceptions without Brand review.

### When Third-Party Names May Be Used Descriptively

| Context | Allowed | Example |
|---------|---------|---------|
| Compatibility label | Yes | "Pulser for Odoo" |
| Integration description | Yes | "works with Microsoft Teams" |
| Technical documentation | Yes | "connects to Azure AI Foundry" |
| Architecture diagrams | Yes | "Odoo CE 19 runtime" |
| Marketplace listing subtitle | Yes | "ERP intelligent assistant for Odoo" |

### When Third-Party Names Must Not Appear in Primary Product Name

| Context | Prohibited | Why |
|---------|-----------|-----|
| Product name lead word | "Odoo Copilot" | Implies Odoo S.A. endorsement |
| Feature name with trademark | "Copilot Actions" | Implies Microsoft Copilot affiliation |
| Marketing headline | "The Odoo AI" | Appropriates Odoo brand equity |
| App store primary title | "Odoo Copilot by InsightPulseAI" | Third-party mark dominates |

### How Platform-Specific Variants Are Named

```
Pulser for [Platform]
```

Examples:
- Pulser for Odoo
- Pulser for Teams
- Pulser for Slack
- Pulser for Power BI

The platform name is always a trailing descriptor, never a prefix.

### How Internal Names Differ from Customer-Facing Names

| Layer | Convention | Example |
|-------|-----------|---------|
| Customer-facing product | Pulser [Edition] | Pulser Diva |
| Odoo module technical name | `ipai_[domain]_[feature]` | `ipai_odoo_copilot` |
| YAML/config key | `snake_case` identifier | `pulser_erp`, `odoo_copilot` |
| Azure resource | `ipai-[service]-dev` | `ipai-copilot-gateway` |
| Repository name | `kebab-case` | `pulser-core`, `pulser-studio` |
| npm/pip package | `@insightpulseai/pulser-*` | `@insightpulseai/pulser-sdk` |

Internal technical identifiers do not need to match the customer-facing brand exactly. Renaming infrastructure is lower priority than renaming customer-facing surfaces.

---

## C. Third-Party Brand and Trademark Usage Policy

### Third-Party Brand and Trademark Usage Policy

**Effective**: 2026-03-25
**Scope**: All InsightPulseAI employees, contractors, agents, and automated systems producing customer-facing content.

---

### 1. Purpose

This policy ensures that InsightPulseAI references third-party brands, trademarks, and product names accurately, respectfully, and in compliance with applicable trademark law and partnership agreements. It protects InsightPulseAI from infringement risk while maintaining clear, honest communication about platform compatibility and integrations.

### 2. Scope

Applies to all materials including: product names, UI labels, marketing copy, website pages, documentation, pitch decks, demo scripts, marketplace listings, API documentation, repository names, social media, and automated agent outputs.

### 3. Guiding Principles

1. **Attribution, not appropriation.** Use third-party marks to describe compatibility, not to build our brand identity.
2. **Accuracy.** Use the correct form of a mark (e.g., "Odoo" not "odoo," "Microsoft Copilot" not just "Copilot").
3. **Necessity.** Include a third-party mark only when it adds genuine clarity for the reader.
4. **Subordination.** Our owned brand must always be more prominent than any third-party mark.
5. **Freshness.** Verify current trademark status and usage guidelines annually or when a partner changes their brand.

### 4. Allowed Usage

| Usage Type | Example | Notes |
|-----------|---------|-------|
| Descriptive compatibility | "Pulser for Odoo" | Odoo in smaller/secondary position |
| Integration listing | "Integrates with Slack, Azure, Databricks" | List format, no lead position |
| Technical documentation | "Requires Odoo CE 19.0 or later" | Factual, necessary for setup |
| Architecture description | "Runs on Azure Container Apps" | Technical accuracy |
| Marketplace subtitle | "Intelligent assistant for Odoo ERP" | Below the Pulser product name |
| Attribution footnote | "Odoo is a trademark of Odoo S.A." | Required where marks appear |

### 5. Restricted Usage (Requires Brand Review)

| Usage Type | Example | When Allowed |
|-----------|---------|--------------|
| Co-branded landing page | "InsightPulseAI + Odoo" | Only with written partner agreement |
| Joint logo usage | Odoo logo next to InsightPulseAI logo | Only with written partner agreement |
| Case study naming a partner's product | "How [Customer] uses Pulser with Odoo" | With customer and trademark holder permission |
| Paid search on competitor names | Bidding on "Odoo Copilot" keywords | Legal review required |

### 6. Prohibited Usage

| Usage Type | Example | Why Prohibited |
|-----------|---------|---------------|
| Third-party mark as product name | "Odoo Copilot" | Implies endorsement/affiliation |
| Third-party mark as feature name | "Copilot Actions" | Implies Microsoft branding |
| Modified third-party mark | "OdooPulse," "CopilotAI" | Creates confusing derivative |
| Third-party logo without license | Odoo logo on our sales deck | Requires written permission |
| Implying certification without it | "Certified Odoo Partner" | Only if actually certified |
| Third-party mark in domain name | "odoo-copilot.insightpulseai.com" | Trademark in subdomain |

### 7. Naming Review Workflow

```
1. Proposer drafts name
2. Check against this policy (self-serve)
3. If any third-party mark appears in primary name → STOP, revise
4. If third-party mark in descriptor position → Brand lead reviews
5. If co-branding or joint marketing → Legal counsel reviews
6. Approved names added to naming registry (ssot/brand/naming_registry.yaml)
```

### 8. Examples: Compliant vs Non-Compliant

| Compliant | Non-Compliant | Issue |
|-----------|--------------|-------|
| Pulser for Odoo | Odoo Copilot | Two third-party marks as product name |
| "Built on Odoo CE" | "The Odoo AI Platform" | Appropriates Odoo brand |
| "Copilot-style assistance" (lowercase) | "InsightPulseAI Copilot" | Microsoft trademark as product modifier |
| "Works with Microsoft Teams" | "Teams Copilot by InsightPulseAI" | Two Microsoft marks as identity |
| Pulser Studio | W9 Studio Copilot | "Copilot" in product name |
| "Intelligent assistant" | "AI Copilot" as product category | "Copilot" becoming de facto brand |

### 9. Disclaimer Language Patterns

**Website footer (where third-party marks appear):**
> Odoo is a registered trademark of Odoo S.A. Microsoft, Azure, Copilot, Teams, and Power BI are trademarks of Microsoft Corporation. All other trademarks are the property of their respective owners. InsightPulseAI is not affiliated with or endorsed by Odoo S.A. or Microsoft Corporation.

**Documentation header:**
> Pulser is a product of InsightPulseAI. References to Odoo, Azure, and other third-party products are for compatibility description only and do not imply affiliation or endorsement.

**Demo/deck footnote:**
> Product names referenced herein are trademarks of their respective owners. InsightPulseAI products are independently developed.

**Marketplace listing:**
> Pulser is an independently developed intelligent assistant that works with Odoo CE. Odoo is a trademark of Odoo S.A. This product is not developed, endorsed, or certified by Odoo S.A.

### 10. Microsoft Copilot Referential Allowlist

Microsoft uses "Copilot" in three ways: (1) as a product brand, (2) as a platform/extensibility surface, and (3) in educational content as a pattern word. This does **not** grant permission to brand your own product as "Copilot."

**Allowed referential strings (CI allowlist):**

| String | Context | Example |
|--------|---------|---------|
| `Microsoft Copilot` | Product reference | "Integrates with Microsoft Copilot" |
| `Microsoft 365 Copilot` | Product reference | "Works with Microsoft 365 Copilot" |
| `Security Copilot` | Product reference | "Send to Security Copilot" |
| `GitHub Copilot SDK` | SDK/platform reference | "Built with GitHub Copilot SDK" |
| `GitHub Copilot` | Product reference | "Powered by GitHub Copilot" |
| `copilot-style` | Generic descriptor (lowercase) | "A copilot-style assistant for ERP" |
| `build a copilot` | Educational context (lowercase) | "Learn how to build a copilot experience" |

**Still prohibited as first-party product names:**

| Prohibited | Why |
|-----------|-----|
| `Odoo Copilot` | Two third-party marks as product name |
| `InsightPulse Copilot` | Microsoft trademark as product modifier |
| `Pulser Copilot` | "Copilot" should not appear as product suffix |
| `IPAI Copilot` | First-party brand + Microsoft trademark |

**Governance clause (for automated enforcement):**

> Public-facing first-party AI branding must use Pulser. The term Copilot may appear only in referential usage for Microsoft-owned products, platforms, SDKs, or integrations (for example: Microsoft Copilot, Microsoft 365 Copilot, Security Copilot, GitHub Copilot SDK). Internal technical symbols may retain copilot naming temporarily, but public UI, routes, metadata, APIs, and marketing copy must expose Pulser terminology.

---

## D. Brand Architecture

### Layered Naming Model

```
┌─────────────────────────────────────────────┐
│  Layer 1: Corporate Brand                   │
│  InsightPulseAI                             │
├─────────────────────────────────────────────┤
│  Layer 2: Product Family Brand              │
│  Pulser                                     │
├─────────────────────────────────────────────┤
│  Layer 3: Edition / Domain Name             │
│  Diva | Studio | Genie | Docs | (none=ERP)  │
├─────────────────────────────────────────────┤
│  Layer 4: Platform Descriptor (optional)    │
│  for Odoo | for Teams | on Azure            │
├─────────────────────────────────────────────┤
│  Layer 5: Capability Descriptor (optional)  │
│  Intelligent Assistant | Analytics | Ops    │
└─────────────────────────────────────────────┘
```

### Naming Formula

```
[Pulser] + [Edition?] + [for Platform?]
```

| Full Name | Edition | Platform | Use When |
|-----------|---------|----------|----------|
| Pulser | — | — | Generic/umbrella reference |
| Pulser for Odoo | — | Odoo | ERP assistant, platform-specific context |
| Pulser Diva | Diva | — | Orchestration/routing shell |
| Pulser Studio | Studio | — | Creative ops assistant |
| Pulser Genie | Genie | — | Analytics assistant |
| Pulser Docs | Docs | — | Document intelligence |
| Pulser for Teams | — | Teams | Teams channel delivery |
| Pulser for Slack | — | Slack | Slack channel delivery |

### When to Use Each Layer

| Context | Format |
|---------|--------|
| Website hero | "Pulser — Intelligent Assistant" |
| Product page | "Pulser for Odoo" |
| In-product UI (ERP) | "Pulser" (edition implied by context) |
| In-product UI (analytics) | "Pulser Genie" |
| Marketing one-liner | "InsightPulseAI Pulser" |
| Pitch deck | "InsightPulseAI Pulser" |
| Technical docs | "Pulser for Odoo" or "Pulser (ERP)" |
| Marketplace listing | "Pulser — Intelligent ERP Assistant for Odoo" |
| Internal codename | Any (not customer-visible) |

---

## E. Rename Matrix

### Current Products

#### 1. Odoo Copilot → Pulser (for Odoo)

| Attribute | Value |
|-----------|-------|
| **Current name** | Odoo Copilot |
| **Risk/issues** | "Odoo" (trademark of Odoo S.A.) + "Copilot" (trademark of Microsoft). Dual third-party mark exposure. Implies official Odoo product or Microsoft Copilot variant. Neither is true. |
| **Recommended replacement** | **Pulser** (in ERP context) or **Pulser for Odoo** (when platform clarity needed) |
| **Acceptable fallbacks** | Pulser ERP, Pulser ERP Assistant, InsightPulse Assistant for Odoo |
| **Names to avoid** | Odoo Pulser (Odoo leads), Copilot for Odoo (Microsoft mark leads), OdooPulse (derivative mark) |
| **Rationale** | Removes both third-party marks from the product identity. "for Odoo" as trailing descriptor is nominative fair use — describing what the product works with, not claiming the Odoo brand. |

#### 2. DIVA Copilot → Pulser Diva

| Attribute | Value |
|-----------|-------|
| **Current name** | DIVA Copilot |
| **Risk/issues** | "Copilot" (Microsoft trademark). "DIVA" itself is owned/original — no third-party risk. |
| **Recommended replacement** | **Pulser Diva** |
| **Acceptable fallbacks** | Diva by Pulser, InsightPulse Diva |
| **Names to avoid** | DIVA Copilot (retains Microsoft mark), Diva AI (too generic), CopilotDiva (compound mark) |
| **Rationale** | Drops "Copilot," keeps the distinctive "Diva" name that teams already know. Clean owned name. |

#### 3. W9 Studio Copilot → Pulser Studio

| Attribute | Value |
|-----------|-------|
| **Current name** | W9 Studio Copilot / W9 Studio |
| **Risk/issues** | "Copilot" (Microsoft trademark). "W9" is obscure — low recognition, potential confusion with US tax form W-9. "Studio" alone is generic. |
| **Recommended replacement** | **Pulser Studio** |
| **Acceptable fallbacks** | Pulser Creative, Pulser MediaOps, InsightPulse Studio |
| **Names to avoid** | W9 Studio Copilot (retains Microsoft mark + confusing "W9"), Studio Copilot (generic + Microsoft mark), CreatorPulse (dilutes Pulser family) |
| **Rationale** | "Pulser Studio" is clean, immediately signals creative/production domain, and fits the `Pulser [Edition]` formula. "W9" can remain as an internal codename if teams are attached to it. |

### Three Naming Routes

#### Route A: Conservative / Low-Risk

| Product | Name | Notes |
|---------|------|-------|
| ERP assistant | Pulser for Odoo | Maximum clarity, safe "for" descriptor |
| Orchestration | Pulser Diva | Clean owned name |
| Creative | Pulser Studio | Clean owned name |
| Analytics | Pulser Genie | Clean owned name |
| Documents | Pulser Docs | Clean owned name |
| Landing page | Ask Pulser | Clean owned name |

**Pros**: Zero trademark exposure. Clear. Scalable.
**Cons**: "for Odoo" may feel wordy in some UI contexts.

#### Route B: Balanced / Marketable

| Product | Name | Notes |
|---------|------|-------|
| ERP assistant | Pulser | Context implies ERP |
| Orchestration | Pulser Diva | Same as Route A |
| Creative | Pulser Studio | Same as Route A |
| Analytics | Pulser Genie | Same as Route A |
| Documents | Pulser Docs | Same as Route A |
| Landing page | Ask Pulser | Same as Route A |

**Pros**: Shorter. "Pulser" alone carries the brand. Platform descriptor added only when needed.
**Cons**: Requires context to distinguish ERP from umbrella.

#### Route C: Bold / Premium-Brand

| Product | Name | Notes |
|---------|------|-------|
| ERP assistant | Pulser | The flagship, no qualifier needed |
| Orchestration | Diva | Drops "Pulser" prefix, standalone sub-brand |
| Creative | Studio | Standalone, context does the work |
| Analytics | Genie | Standalone |
| Documents | Docs Intelligence | Standalone |
| Landing page | Pulser | Unified brand |

**Pros**: Maximum brand confidence. Each product stands alone.
**Cons**: Loses family cohesion. "Studio" and "Genie" alone are too generic for search/SEO. Harder to communicate the portfolio.

### Recommendation: **Route B** (Balanced)

Use `Pulser` as the default in ERP context. Use `Pulser [Edition]` for non-ERP surfaces. Add `for [Platform]` only when disambiguation is needed.

---

## F. Final Name Recommendations

### Umbrella Assistant Family

| Option | Pros | Cons | Trademark Risk | Clarity | Extensibility |
|--------|------|------|---------------|---------|--------------|
| **Pulser** | Owned, evocative, short, scales | New name, requires brand-building | None | High | Excellent |
| InsightPulse Assistant | Uses corporate brand directly | Long, corporate-feeling | None | Medium | Good |
| Pulse AI | Short, memorable | "Pulse" is common in tech | Low-medium (crowded space) | Medium | Good |

**Winner: Pulser**

### ERP Assistant (was "Odoo Copilot")

| Option | Pros | Cons | Trademark Risk | Clarity | Extensibility |
|--------|------|------|---------------|---------|--------------|
| **Pulser** (in ERP context) | Clean, short, flagship position | Needs context | None | High in-product | Excellent |
| **Pulser for Odoo** | Explicit platform | Slightly wordy | None (descriptive "for") | Very high | Good |
| Pulser ERP | Domain-clear | "ERP" is jargon | None | Medium | Good |

**Winner: Pulser** (default) / **Pulser for Odoo** (when platform clarity needed)

### Orchestration Assistant (was "DIVA Copilot")

| Option | Pros | Cons | Trademark Risk | Clarity | Extensibility |
|--------|------|------|---------------|---------|--------------|
| **Pulser Diva** | Keeps beloved name, family-consistent | None significant | None | High | Good |
| Diva by InsightPulseAI | Standalone brand feel | Loses Pulser family | None | Medium | Limited |

**Winner: Pulser Diva**

### Creative Assistant (was "W9 Studio Copilot")

| Option | Pros | Cons | Trademark Risk | Clarity | Extensibility |
|--------|------|------|---------------|---------|--------------|
| **Pulser Studio** | Clean, signals creative | "Studio" is common | None | High | Good |
| Pulser Creative | More descriptive | Less punchy | None | High | Good |
| Pulser MediaOps | Technical, specific | Too narrow | None | Medium | Limited |

**Winner: Pulser Studio**

### Analytics Assistant

| Option | Pros | Cons | Trademark Risk | Clarity | Extensibility |
|--------|------|------|---------------|---------|--------------|
| **Pulser Genie** | Memorable, playful | "Genie" used by Databricks | Low (different domain) | High | Good |
| Pulser Analytics | Descriptive | Generic | None | High | Limited |
| Pulser Insight | Ties to corporate brand | Could confuse with parent | None | Medium | Good |

**Winner: Pulser Genie** (note: review Databricks Genie trademark status with counsel)

### Document Intelligence Assistant

| Option | Pros | Cons | Trademark Risk | Clarity | Extensibility |
|--------|------|------|---------------|---------|--------------|
| **Pulser Docs** | Short, clear | Could imply documentation app | None | Medium | Good |
| Pulser Document Intelligence | Very descriptive | Long | Low ("Document Intelligence" used by Azure) | High | Limited |
| Pulser Extract | Action-oriented | Narrow | None | Medium | Limited |

**Winner: Pulser Docs**

### Landing Page Widget

| Option | Pros | Cons | Trademark Risk | Clarity | Extensibility |
|--------|------|------|---------------|---------|--------------|
| **Ask Pulser** | Clean, action-oriented | — | None | High | Good |
| Pulser Assistant | Descriptive | Generic | None | High | Good |

**Winner: Ask Pulser**

---

## G. Usage Rules for "Copilot" and "Odoo"

### Usage Rules for "Copilot"

"Copilot" is a registered trademark of Microsoft Corporation. GitHub Copilot, Microsoft 365 Copilot, and Microsoft Copilot are established products. Using "Copilot" as a proper noun in product names creates confusion and potential infringement.

| Context | Classification | Guidance |
|---------|---------------|----------|
| In product names (e.g., "Pulser Copilot") | **Prohibited** | Never use as part of a product name |
| In feature names (e.g., "Copilot Actions") | **Prohibited** | Use "Pulser Actions" or "AI-assisted actions" |
| In descriptive subtitles | **Avoid** | Prefer "intelligent assistant" or "AI assistant" |
| In UI labels (e.g., button text) | **Avoid** | Use "Ask Pulser," "Assistant," or "AI Help" |
| In documentation (describing our product) | **Avoid** | Use "assistant," "AI assistant," or "Pulser" |
| In documentation (describing Microsoft's product) | **Allowed with caution** | Use full form: "Microsoft Copilot" or "Microsoft 365 Copilot" |
| In SEO/landing page copy | **Avoid** | Do not target "copilot" as a keyword for our product |
| In competitive comparison tables | **Allowed with caution** | Factual comparison only, proper attribution |
| In generic lowercase descriptive text | **Allowed with caution** | "copilot-style experience" (lowercase, descriptive) |
| As internal shorthand | **Allowed** | Internal docs/Slack can say "copilot" casually |

### Usage Rules for "Odoo"

"Odoo" is a registered trademark of Odoo S.A. InsightPulseAI uses Odoo CE (LGPL-3) as a platform. The LGPL license grants code rights, not trademark rights.

| Context | Classification | Guidance |
|---------|---------------|----------|
| In product names (lead position) | **Prohibited** | Never: "Odoo Pulser," "Odoo Assistant" |
| As "for Odoo" (trailing descriptor) | **Preferred** | "Pulser for Odoo" — nominative fair use |
| As "built on Odoo CE" (factual) | **Preferred** | Accurate platform description |
| In Odoo module technical names | **Allowed with caution** | `ipai_odoo_copilot` is internal, acceptable |
| In repo names | **Avoid** | Prefer `pulser-core` over `odoo-copilot` |
| In documentation | **Preferred** | Factual references: "Odoo CE 19.0," "Odoo ERP" |
| In marketplace/integration listings | **Preferred** | "Pulser — Intelligent Assistant for Odoo" |
| In marketing headlines | **Avoid** | Don't lead with "Odoo." Lead with Pulser or InsightPulseAI |
| In UI within Odoo (systray, settings) | **Allowed with caution** | "Pulser" label in systray, settings say "Pulser for Odoo" |
| With Odoo logo | **Restricted** | Requires written permission from Odoo S.A. |
| Claiming "Certified Odoo Partner" | **Prohibited** (unless certified) | Do not claim partnership without agreement |
| In domain names / subdomains | **Prohibited** | No `odoo-copilot.insightpulseai.com` |

---

## H. Canonical Naming Standard

### Grammar

```
[Family Brand] [Edition?] [for Platform?]
```

- **Family Brand**: Always `Pulser` (capitalized, no prefix)
- **Edition**: Capitalized proper noun — `Diva`, `Studio`, `Genie`, `Docs`
- **Platform descriptor**: lowercase `for` + capitalized platform — `for Odoo`, `for Teams`

### Capitalization

| Element | Rule | Example |
|---------|------|---------|
| Pulser | Always capitalized | Pulser |
| Edition name | Capitalized | Pulser Diva |
| Platform descriptor | "for" lowercase, platform capitalized | Pulser for Odoo |
| Generic descriptors | lowercase | "intelligent assistant," "AI-powered" |
| In running text | Capitalize on first use, then natural | "Use Pulser to..." |

### Spacing

- Always a space between words: `Pulser Diva`, never `PulserDiva`
- No hyphens in customer-facing names: `Pulser Studio`, never `Pulser-Studio`
- Hyphens allowed in technical identifiers: `pulser-core`, `pulser-studio`

### Suffix Rules

| Suffix | Use When | Example |
|--------|----------|---------|
| (none) | Default ERP/flagship context | Pulser |
| Edition name | Non-ERP surface | Pulser Diva |
| `for [Platform]` | Platform disambiguation needed | Pulser for Odoo |
| `on [Infrastructure]` | Infrastructure context | Pulser on Azure |
| `+ [Integration]` | Integration highlight | Pulser + Databricks |

### When to Use Each Term

| Term | Use | Do Not Use |
|------|-----|-----------|
| **Assistant** | Generic descriptor for any Pulser surface | As part of a proper product name |
| **Agent** | Technical/architectural context (agent framework) | Customer-facing product name |
| **Copilot** | Never as our product name; only referencing Microsoft's | As our brand |
| **Workspace** | Describing the user's working environment | As a product name |
| **Studio** | Only for Pulser Studio (creative ops) | Generic "studio" for other products |
| **Intelligence** | Describing a capability ("document intelligence") | As a standalone product name |

### Repository / Package / Module Naming

| Layer | Convention | Example |
|-------|-----------|---------|
| Git repo | `pulser-[component]` | `pulser-core`, `pulser-studio` |
| npm package | `@insightpulseai/pulser-[pkg]` | `@insightpulseai/pulser-sdk` |
| Odoo module | `ipai_[domain]_[feature]` (unchanged) | `ipai_odoo_copilot` |
| Python package | `pulser_[component]` | `pulser_gateway` |
| Azure resource | `ipai-[service]-[env]` (unchanged) | `ipai-copilot-gateway` |
| Docker image | `ipai-[service]` (unchanged) | `ipai-website` |
| YAML config key | `pulser_[surface]` or legacy key | `pulser_erp`, `odoo_copilot` |

Note: Internal technical identifiers (Odoo modules, Azure resources, Docker images) do NOT need immediate renaming. Customer-facing surfaces are the priority.

---

## I. Messaging Guide

### Website Hero

> **Pulser — Intelligent Assistant by InsightPulseAI**
> AI-native operations for marketing, media, retail, and financial services. Pulser combines ERP intelligence, AI-assisted workflows, and modern data operations to help teams unify, automate, and scale.

### Product Description (Pulser for Odoo)

> Pulser is an intelligent ERP assistant built on Odoo CE. It helps teams understand records, navigate workflows, summarize activity, and make faster decisions — all from within the platform they already use.

### Product Description (Pulser Diva)

> Pulser Diva is the orchestration layer that routes questions to the right specialist — strategy, operations, tax, governance, or capability — assembling context from across your organization.

### Product Description (Pulser Studio)

> Pulser Studio turns raw and AI-generated assets into finished, publish-ready content. From capture to export, it handles the last-mile creative finishing that slows teams down.

### Integration Page

> Pulser works with your existing stack — Odoo, Azure, Databricks, Slack, Power BI, and more. It connects to the tools you already use without replacing them.
>
> *Odoo is a trademark of Odoo S.A. Pulser is independently developed by InsightPulseAI and is not affiliated with or endorsed by Odoo S.A.*

### Marketplace / App Store Description

> **Pulser — Intelligent ERP Assistant for Odoo**
>
> Pulser helps Odoo users work faster with AI-powered record summaries, workflow guidance, and operational intelligence. Built on Odoo CE 19.0, deployed on Azure.
>
> *Odoo is a registered trademark of Odoo S.A. This product is independently developed by InsightPulseAI.*

### Pitch Deck One-Liner

> InsightPulseAI Pulser: the intelligent assistant platform for ERP, analytics, creative ops, and document intelligence.

### Legal Footnote / Attribution Line

> Pulser is a product of InsightPulseAI. Odoo is a registered trademark of Odoo S.A. Microsoft, Azure, Copilot, Teams, and Power BI are trademarks of Microsoft Corporation. Databricks is a trademark of Databricks, Inc. All other trademarks are the property of their respective owners. InsightPulseAI is not affiliated with or endorsed by any third-party trademark holder referenced herein.

---

## J. Migration Plan

### Phase 1: Immediate (Week 1) — High-Visibility Surfaces

| Action | Files | Priority |
|--------|-------|----------|
| Rename landing page widget from "Ask Odoo Copilot" to "Ask Pulser" | `web/ipai-landing/src/components/AIChatCopilot.tsx` | **P0** |
| Update widget greeting to use Pulser name + doctrine disclosure | `web/ipai-landing/src/components/AIChatCopilot.tsx` | **P0** |
| Rename component file | `AIChatCopilot.tsx` → `AskPulser.tsx` | **P0** |
| Update landing page hero/nav references | `web/ipai-landing/src/App.tsx` | **P0** |
| Update `assistant_surfaces.yaml` naming rules | `ssot/agents/assistant_surfaces.yaml` | **P0** |
| Update `MARKETING_ASSISTANT_DOCTRINE.md` | `docs/architecture/MARKETING_ASSISTANT_DOCTRINE.md` | **P0** |
| Update `ASSISTANT_SURFACES.md` | `docs/architecture/agents/ASSISTANT_SURFACES.md` | **P0** |
| Add trademark disclaimer to website footer | `web/ipai-landing/src/App.tsx` | **P0** |

### Phase 2: Documentation (Week 2) — Architecture & SSOT

| Action | Files | Priority |
|--------|-------|----------|
| Rename in all `docs/architecture/*.md` files | ~25 files | **P1** |
| Rename in all `ssot/agents/*.yaml` files | ~15 files | **P1** |
| Update `README.md` | Root README | **P1** |
| Update Odoo module `__manifest__.py` description | `addons/ipai/ipai_odoo_copilot/__manifest__.py` | **P1** |
| Update Odoo systray XML label | `static/src/xml/copilot_systray.xml` | **P1** |
| Update `CLAUDE.md` references | Root + nested | **P1** |

### Phase 3: Spec Bundles & Governance (Week 3)

| Action | Files | Priority |
|--------|-------|----------|
| Update spec bundle product names | `spec/*/prd.md`, `constitution.md` | **P2** |
| Update governance YAML | `ssot/governance/*.yaml` | **P2** |
| Update eval/benchmark names | `infra/ssot/evals/*.yaml` | **P2** |
| Update agent platform references | `agent-platform/` | **P2** |

### Phase 4: Internal Cleanup (Week 4+)

| Action | Files | Priority |
|--------|-------|----------|
| Update web app UIs (control-room, saas-landing) | `web/*/` | **P3** |
| Update n8n workflow display names | `automations/n8n/workflows/` | **P3** |
| Update Databricks notebook references | `infra/databricks/` | **P3** |
| Archive old names in `archive/` | Historical reference | **P3** |

### What Does NOT Change (Deferred / Internal)

- Odoo module technical name `ipai_odoo_copilot` — rename only if/when module gets a major version bump
- Azure resource names (`ipai-copilot-gateway`) — infrastructure rename is high-risk, low customer visibility
- Git history — unchanged
- YAML config keys — old keys remain as machine identifiers, new aliases added gradually
- Archive directory contents — historical record, leave as-is

### Customer Communication

Since Pulser is currently `internal_beta` with trusted users only, the rename is low-impact externally:

1. Update the landing page (public-facing, immediate)
2. Update in-product UI labels in next Odoo module release
3. No formal "rebrand announcement" needed at this stage — the product hasn't launched publicly under the old name
4. When GA launches, launch as "Pulser" from day one — no migration narrative needed

---

## K. Final Recommended Policy

### One-Page Concise Policy

---

**InsightPulseAI Product Naming Policy**

1. All AI assistant products ship under the **Pulser** family brand.
2. Product names follow the formula: **Pulser** + **[Edition]** + optional **for [Platform]**.
3. Third-party names (Odoo, Microsoft, Copilot, Azure, Databricks) appear only as **trailing compatibility descriptors**, never as lead words in product names.
4. "Copilot" is **never** used as part of an InsightPulseAI product name.
5. "Odoo" appears only as **"for Odoo"** or **"built on Odoo CE"** — descriptive, not branded.
6. Every customer-facing surface where a third-party mark appears must include an **attribution disclaimer**.
7. Source labels are mandatory on all Pulser assistant responses.
8. Internal technical names (module IDs, Azure resources, YAML keys) may differ from customer-facing names.
9. New products must pass **naming review** before launch.
10. This policy is reviewed annually or when a referenced brand changes its trademark guidance.

---

### Decision Table

| Decision | Answer |
|----------|--------|
| Is "Pulser" the master assistant brand? | **Yes** |
| Can we use "Odoo" in product names? | **No** (only as "for Odoo" descriptor) |
| Can we use "Copilot" in product names? | **No** |
| Can we use "Copilot" in UI labels? | **No** (use "Assistant" or "Pulser") |
| Can we use "Copilot" in documentation? | **Only when referencing Microsoft's product** |
| What is the ERP assistant called? | **Pulser** or **Pulser for Odoo** |
| What is the orchestration assistant called? | **Pulser Diva** |
| What is the creative assistant called? | **Pulser Studio** |
| What is the analytics assistant called? | **Pulser Genie** |
| What is the document assistant called? | **Pulser Docs** |
| What is the landing page widget called? | **Ask Pulser** |
| Do we rename Odoo modules now? | **No** — internal technical name, rename at next major version |
| Do we rename Azure resources now? | **No** — infrastructure, low customer visibility |
| Where do we start? | **Landing page widget + architecture docs + SSOT YAML** |

### Final Recommendation Summary

**Adopt Pulser as the owned assistant family brand immediately.** Rename customer-facing surfaces in a 4-week phased rollout starting with the landing page and architecture documentation. Defer internal technical identifier renaming. Apply the Third-Party Trademark Usage Policy to all new content from this date forward. Review with trademark counsel before any co-branded marketing or marketplace listing that uses the Odoo or Microsoft marks prominently.

The naming architecture is designed to scale. As InsightPulseAI adds new domains (HR, supply chain, legal), each gets a `Pulser [Edition]` name without touching the core brand or creating new trademark dependencies.

---

*This document is practical brand guidance, not formal legal advice. Consult qualified trademark counsel for definitive legal opinions on trademark usage, registration, and enforcement.*

---

## L. Phase 1 Rollout Scope (Complete — 2026-03-25)

### Canonical Names Table

| Surface | Canonical Name | UI Label | Compact | Legacy (Deprecated) |
|---------|---------------|----------|---------|---------------------|
| ERP assistant | **Pulser** | Pulser | Pulser | Odoo Copilot |
| ERP assistant (explicit) | **Pulser for Odoo** | Pulser | Pulser | Odoo Copilot |
| Orchestration shell | **Pulser Diva** | Diva | Diva | DIVA Copilot |
| Creative ops | **Pulser Studio** | Studio | Studio | W9 Studio Copilot |
| Analytics | **Pulser Genie** | Genie | Genie | Genie |
| Document intelligence | **Pulser Docs** | Docs | Docs | Document Intelligence |
| Landing page widget | **Ask Pulser** | Ask Pulser | Ask Pulser | Ask Odoo Copilot |

### Spelling Rule

**Pulser** is the only accepted spelling. **Pulsar** is deprecated and must not appear as an active brand reference. The `ssot/brand/assistant-brand.yaml` registry lists "Pulsar" under `deprecated_spellings`.

### Phase 1 Deliverables (All Complete)

- [x] Landing page widget renamed: `AskPulser.tsx` (was `AIChatCopilot.tsx`)
- [x] Landing page title: "InsightPulse AI — Pulser Intelligent Assistant"
- [x] App.tsx: all UI labels say "Pulser"
- [x] Server gateway: `/api/pulser/chat` (canonical) + `/api/copilot/chat` (legacy redirect)
- [x] Mock responses include `sourceLabel` per Marketing Assistant Doctrine
- [x] SSOT brand registry: `ssot/brand/assistant-brand.yaml`
- [x] SSOT assistant surfaces: `ssot/agents/assistant_surfaces.yaml` v2.0.0
- [x] Architecture docs: `ASSISTANT_SURFACES.md`, `MARKETING_ASSISTANT_DOCTRINE.md`
- [x] This naming doctrine: marked Approved / Canonical
- [x] Migration map: `docs/brand/NAME_MIGRATION_MAP.md`

### Phase 2 Remaining (see `NAME_MIGRATION_MAP.md`)

- ~20 remaining `docs/architecture/*.md` files
- Spec bundles, governance YAML, agent platform references
- Web apps: `web/saas-landing/`, `web/web/public/odoo-copilot-cards-*.html`
- Odoo module `__manifest__.py` description + systray XML label
- n8n workflow display names, Databricks notebook references

---

**SSOT References:**
- Brand registry: `ssot/brand/assistant-brand.yaml`
- Assistant surfaces: `ssot/agents/assistant_surfaces.yaml`
- Migration map: `docs/brand/NAME_MIGRATION_MAP.md`
- Marketing doctrine: `docs/architecture/MARKETING_ASSISTANT_DOCTRINE.md`
- Trademark policy: This document, Section C
