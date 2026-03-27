# Deep Research Report: Google OAuth Verification & Agent Skills Architecture

> Research date: 2026-03-27
> Researcher: Claude Opus 4.6 (1M context)
> Confidence: HIGH (85%+) for OAuth verification, HIGH (90%+) for agent skills architecture
> Scope: InsightPulseAI Gmail Add-on compliance + knowledge base design

---

## Executive Summary

This report covers two interconnected topics: (1) the Google OAuth app verification process as it applies to the InsightPulseAI Gmail add-on, and (2) the architecture for building a cross-platform agent skills knowledge base. The key findings are:

**OAuth Verification**: The add-on's single sensitive scope (`gmail.readonly`) is likely removable, which would eliminate the entire sensitive-scope verification process. For internal/org-only deployment within a Google Workspace domain, no verification is needed at all -- even for sensitive and restricted scopes. The recommended path is: deploy internally first (zero verification), then test `gmail.readonly` removal, then consider public publishing only if needed.

**Agent Skills**: The repo already has a mature skill contract system (`agents/skills/schema/skill.schema.json`) with 80+ skills. The Vercel `npx skills` standard and the `gws` CLI skills format are the two dominant external patterns. Cross-platform compatibility (Claude, Gemini, Codex, Cursor) is achieved through the SKILL.md file convention. The knowledge base should organize around the existing `agents/skills/` directory with progressive disclosure for context efficiency.

---

## Part 1: Google OAuth App Verification

### 1.1 Verification Tier System

Google classifies OAuth scopes into three tiers, each with increasing verification requirements:

| Tier | Examples | Verification Required | Timeline | Cost |
|------|----------|----------------------|----------|------|
| **Non-sensitive** | `userinfo.email`, `script.locale`, `gmail.addons.*` | None (brand verification only) | Instant | Free |
| **Sensitive** | `gmail.readonly`, `calendar.events`, `drive.file` | OAuth verification: video demo + scope justification + privacy policy | 3-6 weeks | Free |
| **Restricted** | `gmail.modify`, `mail.google.com`, `drive` (full) | OAuth verification + CASA security assessment + annual recertification | 4-8+ weeks initial, annual renewal | $500-$4,500/year (CASA assessor fee) |

### 1.2 Our Scope Classification

| Scope | Full URI | Tier | Verification | Notes |
|-------|----------|------|-------------|-------|
| `gmail.readonly` | `googleapis.com/auth/gmail.readonly` | **SENSITIVE** | Video demo + justification | **Likely removable** -- see 1.3 |
| `gmail.addons.current.message.readonly` | `googleapis.com/auth/gmail.addons.current.message.readonly` | Non-sensitive | None | Required: contextual trigger reads current message |
| `gmail.addons.current.action.compose` | `googleapis.com/auth/gmail.addons.current.action.compose` | Non-sensitive | None | Required: compose actions from sidebar |
| `script.external_request` | `googleapis.com/auth/script.external_request` | Non-sensitive | None | Required: `UrlFetchApp` calls to Odoo |
| `script.locale` | `googleapis.com/auth/script.locale` | Non-sensitive | None | Required: `useLocaleFromApp: true` |
| `gmail.addons.execute` | `googleapis.com/auth/gmail.addons.execute` | Non-sensitive | None | Required: add-on execution framework |
| `userinfo.email` | `googleapis.com/auth/userinfo.email` | Non-sensitive | None | Required: user identification |

**Result**: 6 of 7 scopes are non-sensitive. Only `gmail.readonly` triggers verification.

### 1.3 Decision Tree for Our Gmail Add-on

```
START: What is the deployment target?
  |
  +-- INTERNAL (org-only, e.g., w9studio.net Workspace)
  |     |
  |     +-- Does the Workspace have a paid edition (Business Starter+)?
  |           |
  |           +-- YES --> Deploy as Private app in Marketplace SDK
  |           |           * No Google review needed
  |           |           * No OAuth verification needed (even for sensitive/restricted scopes)
  |           |           * Available immediately to domain users
  |           |           * OAuth consent screen set to "Internal"
  |           |           * RECOMMENDED PATH FOR V1
  |           |
  |           +-- NO (free Workspace / personal Gmail)
  |                 * Cannot use internal Marketplace
  |                 * Must use External OAuth consent screen
  |                 * Falls through to PUBLIC path below
  |
  +-- PUBLIC (anyone on Marketplace)
        |
        +-- Can gmail.readonly be removed?
              |
              +-- YES (test confirms gmail.addons.current.message.readonly is sufficient)
              |     * ALL scopes are non-sensitive
              |     * Only brand verification needed (domain, privacy policy, logo)
              |     * Timeline: 3-7 business days for Marketplace review
              |     * No video demo, no scope justification
              |     * BEST PUBLIC PATH
              |
              +-- NO (gmail.readonly is required)
                    * Sensitive scope verification triggered
                    * Requirements:
                    *   - Video demo (unlisted YouTube)
                    *   - Written scope justification
                    *   - Privacy policy on verified domain
                    *   - Homepage with visible privacy policy link
                    * Timeline: 4-10 weeks combined
                    * No CASA (no restricted scopes)
```

### 1.4 Internal-Only App Path (Recommended for V1)

For apps deployed only within a Google Workspace organization, the verification burden is zero. Here is what "internal" means precisely:

**Requirements**:
1. The GCP project must be owned by an account in the target Google Workspace domain
2. The OAuth consent screen must be configured with User Type = "Internal"
3. The Google Workspace must be a paid edition (Business Starter, Standard, Plus, Enterprise, Education, or Nonprofits)

**What you get**:
- No unverified app warning screen for domain users
- No 100-user test cap
- No Google review or OAuth verification, even for sensitive and restricted scopes
- Immediate availability after publishing as Private in Marketplace SDK
- Admin can force-install for all domain users via Marketplace admin settings

**What you do NOT get**:
- Users outside the Workspace domain cannot install the app
- Cannot list on public Marketplace
- Cannot share with external partners (unless they are added to the Workspace domain)

**Exact steps for InsightPulseAI**:
1. Create a standard GCP project from a `w9studio.net` Workspace account
2. Link the Apps Script project (script ID `1QaH14jbBl7PcvjLXgkzZogh6SzqS_kXoTJ_MzzmavW6CRLMANG24Ko4q`) to that GCP project
3. Set OAuth consent screen to "Internal"
4. Enable Gmail API, Apps Script API, Workspace Marketplace SDK, Workspace Add-ons API
5. Configure Marketplace SDK: visibility = Private, integration = Apps Script, deployment ID from `clasp deploy`
6. Fill store listing (name, description, icons, screenshots, privacy policy URL)
7. Publish -- immediately available to all `w9studio.net` users

### 1.5 Security Assessment (CASA) -- When It Applies

CASA is only triggered by **restricted** scopes. None of our current scopes are restricted. For reference:

**Restricted Gmail scopes** (would trigger CASA if added):
- `mail.google.com` (full mailbox access)
- `gmail.modify` (read + modify + delete)
- `gmail.compose` (full compose, not just contextual)
- `gmail.metadata` (metadata read across all messages)
- `gmail.settings.basic` (manage settings)
- `gmail.settings.sharing` (manage sharing)

**CASA process if ever needed**:
1. Google assigns a tier (Tier 1/2/3) based on user count, scope breadth, and app risk
2. Developer selects from Google-empanelled assessors (Leviathan, Prescient, Bishop Fox, etc.)
3. Assessment covers: code review, penetration testing, access control, data handling, encryption
4. Assessor issues a Letter of Validation (LOV)
5. LOV is valid for 12 months from issue date
6. Google contacts developer via email when recertification is due
7. Cost: $500-$4,500 depending on tier and assessor (Google does not charge; fee is between developer and assessor)

**Our status**: Not applicable. No restricted scopes. No CASA needed.

### 1.6 Limited Use Policy and AI/ML Restrictions

This is critical for any future AI features that process Gmail data.

**The Google API Services User Data Policy "Limited Use" requirements state**:

1. **Transfer restrictions**: Apps must NOT transfer, sell, or use Google user data to create, train, or improve a machine-learning or artificial intelligence model beyond that specific user's personalized model

2. **Generative AI prohibition**: You MUST NOT use Google Workspace user data to train non-personalized generative AI/ML models. This means:
   - You CANNOT feed Gmail message content into a shared LLM fine-tuning dataset
   - You CANNOT use email data to train a company-wide AI model
   - You CAN use email data for per-user features (e.g., "summarize this email for me" using an API call that does not retain data for training)

3. **Privacy policy requirement**: Developers must commit in their privacy policy that they do not retain user data obtained through Workspace APIs to develop, improve, or train non-personalized AI/ML models

4. **Approved use cases**: Limited to user-benefiting features such as productivity enhancements, data backup, and reporting

**What this means for InsightPulseAI**:
- The current add-on is compliant: it sends sender email + subject to Odoo for CRM record creation (user-benefiting productivity feature)
- If we add "Ask Pulser" AI features that analyze email content:
  - Using Azure OpenAI API per-request (not training) with zero data retention = COMPLIANT
  - Storing email content in a vector DB for cross-user search = NOT COMPLIANT
  - Fine-tuning a model on user email data = NOT COMPLIANT unless per-user only
- The privacy policy must include an affirmative Limited Use statement

### 1.7 Annual Recertification

Annual recertification only applies to apps with **restricted** scopes that have completed CASA. Since our app has no restricted scopes:

- **No annual recertification required** for our current scope set
- If `gmail.readonly` is retained (sensitive, not restricted), verification is one-time -- no annual renewal
- Only if we add restricted scopes would the 12-month CASA renewal cycle begin

### 1.8 Privacy Policy Requirements

Regardless of verification path, a privacy policy is required for Marketplace publishing. It must cover:

| Requirement | Our Implementation |
|-------------|-------------------|
| Data controller identity | InsightPulseAI (W9 Studio LLC or equivalent entity) |
| Data collected | Sender email, email subject, user Gmail address |
| Purpose | CRM integration: lead creation, ticket creation, chatter logging |
| Third-party sharing | Data sent to user's Odoo ERP instance at `erp.insightpulseai.com` |
| Data retention | Session tokens in UserProperties (per-user, encrypted by Google); message data not stored |
| User rights | Disconnect via add-on settings, data deletion via Odoo admin |
| Security measures | HTTPS-only, per-user encrypted storage, no message body retention |
| Limited Use statement | "This app's use of information received from Google APIs will adhere to the Google API Services User Data Policy, including the Limited Use requirements." |
| Contact info | Support email + physical address (required by Google) |

**Hosting**: Must be at a URL on a verified domain (e.g., `https://insightpulseai.com/privacy`).

---

## Part 2: Agent Skills Architecture & Knowledge Base

### 2.1 Canonical SKILL.md Format

The industry has converged on SKILL.md as the standard skill definition file. Two variants exist:

**Variant A: Vercel/npx skills standard** (adopted by 27+ agent platforms):

```markdown
---
name: my-skill-name
description: When and why an agent should use this skill. Include trigger phrases.
license: Apache-2.0
compatibility: "Requires Node.js 18+, gws CLI on PATH"
metadata:
  author: insightpulseai
  version: "1.0.0"
  platform: odoo
allowed-tools:
  - Bash
  - Read
  - Edit
---

# Skill Name

Brief description of what this skill does.

## How It Works

Step-by-step workflow.

## Usage

\```bash
command examples
\```

## Output

Expected output format.

## Present Results to User

Template for agent output formatting.

## Troubleshooting

Common issues and solutions.
```

**Frontmatter constraints**:
- `name`: 1-64 chars, lowercase + digits + single hyphens, must match directory name, regex `^[a-z0-9]+(-[a-z0-9]+)*$`
- `description`: 1-1024 chars
- Unknown fields are ignored (forward compatible)

**Variant B: InsightPulseAI contract system** (existing in repo):

```yaml
# skill.yaml
id: domain.feature.action
version: 1
description: "10-500 char description"
maturity: L2  # L0-L4 scale
inputs: { ... }
requires:
  secrets: []
  ssot_files: []
outputs:
  artifacts: []
  evidence: "docs/evidence/<stamp>/<topic>/"
policies:
  no_plaintext_secrets: true
  must_pass_ci: []
  idempotent: true
  rollback_supported: false
verification:
  checks: [...]
```

**Recommendation**: Keep both. The SKILL.md variant is for agent consumption (progressive disclosure). The skill.yaml variant is for CI/governance (schema validation, policy enforcement). They serve different purposes.

### 2.2 Cross-Platform Skill Discovery

Skills are discovered differently by each platform:

| Platform | Discovery Path | Format | Status |
|----------|---------------|--------|--------|
| **Claude Code** | `.claude/commands/`, project SKILL.md files | SKILL.md frontmatter + body | Native support |
| **Gemini CLI** | `.gemini/antigravity/skills/`, `.agent/skills/` | SKILL.md (same format as Claude) | Adopted Jan 2026 |
| **Codex** | `.agent/skills/`, workspace SKILL.md files | SKILL.md | Native support |
| **Cursor** | `.cursor/skills/`, project SKILL.md files | SKILL.md | Native support |
| **Windsurf** | `.windsurf/skills/` | SKILL.md | Native support |
| **GitHub Copilot** | `.github/copilot-skills/` | SKILL.md | Native support |

**Progressive disclosure pattern** (how agents load skills efficiently):
1. Agent scans skill directories at startup
2. Parses YAML frontmatter only (~50-100 tokens per skill)
3. When user prompt matches a skill's description, full SKILL.md loads
4. Scripts and references become available
5. Context is released when skill execution completes

### 2.3 The npx skills CLI

`npx skills` (npm package: `skills`) is the Vercel-maintained CLI for managing agent skill packages:

```bash
# Search and discover skills
npx skills find                          # Interactive search
npx skills find --query "gmail"          # Non-interactive (agent mode)

# Install skills
npx skills add https://github.com/googleworkspace/cli    # Install all skills from repo
npx skills add <package-name>                              # Install from npm

# List installed skills
npx skills list

# Create new skill
npx skills init my-skill-name
```

**Registry**: skills.sh serves as the central directory with telemetry-based popularity rankings. VoltAgent/awesome-agent-skills (6,900+ stars) is the community catalog.

### 2.4 Skill Taxonomy

Based on analysis of gws CLI (95 skills) and the InsightPulseAI repo (80+ skills), skills fall into four categories:

| Category | Pattern | Example | Purpose |
|----------|---------|---------|---------|
| **Service** | `<platform>-<service>` | `gws-gmail`, `odoo-cli-safe` | Raw API/CLI coverage for a single service |
| **Helper** | `<platform>-<service>-<verb>` | `gws-gmail-send`, `gws-script-push` | Single-action convenience wrappers |
| **Persona** | `persona-<role>` | `persona-sales-ops` | Role-based skill bundles (multiple services) |
| **Recipe** | `recipe-<workflow>` | `recipe-email-to-task` | Multi-step compositions across services |

InsightPulseAI adds two additional categories:

| Category | Pattern | Example | Purpose |
|----------|---------|---------|---------|
| **Contract** | `<domain>.<feature>.<action>` | `odoo.mail.configure` | CI-governed skill with schema, policies, and verification |
| **Knowledge** | `<domain>-<topic>` | `odoo19-orm`, `refresh-odoo19-kb` | Reference documentation for agent consumption |

### 2.5 Skill Composition Patterns

**Sequential composition** (Recipe pattern):
```
recipe-email-to-lead:
  1. gws-gmail-read (get email content)
  2. Extract sender, subject, body summary
  3. odoo-cli-safe (create CRM lead via API)
  4. gws-gmail (label email as "Processed")
```

**Parallel composition** (Persona pattern):
```
persona-sales-ops:
  includes:
    - gws-gmail (email management)
    - gws-sheets (pipeline tracking)
    - gws-calendar (meeting scheduling)
    - odoo-cli-safe (CRM operations)
  context: "You are a sales operations assistant..."
```

**Hierarchical composition** (Contract pattern):
```
odoo.mail.configure:
  requires:
    ssot_files: [config/odoo/mail_settings.yaml]
    secrets: [zoho_client_id, zoho_client_secret]
  verification:
    - smtp_connect: smtppro.zoho.com:587
    - ci_script: scripts/ci/check_prod_settings_ssot.py
```

### 2.6 Skill Maturity Model

The InsightPulseAI repo defines a 5-level maturity model (already in `skill.schema.json`):

| Level | Name | Requirements | Production Use |
|-------|------|-------------|----------------|
| L0 | Prompt-only | No contract, just a SKILL.md | No |
| L1 | Contract + examples | Schema validates, has examples | No |
| L2 | Tool + verify | Tool calls + deterministic verification | Yes (default target) |
| L3 | Prod policy + drift | SSOT gates, health checks, drift detection | Yes (operational) |
| L4 | Self-healing | Can revert + re-verify autonomously | Yes (autonomous) |

### 2.7 Knowledge Base Structure Recommendation

Based on analysis of the existing `agents/skills/` directory (80+ skills), the `docs/skills/` knowledge base (6 docs), and external patterns:

```
agents/
  skills/
    # Governance
    schema/
      skill.schema.json              # JSON Schema for skill.yaml contracts
    _template/                        # Copy-paste template for new skills
    _templates/                       # Port templates (anthropic, etc.)
    AGENTS.md                         # Agent entry point (discovery index)

    # Service skills (L0-L1: SKILL.md only)
    gws-gmail/SKILL.md               # Google Workspace Gmail operations
    gws-script/SKILL.md              # Apps Script deployment
    gws-drive/SKILL.md               # Drive operations
    gws-shared/SKILL.md              # Cross-service auth/setup

    # Contract skills (L2-L4: skill.yaml + SKILL.md)
    odoo.mail.configure/
      skill.yaml                     # Machine-readable contract
      prompt.md                      # Agent instructions
      examples/                      # Input/output examples
    deploy-odoo-modules-git/
      SKILL.md
      KB_SOURCES.yaml

    # Knowledge skills (reference docs for agent consumption)
    odoo/
      ODOO19_SKILLS_INDEX.md         # Index of all Odoo 19 knowledge skills
      odoo19-orm/SKILL.md            # ORM reference
      odoo19-security/SKILL.md       # Security reference
      ...

    # Persona bundles
    persona-sales-ops/SKILL.md
    persona-erp-admin/SKILL.md

    # Recipe compositions
    recipe-gmail-to-odoo-lead/SKILL.md
    recipe-deploy-addon/SKILL.md

docs/
  skills/
    # Deep knowledge bases (too large for SKILL.md)
    gmail-addon-marketplace-publishing.md     # OAuth/Marketplace KB
    gws-cli-evaluation.md                     # gws CLI evaluation
    google-workspace-extensibility-platform.md # Platform research
    google-oauth-verification-and-agent-skills-research.md  # This document
    ios-native-wrapper.md                     # iOS wrapper skill
```

**Key principles**:
1. `agents/skills/` is the primary skill directory -- agents discover skills here
2. `docs/skills/` holds deep reference material too large for SKILL.md files (>500 lines)
3. Skills in `agents/skills/` use progressive disclosure (frontmatter for discovery, body for execution)
4. Contract skills (`skill.yaml`) get CI validation via `scripts/ci/check_agent_skills.py`
5. Knowledge skills are read-only reference (never execute code)
6. Cross-platform compatibility achieved by placing skills in `agents/skills/` (Claude) and symlinking to `.agent/skills/` (Gemini/Codex) if needed

### 2.8 Versioning and Lifecycle

**Skill versioning**:
- `skill.yaml`: `version` field (integer, monotonically increasing)
- SKILL.md frontmatter: `metadata.version` (semver string)
- Both must be updated when the skill contract changes

**Lifecycle states**:
1. **Draft**: In development, not in CI
2. **Active**: In CI, available to agents
3. **Deprecated**: Still functional, agents warned, replacement identified
4. **Retired**: Removed from discovery, kept in git history

**Deprecation pattern**:
```yaml
# In skill.yaml
deprecated: true
deprecated_by: new-skill-id
deprecated_date: "2026-03-27"
```

---

## Part 3: Practical Next Steps

### 3.1 Gmail Add-on -- Immediate Actions

| Priority | Action | Effort | Blocker |
|----------|--------|--------|---------|
| **P0** | Test `gmail.readonly` removal (see test plan in existing KB) | 30 min | None |
| **P0** | Migrate `newKeyValue()` to `newDecoratedText()` in all `.gs` files | 1-2 hours | None |
| **P1** | Create standard GCP project from `w9studio.net` Workspace account | 15 min | Requires Workspace admin access |
| **P1** | Link Apps Script project to standard GCP project | 5 min | Requires GCP project from P1 |
| **P1** | Configure OAuth consent screen as "Internal" | 10 min | Requires GCP project from P1 |
| **P1** | Host privacy policy at `insightpulseai.com/privacy` | 1 hour | Requires privacy policy draft |
| **P2** | Generate Marketplace icon assets (32x32, 48x48, 96x96) | 30 min | None |
| **P2** | Capture 3-5 screenshots of add-on in Gmail | 30 min | Add-on must be functional |
| **P2** | Configure Marketplace SDK (Private visibility) | 30 min | Requires all P1 items |
| **P2** | Publish as Private to `w9studio.net` | 10 min | Requires all P1 + P2 items |

### 3.2 Gmail Add-on -- Deferred Actions (Public Publishing)

Only needed if the add-on must be available outside the Workspace domain:

| Action | Trigger | Effort |
|--------|---------|--------|
| Switch OAuth consent screen from Internal to External | Decision to go public | 5 min (irreversible) |
| Submit OAuth verification (if `gmail.readonly` retained) | Public publishing | 3-6 weeks wait |
| Record demo video for sensitive scope justification | OAuth verification | 2-4 hours |
| Prepare scope justification letter | OAuth verification | 1 hour |
| Verify domain in Google Search Console | Public publishing | 15 min |

### 3.3 Agent Skills Knowledge Base -- Immediate Actions

| Priority | Action | Effort |
|----------|--------|--------|
| **P1** | Install `gws-shared` + `gws-script` + `gws-drive` + `gws-sheets` skills | 10 min |
| **P1** | Create `recipe-deploy-gmail-addon/SKILL.md` composing clasp/gws workflow | 1 hour |
| **P2** | Create `.agent/skills/` symlink to `agents/skills/` for Gemini/Codex compat | 5 min |
| **P2** | Add `deprecated` field to `skill.schema.json` for lifecycle management | 30 min |
| **P3** | Create `persona-erp-sales/SKILL.md` bundling Gmail + Odoo + Sheets skills | 1 hour |
| **P3** | Register skills on skills.sh for public discoverability | 30 min |

### 3.4 Privacy Policy Draft (for Gmail Add-on)

A minimal compliant privacy policy should state:

1. InsightPulseAI for Gmail accesses the sender email address and subject line of the currently open email message
2. This data is sent via HTTPS to the user's configured Odoo ERP instance for CRM record creation
3. No email message body content is accessed, transmitted, or stored
4. Session credentials are stored per-user using Google's encrypted UserProperties (not accessible to other users or the developer)
5. Users can disconnect and delete all stored data via the add-on's settings menu
6. This app complies with the Google API Services User Data Policy, including the Limited Use requirements
7. This app does not use data obtained from Google APIs to develop, improve, or train generalized/non-personalized AI or ML models
8. Contact: [support email] | [physical address]

---

## Sources

### Google OAuth Verification
- [OAuth App Verification FAQ](https://support.google.com/cloud/answer/13461325)
- [Verification Requirements](https://support.google.com/cloud/answer/9110914)
- [When Verification is Not Needed](https://support.google.com/cloud/answer/13462713)
- [Security Assessment](https://support.google.com/cloud/answer/13463073)
- [Sensitive Scope Verification](https://developers.google.com/identity/protocols/oauth2/production-readiness/sensitive-scope-verification)
- [Restricted Scope Verification](https://developers.google.com/identity/protocols/oauth2/production-readiness/restricted-scope-verification)
- [Annual Recertification](https://support.google.com/cloud/answer/13463816)
- [OAuth Client Verification for Apps Script](https://developers.google.com/apps-script/guides/client-verification)
- [Manage App Audience](https://support.google.com/cloud/answer/15549945)
- [Unverified Apps](https://support.google.com/cloud/answer/7454865)

### Google API Data Policy
- [Google API Services User Data Policy](https://developers.google.com/terms/api-services-user-data-policy)
- [Google Workspace API User Data and Developer Policy](https://developers.google.com/workspace/workspace-api-user-data-developer-policy)
- [Workspace API Policy Protections for Generative AI](https://workspace.google.com/blog/ai-and-machine-learning/api-policy-protections)
- [Application Use Cases](https://support.google.com/cloud/answer/13805798)

### Gmail Scopes
- [Choose Gmail API Scopes](https://developers.google.com/workspace/gmail/api/auth/scopes)
- [Workspace Add-on Scopes](https://developers.google.com/workspace/add-ons/concepts/workspace-scopes)
- [Apps Script Authorization Scopes](https://developers.google.com/apps-script/concepts/scopes)

### CASA Security Assessment
- [Google CASA Overview (DeepStrike)](https://deepstrike.io/blog/google-casa-security-assessment-2025)
- [CASA Prescient Security](https://prescientsecurity.com/casa)
- [CASA Leviathan Security](https://www.leviathansecurity.com/programs/google-casa-cloud-application-security-assessment)

### Agent Skills Architecture
- [Vercel Skills CLI (npx skills)](https://github.com/vercel-labs/skills)
- [Vercel Agent Skills Collection](https://github.com/vercel-labs/agent-skills)
- [Agent Skills FAQ (Vercel)](https://vercel.com/blog/agent-skills-explained-an-faq)
- [Agent Skills Documentation (Vercel)](https://vercel.com/docs/agent-resources/skills)
- [Agent Skills in Claude SDK](https://platform.claude.com/docs/en/agent-sdk/skills)
- [Claude Agent Skills Overview](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
- [Google Workspace CLI (gws)](https://github.com/googleworkspace/cli)
- [VoltAgent Awesome Agent Skills](https://github.com/VoltAgent/awesome-agent-skills)
- [Agent Skill Creator (Cross-Platform)](https://github.com/FrancyJGLisboa/agent-skill-creator)

### Internal Sources (This Repo)
- `web/apps/gmail-odoo-addon/appsscript.json` -- Current scope declarations
- `web/apps/gmail-odoo-addon/docs/MARKETPLACE_PUBLISHING_KNOWLEDGE_BASE.md` -- Existing marketplace KB
- `docs/skills/gws-cli-evaluation.md` -- gws CLI evaluation
- `agents/skills/schema/skill.schema.json` -- Skill contract schema
- `agents/skills/_template/skill.yaml` -- Skill template
- `agents/skills/AGENTS.md` -- Agent skills index
- `agents/skills/odoo.mail.configure/skill.yaml` -- Example L3 contract skill
- `agents/skills/deep-research/SKILL.md` -- Example SKILL.md format

---

*This document is a point-in-time research artifact. Google's OAuth policies and the agent skills ecosystem are evolving. Re-evaluate quarterly or when significant policy changes are announced.*
