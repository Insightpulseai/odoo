# Wix Git Integration & CLI -- Comprehensive Research Report

> Research date: 2026-03-27
> Sources: Wix Developer Documentation (dev.wix.com), read via MCP tools
> Purpose: Inform W9 Studio site workflow (GitHub-connected Wix Studio site)

---

## Table of Contents

1. [Git Integration Architecture](#1-git-integration-architecture)
2. [What Lives in Git vs What Lives in the Editor](#2-what-lives-in-git-vs-what-lives-in-the-editor)
3. [Local Editor Workflow](#3-local-editor-workflow)
4. [Publishing Flow](#4-publishing-flow)
5. [CMS / Data Collections via Code](#5-cms--data-collections-via-code)
6. [Limitations and Gotchas](#6-limitations-and-gotchas)
7. [Best Practices for W9 Studio](#7-best-practices-for-w9-studio)
8. [Automated Workflows (GitHub Actions)](#8-automated-workflows-github-actions)

---

## 1. Git Integration Architecture

### How It Works

Wix Git Integration connects a Wix Studio (or Wix Editor) site to a **dedicated GitHub repository** via the **Velo GitHub App**. This app maintains a bidirectional sync between the site's code and the repo.

### Source of Truth Split

| Artifact | Source of Truth | Storage |
|----------|----------------|---------|
| **Code** (page code, backend, public) | **GitHub repo** (default branch) | `src/` folder in repo |
| **Design** (layout, elements, styling) | **Wix Editor** (UI versions) | Wix internal platform |
| **CMS data** (collection content) | **Wix CMS** (live database) | Wix internal platform |
| **Media** (images, videos) | **Wix Media Manager** | Wix CDN |
| **npm packages** | **Repo** (`velo.dependencies.json`) | `src/velo.dependencies.json` |
| **Code-to-UI binding** | **`wix.config.json`** in repo | Repo root |

### Sync Direction

```
IDE (local files) --push--> GitHub (default branch) --auto-sync--> Wix Editor (code panel)
Wix Editor (design changes) --Save--> UI Version --wix dev sync--> IDE (wix.config.json updated)
```

The Velo GitHub App watches the default branch. When a commit lands on `main` (or whatever the default branch is), the code is automatically synced to the editor's code panel. This is **not** an auto-publish -- it only updates the editor's view of the code.

### Key Configuration File: `wix.config.json`

This file in the repo root associates the repo with:
- A specific Wix site
- A specific **UI version** (a snapshot of the site's design state)

This file is auto-managed. **Never edit it manually.**

---

## 2. What Lives in Git vs What Lives in the Editor

### Repository File Structure

```
repo-root/
  wix.config.json          # Site + UI version binding (auto-managed, never edit)
  src/
    pages/
      Home.{id}.js         # Page code files (one per page)
      About.{id}.js        # Page name + internal ID, period-separated
      masterpage.js         # Global site code (runs on every page)
    backend/
      data.js               # Data hooks for CMS collections
      routers.js            # Custom routing / sitemap
      events.js             # Backend event handlers
      http-functions.js     # HTTP endpoints exposed on the site
      jobs.config           # Scheduled recurring jobs
      permissions.json      # Function-level permissions (for .jsw files)
      *.web.js              # Web modules (backend functions callable from frontend)
      *.js                  # General backend code
    public/
      *.js                  # Public code files (importable from any file)
    velo.dependencies.json  # npm package tracking (auto-managed)
```

### What IS in the Repo (Git-Tracked)

- Page code files (JavaScript for each page)
- Backend code (web modules, data hooks, routers, HTTP functions, events, jobs)
- Public code (shared frontend utilities)
- npm package manifest (`velo.dependencies.json`)
- Site/UI binding (`wix.config.json`)
- `masterpage.js` (global code)

### What is NOT in the Repo

- **Page design/layout** (element positions, sizes, colors, fonts)
- **Element definitions** (which elements exist on a page)
- **CSS/styling** (all managed in the editor)
- **Media files** (images, videos -- stored in Wix Media Manager)
- **CMS data** (collection content/rows)
- **CMS collection schemas** (field definitions -- managed in editor)
- **Site settings** (SEO, domain, analytics)
- **Apps/integrations** installed on the site
- **Dynamic page structure** (created in editor, generates code files)

### What Happens When You Push Code to Main

1. Commit lands on the default branch in GitHub
2. Velo GitHub App detects the change
3. Code is synced to the Wix editor's code panel (there may be a delay)
4. Commit details appear in the GitHub Integration panel in the editor
5. **The site is NOT auto-published** -- code is staged in the editor, awaiting explicit publish

### What Happens When You Make Design Changes in the Editor

1. Design change made in Regular Editor or Local Editor
2. A new **UI version** is generated (snapshot of the design)
3. The UI version number is updated in `wix.config.json`
4. If using Local Editor (`wix dev`), the updated `wix.config.json` is synced to your local IDE
5. You must commit and push the updated `wix.config.json` to keep the repo in sync

---

## 3. Local Editor Workflow

### What `wix dev` Actually Does

Running `wix dev` in your terminal (from the repo directory):
1. Opens a **Local Editor** in your default browser
2. Establishes a live sync between your IDE files and the Local Editor
3. Code changes saved in your IDE are immediately reflected in the Local Editor
4. You can preview code execution in the Local Editor

For cloud IDEs (GitHub Codespaces, etc.): use `wix dev --tunnel`.

### Local Editor vs Regular Editor

| Capability | Regular Editor | Local Editor |
|-----------|---------------|--------------|
| Edit design (layout, elements) | Yes | Yes |
| Edit code | Read-only (when GitHub-connected) | Read-only (edit in IDE instead) |
| Publish button | Yes (Publish) | No (replaced with Save) |
| Install packages/apps | Read-only | Read-only (use IDE) |
| Wix IDE | Available | Disabled |
| Page duplication | Code included | Code NOT included |

### Code Sync Flow

```
Local IDE (save file)
  --> Live sync to Local Editor (immediate, hot reload)
  --> Preview in Local Editor to test
  --> Commit & push to GitHub when satisfied
```

### Design Changes in Local Editor

Yes, you **can** make design changes in the Local Editor. The flow is:

1. Make design changes (add/modify elements, change layout) in the Local Editor
2. Click **Save** (not Publish -- there is no Publish in Local Editor)
3. This creates a new UI version
4. The UI version is synced back to your IDE (updates `wix.config.json`)
5. New page code files appear in your repo for any newly added pages
6. Autocomplete for newly added elements becomes available

**Critical**: The Local Editor and Regular Editor are synced. Design changes in one are immediately reflected in the other.

### What is Read-Only in Local Editor

- All code files (page code, backend, public) -- edit in IDE only
- Packages & Apps -- install via IDE/CLI only
- Wix IDE panel -- disabled entirely

---

## 4. Publishing Flow

### Publishing Does NOT Happen Automatically on Push

Pushing to `main` syncs code to the editor but **does not publish**. Publishing is always an explicit action.

### Three Publishing Methods

| Method | Code Source | UI Version Source |
|--------|-----------|------------------|
| **Editor Publish button** | Code from default branch in repo | **Latest UI version** (even if it does not match the repo) |
| **CLI: `wix publish` > "Latest commit from origin/main"** | Code from default branch in repo | UI version from `wix.config.json` in repo |
| **CLI: `wix publish` > "Local code"** | Code from your local IDE (unpushed) | UI version from `wix.config.json` in repo |

### Key Differences

- **Editor publish** uses the latest UI version regardless of what `wix.config.json` says. This means if someone made design changes in the editor but nobody committed the updated `wix.config.json`, the editor publish will use the newer design.
- **CLI publish** always uses the UI version pinned in `wix.config.json`. This is more deterministic and predictable.
- **CLI local code publish** is dangerous: it puts the live site out of sync with the GitHub repo. If someone later publishes from the repo, the local-only code is lost.

### Preview (Non-Publishing)

`wix preview` builds a shareable preview URL without publishing. Same source options as publish. Preview URLs are temporary and do not appear in the Release Manager.

**Limitation**: Preview uses live HTTP functions. You cannot test HTTP function changes via preview.

### Git Commits vs Site Versions

Git commits and site versions are **not** 1:1. Multiple commits can land before a publish. A publish creates a new site version from whatever code and UI version are selected at publish time.

---

## 5. CMS / Data Collections — corrected

### What is true
- In a Git-integrated Wix site, **code** remains Git-managed, while **design/layout** remains managed through Wix UI versions.
- Wix's docs state that the current UI version paired with the repo is tracked in `wix.config.json`.
- The Local Editor lets you make design changes, but those changes create a **new UI version** that must be synced with the IDE/repo workflow.
- Pushing code to the repo's default branch syncs code to the editor, but it does **not** publish the site.

### Important correction
It is **not accurate** to say that CMS collections cannot be created from code.

Wix's current Data Collections documentation says collection structure can be managed programmatically:
- create collections
- modify collections
- delete collections

This is available through Wix's Data Collections API / SDK surfaces.

### What You CAN Do in Code

1. **Data hooks** (`src/backend/data.js`): Intercept CRUD operations on collections with before/after hooks:
   - `beforeInsert`, `afterInsert`
   - `beforeUpdate`, `afterUpdate`
   - `beforeRemove`, `afterRemove`
   - `beforeQuery`, `afterQuery`
   - `beforeCount`, `afterCount`

2. **Read/write CMS data** from backend code using the `@wix/data` npm package (Wix JavaScript SDK)

3. **HTTP functions** (`src/backend/http-functions.js`): Expose REST endpoints that can read/write CMS data

4. **Dynamic pages**: Created in the editor, they auto-generate code files for list and item pages

5. **Create/modify/delete collection schemas** via the Data Collections API (`wix-data-v2/collections`)

### Practical interpretation for W9 Studio
For W9 Studio, the operationally safest approach is still:

1. Create `W9Inquiries` manually in the Wix CMS dashboard.
2. Keep `backend/inquiries.jsw` responsible for writing records into that collection.
3. Avoid introducing additional collections (`Services`, `Gallery`, `Testimonials`) until those sections truly need to become dynamic.

This recommendation is based on simplicity and lower execution risk — **not** on a platform limitation that forbids schema creation from code.

> For W9 Studio, create `W9Inquiries` in the Wix CMS dashboard as the simplest operational path. However, current Wix documentation indicates collection schemas can also be created and modified programmatically through the Data Collections API / SDK.

### Warnings
- Do not assume that schema work done in code removes the need for Wix UI awareness; collection fields and UI versions can still affect runtime behavior.
- Do not confuse **repo-managed code** with **fully repo-managed site structure**. Layout, element tree, and page design still depend on Wix UI versions.
- Do not assume pushing to `main` publishes the site. Publishing is still a separate action.
- **Collection field changes are immediately reflected on the live site, even before you publish.** Changing a field type, adding a required field, or deleting a field takes effect immediately on production data.

> References:
> - Wix Git Integration & Local Editor docs: code is synced from the repo's default branch, code/packages are read-only in the Local Editor, design changes create UI versions, and `wix.config.json` tracks the repo's current UI version.
> - Wix Publish docs: pushing to the default branch syncs code to the editor, but publishing is a separate step.
> - Wix Data Collections docs: collection structure can be created/modified/deleted programmatically through the Data Collections API / SDK.

---

## 6. Limitations and Gotchas

### Hard Limitations

| Limitation | Detail |
|-----------|--------|
| **No page creation from IDE** | Pages must be created in a Wix editor (Local or Regular). Code files are generated automatically. |
| **No page deletion from IDE** | Deleting a page code file from the repo does NOT delete the page from the site. Pages are deleted in the editor. |
| **No file renaming** | Renaming a page code file breaks the association. Wix uses the filename (including the internal ID) to bind code to pages. A renamed file is ignored and a new empty file is created. |
| **No Custom Extensions (SPIs)** | Cannot be added when using Git Integration. |
| **No Velo Packages** | Cannot connect to GitHub if Velo Packages are set up. npm packages are supported. |
| **No DOM manipulation** | Wix uses `$w` APIs, not direct DOM access. npm packages that manipulate the DOM have limited use. |
| **No ES modules** | ES modules and native modules are incompatible with Wix runtime. |
| **Import syntax is path-based, not relative** | Must use `import from 'backend/file'` not `import from '../backend/file'`. |
| **Code panel read-only when connected** | Cannot edit code in the Regular Editor while GitHub is connected. |

### Things That Will Break Your Integration

1. **Deleting the GitHub repo** -- Integration breaks. Must disconnect and reconnect (creates a new repo, cannot reuse old one).
2. **Renaming the GitHub repo** -- Integration breaks. Same recovery as deletion.
3. **Transferring repo to another account** -- Integration breaks.
4. **Changing GitHub username** -- Integration breaks.
5. **Revoking Velo App access** -- Integration breaks (recoverable by re-granting access).
6. **Uninstalling the Velo GitHub App** -- Integration breaks (recoverable by reinstalling).

### Once Disconnected, Cannot Reconnect to Same Repo

If you disconnect a site from GitHub, you **cannot reconnect it to the same repository**. A new repo must be created. The old repo still exists but is orphaned.

### Design Changes Are Not Versioned in Git

Design (layout, elements, styling) is tracked by Wix's internal UI versioning system, not Git. You only get a UI version number in `wix.config.json`. There is no diff, no rollback, and no merge capability for design changes.

### Publishing from Editor vs CLI Can Diverge

If design changes are made in the editor but `wix.config.json` is not committed:
- Editor publish uses the latest design (newer)
- CLI publish uses the design pinned in `wix.config.json` (older)

This can cause confusion about which version of the design is live.

### Collection Field Changes Are Immediate

CMS collection field changes (add/remove/rename fields) take effect on the live site immediately, bypassing the publish workflow entirely.

---

## 7. Best Practices for W9 Studio

### Recommended Workflow

```
1. Design phase (Editor):
   - Create pages and elements in Wix Studio editor
   - Set up CMS collections and schemas in the editor
   - Save to generate UI versions

2. Development phase (IDE + Local Editor):
   - Clone the repo
   - Write page code, backend code, public utilities in IDE
   - Run `wix dev` to test in Local Editor
   - If design tweaks are needed, make them in Local Editor and Save
   - Commit updated wix.config.json along with code changes

3. Review phase (GitHub):
   - Use branches and pull requests for code review
   - Use `wix preview` on PRs to generate shareable preview links

4. Publish phase (CLI):
   - Merge to main
   - Run `wix publish` selecting "Latest commit from origin/main"
   - Or set up GitHub Actions to auto-publish on merge
```

### Multi-Contributor Rules

For a team with human + AI agent contributors:

1. **Designate design ownership**: Only one person/role should make design changes at a time. Design changes in the editor generate UI versions, and concurrent design edits from multiple contributors can cause confusion.

2. **Always commit `wix.config.json` after design changes**: After any design work in the Local Editor, commit the updated `wix.config.json` and push it. This keeps the repo's UI version reference in sync.

3. **AI agents should only touch code files**: AI agents writing code should limit changes to:
   - `src/pages/*.js` (page code)
   - `src/backend/*.js` or `*.web.js` (backend code)
   - `src/public/*.js` (public utilities)
   - Never touch `wix.config.json` or `velo.dependencies.json` manually.

4. **Use CLI publish, not editor publish**: CLI publish is more deterministic (uses the UI version from `wix.config.json`). Editor publish uses whatever the latest UI version is, which may not match the code in the repo.

5. **Never rename page code files**: The filename contains an internal ID that Wix uses for binding. Renaming breaks the binding silently.

6. **Never delete page code files from Git to delete pages**: Delete pages from the editor only. The code file will be removed from the repo automatically.

7. **Protect CMS collections**: Field changes take effect immediately on production. Gate CMS schema changes behind a human review step.

### GitHub Actions for CI/CD

Set up two workflows:

1. **Preview on PR**: When a PR is opened, run `wix preview` and post the preview URL as a PR comment.
2. **Publish on merge**: When a PR is merged to `main`, run `wix publish` to auto-deploy.

Authentication: Generate a Wix API key with "Wix CLI for Sites - Git Integration" permission, store it as a GitHub secret (`WIX_CLI_API_KEY`).

```yaml
# Example: Publish on merge to main
name: Publish Site
on:
  push:
    branches: [main]
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm install
      - run: npm run wix login -- --api-key ${{ secrets.WIX_CLI_API_KEY }}
      - run: npm run wix publish
```

### What W9 Studio Cannot Do via Git/CLI

- Create or modify page layouts (must use editor)
- Create CMS collections or modify their schemas (must use editor/CMS dashboard)
- Upload or manage media assets (must use Wix Media Manager)
- Install Wix apps/integrations (must use editor)
- Create new pages (must use editor, then code files auto-generate)
- Manage SEO settings, domain config, site settings (must use dashboard)

---

## 8. Automated Workflows (GitHub Actions)

### Prerequisites

1. Site must be connected to GitHub via Git Integration
2. Wix API key generated from API Keys Manager
3. API key must have "Wix CLI for Sites - Git Integration" site permission
4. API key stored as GitHub repository secret

### Workflow Setup Steps

1. **Generate API key**: Go to Wix API Keys Manager, create key with CLI permissions
2. **Store as secret**: In GitHub repo Settings > Secrets > Actions, create `WIX_CLI_API_KEY`
3. **Install CLI in workflow**: `npm install` (installs `@wix/cli` from repo deps)
4. **Authenticate**: `npm run wix login -- --api-key ${{ secrets.WIX_CLI_API_KEY }}`
5. **Execute commands**: `npm run wix preview` or `npm run wix publish`

### Suggested Workflows

| Trigger | Action | Command |
|---------|--------|---------|
| PR opened/updated | Create preview deployment | `npm run wix preview` |
| Push to main (merge) | Publish site | `npm run wix publish` |

---

## Summary: Key Takeaways for W9 Studio

1. **Git owns code, Wix owns design.** These are fundamentally separate concerns with different versioning systems.
2. **Publishing is always explicit.** Push to main does not auto-publish (unless you set up GitHub Actions to do so).
3. **CLI publish is more predictable than editor publish** because it respects the UI version pinned in `wix.config.json`.
4. **CMS schemas are not in Git.** Collection structures must be managed in the editor/dashboard.
5. **CMS field changes are immediately live.** This is the biggest foot-gun -- schema changes bypass the publish workflow.
6. **Never rename page code files.** The internal ID in the filename is the binding key.
7. **Design changes are not diffable or mergeable.** Treat design as a separate, serialized workflow.
8. **Disconnecting from GitHub is irreversible for that repo.** You can reconnect to GitHub, but a new repo is created.
9. **AI agents should be code-only contributors.** Design changes require the editor and should be human-managed.
10. **Set up GitHub Actions for preview + auto-publish.** This gives you a proper CI/CD pipeline on top of Wix.
