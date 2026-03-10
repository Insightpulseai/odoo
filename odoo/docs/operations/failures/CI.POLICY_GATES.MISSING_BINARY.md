# Policy Gates: Missing Binary (exit 127)

**Failure code**: `CI.POLICY_GATES.MISSING_BINARY`
**Severity**: medium
**CI behavior**: non-blocking until fixed
**SSOT**: `ssot/errors/failure_modes.yaml`

---

## What it means

The `policy-violation-gate.yml` workflow exited with code 127. Exit code 127 means
the shell could not find the command or script it was asked to run. This is a runner
environment problem, not a policy violation.

---

## Likely causes

1. **Script not found**: `scripts/gates/scan-policy-violations.sh` does not exist
   in the repo or was moved without updating the workflow.

2. **Tool not installed**: The script depends on a binary (e.g., `jq`, `supabase`)
   that is not present in the `ubuntu-latest` runner or was not installed in a prior step.

3. **PATH not set**: The install step ran but did not export the binary to `$GITHUB_PATH`.

---

## Deterministic fix

### Step 1 — Confirm the script exists in the repo

```bash
ls -la scripts/gates/scan-policy-violations.sh
```

If missing, find the script under a different path:
```bash
find scripts/ -name "scan-policy-violations*" 2>/dev/null
```

Update the workflow step if the path changed:
```yaml
# In .github/workflows/policy-violation-gate.yml:
run: bash scripts/gates/scan-policy-violations.sh
# change to the correct path
```

### Step 2 — Identify which binary is missing

Add a debug step immediately before the failing step in the workflow:
```yaml
- name: Debug PATH and tools
  run: |
    echo "PATH=$PATH"
    which bash jq supabase 2>&1 || true
    ls scripts/gates/ 2>/dev/null || echo "scripts/gates/ not found"
```

Re-run the workflow with `gh run rerun` to see the output.

### Step 3 — Add missing install step

If `supabase` CLI is missing:
```yaml
- name: Setup Supabase CLI
  run: |
    curl -o- https://raw.githubusercontent.com/supabase/cli/main/install.sh | bash
    echo "$HOME/.supabase/bin" >> $GITHUB_PATH
```

If `jq` is missing (should be pre-installed on ubuntu-latest, but confirm):
```yaml
- name: Install jq
  run: sudo apt-get install -y jq
```

### Step 4 — Verify the gate passes

```bash
# Locally (if script exists):
bash scripts/gates/scan-policy-violations.sh
echo "Exit code: $?"
```

---

## Prevention

The gate workflow already has `continue-on-error: true` on the scan step, so a
missing binary does not block PRs. Additionally, path filtering ensures the gate
only triggers on relevant paths:

```yaml
on:
  pull_request:
    paths:
      - 'ssot/**'
      - 'supabase/migrations/**'
      - 'infra/**'
      - '.github/workflows/**'
```

PRs touching only app code (e.g., `apps/`, `addons/`) will skip this gate entirely.

---

## Related files

- `.github/workflows/policy-violation-gate.yml`
- `scripts/gates/scan-policy-violations.sh`
- `ssot/errors/failure_modes.yaml` (entry: `CI.POLICY_GATES.MISSING_BINARY`)
