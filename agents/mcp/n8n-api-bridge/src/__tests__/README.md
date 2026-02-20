# n8n MCP Bridge Test Suite

Comprehensive test suite for the n8n MCP bridge implementation.

## Test Files

### 1. `n8nClient.test.ts`

Tests for the original `n8nClient.ts` implementation.

**Coverage:**
- ✅ Constructor validation (missing env vars, trailing slash removal)
- ✅ Authentication header injection (X-N8N-API-KEY)
- ✅ URL construction (base URL + paths, query parameters)
- ✅ Error normalization (401, 404, 429 status codes)
- ✅ Mutation guard (ALLOW_MUTATIONS check)
- ✅ API methods (listWorkflows, getWorkflow, getExecution, audit)
- ✅ Singleton pattern (getN8nClient, resetN8nClient)
- ✅ N8nApiError class

**Mocking:**
- `node-fetch` fully mocked using vitest mocks
- Environment variables reset per test

### 2. `client.test.ts`

Tests for the enhanced `client.ts` implementation.

**Coverage:**
- ✅ Constructor with N8nConfig object
- ✅ Request timeout handling (AbortController)
- ✅ HTTP methods (GET, POST, PATCH, DELETE)
- ✅ Error handling (JSON extraction, 204 No Content)
- ✅ Mutation guards for all mutation operations
- ✅ Workflow API (list, get, activate, deactivate, trigger)
- ✅ Execution API (list, get, delete, includeData flag)
- ✅ Credentials API (metadata only)
- ✅ Tags API

**Mocking:**
- `node-fetch` fully mocked
- Fake timers for timeout testing

### 3. `integration.test.ts`

Optional integration tests against a real n8n instance.

**Coverage:**
- ✅ Smoke tests (connection, list operations)
- ✅ Error handling (404 errors)
- ✅ Pagination (limit, cursor)
- ✅ Filters (active, tags, status, workflowId)
- ✅ Mutation operations (activate/deactivate workflow)

**Configuration:**
```bash
export N8N_TEST_BASE_URL="https://your-n8n-instance.com"
export N8N_TEST_API_KEY="your-api-key"
export ALLOW_MUTATIONS="false"  # Set to "true" for mutation tests
```

**Behavior:**
- Skipped if credentials not provided (safe for CI without secrets)
- Uses `describe.skipIf()` to conditionally skip all tests
- 10-second timeout for network operations

## Running Tests

### All Tests (Unit Only)
```bash
pnpm test
```

### Watch Mode
```bash
pnpm test:watch
```

### With Coverage
```bash
pnpm test:coverage
```

### Integration Tests Only
```bash
export N8N_TEST_BASE_URL="https://n8n.example.com"
export N8N_TEST_API_KEY="your-key"
pnpm test:integration
```

## Test Configuration

### `vitest.config.ts`
```typescript
export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'dist/',
        '**/*.test.ts',
        '**/*.config.ts',
      ],
    },
  },
});
```

### Coverage Targets
- **Statements:** >80%
- **Branches:** >75%
- **Functions:** >80%
- **Lines:** >80%

## Writing New Tests

### Pattern: Mock fetch response
```typescript
mockedFetch.mockResolvedValueOnce({
  ok: true,
  status: 200,
  json: async () => ({ data: [] }),
} as any);
```

### Pattern: Test error handling
```typescript
mockedFetch.mockResolvedValueOnce({
  ok: false,
  status: 404,
  statusText: 'Not Found',
  text: async () => '{}',
} as any);

await expect(client.getWorkflow('invalid')).rejects.toThrow('Resource not found');
```

### Pattern: Test mutation guard
```typescript
process.env.ALLOW_MUTATIONS = 'false';
const client = new N8nClient();

await expect(client.retryExecution('exec-123')).rejects.toThrow(
  "Mutation operation 'retryExecution' is disabled"
);
```

## CI Integration

Tests run automatically on:
- Push to main/master
- Pull requests
- Pre-commit hooks (if configured)

Integration tests are skipped in CI unless secrets are configured in repository settings.

## Debugging Tests

### Run specific test file
```bash
pnpm vitest run src/__tests__/n8nClient.test.ts
```

### Run specific test suite
```bash
pnpm vitest run -t "Error Normalization"
```

### Enable debug output
```bash
DEBUG=* pnpm test
```

## Dependencies

- **vitest**: ^2.1.8 (test runner)
- **@vitest/coverage-v8**: ^2.1.8 (coverage provider)
- **node-fetch**: ^2.6.7 (HTTP client, mocked in tests)

## Known Issues

1. **Monorepo Setup:** This package is part of a pnpm workspace. Run `pnpm install` from repo root.
2. **Module Resolution:** Ensure `.js` extensions in imports for ESM compatibility.
3. **Timeout Tests:** Use `vi.useFakeTimers()` for deterministic timeout testing.

## Contributing

When adding new functionality:

1. Write tests first (TDD)
2. Ensure >80% coverage
3. Mock all external dependencies
4. Add integration test if applicable
5. Update this README
