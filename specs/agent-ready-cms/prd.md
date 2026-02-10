# PRD — Agent-Ready Repo Standardization + Odoo CMS Template

**Version**: 1.0.0
**Status**: Approved
**Author**: InsightPulse AI
**Date**: 2026-02-07

---

## 1. Executive Summary

This PRD defines the implementation of an agent-ready repository standardization across the Insightpulseai organization, plus an Odoo-native CMS template factory for Copilot-style landing pages.

**Goals**:
1. Standardize agent entrypoints across ~24 repos with `CLAUDE.md` + `docs/` taxonomy
2. Provide Odoo 19 CMS theme template with modern animations (CSS/JS, Lottie, Rive)
3. Automate org-wide rollout via PR generation
4. Enforce structure via CI guards

---

## 2. Problem Statement

### Current Pain Points
- Agents lack consistent entrypoints across repos
- No standardized documentation structure
- Odoo landing pages require manual coding (no CMS snippets)
- No Copilot-style design patterns for Odoo Website

### Impact
- Agent context gathering takes >5 file reads
- Documentation scattered or missing
- Landing page development is slow and inconsistent
- Rebranding requires code changes

---

## 3. Proposed Solution

### 3.1 Agent-Ready Docs Scaffold

**Structure**:
```
/CLAUDE.md                    # Agent contract (root)
/docs/
├── README.md                 # Index + agent entrypoints
├── 01-Discovery/             # Problem framing
├── 02-Frameworks/            # Playbooks
├── 03-PRDs/                  # Requirements
├── 04-Architecture/          # Diagrams/ADRs
├── 05-Design/                # Tokens/UI
├── 06-Development/           # Conventions
├── 07-Tests/                 # Test plans
├── 08-Feedback/              # User feedback
├── 09-Analytics/             # Metrics
├── 99-Archive/               # Deprecated
└── XX-Archive/               # Overflow
```

**Generator**: `scripts/scaffold_agent_docs.sh` (idempotent)

### 3.2 Odoo CMS Copilot Theme

**Template Location**: `templates/odoo-cms-copilot/`

**CMS Snippets**:
| Snippet | Description |
|---------|-------------|
| `s_hero_copilot` | Hero with headline, CTAs, video/animation |
| `s_trust_band` | Logo trust strip |
| `s_feature_grid` | 3-up feature cards with hover |
| `s_media_section` | Alternating text + media |
| `s_cta_endcap` | Conversion section |

**Animation Support**:
- CSS/JS IntersectionObserver scroll reveals
- Lottie-web JSON animations (CDN)
- Rive interactive animations (CDN)
- All respect `prefers-reduced-motion`

**Generator**: `scripts/new_odoo_cms_theme.sh`

### 3.3 Factory Integration

**Commands**:
```bash
./scripts/factory.sh list                     # Show all templates
./scripts/factory.sh new odoo-cms-copilot "My Theme"
./scripts/factory.sh new agent-docs-scaffold .
```

### 3.4 Org-Wide Rollout

**Script**: `scripts/rollout_agent_docs.sh`

**Behavior**:
1. Fetch non-archived repos via `gh repo list`
2. Clone each repo with depth 1
3. Create `chore/agent-docs-scaffold` branch
4. Run scaffold script
5. Create PR with standardized title/body
6. Skip compliant repos

---

## 4. Copilot-Style Copy (Production-Ready)

### Hero Section
```
H1: Work faster with AI that understands your business.
Sub: Automate reporting, answer questions across systems, and turn documents into actions—securely and in context.
CTA1: Request a demo
CTA2: See it in action
Link: View platform architecture
```

### Feature Cards
```
Card 1:
  Title: Ask in plain English
  Body: Get answers from your data, documents, and operations—without switching tools.

Card 2:
  Title: Turn work into workflows
  Body: Convert requests into approvals, tasks, and automations with full auditability.

Card 3:
  Title: Built for control
  Body: Role-aware access, policy enforcement, and predictable execution paths.
```

### Media Sections
```
Section 1:
  Title: From document to decision in minutes.
  Body: Extract key fields, validate against policy, and route into your system of record.

Section 2:
  Title: One interface. Many systems.
  Body: Connect Odoo, Google Workspace, Zoho Mail, Stripe, and your lakehouse.
```

### CTA Endcap
```
Title: Ready to see it live?
CTA1: Request a demo
CTA2: Talk to the team
```

---

## 5. Technical Requirements

### 5.1 Docs Scaffold
- **Idempotent**: Safe to re-run
- **Minimal footprint**: ~15 files created
- **CI guard**: GitHub Actions workflow validates structure

### 5.2 Odoo Theme
- **Odoo version**: 19.0
- **License**: LGPL-3
- **Dependencies**: `website`, `website_blog`
- **Assets**: Loaded via manifest (Odoo 19 style)

### 5.3 Animation Libraries
| Library | CDN | Version | Size |
|---------|-----|---------|------|
| Lottie | cdnjs/unpkg | 5.12.2 | ~150KB |
| Rive | unpkg/jsdelivr | 2.7.0 | ~200KB |

### 5.4 Browser Support
- Chrome 88+
- Firefox 85+
- Safari 14+
- Edge 88+

---

## 6. Acceptance Criteria

### Agent Docs Scaffold
- [ ] `CLAUDE.md` exists at repo root
- [ ] `docs/README.md` exists with folder index
- [ ] All 11 folders have README.md
- [ ] CI guard passes on PRs

### Odoo Theme
- [ ] Template generates valid Odoo 19 module
- [ ] All 5 snippets appear in Website Builder
- [ ] Animations work (scroll reveals, hover)
- [ ] `prefers-reduced-motion` respected

### Factory Integration
- [ ] `./scripts/factory.sh list` shows both templates
- [ ] Generator scripts work end-to-end
- [ ] Templates in `catalog.yaml`

### Org Rollout
- [ ] Dry-run shows expected changes
- [ ] PRs created for non-compliant repos
- [ ] Compliant repos skipped

---

## 7. Rollback Strategy

### Docs Scaffold
```bash
git revert HEAD  # If committed
rm -rf docs/ CLAUDE.md  # Manual cleanup
```

### Theme Template
```bash
rm -rf templates/odoo-cms-copilot/
rm scripts/new_odoo_cms_theme.sh
git checkout -- templates/catalog.yaml scripts/factory.sh
```

### Org PRs
```bash
# Close without merging
gh search prs --owner "Insightpulseai" \
  --head "chore/agent-docs-scaffold" --state open \
  --json url --jq '.[].url' | xargs -I{} gh pr close {}
```

---

## 8. Dependencies

- Odoo 19 CE environment (theme testing)
- `gh` CLI authenticated (org PRs)
- GitHub org write access
- Node.js (optional: animation development)

---

## 9. Timeline

| Milestone | Status |
|-----------|--------|
| Docs scaffold complete | ✅ Done |
| CI guard created | ✅ Done |
| Odoo theme template | ✅ Done |
| Generator scripts | ✅ Done |
| Factory integration | ✅ Done |
| Org rollout script | ✅ Done |
| PRD documentation | ✅ Done |
| End-to-end testing | 🔄 Pending |
| Org-wide rollout | ⏳ Ready |

---

## 10. References

- [Plan File](/Users/tbwa/.claude/plans/splendid-purring-lark.md)
- [Constitution](./constitution.md)
- [Tasks](./tasks.md)
- [Template README](/templates/odoo-cms-copilot/README.md)
