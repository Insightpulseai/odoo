# C-TOOLS-PERMISSIONS-01 — Agent Tool Permissions Contract

**Contract ID**: C-TOOLS-PERMISSIONS-01
**Status**: ✅ Active
**Source SSOT**: `ssot/tools/registry.yaml`
**Consumer**: All IPAI agent skills (`ssot/agents/skills.yaml`)
**Validator**: `scripts/ci/validate_skills_registry.py` (via `agent-skills-gate.yml`)
**Last updated**: 2026-03-02

---

## Purpose

This contract defines the boundary between the tool registry (what tools exist and who
may invoke them) and the agent skills registry (what each skill is permitted to do).

A skill that is not listed in a tool's `allowed_in_skills` must not invoke that tool at
runtime. The CI validator enforces this constraint at PR time.

---

## Source SSOT: `ssot/tools/registry.yaml`

The tool registry is the single source of truth for:

1. Which tools exist (`id` — unique kebab-case identifier)
2. What executor type each tool targets (`supabase_rpc`, `github_api`, `slack_api`, `mcp_api`, `edge_fn`, `repo_fs`)
3. Which skills are permitted to use each tool (`allowed_in_skills`)
4. Whether a human approval gate is required (`requires_human_approval`)
5. Observable side effects produced by each tool invocation (`side_effects`)
6. Filesystem paths each tool may access (`sensitive_paths`)

**Key invariant**: `ssot/tools/registry.yaml` is **append-only**.
To disable a tool, set `allowed_in_skills: []`; never delete the entry.
Deletion breaks the audit trail of which skills used which tools historically.

---

## Consumer: `ssot/agents/skills.yaml`

Each skill entry must declare:

```yaml
allowed_tools:
  - <tool_id>   # must exist in ssot/tools/registry.yaml
```

The special value `"__none__"` is allowed for read-only diagnostic skills that call no
external tools.

---

## Enforcement Rules

| Rule | Validator check | Failure message |
|------|-----------------|-----------------|
| Tool ID exists in registry | `validate_skills_registry.py` cross-ref | `'{tool_id}' not found in ssot/tools/registry.yaml` |
| Skill is in tool's `allowed_in_skills` | `validate_skills_registry.py` cross-ref | `tool '{tool_id}' does not list skill '{sid}' in its allowed_in_skills` |
| `security` block present and complete | `validate_skills_registry.py` | `required field missing (see ssot/agents/interface_schema.yaml for defaults)` |
| `path_traversal_guard: true` for `repo_*` tools | Runtime executor | `403 PATH_TRAVERSAL` |
| `symlink_guard: true` for `repo_write_file` | Runtime executor | `403 SYMLINK_TRAVERSAL` |
| No secret values in `data jsonb` (ops.run_events) | `metadata_escaping: true` | Runtime sanitizer redacts secret-shaped strings |

---

## Permitted Tool Categories (as of 2026-03-02)

| Category | Tool IDs | Side effects |
|----------|----------|--------------|
| Supabase ops RPC | `ops_start_run`, `ops_log_event`, `ops_complete_run`, `ops_fail_run`, `ops_add_artifact`, `ops_write_convergence_finding` | `ops.*` table writes |
| GitHub API | `github_read_issue`, `github_open_pr`, `github_read_ci_run` | PR creation (write); others read-only |
| Plane/MCP API | `mcp_plane_read_issue`, `mcp_plane_create_issue` | Issue creation (write); read read-only |
| Slack | `slack_post_ops_alert`, `slack_post_approval_request` | Channel messages |
| Edge Functions | `edge_fn_convergence_scan` | Convergence findings via Edge Function |
| Repo filesystem | `repo_read_file`, `repo_write_file` | File creation/modification in working tree |

---

## Human-Gated Tools

The following tools set `requires_human_approval: true`:

| Tool ID | Approval channel | Timeout |
|---------|-----------------|---------|
| `slack_post_approval_request` | `#ops-approvals` | 24h — run marked `failed` on timeout |

Implementors must not bypass the approval gate by calling lower-level tools directly.

---

## Relationship to `prod_policy.yaml`

This contract **refines** (not replaces) the global
[`ssot/agents/prod_policy.yaml`](../../ssot/agents/prod_policy.yaml)
`forbidden_actions` list.  `prod_policy.yaml` defines what agents may never do;
this contract defines what tools exist and which skills may use them.

Both constraints must be satisfied simultaneously.

---

## Invariants

1. **Every tool invoked by a skill must exist in `ssot/tools/registry.yaml`.**
2. **A skill must appear in the tool's `allowed_in_skills` list (or the list is `["*"]`).**
3. **Every skill must declare `security.path_traversal_guard: true` before using any `repo_*` tool.**
4. **Tool registry is append-only; use `allowed_in_skills: []` to disable.**
5. **`requires_human_approval: true` tools block run progression until acknowledged.**

---

## Adding a New Tool

1. Add an entry to `ssot/tools/registry.yaml` with all required fields.
2. Add the tool to `allowed_in_skills` in each skill that needs it.
3. Run `python scripts/ci/validate_skills_registry.py` locally to verify.
4. Open a PR — CI gate `agent-skills-gate.yml` must pass before merge.

---

## References

- Source: [`ssot/tools/registry.yaml`](../../ssot/tools/registry.yaml)
- Schema: [`ssot/agents/interface_schema.yaml`](../../ssot/agents/interface_schema.yaml)
- Skills: [`ssot/agents/skills.yaml`](../../ssot/agents/skills.yaml)
- Policy: [`ssot/agents/prod_policy.yaml`](../../ssot/agents/prod_policy.yaml)
- Validator: [`scripts/ci/validate_skills_registry.py`](../../scripts/ci/validate_skills_registry.py)
- CI gate: [`.github/workflows/agent-skills-gate.yml`](../../.github/workflows/agent-skills-gate.yml)
