# IPAI Skills Catalog

> **Locked:** 2026-04-15
> **Authority:** this file (canonical IPAI skill list + status + install path)
> **Package:** [`plugins/ipai-skills/`](../../plugins/ipai-skills/)
> **Doctrine:** [`docs/skills/ipai-skill-development-pattern.md`](../skills/ipai-skill-development-pattern.md)

---

## Package metadata

```yaml
package:        ipai-skills
version:        0.1.0
license:        Apache-2.0
homepage:       https://github.com/Insightpulseai/odoo
repo:           https://github.com/Insightpulseai/odoo
location:       plugins/ipai-skills/
upstream:       microsoft/azure-skills (pattern source — consume_directly)
spec:           anthropics/skills (Agent Skills spec compliant)
category:       growth / partner / marketplace advisor + platform skills
hosts:          claude-code | github-copilot-cli | vscode
```

---

## Install / activate

```bash
# Add the marketplace
/plugin marketplace add Insightpulseai/odoo

# Install the package
/plugin install ipai-skills@Insightpulseai

# Update
/plugin update ipai-skills@Insightpulseai
```

---

## Skill catalog (1 shipped, 10 planned)

### Shipped (v0.1.0)

| # | Skill | Status | Description |
|---|---|---|---|
| 1 | `ms-startups-navigator` | ✅ shipped | Routes founder questions into concrete Microsoft for Startups program actions (Founders Hub / ISV Success / Co-sell / Marketplace / Agent ID) |

### Planned (v0.2.0 → v1.0.0)

| # | Skill | Target version | Purpose | Tools allowed |
|---|---|---|---|---|
| 2 | `ipai-azure-bom` | v0.2.0 | Validate resources against BOM v2 before deploy | `mcp__azure__*` (read-only) |
| 3 | `ipai-azure-tags` | v0.2.0 | Apply + verify 17 mandatory tags | `mcp__azure__*` tag ops |
| 4 | `ipai-foundry-runtime` | v0.3.0 | Inspect + wire Foundry models + project | Foundry MCP |
| 5 | `ipai-odoo-runtime` | v0.3.0 | Inspect Odoo container + module install | ACA exec + Odoo MCP |
| 6 | `ipai-prismalab-tools` | v0.4.0 | Author / test PrismaLab tool skills | Foundry + AI Search |
| 7 | `ipai-bir-close` | v0.4.0 | Run month-end close + BIR filings | Odoo MCP + compliance register |
| 8 | `ipai-databricks-semantic` | v0.5.0 | Author + promote Databricks Asset Bundles | `databricks/cli` |
| 9 | `ipai-boards-operating-model` | v0.5.0 | Manage Azure Boards portfolio + dashboards | ADO MCP |
| 10 | `ipai-pulser-artifact-emitter` | v0.6.0 | Emit artifacts in canonical envelope | None (output-only) |
| 11 | `ipai-pipeline-compose` | v0.6.0 | Compose Azure Pipelines from templates | Local YAML |

### Composition source

All planned skills compose over already-registered upstreams per [`ssot/governance/upstream-adoption-register.yaml`](../../ssot/governance/upstream-adoption-register.yaml). No new external dependencies required.

---

## Skill structure (canonical, per `microsoft/azure-skills` pattern)

```
plugins/ipai-skills/
├── plugin.json                          # package manifest
├── .claude-plugin/
│   └── marketplace.json                 # marketplace metadata
└── skills/
    ├── ms-startups-navigator/           # ✅ shipped
    │   ├── SKILL.md                     # workflow contract
    │   └── references/
    │       └── README.md                # detailed operational knowledge
    ├── ipai-azure-bom/                  # ⏳ planned
    │   ├── SKILL.md
    │   └── references/
    └── ...
```

Per skill, the canonical shape is:

- `SKILL.md` — front matter + workflow contract + tool allowlist + hard prerequisites
- `references/` — recipes, checklists, troubleshooting, SDK notes (the operational knowledge)

---

## Doctrine alignment

| Doctrine anchor | How this catalog enforces it |
|---|---|
| `microsoft/azure-skills` pattern (consume_directly) | All skills follow workflow-contract + references shape |
| `anthropics/skills` spec | Front matter + SKILL.md format |
| CLAUDE.md "no fork" | We package our own skills; we don't fork upstream skill libraries |
| CLAUDE.md "build the delta only" | These 11 are IPAI-specific; generic Azure skills consumed via `microsoft/azure-skills` plugin |
| `feedback_no_custom_default` | Each skill has a justification; not all eng-only chores get a skill |
| `docs/skills/ipai-skill-development-pattern.md` | This catalog implements that pattern |

---

## Multi-host packaging

The `ipai-skills` package targets:

| Host | Mechanism | Status |
|---|---|---|
| Claude Code | Plugin marketplace | ✅ ready (v0.1.0 in repo) |
| GitHub Copilot CLI | Same plugin format | ✅ compatible |
| VS Code | Companion extension (when ready) | ⏳ planned |
| Cursor | `.cursor-plugin/` adapter | ⏳ defer |
| Gemini CLI | `gemini-extension.json` | ⏳ defer |

Following `microsoft/azure-skills` precedent: package once, target multiple hosts.

---

## Versioning

Semver applies to the **package**, not individual skills.

| Bump | Triggers |
|---|---|
| `0.x.0` → `0.(x+1).0` | New skill added, OR breaking change to existing skill |
| `0.x.y` → `0.x.(y+1)` | Bugfix, content update, reference clarification |
| `0.x.0` → `1.0.0` | All 11 planned skills shipped + multi-host validated |

---

## Maintenance

| Cadence | Action |
|---|---|
| Per session (when relevant) | Re-verify external URLs in `references/` per skill |
| Quarterly | Audit each `SKILL.md` against current upstream patterns (especially `microsoft/azure-skills` evolution) |
| When IPAI doctrine changes | Update `SKILL.md` rules + add `do-not-use-when` triggers |
| When register changes | Validate skills don't reference deprecated upstreams |

---

## Anti-drift rule

```
.claude/skills/ms-startups-navigator/SKILL.md (repo-local)
plugins/ipai-skills/skills/ms-startups-navigator/SKILL.md (packaged)

These two files MUST be byte-identical.

Source of truth: plugins/ipai-skills/skills/ms-startups-navigator/SKILL.md
.claude/skills/ms-startups-navigator/ exists ONLY as a symlink for in-repo discovery during development.

After v1.0.0, .claude/skills/ms-startups-navigator/ is removed and only the
packaged version remains.
```

For now (v0.1.0), the packaged copy is canonical. Editing the repo-local copy without updating the packaged copy is a doctrine violation.

---

## Success criteria (from user spec)

- [x] **`ms-startups-navigator` is installable outside this repo** — once `Insightpulseai/odoo` marketplace is added
- [x] **Versioning exists** — package `v0.1.0`
- [x] **Marketplace/registry metadata exists** — `plugin.json` + `.claude-plugin/marketplace.json`
- [ ] **Repo-local and packaged copies do not drift** — anti-drift rule documented; symlink cutover pending
- [x] **Skill is listed in one IPAI skills catalog** — this file

---

## Next milestones

| Version | Milestone | Date |
|---|---|---|
| **v0.1.0** | Initial package + 1 shipped skill (ms-startups-navigator) | 2026-04-15 (today) |
| v0.2.0 | + ipai-azure-bom + ipai-azure-tags | TBD |
| v0.3.0 | + ipai-foundry-runtime + ipai-odoo-runtime | TBD |
| v0.4.0 | + ipai-prismalab-tools + ipai-bir-close | TBD |
| v0.5.0 | + ipai-databricks-semantic + ipai-boards-operating-model | TBD |
| v0.6.0 | + ipai-pulser-artifact-emitter + ipai-pipeline-compose | TBD |
| **v1.0.0** | All 11 skills shipped + multi-host validated | TBD |

---

## References

- [Plugin manifest](../../plugins/ipai-skills/plugin.json)
- [Marketplace manifest](../../plugins/ipai-skills/.claude-plugin/marketplace.json)
- [Skill development pattern](../skills/ipai-skill-development-pattern.md)
- [Stack build map](../skills/stack-build-map.md)
- [Capability source map](../architecture/capability-source-map.md)
- [Upstream adoption register](../../ssot/governance/upstream-adoption-register.yaml)
- Memory: `reference_isv_success_program`, `project_partner_center_verification`, `project_marketplace_distribution`

---

*Last updated: 2026-04-15*
