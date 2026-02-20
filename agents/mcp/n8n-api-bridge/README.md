# n8n API Bridge

TypeScript client for the [n8n Public API](https://docs.n8n.io/api/) with MCP server integration.

## Features

- ✅ **Authentication**: API key-based authentication with `X-N8N-API-KEY` header
- ✅ **Error Handling**: Normalized HTTP errors with status codes and details
- ✅ **Mutation Guard**: Environment-controlled write operations
- ✅ **Type Safety**: Full TypeScript types for all API responses
- ✅ **Pagination**: Cursor-based pagination support
- ✅ **Singleton Pattern**: Shared client instance across modules

## Installation

```bash
pnpm install
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `N8N_BASE_URL` | Yes | n8n instance URL (e.g., `https://n8n.insightpulseai.com`) |
| `N8N_API_KEY` | Yes | n8n Public API key |
| `ALLOW_MUTATIONS` | No | Enable write operations (`true`/`false`, default: `false`) |

## Usage

### Basic Client Usage

```typescript
import { getN8nClient } from '@ipai/n8n-api-bridge';

const client = getN8nClient();

// List workflows
const workflows = await client.listWorkflows({ limit: 10 });

// Get workflow detail
const workflow = await client.getWorkflow('workflow-id');

// List executions
const executions = await client.listExecutions({ 
  workflowId: 'workflow-id',
  limit: 20 
});

// Get execution detail
const execution = await client.getExecution('execution-id');

// Retry failed execution (requires ALLOW_MUTATIONS=true)
const retried = await client.retryExecution('execution-id');

// Submit audit event (always allowed)
await client.audit({
  eventName: 'workflow.executed',
  userId: 'user-123',
  metadata: { workflowId: 'workflow-id' }
});
```

### Error Handling

```typescript
import { N8nApiError } from '@ipai/n8n-api-bridge';

try {
  await client.getWorkflow('invalid-id');
} catch (error) {
  if (error instanceof N8nApiError) {
    console.error(`API Error ${error.statusCode}: ${error.message}`);
    console.error('Details:', error.details);
  } else {
    console.error('Unexpected error:', error);
  }
}
```

### Mutation Guard

By default, write operations (`retryExecution`) are blocked to prevent accidental modifications:

```typescript
// This will throw an error
await client.retryExecution('execution-id');
// Error: Mutation operation 'retryExecution' is disabled. Set ALLOW_MUTATIONS=true to enable.
```

Enable mutations via environment variable:

```bash
ALLOW_MUTATIONS=true node your-script.js
```

**Note**: `audit()` is exempt from the mutation guard as it's a read-only logging operation.

## API Reference

### Workflows

#### `listWorkflows(options?)`

List all workflows with optional pagination.

**Options:**
- `limit?: number` - Maximum number of results (default: 100)
- `cursor?: string` - Pagination cursor from previous response

**Returns:** `{ data: Workflow[], nextCursor?: string }`

#### `getWorkflow(id)`

Get detailed workflow by ID including nodes and connections.

**Returns:** `WorkflowDetail`

### Executions

#### `listExecutions(options?)`

List executions with optional filtering and pagination.

**Options:**
- `limit?: number` - Maximum number of results
- `cursor?: string` - Pagination cursor
- `workflowId?: string` - Filter by workflow ID

**Returns:** `{ data: Execution[], nextCursor?: string }`

#### `getExecution(id)`

Get detailed execution by ID including result data.

**Returns:** `ExecutionDetail`

#### `retryExecution(id)`

Retry a failed execution (requires `ALLOW_MUTATIONS=true`).

**Returns:** `ExecutionDetail`

### Audit

#### `audit(event)`

Submit audit event for logging (always allowed, exempt from mutation guard).

**Event:**
- `eventName: string` - Event identifier (required)
- `userId?: string` - User ID associated with event
- `metadata?: Record<string, unknown>` - Additional event data

**Returns:** `void`

## Type Definitions

### Workflow

```typescript
interface Workflow {
  id: string;
  name: string;
  active: boolean;
  createdAt: string;
  updatedAt: string;
  tags?: Array<{ id: string; name: string }>;
}
```

### WorkflowDetail

```typescript
interface WorkflowDetail extends Workflow {
  nodes: Array<{
    id: string;
    name: string;
    type: string;
    position: [number, number];
    parameters?: Record<string, unknown>;
  }>;
  connections?: Record<string, unknown>;
  settings?: Record<string, unknown>;
}
```

### Execution

```typescript
interface Execution {
  id: string;
  workflowId: string;
  mode: 'manual' | 'trigger' | 'webhook' | 'retry';
  startedAt: string;
  stoppedAt?: string;
  status: 'success' | 'error' | 'waiting' | 'canceled' | 'running';
}
```

### ExecutionDetail

```typescript
interface ExecutionDetail extends Execution {
  data?: {
    resultData?: {
      runData?: Record<string, unknown[]>;
      error?: {
        message: string;
        stack?: string;
      };
    };
  };
}
```

## Development

### Build

```bash
pnpm build
```

### Test

```bash
pnpm test
```

### Lint

```bash
pnpm lint
```

### Type Check

```bash
pnpm typecheck
```

## License

MIT
