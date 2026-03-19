# Policy Gateway - Dataverse Enterprise Console

**Portfolio Initiative**: PORT-2026-012
**Controls**: CTRL-POLICY-001, CTRL-CAPABILITY-001, CTRL-MODEL-001

Policy enforcement middleware for the Dataverse Enterprise Console, implementing Cursor-Enterprise-style control plane patterns.

## Features

### 1. Privacy Mode Enforcement (CTRL-POLICY-001)
- **Pattern**: Cursor's `x-ghost-mode` equivalent
- **Behavior**: Privacy-by-default routing (missing header = privacy ON)
- **Routing**: Dual service (privacy replica vs standard)
- **Storage**: No plaintext code storage in privacy mode

### 2. Model Governance (CTRL-MODEL-001)
- **Allowlist/Blocklist**: Per-organization model policies
- **Enforcement**: Block requests to prohibited models
- **Evidence**: Blocked requests generate evidence artifacts
- **Analytics**: Model usage tracking and reporting

### 3. Capability Validation (CTRL-CAPABILITY-001)
- **Attestation-Based**: Bots must prove capabilities before tool access
- **Evidence Required**: Code scans, test suites, or manual verification
- **Expiry Support**: Time-bound capability attestations
- **Alerts**: Proactive notifications for expiring capabilities

### 4. Real-time Audit Trail
- **Append-Only Log**: All policy decisions logged to `ops.policy_decisions`
- **Evidence Linkage**: Blocked requests linked to evidence artifacts
- **Supabase Realtime**: Live streaming of policy decisions
- **Export**: CSV export for compliance reporting

## Installation

```bash
cd web/policy-gateway
pnpm install
```

## Configuration

Create `.env` file:

```bash
# Supabase Configuration
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<service-role-key>

# Server Configuration
POLICY_GATEWAY_PORT=3000
NODE_ENV=development
```

## Usage

### Development
```bash
pnpm dev
```

### Production
```bash
pnpm build
pnpm start
```

### Testing
```bash
pnpm test
```

## API Endpoints

### Policy Enforcement

**POST `/policy/enforce`** - Main enforcement endpoint
```typescript
{
  org_id: string;
  bot_id: string;
  request_id: string;
  model?: string;
  tool_name?: string;
  headers?: Record<string, string>;
}
```

Response:
```typescript
{
  allowed: boolean;
  reason: string;
  evidence_id?: string;
  route_to?: string;
  metadata?: any;
}
```

### Model Governance

**GET `/api/model-policy/:org_id`** - Get model policies
**POST `/api/model-policy`** - Create/update policy
**DELETE `/api/model-policy/:org_id/:model_name`** - Delete policy
**GET `/api/model-usage/:org_id`** - Get usage stats

### Capability Management

**GET `/api/capabilities/:bot_id`** - Get bot capabilities
**POST `/api/capabilities/attest`** - Attest capability
**GET `/api/capabilities/:bot_id/summary`** - Get status summary

### Audit & Reporting

**GET `/api/audit/decisions`** - Get policy decisions
**GET `/api/audit/metrics`** - Get metrics (allow/block counts)
**GET `/api/audit/violations`** - Get blocked requests
**GET `/api/audit/export`** - Export to CSV

## Privacy Mode Examples

### Default-Safe (Privacy ON)
```bash
curl -X POST http://localhost:3000/policy/enforce \
  -H "Content-Type: application/json" \
  -d '{
    "org_id": "test-org",
    "bot_id": "test-bot",
    "model": "claude-sonnet-4.5"
  }'
```

Response:
```json
{
  "allowed": true,
  "reason": "Privacy mode enforced (default-safe)",
  "route_to": "privacy_safe_replica"
}
```

### Explicit Privacy OFF
```bash
curl -X POST http://localhost:3000/policy/enforce \
  -H "x-privacy-mode: false" \
  -H "Content-Type: application/json" \
  -d '{
    "org_id": "test-org",
    "bot_id": "test-bot",
    "model": "claude-sonnet-4.5"
  }'
```

Response:
```json
{
  "allowed": true,
  "reason": "Standard mode (privacy disabled by header)",
  "route_to": "standard_replica"
}
```

## Model Policy Examples

### Block Model Request
```bash
curl -X POST http://localhost:3000/policy/enforce \
  -H "Content-Type: application/json" \
  -d '{
    "org_id": "test-org",
    "bot_id": "test-bot",
    "model": "gpt-3.5-turbo"
  }'
```

Response:
```json
{
  "allowed": false,
  "reason": "Model gpt-3.5-turbo blocked by org policy: Deprecated model",
  "evidence_id": "EVID-20260213-MODEL-BLOCK"
}
```

### Add Model to Blocklist
```bash
curl -X POST http://localhost:3000/api/model-policy \
  -H "Content-Type: application/json" \
  -d '{
    "org_id": "test-org",
    "model_family": "openai",
    "model_name": "gpt-3.5-turbo",
    "policy_type": "block",
    "reason": "Deprecated model - use claude-sonnet-4.5 instead"
  }'
```

## Capability Validation Examples

### Missing Capability Block
```bash
curl -X POST http://localhost:3000/policy/enforce \
  -H "Content-Type: application/json" \
  -d '{
    "org_id": "test-org",
    "bot_id": "test-bot",
    "tool_name": "execute_shell"
  }'
```

Response:
```json
{
  "allowed": false,
  "reason": "Bot lacks required capabilities: shell_execution",
  "evidence_id": "EVID-20260213-CAPABILITY-MISSING",
  "metadata": {
    "missing_capabilities": ["shell_execution"],
    "remediation": "Attest capabilities via ops.capability_attestations"
  }
}
```

### Attest Capability
```bash
curl -X POST http://localhost:3000/api/capabilities/attest \
  -H "Content-Type: application/json" \
  -d '{
    "bot_id": "test-bot",
    "capability_key": "shell_execution",
    "has_capability": true,
    "attestation_method": "code_scan",
    "attestation_evidence": "docs/evidence/capability-scan.md",
    "validator_id": "admin-user",
    "expiry_days": 90
  }'
```

## Integration with MCP Coordinator

The Policy Gateway is designed to be called by the MCP Coordinator before routing requests:

```typescript
// In mcp/coordinator/app/routing.py

async function routeRequest(requestData) {
  // 1. Policy enforcement (NEW)
  const policyDecision = await fetch('http://policy-gateway:3000/policy/enforce', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestData)
  });

  if (!policyDecision.allowed) {
    return { error: 'Policy violation', ...policyDecision };
  }

  // 2. Existing routing logic continues
  const target = determineTarget(requestData);
  return forwardToTarget(target, requestData, policyDecision.route_to);
}
```

## Evidence System Integration

Blocked requests automatically generate evidence artifacts:

**Evidence ID Format**: `EVID-YYYYMMDD-<POLICY_TYPE>-<ACTION>`
**Evidence Path**: `docs/evidence/<YYYYMMDD-HHMM>/policy-violations/<policy_type>/`

Example:
- **ID**: `EVID-20260213-MODEL-BLOCK`
- **Path**: `docs/evidence/20260213-1500/policy-violations/model-governance/`

## Monitoring & Alerts

### Metrics Endpoint
```bash
curl http://localhost:3000/api/audit/metrics?hours=24
```

Response:
```json
{
  "total": 1543,
  "allowed": 1489,
  "blocked": 48,
  "warned": 6,
  "byPolicyType": {
    "privacy": { "allow": 1200, "block": 0, "warn": 0 },
    "model": { "allow": 234, "block": 34, "warn": 3 },
    "capability": { "allow": 55, "block": 14, "warn": 3 }
  }
}
```

### Recent Violations
```bash
curl http://localhost:3000/api/audit/violations?hours=1&limit=10
```

## Architecture

```
┌─────────────────────────────────────────┐
│     MCP Coordinator (Existing)          │
│  - Context-aware routing                │
│  - A2A coordination                     │
└───────────┬─────────────────────────────┘
            │
            ↓
┌─────────────────────────────────────────┐
│     Policy Gateway (NEW)                │
│  - Privacy Mode Router                  │
│  - Model Allowlist/Blocklist            │
│  - Capability Validation                │
│  - Real-time Audit Log                  │
└───────────┬─────────────────────────────┘
            │
            ↓
┌─────────────────────────────────────────┐
│     Supabase (ops.* schema)             │
│  - model_policy                         │
│  - policy_decisions                     │
│  - capability_attestations              │
│  - privacy_mode_config                  │
└─────────────────────────────────────────┘
```

## Development

### Running Tests
```bash
pnpm test
```

### Type Checking
```bash
pnpm typecheck
```

### Linting
```bash
pnpm lint
```

## Troubleshooting

### Policy Gateway Not Starting
```bash
# Check Supabase connection
curl -X POST http://localhost:3000/policy/enforce \
  -H "Content-Type: application/json" \
  -d '{"org_id": "test", "bot_id": "test"}'

# Expected: 200 OK (if Supabase connected)
# Error 500: Check SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY
```

### Policy Not Enforcing
```bash
# Verify ops.model_policy table exists
psql "$SUPABASE_DB_URL" -c "SELECT * FROM ops.model_policy LIMIT 5;"

# Verify policy_decisions logging
psql "$SUPABASE_DB_URL" -c "SELECT * FROM ops.policy_decisions ORDER BY ts DESC LIMIT 5;"
```

### Blocked Requests Not Creating Evidence
Evidence artifacts are created by the calling service (MCP Coordinator), not the Policy Gateway. The Gateway provides:
- **Evidence ID**: `EVID-*` format
- **Evidence Path**: Suggested path for artifact storage

The caller must write the actual evidence files.

## License

Apache-2.0

## Related Documentation

- **Plan**: `docs/constitution/DATAVERSE_ENTERPRISE_CONSOLE.md`
- **Migration**: `supabase/migrations/20260213_001000_ops_policy_extensions.sql`
- **Traceability**: `docs/TRACEABILITY_INDEX.yaml` (PORT-2026-012)
- **Controls**: CTRL-POLICY-001, CTRL-CAPABILITY-001, CTRL-MODEL-001
