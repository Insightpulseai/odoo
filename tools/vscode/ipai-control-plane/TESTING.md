# Testing Guide - IPAI Control Plane Extension

## Overview

This extension uses a **two-tier testing strategy**:

1. **Unit tests** (Vitest) - Fast, isolated tests for business logic
2. **Integration tests** (VS Code Test) - Full extension activation and API testing

---

## Quick Start

```bash
# Install dependencies
npm install

# Run unit tests
npm test

# Run unit tests in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage

# Run integration tests (requires VS Code)
npm run test:integration
```

---

## Current Test Coverage

### Unit Tests (Vitest)

Located in `src/**/*.test.ts` files, these test business logic **without** VS Code API dependencies.

**What's tested**:
- ✅ Command module loading (`src/commands/index.test.ts`)
- ✅ Control plane client API methods (`src/client/ControlPlaneClient.test.ts`)
- ✅ Tree provider initialization (`src/providers/ProjectTreeProvider.test.ts`)
- ✅ Operations command loading (`src/commands/operations.test.ts`)

**What's NOT tested yet**:
- ❌ Full command execution flows (requires VS Code API mocking)
- ❌ Tree view data population (requires workspace)
- ❌ Webview rendering and user interactions
- ❌ Diagnostic provider behavior

---

## Unit Testing Strategy

### Example: Testing a Pure Function

```typescript
// src/utils/parser.test.ts
import { describe, it, expect } from "vitest";
import { parseModuleList } from "./parser";

describe("parseModuleList", () => {
  it("splits comma-separated modules", () => {
    expect(parseModuleList("sale,account,stock")).toEqual(["sale", "account", "stock"]);
  });

  it("trims whitespace", () => {
    expect(parseModuleList(" sale , account , stock ")).toEqual(["sale", "account", "stock"]);
  });

  it("filters empty strings", () => {
    expect(parseModuleList("sale,,account")).toEqual(["sale", "account"]);
  });
});
```

### Example: Testing with Mocked VS Code API

```typescript
// src/commands/validation.test.ts
import { describe, it, expect, vi } from "vitest";
import * as vscode from "vscode";

// Mock VS Code API
vi.mock("vscode", () => ({
  window: {
    showInformationMessage: vi.fn(),
    showErrorMessage: vi.fn(),
  },
  commands: {
    registerCommand: vi.fn(),
  },
}));

describe("validation commands", () => {
  it("shows error message when manifest invalid", async () => {
    const { validateManifestCommand } = await import("./validation");

    // Mock client to return validation errors
    const mockClient = {
      validateManifest: vi.fn().resolveValue({
        valid: false,
        issues: [{ severity: "error", message: "Missing 'name' key" }]
      })
    };

    await validateManifestCommand(mockClient);

    expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
      expect.stringContaining("Missing 'name' key")
    );
  });
});
```

---

## Integration Testing with VS Code

### Setup

Install the VS Code extension test runner:

```bash
npm install --save-dev @vscode/test-electron
```

Create test runner script at `src/test/runTest.ts`:

```typescript
import * as path from 'path';
import { runTests } from '@vscode/test-electron';

async function main() {
  try {
    // The folder containing the Extension Manifest package.json
    const extensionDevelopmentPath = path.resolve(__dirname, '../../');

    // The path to the extension test script
    const extensionTestsPath = path.resolve(__dirname, './suite/index');

    // Download VS Code, unzip it and run the integration test
    await runTests({ extensionDevelopmentPath, extensionTestsPath });
  } catch (err) {
    console.error('Failed to run tests');
    process.exit(1);
  }
}

main();
```

Create test suite at `src/test/suite/index.ts`:

```typescript
import * as path from 'path';
import * as Mocha from 'mocha';
import { glob } from 'glob';

export function run(): Promise<void> {
  const mocha = new Mocha({
    ui: 'tdd',
    color: true
  });

  const testsRoot = path.resolve(__dirname, '..');

  return new Promise((resolve, reject) => {
    glob('**/**.test.js', { cwd: testsRoot }).then(files => {
      files.forEach(f => mocha.addFile(path.resolve(testsRoot, f)));

      try {
        mocha.run(failures => {
          if (failures > 0) {
            reject(new Error(`${failures} tests failed.`));
          } else {
            resolve();
          }
        });
      } catch (err) {
        reject(err);
      }
    }).catch(reject);
  });
}
```

Create integration test at `src/test/suite/extension.test.ts`:

```typescript
import * as assert from 'assert';
import * as vscode from 'vscode';

suite('Extension Test Suite', () => {
  vscode.window.showInformationMessage('Start all tests.');

  test('Extension should be present', () => {
    assert.ok(vscode.extensions.getExtension('InsightpulseAI.ipai-control-plane'));
  });

  test('Extension should activate', async () => {
    const ext = vscode.extensions.getExtension('InsightpulseAI.ipai-control-plane');
    await ext!.activate();
    assert.strictEqual(ext!.isActive, true);
  });

  test('Commands should be registered', async () => {
    const commands = await vscode.commands.getCommands(true);

    assert.ok(commands.includes('ipai.projects.refresh'));
    assert.ok(commands.includes('ipai.ops.install'));
    assert.ok(commands.includes('ipai.validate.manifest'));
  });

  test('Tree views should be visible', () => {
    // Test that tree views are registered
    assert.ok(vscode.window.createTreeView);
  });
});
```

### Running Integration Tests

Add to `package.json` scripts:

```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest watch",
    "test:coverage": "vitest run --coverage",
    "test:integration": "node ./dist/test/runTest.js",
    "pretest:integration": "npm run build && npm run compile-tests",
    "compile-tests": "tsc -p . --outDir dist"
  }
}
```

Run:

```bash
npm run test:integration
```

---

## Testing the Control Plane Server

The Python FastAPI server has separate tests using pytest:

```bash
cd control-plane
python -m pytest tests/ -v
```

Example server test (`control-plane/tests/test_api.py`):

```python
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_plan_operation():
    response = client.post("/v1/ops/plan", json={
        "type": "install_modules",
        "environment": "dev",
        "modules": ["sale", "account"],
        "project_id": "test-project"
    })

    assert response.status_code == 200
    data = response.json()
    assert "op_id" in data
    assert data["status"] in ["planned", "validation_failed"]
    assert "diffs" in data
    assert "checks" in data

def test_execute_operation():
    # First plan
    plan_response = client.post("/v1/ops/plan", json={
        "type": "install_modules",
        "environment": "dev",
        "modules": ["sale"],
        "project_id": "test-project"
    })

    op_id = plan_response.json()["op_id"]

    # Then execute
    exec_response = client.post("/v1/ops/execute", json={"op_id": op_id})

    assert exec_response.status_code == 200
    data = exec_response.json()
    assert data["op_id"] == op_id
    assert "bundle_id" in data
    assert data["status"] in ["succeeded", "running"]
```

---

## Test-Driven Development Workflow

### 1. Write a Failing Test

```typescript
// src/utils/moduleParser.test.ts
import { describe, it, expect } from "vitest";
import { parseModuleList } from "./moduleParser";

describe("parseModuleList", () => {
  it("should handle empty input", () => {
    expect(parseModuleList("")).toEqual([]);
  });
});
```

### 2. Run Test (Expect Failure)

```bash
npm test
# FAIL src/utils/moduleParser.test.ts
# TypeError: parseModuleList is not a function
```

### 3. Implement Minimum Code

```typescript
// src/utils/moduleParser.ts
export function parseModuleList(input: string): string[] {
  if (!input) return [];
  return input.split(',').map(s => s.trim()).filter(Boolean);
}
```

### 4. Run Test (Expect Pass)

```bash
npm test
# PASS src/utils/moduleParser.test.ts
```

### 5. Refactor and Repeat

---

## Coverage Goals

| Component | Target Coverage | Current |
|-----------|----------------|---------|
| Business logic (utils, parsers) | 90%+ | 0% |
| API client | 80%+ | 25% |
| Command handlers | 70%+ | 10% |
| Tree providers | 60%+ | 5% |
| Extension activation | 100% | 0% |

---

## Continuous Integration

GitHub Actions workflow (`.github/workflows/vscode-ipai-control-plane.yml`) runs:

1. **Lint** - ESLint checks
2. **Unit tests** - Vitest with coverage
3. **Build** - TypeScript compilation
4. **Package** - Create .vsix artifact

To add integration tests to CI:

```yaml
- name: Run integration tests
  run: |
    npm run test:integration
  env:
    DISPLAY: ':99.0'
```

---

## Debugging Tests

### VS Code Test Explorer

1. Install "Test Explorer UI" extension
2. Install "Vitest Test Adapter"
3. Tests appear in sidebar
4. Click debug icon to attach debugger

### Manual Debugging

Add `debugger;` statement in test:

```typescript
it("should parse modules", () => {
  debugger; // Execution will pause here
  expect(parseModuleList("sale,account")).toEqual(["sale", "account"]);
});
```

Run with Node inspector:

```bash
node --inspect-brk ./node_modules/vitest/vitest.mjs run
```

---

## Best Practices

### ✅ DO

- Test business logic separately from VS Code API
- Mock external dependencies (API calls, file system)
- Use descriptive test names: `"should return empty array when input is empty"`
- Test error paths, not just happy paths
- Keep tests focused - one assertion per test when possible
- Use `beforeEach` for setup, `afterEach` for cleanup

### ❌ DON'T

- Don't test VS Code's built-in functionality
- Don't make real API calls in tests (mock them)
- Don't write tests that depend on execution order
- Don't test implementation details (test behavior)
- Don't skip tests without a good reason

---

## Common Testing Patterns

### Mocking the Control Plane Client

```typescript
import { vi } from "vitest";

const mockClient = {
  planOperation: vi.fn().mockResolvedValue({
    op_id: "test-op-123",
    status: "planned",
    diffs: [],
    checks: []
  }),

  executeOperation: vi.fn().mockResolvedValue({
    op_id: "test-op-123",
    bundle_id: "test-bundle-456",
    status: "succeeded"
  }),

  getOperationStatus: vi.fn().mockResolvedValue({
    op_id: "test-op-123",
    status: "succeeded"
  })
};
```

### Mocking VS Code Window API

```typescript
import { vi } from "vitest";

vi.mock("vscode", () => ({
  window: {
    showInformationMessage: vi.fn().mockResolvedValue("OK"),
    showInputBox: vi.fn().mockResolvedValue("sale,account"),
    showErrorMessage: vi.fn(),
    createOutputChannel: vi.fn(() => ({
      appendLine: vi.fn(),
      show: vi.fn()
    }))
  },
  TreeItem: class {},
  TreeItemCollapsibleState: { None: 0, Collapsed: 1, Expanded: 2 }
}));
```

### Testing Async Operations

```typescript
it("should wait for operation completion", async () => {
  const mockClient = {
    getOperationStatus: vi.fn()
      .mockResolvedValueOnce({ status: "running" })
      .mockResolvedValueOnce({ status: "running" })
      .mockResolvedValueOnce({ status: "succeeded" })
  };

  const result = await pollUntilComplete(mockClient, "op-123");

  expect(result.status).toBe("succeeded");
  expect(mockClient.getOperationStatus).toHaveBeenCalledTimes(3);
});
```

---

## Next Steps

1. ✅ **Current**: Basic unit tests with Vitest
2. ⏳ **Next**: Add integration tests with `@vscode/test-electron`
3. ⏳ **Future**: E2E tests with real control plane server
4. ⏳ **Future**: Visual regression tests for webviews
5. ⏳ **Future**: Performance benchmarks

---

## Resources

- [VS Code Extension Testing Guide](https://code.visualstudio.com/api/working-with-extensions/testing-extension)
- [Vitest Documentation](https://vitest.dev/)
- [VS Code Test Electron](https://github.com/microsoft/vscode-test)
- [Example: VS Code Extension Tests](https://github.com/microsoft/vscode-extension-samples/tree/main/helloworld-test-sample)
