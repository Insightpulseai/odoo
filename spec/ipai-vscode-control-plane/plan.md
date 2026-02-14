# ipai-vscode-control-plane — Technical Plan

## 1. Architecture Overview

### 1.1 Three-Layer Model

```
┌─────────────────────────────────────────────────┐
│ Layer 1: VS Code Extension (TS)                │
│  - Command handlers                             │
│  - Tree providers                               │
│  - Diagnostic providers                         │
│  - Diff previewers                              │
│  Role: Stateless UI surface                    │
└────────────────┬────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────┐
│ Layer 2: Control Plane API (Node/Python)       │
│  - Project registry                             │
│  - Environment manager                          │
│  - Validator engine                             │
│  - Diff generators                              │
│  - Evidence bundler                             │
│  - AI relay orchestrator                        │
│  Role: Business logic + orchestration          │
└────────────────┬────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────┐
│ Layer 3: Runtime Targets                       │
│  - Odoo DBs (dev/stage/prod)                   │
│  - Supabase ops schema                          │
│  - CI pipelines (GitHub Actions)                │
│  - File system (specs, evidence)                │
│  Role: State + execution                       │
└─────────────────────────────────────────────────┘
```

**Critical invariant**: Extension has ZERO business logic. All decisions happen in Layer 2.

---

## 2. Control Plane API Contract

### 2.1 Core Concepts

```typescript
// Project = Odoo instance + addon set
interface Project {
  id: string;              // e.g., "tbwa-finance"
  repo_root: string;
  environments: Environment[];
  spec_bundles: SpecBundle[];
}

// Environment = isolated runtime state
interface Environment {
  name: string;            // dev | stage | prod
  db_name: string;
  odoo_version: string;
  modules_installed: string[];
  schema_hash: string;
  last_deploy: ISO8601;
  health: HealthStatus;
  pending_migrations: Migration[];
}

// Operation = deterministic state transition
interface Operation {
  type: OperationType;
  target_env: string;
  spec_bundle?: string;    // optional link to spec
  diffs: Diff[];
  validators: Validator[];
  evidence_path: string;
}

// Evidence = immutable audit trail
interface EvidenceBundle {
  timestamp: ISO8601;
  operation: Operation;
  plan: string;            // markdown
  diffs: Diff[];
  validation_results: ValidationResult[];
  logs: string;
  artifacts: ArtifactRef[];
}
```

### 2.2 API Endpoints (Local Server)

Control Plane runs as **local HTTP server** (Node/Python) that extension calls.

```yaml
# Project & Environment Discovery
GET  /api/projects
GET  /api/projects/:id/environments
GET  /api/projects/:id/environments/:env/status

# Validation (read-only)
POST /api/validate/manifest
POST /api/validate/xml
POST /api/validate/security
POST /api/validate/schema-drift

# Operations (write, gated)
POST /api/operations/install-modules
POST /api/operations/run-migration
POST /api/operations/upgrade-odoo
POST /api/operations/rollback

# Evidence
GET  /api/evidence/:bundle_id
POST /api/evidence/generate

# AI Relay
POST /api/ai/generate-patch
POST /api/ai/explain-drift
POST /api/ai/plan-upgrade
```

**Authentication**: Local only (no auth), or optionally via local token file.

---

## 3. VS Code Extension Implementation

### 3.1 Package Structure

```
tools/vscode/ipai-vscode-control-plane/
├── src/
│   ├── extension.ts              # Entry point
│   ├── commands/
│   │   ├── projects.ts
│   │   ├── operations.ts
│   │   ├── validators.ts
│   │   └── ai.ts
│   ├── providers/
│   │   ├── ProjectTreeProvider.ts
│   │   ├── DiagnosticProvider.ts
│   │   └── DiffPreviewProvider.ts
│   ├── client/
│   │   └── ControlPlaneClient.ts  # API client
│   └── config/
│       └── settings.ts
├── package.json
├── tsconfig.json
└── README.md
```

### 3.2 Command Registration

```typescript
// src/extension.ts
export function activate(context: vscode.ExtensionContext) {
  const client = new ControlPlaneClient(getApiUrl());

  // Project commands
  registerCommand('ipai.projects.refresh', refreshProjects);
  registerCommand('ipai.projects.select', selectProject);

  // Environment commands
  registerCommand('ipai.env.deploy', deployToEnv);
  registerCommand('ipai.env.rollback', rollbackEnv);
  registerCommand('ipai.env.shell', openShell);
  registerCommand('ipai.env.logs', tailLogs);

  // Validation commands
  registerCommand('ipai.validate.manifest', validateManifest);
  registerCommand('ipai.validate.xml', validateXml);
  registerCommand('ipai.validate.security', validateSecurity);
  registerCommand('ipai.validate.all', validateAll);

  // Operation commands
  registerCommand('ipai.ops.install', installModules);
  registerCommand('ipai.ops.migrate', runMigration);
  registerCommand('ipai.ops.upgrade', upgradeOdoo);

  // AI commands
  registerCommand('ipai.ai.generatePatch', generatePatch);
  registerCommand('ipai.ai.explainDrift', explainDrift);
  registerCommand('ipai.ai.planUpgrade', planUpgrade);

  // Tree view
  const treeProvider = new ProjectTreeProvider(client);
  vscode.window.registerTreeDataProvider('ipaiProjects', treeProvider);

  // Diagnostics
  const diagnosticProvider = new DiagnosticProvider(client);
  context.subscriptions.push(diagnosticProvider);
}
```

### 3.3 Tree View (Project Explorer)

```typescript
// src/providers/ProjectTreeProvider.ts
export class ProjectTreeProvider implements vscode.TreeDataProvider<TreeItem> {
  private client: ControlPlaneClient;

  async getChildren(element?: TreeItem): Promise<TreeItem[]> {
    if (!element) {
      // Root: list projects
      const projects = await this.client.getProjects();
      return projects.map(p => new ProjectItem(p));
    }

    if (element instanceof ProjectItem) {
      // Project node: list environments
      const envs = await this.client.getEnvironments(element.project.id);
      return envs.map(e => new EnvironmentItem(e));
    }

    if (element instanceof EnvironmentItem) {
      // Environment node: show status details
      return [
        new StatusItem('Modules', element.env.modules_installed.length),
        new StatusItem('Schema', element.env.schema_hash.substring(0, 8)),
        new StatusItem('Health', element.env.health),
        new StatusItem('Pending', element.env.pending_migrations.length)
      ];
    }

    return [];
  }

  getTreeItem(element: TreeItem): vscode.TreeItem {
    return element;
  }
}

class ProjectItem extends vscode.TreeItem {
  constructor(public project: Project) {
    super(project.id, vscode.TreeItemCollapsibleState.Collapsed);
    this.iconPath = new vscode.ThemeIcon('database');
  }
}

class EnvironmentItem extends vscode.TreeItem {
  constructor(public env: Environment) {
    super(env.name, vscode.TreeItemCollapsibleState.Collapsed);
    this.iconPath = this.getIcon(env.health);
    this.description = env.odoo_version;
  }

  private getIcon(health: HealthStatus): vscode.ThemeIcon {
    switch (health) {
      case 'healthy': return new vscode.ThemeIcon('check', new vscode.ThemeColor('testing.iconPassed'));
      case 'degraded': return new vscode.ThemeIcon('warning', new vscode.ThemeColor('testing.iconQueued'));
      case 'failed': return new vscode.ThemeIcon('error', new vscode.ThemeColor('testing.iconFailed'));
      default: return new vscode.ThemeIcon('circle-outline');
    }
  }
}
```

---

## 4. Validator Engine

### 4.1 Validator Contract

```typescript
interface Validator {
  name: string;
  run(context: ValidationContext): Promise<ValidationResult>;
}

interface ValidationContext {
  project_root: string;
  target_files: string[];
  environment?: Environment;
}

interface ValidationResult {
  validator: string;
  status: 'pass' | 'warn' | 'fail';
  issues: ValidationIssue[];
  fixes?: QuickFix[];
}

interface ValidationIssue {
  file: string;
  line?: number;
  column?: number;
  severity: 'error' | 'warning' | 'info';
  message: string;
  rule: string;
}

interface QuickFix {
  label: string;
  diff: FileDiff;
}
```

### 4.2 Validator Implementations

#### Manifest Validator

```python
# control-plane/validators/manifest.py
class ManifestValidator:
    REQUIRED_KEYS = ['name', 'version', 'depends', 'data', 'installable']

    def validate(self, manifest_path: Path) -> ValidationResult:
        issues = []

        # Parse manifest
        manifest = ast.literal_eval(manifest_path.read_text())

        # Check required keys
        for key in self.REQUIRED_KEYS:
            if key not in manifest:
                issues.append(ValidationIssue(
                    file=str(manifest_path),
                    line=1,
                    severity='error',
                    message=f"Missing required key: {key}",
                    rule='manifest.required-keys'
                ))

        # Check dependencies exist
        if 'depends' in manifest:
            for dep in manifest['depends']:
                if not self.module_exists(dep):
                    issues.append(ValidationIssue(
                        file=str(manifest_path),
                        severity='error',
                        message=f"Dependency not found: {dep}",
                        rule='manifest.dependency-exists'
                    ))

        # Check for EE-only dependencies
        if 'depends' in manifest:
            ee_deps = [d for d in manifest['depends'] if self.is_ee_module(d)]
            if ee_deps:
                issues.append(ValidationIssue(
                    file=str(manifest_path),
                    severity='error',
                    message=f"Enterprise-only dependencies: {ee_deps}",
                    rule='manifest.no-ee-deps'
                ))

        return ValidationResult(
            validator='manifest',
            status='fail' if any(i.severity == 'error' for i in issues) else 'pass',
            issues=issues
        )
```

#### XML Validator

```python
# control-plane/validators/xml.py
class XmlValidator:
    def validate(self, xml_path: Path) -> ValidationResult:
        issues = []

        tree = etree.parse(str(xml_path))

        # Check for deprecated <tree> elements
        for tree_elem in tree.xpath('//tree'):
            if tree_elem.get('string'):  # Has a label, likely a view
                issues.append(ValidationIssue(
                    file=str(xml_path),
                    line=tree_elem.sourceline,
                    severity='warning',
                    message='Deprecated <tree> element, use <list> in Odoo 19+',
                    rule='xml.tree-deprecated'
                ))

                # Generate quick fix
                issues[-1].fixes = [QuickFix(
                    label='Replace <tree> with <list>',
                    diff=self.generate_tree_to_list_diff(xml_path, tree_elem)
                )]

        # Check for missing external IDs
        for record in tree.xpath('//record'):
            if not record.get('id'):
                issues.append(ValidationIssue(
                    file=str(xml_path),
                    line=record.sourceline,
                    severity='error',
                    message='Record missing id attribute',
                    rule='xml.record-id-required'
                ))

        # Check for external ID collisions
        external_ids = self.collect_external_ids(tree)
        collisions = self.find_collisions(external_ids)
        for collision in collisions:
            issues.append(ValidationIssue(
                file=str(xml_path),
                line=collision.line,
                severity='error',
                message=f"Duplicate external ID: {collision.id}",
                rule='xml.duplicate-id'
            ))

        return ValidationResult(
            validator='xml',
            status='fail' if any(i.severity == 'error' for i in issues) else 'pass',
            issues=issues
        )
```

#### Security Validator

```python
# control-plane/validators/security.py
class SecurityValidator:
    def validate(self, module_path: Path) -> ValidationResult:
        issues = []

        # Check for ir.model.access.csv
        access_csv = module_path / 'security' / 'ir.model.access.csv'
        if not access_csv.exists():
            issues.append(ValidationIssue(
                file=str(module_path),
                severity='warning',
                message='Missing ir.model.access.csv',
                rule='security.access-csv-missing'
            ))
        else:
            # Validate access rules cover all models
            models = self.find_models(module_path)
            access_rules = self.parse_access_csv(access_csv)

            for model in models:
                if model not in access_rules:
                    issues.append(ValidationIssue(
                        file=str(access_csv),
                        severity='error',
                        message=f"No access rule for model: {model}",
                        rule='security.model-not-covered'
                    ))

        # Check for record rules (RLS)
        security_xml = module_path / 'security' / 'security.xml'
        if security_xml.exists():
            tree = etree.parse(str(security_xml))
            rules = tree.xpath('//record[@model="ir.rule"]')

            for rule in rules:
                domain = rule.find('.//field[@name="domain_force"]')
                if domain is None or not domain.text:
                    issues.append(ValidationIssue(
                        file=str(security_xml),
                        line=rule.sourceline,
                        severity='warning',
                        message='RLS rule with empty domain',
                        rule='security.empty-domain'
                    ))

        return ValidationResult(
            validator='security',
            status='fail' if any(i.severity == 'error' for i in issues) else 'pass',
            issues=issues
        )
```

### 4.3 Diagnostic Provider Integration

```typescript
// src/providers/DiagnosticProvider.ts
export class DiagnosticProvider {
  private diagnostics: vscode.DiagnosticCollection;
  private client: ControlPlaneClient;

  constructor(client: ControlPlaneClient) {
    this.client = client;
    this.diagnostics = vscode.languages.createDiagnosticCollection('ipai');

    // Watch for file changes
    const watcher = vscode.workspace.createFileSystemWatcher('**/{__manifest__.py,*.xml,security/*.csv}');
    watcher.onDidChange(uri => this.validateFile(uri));
    watcher.onDidCreate(uri => this.validateFile(uri));
  }

  async validateFile(uri: vscode.Uri) {
    const results = await this.client.validate(uri.fsPath);

    const diagnostics: vscode.Diagnostic[] = results.issues.map(issue => {
      const range = new vscode.Range(
        (issue.line || 1) - 1, issue.column || 0,
        (issue.line || 1) - 1, 999
      );

      const severity = issue.severity === 'error'
        ? vscode.DiagnosticSeverity.Error
        : issue.severity === 'warning'
        ? vscode.DiagnosticSeverity.Warning
        : vscode.DiagnosticSeverity.Information;

      const diagnostic = new vscode.Diagnostic(range, issue.message, severity);
      diagnostic.code = issue.rule;
      diagnostic.source = 'ipai';

      return diagnostic;
    });

    this.diagnostics.set(uri, diagnostics);
  }

  dispose() {
    this.diagnostics.dispose();
  }
}
```

---

## 5. Diff Generation

### 5.1 Diff Types

```typescript
interface FileDiff {
  path: string;
  before: string;
  after: string;
  hunks: DiffHunk[];
}

interface SqlDiff {
  statements: string[];
  safe: boolean;  // Can be rolled back?
}

interface OrmDiff {
  models_added: string[];
  models_removed: string[];
  fields_changed: FieldChange[];
}
```

### 5.2 Diff Preview UI

```typescript
// src/commands/operations.ts
async function previewInstall(modules: string[]) {
  // Get diffs from control plane
  const diffs = await client.previewInstallModules(modules);

  // Show SQL diff
  const sqlDoc = await vscode.workspace.openTextDocument({
    content: diffs.sql.statements.join(';\n'),
    language: 'sql'
  });
  await vscode.window.showTextDocument(sqlDoc);

  // Show file diffs
  for (const fileDiff of diffs.files) {
    const uri = vscode.Uri.file(fileDiff.path);
    await vscode.commands.executeCommand('vscode.diff',
      uri.with({ scheme: 'ipai-before' }),
      uri.with({ scheme: 'ipai-after' }),
      `${path.basename(fileDiff.path)} (Preview)`
    );
  }

  // Confirm
  const confirm = await vscode.window.showInformationMessage(
    `Install ${modules.length} module(s)?`,
    { modal: true },
    'Install', 'Cancel'
  );

  if (confirm === 'Install') {
    await client.installModules(modules);
  }
}
```

---

## 6. Evidence Bundle Generation

### 6.1 Bundle Structure

```
docs/evidence/YYYYMMDD-HHMM-<operation>/
├── plan.md                    # Human-readable summary
├── operation.json             # Machine-readable metadata
├── diffs/
│   ├── schema.sql
│   ├── orm.diff
│   ├── data.diff
│   └── files/
│       └── addons/ipai/foo/...
├── validation/
│   ├── manifest.json
│   ├── xml.json
│   ├── security.json
│   └── summary.json
├── logs/
│   ├── odoo.log
│   ├── control-plane.log
│   └── errors.log
└── artifacts/
    ├── backup.dump          # DB snapshot (if rollback enabled)
    └── checksums.txt
```

### 6.2 Generation Implementation

```python
# control-plane/evidence.py
class EvidenceBundler:
    def __init__(self, evidence_root: Path):
        self.evidence_root = evidence_root

    def create_bundle(self, operation: Operation) -> EvidenceBundle:
        timestamp = datetime.now().strftime('%Y%m%d-%H%M')
        bundle_dir = self.evidence_root / f"{timestamp}-{operation.type}"
        bundle_dir.mkdir(parents=True, exist_ok=True)

        # Write plan
        self.write_plan(bundle_dir, operation)

        # Write diffs
        self.write_diffs(bundle_dir, operation.diffs)

        # Write validation results
        self.write_validation(bundle_dir, operation.validators)

        # Capture logs
        self.capture_logs(bundle_dir)

        # Generate checksums
        self.generate_checksums(bundle_dir)

        # Write metadata
        metadata = {
            'timestamp': timestamp,
            'operation': operation.type,
            'target_env': operation.target_env,
            'spec_bundle': operation.spec_bundle,
            'status': 'pending'
        }
        (bundle_dir / 'operation.json').write_text(json.dumps(metadata, indent=2))

        return EvidenceBundle(
            path=bundle_dir,
            metadata=metadata
        )

    def write_plan(self, bundle_dir: Path, operation: Operation):
        plan = f"""# Operation Plan

**Type**: {operation.type}
**Target**: {operation.target_env}
**Timestamp**: {datetime.now().isoformat()}
**Spec**: {operation.spec_bundle or 'N/A'}

## Changes

{self.format_changes(operation.diffs)}

## Validation

{self.format_validation(operation.validators)}

## Rollback Plan

{self.format_rollback(operation)}
"""
        (bundle_dir / 'plan.md').write_text(plan)
```

---

## 7. AI Command Surface

### 7.1 Command Design (Non-Hallucinatory)

```typescript
// src/commands/ai.ts

// AI Command: Generate Module Patch
async function generatePatch() {
  // 1. Get context
  const selection = await vscode.window.showQuickPick([
    'Fix failing CI checks',
    'Add missing security rules',
    'Migrate deprecated XML',
    'Upgrade module to Odoo 19'
  ]);

  // 2. Collect context pack
  const context = await client.buildContextPack({
    selection,
    include_spec: true,
    include_validators: true,
    include_recent_evidence: true
  });

  // 3. Generate patch via AI relay
  const patch = await client.aiGeneratePatch(context);

  // 4. Preview diff
  await showPatchPreview(patch);

  // 5. Confirm
  const confirm = await vscode.window.showInformationMessage(
    'Apply AI-generated patch?',
    { modal: true, detail: patch.summary },
    'Apply', 'Cancel'
  );

  if (confirm === 'Apply') {
    // 6. Validate patch
    const validation = await client.validatePatch(patch);
    if (validation.status !== 'pass') {
      await vscode.window.showErrorMessage('Patch validation failed');
      return;
    }

    // 7. Apply + generate evidence
    const evidence = await client.applyPatch(patch);
    await vscode.window.showInformationMessage(
      `Patch applied. Evidence: ${evidence.path}`
    );
  }
}

// AI Command: Explain Schema Drift
async function explainDrift() {
  const env = await selectEnvironment();

  const drift = await client.getSchemaDrift(env);
  const explanation = await client.aiExplainDrift(drift);

  // Show in webview with:
  // - Visual diff
  // - AI explanation
  // - Recommended fix options
  const panel = vscode.window.createWebviewPanel(
    'driftExplainer',
    'Schema Drift Explanation',
    vscode.ViewColumn.One,
    {}
  );

  panel.webview.html = renderDriftExplanation(drift, explanation);
}
```

### 7.2 AI Relay Protocol

```python
# control-plane/ai_relay.py
class AiRelay:
    """
    AI Relay enforces:
    - Spec Kit SSOT
    - Patch-only output
    - Validation gates
    - Evidence generation
    """

    def generate_patch(self, context: ContextPack) -> Patch:
        # Build prompt
        prompt = self.build_prompt(context)

        # Call AI provider (Claude/Codex/Gemini)
        response = self.ai_provider.complete(prompt)

        # Parse response into patch
        patch = self.parse_patch(response)

        # Validate patch
        validation = self.validate_patch(patch)
        if not validation.safe:
            raise ValueError(f"Unsafe patch: {validation.reason}")

        return patch

    def build_prompt(self, context: ContextPack) -> str:
        """
        Build a constrained, non-hallucinatory prompt.
        """
        return f"""You are a coding agent working in repo: {context.repo_root}

**HARD CONSTRAINTS**:
- Repo is SSOT; do not invent conventions
- Generate ONLY a unified diff patch
- No explanations, no markdown, just the diff
- Patch must pass validators
- No secrets, no hardcoded values

**CONTEXT**:
Spec Bundle: {context.spec_bundle}
Validation Errors:
{json.dumps(context.validation_errors, indent=2)}

**TASK**:
{context.task}

**OUTPUT FORMAT**:
```diff
(unified diff only)
```
"""

    def validate_patch(self, patch: Patch) -> PatchValidation:
        """
        Safety checks before applying.
        """
        unsafe_patterns = [
            r'os\.system',
            r'eval\(',
            r'exec\(',
            r'__import__',
            r'password\s*=',
            r'api_key\s*='
        ]

        for pattern in unsafe_patterns:
            if re.search(pattern, patch.content):
                return PatchValidation(
                    safe=False,
                    reason=f"Unsafe pattern detected: {pattern}"
                )

        # Must pass validators
        validation_results = self.run_validators(patch)
        if any(r.status == 'fail' for r in validation_results):
            return PatchValidation(
                safe=False,
                reason="Patch fails validation",
                details=validation_results
            )

        return PatchValidation(safe=True)
```

---

## 8. Deployment Model

### 8.1 Control Plane Server

```python
# control-plane/server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="IPAI Control Plane")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["vscode-webview://*"],  # VS Code webviews only
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/projects")
async def list_projects():
    return project_registry.list_all()

@app.post("/api/validate/manifest")
async def validate_manifest(request: ValidateRequest):
    validator = ManifestValidator()
    return validator.validate(Path(request.file_path))

@app.post("/api/operations/install-modules")
async def install_modules(request: InstallRequest):
    operation = Operation(
        type='install_modules',
        target_env=request.environment,
        modules=request.modules
    )

    # Generate evidence bundle first
    evidence = evidence_bundler.create_bundle(operation)

    # Execute operation
    result = odoo_runtime.install_modules(
        environment=request.environment,
        modules=request.modules
    )

    # Update evidence with results
    evidence.finalize(result)

    return {
        'status': result.status,
        'evidence': str(evidence.path)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9876)
```

### 8.2 Extension Startup

```typescript
// src/extension.ts
export async function activate(context: vscode.ExtensionContext) {
  // Start control plane server
  const serverProcess = await startControlPlane(context);
  context.subscriptions.push({
    dispose: () => serverProcess.kill()
  });

  // Wait for server ready
  await waitForServer('http://127.0.0.1:9876');

  // Initialize client
  const client = new ControlPlaneClient('http://127.0.0.1:9876');

  // Register all commands and providers
  registerCommands(context, client);
  registerTreeProviders(context, client);
  registerDiagnostics(context, client);
}

async function startControlPlane(context: vscode.ExtensionContext): Promise<ChildProcess> {
  const serverPath = path.join(context.extensionPath, 'control-plane', 'server.py');

  const process = spawn('python', [serverPath], {
    env: { ...process.env, PYTHONUNBUFFERED: '1' }
  });

  process.stdout.on('data', data => {
    console.log(`[Control Plane] ${data}`);
  });

  process.stderr.on('data', data => {
    console.error(`[Control Plane] ${data}`);
  });

  return process;
}
```

---

## 9. Configuration

### 9.1 Settings Schema

```json
{
  "ipai.controlPlane.port": {
    "type": "number",
    "default": 9876,
    "description": "Port for local control plane server"
  },
  "ipai.projects.repoRoot": {
    "type": "string",
    "description": "Path to Odoo repo root (auto-detected if omitted)"
  },
  "ipai.projects.defaultEnvironment": {
    "type": "string",
    "default": "dev",
    "enum": ["dev", "stage", "prod"]
  },
  "ipai.validation.autoRun": {
    "type": "boolean",
    "default": true,
    "description": "Run validators on file save"
  },
  "ipai.evidence.autoGenerate": {
    "type": "boolean",
    "default": true,
    "description": "Automatically generate evidence bundles for operations"
  },
  "ipai.ai.provider": {
    "type": "string",
    "default": "claude",
    "enum": ["claude", "codex", "gemini", "none"]
  },
  "ipai.ai.apiKey": {
    "type": "string",
    "description": "API key for AI provider (optional, uses env var if omitted)"
  }
}
```

---

## 10. Testing Strategy

### 10.1 Unit Tests

```typescript
// src/__tests__/ProjectTreeProvider.test.ts
describe('ProjectTreeProvider', () => {
  it('should list projects from control plane', async () => {
    const mockClient = {
      getProjects: jest.fn().mockResolvedValue([
        { id: 'test-project', repo_root: '/tmp/test' }
      ])
    };

    const provider = new ProjectTreeProvider(mockClient as any);
    const items = await provider.getChildren();

    expect(items).toHaveLength(1);
    expect(items[0].label).toBe('test-project');
  });
});
```

### 10.2 Integration Tests

```python
# control-plane/tests/test_validators.py
def test_manifest_validator_detects_missing_keys():
    manifest_path = fixtures / 'invalid_manifest' / '__manifest__.py'
    validator = ManifestValidator()

    result = validator.validate(manifest_path)

    assert result.status == 'fail'
    assert any('name' in issue.message for issue in result.issues)
```

### 10.3 E2E Tests

```typescript
// e2e/install-modules.test.ts
test('install modules workflow', async () => {
  // 1. Select modules
  await vscode.commands.executeCommand('ipai.ops.install', ['sale', 'account']);

  // 2. Verify preview shown
  const preview = await waitForDiffPreview();
  expect(preview).toBeDefined();

  // 3. Confirm install
  await clickButton('Install');

  // 4. Verify evidence generated
  const evidence = await waitForEvidence();
  expect(evidence.path).toMatch(/docs\/evidence\/\d{8}-\d{4}/);

  // 5. Verify modules installed
  const env = await client.getEnvironment('dev');
  expect(env.modules_installed).toContain('sale');
  expect(env.modules_installed).toContain('account');
});
```

### 10.4 Verification

Verification is enforced by CI gate `ipai-vscode-control-plane-gate` and must pass before merge.
Local execution is allowed but not authoritative.

---

## 11. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Control plane crashes | Auto-restart + health checks |
| Slow validators | Background validation + caching |
| AI hallucinations | Strict prompt templates + validation gates |
| Large diffs preview | Paginate + syntax highlighting + virtual scrolling |
| Cross-platform issues | CI tests on Windows/macOS/Linux |
| Version compatibility | Pin Odoo/OCA versions in spec |

---

## 12. Extension Release Pipeline (Required)

### Build Process
```bash
# TypeScript compilation
npm run build          # Compile src/ → dist/

# Testing
npm test              # Run vitest unit tests

# Packaging
npm run package       # Create .vsix artifact

# Publishing
vsce publish          # Marketplace (manual trigger)
```

### Build Artifacts
- **Development**: `dist/` directory (TypeScript output)
- **Release**: `.vsix` file (extension package)
- **Tests**: `coverage/` directory (test coverage reports)

### CI/CD Pipeline
- **Trigger**: PR to main, push to main
- **Steps**: lint → test → build → package
- **Artifacts**: `.vsix` uploaded to GitHub Release
- **Gates**: All steps must pass before merge

---

## 13. Local Dev Contract (Required)

### Development Workflow
```bash
# Setup
npm install

# Watch mode (incremental build)
npm run watch

# Run tests
npm test

# Lint
npm run lint

# Package for testing
npm run package
# Install: code --install-extension ipai-control-plane-*.vsix
```

### Testing Requirements
- **Unit tests**: Provider logic, command wiring
- **Integration tests**: Control plane API calls (mocked)
- **Coverage target**: ≥70% line coverage

### Debugging
- Launch VS Code Extension Host via F5
- Control plane server must be running separately
- Use `console.log` → Extension Host Debug Console

---

## 14. Implementation Phases

### Phase 1: Foundation (2-3 weeks)
- [ ] Control plane API skeleton
- [ ] VS Code extension scaffold
- [ ] Project/environment discovery
- [ ] Basic tree view

### Phase 2: Validators (2 weeks)
- [ ] Manifest validator
- [ ] XML validator
- [ ] Security validator
- [ ] Diagnostic provider integration

### Phase 3: Operations (3 weeks)
- [ ] Install/update modules
- [ ] Run migrations
- [ ] Diff preview UI
- [ ] Evidence bundle generation

### Phase 4: AI Integration (2 weeks)
- [ ] Context pack builder
- [ ] AI relay implementation
- [ ] Patch validation
- [ ] AI command surface

### Phase 5: Polish (1 week)
- [ ] Settings UI
- [ ] Documentation
- [ ] E2E tests
- [ ] Performance optimization

---

## 15. Success Criteria

### Technical
- [ ] All validators pass on repo modules
- [ ] Evidence bundles generated for all operations
- [ ] AI patches validated before apply
- [ ] Zero crashes in 1-week dogfooding

### User Experience
- [ ] < 2 seconds to preview install diff
- [ ] < 5 seconds to generate evidence bundle
- [ ] < 10 seconds for AI patch generation
- [ ] Zero manual YAML/JSON editing required

### Governance
- [ ] 100% operations have evidence trails
- [ ] Zero unsafe AI outputs applied
- [ ] All mutations require confirmation
- [ ] Spec Kit compliance enforced

---

**Next artifact**: `tasks.md` (implementable checklist) or scaffold the extension package?
