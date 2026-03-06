# Azure Target State — Implementation Plan

> Phased migration to GitHub-primary with Azure DevOps minimization.

## Phase 1: Audit & Freeze (Week 1)
- Inventory all Azure DevOps assets (repos, pipelines, wikis, boards)
- Freeze creation of new Azure DevOps assets
- Document current sync flows between platforms

## Phase 2: Repo Consolidation (Week 2-3)
- Mirror remaining Azure repos to GitHub
- Update all CI/CD references to point to GitHub
- Archive Azure repos (read-only)

## Phase 3: Pipeline Migration (Week 3-4)
- Convert Azure Pipelines to GitHub Actions
- Validate all builds pass on GitHub Actions
- Disable Azure Pipelines

## Phase 4: Documentation Consolidation (Week 4-5)
- Extract Azure Wiki content to in-repo docs
- Update all links and references
- Archive Azure Wiki

## Phase 5: Boards Decision (Week 5-6)
- Evaluate if Azure Boards adds value over GitHub Projects + Plane
- If yes: configure one-way sync (GitHub → Azure Boards)
- If no: migrate board content to Plane, decommission Azure DevOps entirely
