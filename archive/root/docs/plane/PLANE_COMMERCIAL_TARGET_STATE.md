# Plane Commercial Self-Hosted: Target State

---

## A. Edition Decision

| Item | Value |
|------|-------|
| **Target edition** | Plane Commercial Self-Hosted |
| **Reason** | Full Cloud parity -- every feature available in Plane Cloud is available in Commercial self-hosted |
| **Not Community** | Community edition only tracks Cloud Free-tier parity; missing paid-tier features we need |
| **Airgapped** | Not required now; available as a future deployment option if strict isolation is needed |

Reference: https://developers.plane.so/self-hosting/editions-and-versions

---

## B. Consolidated Feature Inventory

### Core Concepts

| Feature | Role in Our Stack | Reference |
|---------|-------------------|-----------|
| **Workspaces** | Org / company boundary -- one workspace per operating entity | https://docs.plane.so/introduction/core-concepts |
| **Projects** | Product / stream / department containers -- maps to delivery programs | https://docs.plane.so/core-concepts/projects/overview |
| **Work Items** | Execution unit: comments, relations, attachments, automations | https://docs.plane.so/core-concepts/issues/overview |
| **Cycles** | Time-boxed execution periods (sprints, monthly close windows) | https://docs.plane.so/introduction/core-concepts |
| **Views** | Saved layouts and filtered operating surfaces per role | https://docs.plane.so/introduction/core-concepts |
| **Pages** | Project knowledge: PRDs, constitutions, decision logs, rollout notes | https://docs.plane.so/core-concepts/pages/overview |
| **Wiki** | Org-wide knowledge base for company policy, process docs, runbooks | https://docs.plane.so/core-concepts/pages/wiki |
| **Analytics** | Project / cycle / module analytics for delivery visibility | https://docs.plane.so/core-concepts/analytics |
| **Search** | Workspace-wide search across projects, work items, cycles, modules, pages | https://docs.plane.so/workspaces-and-users/search-workspace |

### Why These Features Matter

- **Workspaces + Projects** replace fragmented planning surfaces (spreadsheets, separate boards).
- **Pages + Wiki** consolidate documentation that currently lives across multiple tools.
- **Cycles + Views** provide the delivery cadence and role-based visibility needed for PPM.
- **Analytics + Search** give real-time delivery intelligence without building custom dashboards.

---

## C. Integration Consolidation

Three canonical integrations -- no others unless explicitly approved:

| Integration | Purpose | Reference |
|-------------|---------|-----------|
| **Slack** | Notifications, thread sync, work item creation from conversations | https://docs.plane.so/integrations/slack |
| **Draw.io** | Diagrams and whiteboards embedded inside Pages / Wiki | https://docs.plane.so/integrations/draw-io |
| **GitHub / GitHub Enterprise** | Repo-project linkage for engineering execution, PR/commit tracking | https://docs.plane.so/integrations/github |

### Integration Rationale

- **Slack** is already the team coordination surface (replaced Mattermost). Plane Slack integration keeps work item activity visible in existing channels.
- **Draw.io** eliminates external diagram drift by keeping architecture docs next to execution artifacts inside Pages/Wiki.
- **GitHub** ties roadmap and delivery to repos. Engineering work items link directly to PRs and commits.

---

## D. PPM + Roadmap Consolidation

### Operating Model

Plane is the **single system** for roadmap, PPM execution, work tracking, and documentation context.

| Plane Concept | Operating Model Role |
|---------------|---------------------|
| **Workspace** | Company / org operating surface |
| **Projects** | Product lines, internal platforms, delivery programs |
| **Pages** | PRD, constitution, decision logs, rollout notes |
| **Work Items** | Execution tasks with full lifecycle tracking |
| **Cycles** | Sprint / monthly planning windows |
| **Views** | Role-based filtered boards (exec, product, engineering, ops) |
| **Wiki** | Company-wide policy, process docs, runbooks |

### What This Replaces

Instead of separate fragmented planning artifacts, use:

```
Roadmap       = Projects + Cycles + Views + Pages
PPM Execution = Work Items + Cycles + Views
Work Tracking = Work Items + Projects
Documentation = Pages + Wiki
```

### Consolidation Boundary

| Previously | Now |
|------------|-----|
| Separate roadmap spreadsheets | Projects + Cycles + Views |
| Scattered PRDs in Notion/Google Docs | Pages inside Projects |
| Architecture diagrams in external tools | Draw.io inside Pages/Wiki |
| Engineering tracking in GitHub Issues alone | Work Items linked to GitHub |
| Sprint planning in standalone boards | Cycles within Projects |
| Status reports built manually | Analytics + Views |

---

## E. Production Readiness Gates

Production is **not considered complete** until all gates pass:

| Gate | Acceptance Criteria |
|------|-------------------|
| **Production auth configured** | Auth mode selected and operational (local, SSO/OIDC, or SAML) |
| **Production email configured** | Outbound SMTP working; invite emails, comment notifications, and auth flows verified |
| **Slack connected** | Workspace linked; test notification sent and received |
| **Draw.io connected** | Integration enabled; test diagram created in a Page |
| **GitHub connected** | Org linked; test repo-project linkage verified |
| **Initial workspace/project seed loaded** | Workspace + all standard projects created per seed doc |
| **Roadmap seed loaded** | Initial cycles, views, and pages populated |
| **PPM taxonomy loaded** | Work item types, labels, and states configured |
| **Role model confirmed** | Workspace roles assigned; view permissions verified |
| **Backup/update path confirmed** | Backup procedure tested; upgrade path documented |

### Gate Verification

Each gate must produce evidence:

```
docs/evidence/<YYYYMMDD-HHMM>/plane/
  auth_verified.txt         # Auth mode + test login result
  email_verified.txt        # SMTP test + sample notification
  slack_verified.txt        # Integration link + test message
  drawio_verified.txt       # Test diagram URL
  github_verified.txt       # Linked repo + test PR linkage
  seed_verified.txt         # Project list + cycle list
  roles_verified.txt        # Role assignments + permission check
  backup_verified.txt       # Backup file + restore test result
```

---

## F. Community vs Commercial Feature Scope

| Capability | Community | Commercial Self-Hosted |
|------------|-----------|----------------------|
| Workspaces | Yes | Yes |
| Projects | Yes | Yes |
| Work Items | Yes | Yes |
| Cycles | Yes | Yes |
| Views | Yes | Yes |
| Pages | Yes | Yes |
| Wiki | Limited | Full |
| Analytics | Basic | Full |
| Search | Basic | Full |
| Integrations (Slack, GitHub, Draw.io) | Limited | Full |
| Custom workflows | Limited | Full |
| Advanced permissions | No | Yes |
| Priority support | No | Yes |
| SSO/SAML | No | Yes |

**Decision**: Commercial self-hosted eliminates all feature-scope ambiguity. No future "this needs Enterprise" blockers.
