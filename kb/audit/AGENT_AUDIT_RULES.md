# Agent Audit Rules

## Hard Gates for Production Audits

Any audit claiming production readiness or deployment status MUST include the following evidence. Claims without evidence are invalid.

### Required Evidence

1. **Runtime Snapshot Output**
   - Git SHA and branch
   - Submodule status
   - `addons_path` configuration
   - Config file path
   - Container/image info (if Docker)
   - Odoo version

2. **DB Truth Output**
   - List of installed modules with versions
   - Pending upgrades/installs
   - IPAI module states

3. **SHA/Submodule/Config Match Verification**
   - If SHA/submodules/addons_path/config do not match the repo state being reviewed, STOP
   - Report mismatch first before any other findings

4. **Evidence-Backed Findings**
   - Every finding must include: file+line OR command output OR DB output OR log excerpt
   - No assertions without proof

5. **Health Check Evidence**
   - Do not claim a URL is live, healthy, or "running" without a captured health check output
   - Include actual response codes, timestamps, and content hashes

## Generating Evidence

```bash
# Generate runtime snapshot
./tools/audit/snapshot.sh

# Generate DB truth (requires DB access)
psql -h localhost -U odoo -d odoo -f tools/audit/db_truth.sql > audit/db_truth.txt

# Verify artifacts exist
./tools/audit/require_audit_artifacts.sh
```

## CI Integration

Add to `.github/workflows/`:

```yaml
- name: Require audit artifacts
  run: bash tools/audit/require_audit_artifacts.sh
  if: contains(github.event.pull_request.labels.*.name, 'production-ready')
```

## Invalid Audit Patterns

The following patterns indicate an invalid audit:

- "Production is running at..." without health check evidence
- "All modules installed" without DB query output
- "Customization is possible" without specific file/code references
- "No issues found" without specific checks enumerated
- Version claims without `git rev-parse HEAD` output
