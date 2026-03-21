# CLAUDE.md Alignment Repair — 2026-03-21

## Problem

The CLAUDE.md instruction hierarchy had grown organically:
- Innermost file (`odoo/odoo/odoo/CLAUDE.md`) was **1,925 lines** (10x target)
- `odoo/CLAUDE.md` and `odoo/odoo/CLAUDE.md` were **byte-identical copies** of the monorepo root
- 6 rule families were duplicated **3-5 times** across nested `.claude/rules/` directories
- 10 contradictions between files (deprecated items still active, wrong hosting references)

## Canonical Hierarchy (Post-Repair)

```
~/.claude/CLAUDE.md                       ← Global agent instructions (all projects)
├── ~/.claude/rules/*.md                  ← Global rules (secrets, testing, infra, etc.)
│
/Users/tbwa/CLAUDE.md                     ← Home-level project instructions
│
Insightpulseai/CLAUDE.md                  ← Monorepo root (full operating contract)
├── .claude/rules/*.md                    ← Monorepo rules (platform, security, ssot, etc.)
│
├── odoo/CLAUDE.md                        ← SHIM (inherits from root, no overrides)
│
├── odoo/odoo/CLAUDE.md                   ← SHIM (inherits from root, no overrides)
│
└── odoo/odoo/odoo/CLAUDE.md              ← Odoo CE 19 routing contract (~110 lines)
    └── .claude/rules/*.md                ← Odoo-specific rules (runtime, security, etc.)
```

**Key principle**: Each level inherits from above. Only the leaf (`odoo/odoo/odoo/CLAUDE.md`) and the monorepo root contain substantive content. Mid-level files are 4-line shims.

## Changes Made

### 1. Innermost CLAUDE.md — Slim to 110 Lines

**File**: `odoo/odoo/odoo/CLAUDE.md`
**Before**: 1,925 lines (full EE parity matrix, MCP jobs docs, Supabase guide, BIR tables, Figma, full architecture diagrams)
**After**: 110 lines — thin routing contract with Quick Reference, Odoo Rules, IPAI Naming, pointers to `.claude/rules/*.md`

All heavy content was already present in `.claude/rules/*.md` files — the CLAUDE.md was a kitchen sink duplicate.

### 2. Shim Files Created

| File | Before | After |
|------|--------|-------|
| `odoo/CLAUDE.md` | 177 lines (byte-identical to monorepo root) | 4-line shim |
| `odoo/odoo/CLAUDE.md` | 177 lines (byte-identical to monorepo root) | 4-line shim |

### 3. Duplicate Rules Files Deleted (20 copies)

| Rule Family | Canonical Location | Copies Deleted |
|-------------|-------------------|----------------|
| `platform-architecture.md` | `Insightpulseai/.claude/rules/` | 3 (odoo/, odoo/odoo/, odoo/odoo/odoo/) |
| `repo-topology.md` | `Insightpulseai/.claude/rules/` | 3 |
| `security-baseline.md` | `Insightpulseai/.claude/rules/` | 3 |
| `ssot-platform.md` | `Insightpulseai/.claude/rules/` | 5 (including extra nested copies) |
| `odoo-runtime.md` | `odoo/odoo/odoo/.claude/rules/` | 3 |
| `odoo-security.md` | `odoo/odoo/odoo/.claude/rules/` | 3 |

Before deletion, each copy was diffed against the canonical version. Unique content (if any) was merged into the canonical copy.

### 4. Contradictions Fixed (10 total)

| # | Contradiction | Fix |
|---|-------------|-----|
| 1 | `~/.claude/CLAUDE.md` Web/CMS: "Hybrid: Next.js on Vercel" | → "Azure Container Apps (public + internal), Odoo website" |
| 2 | `~/.claude/CLAUDE.md` missing Mailgun deprecation | Added row |
| 3 | `~/.claude/CLAUDE.md` missing Vercel deprecation | Added row |
| 4 | `~/CLAUDE.md` execution surfaces: "SSH (DO droplet)" | → "SSH, Docker, Supabase CLI, Azure CLI" |
| 5 | `ssot-platform.md` quick-ref: "DO droplet stack" | → "Azure Container Apps" |
| 6 | `odoo/CLAUDE.md` full duplicate | → shim (inherits from root) |
| 7 | `odoo/odoo/CLAUDE.md` full duplicate | → shim (inherits from root) |
| 8 | Python version (3.12+ vs 3.11.x) | Added clarifying note in path-contract.md |
| 9-10 | Duplicate rule files with drifted content | Merged unique content, deleted duplicates |

### 5. Drift Guard Script

**File**: `scripts/validate_claude_alignment.sh`

Checks:
- Innermost CLAUDE.md ≤ 200 lines
- Mid-level files are shims (≤ 10 lines)
- No deprecated strings used actively (DO, Vercel, Mattermost, etc.)
- Each rule family has exactly 1 canonical copy
- Python version references are consistent

Run: `./scripts/validate_claude_alignment.sh`

## Verification

| Check | Result |
|-------|--------|
| `odoo/odoo/odoo/CLAUDE.md` ≤ 200 lines | PASS (110 lines) |
| `odoo/CLAUDE.md` is a shim | PASS (5 lines) |
| `odoo/odoo/CLAUDE.md` is a shim | PASS (5 lines) |
| Each rule family has 1 canonical copy | PASS (6 families verified) |
| 10 contradictions resolved | PASS |
| No active deprecated references | PASS |
| Drift guard script exists | PASS |
