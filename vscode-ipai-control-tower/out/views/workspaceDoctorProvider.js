"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.DoctorTreeItem = exports.WorkspaceDoctorProvider = void 0;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
const fs = __importStar(require("fs/promises"));
/**
 * Workspace Doctor — scans for structural and doctrine violations.
 *
 * Checks:
 * - missing __manifest__.py / __init__.py
 * - missing tests for active ipai_* modules
 * - deprecated module imports
 * - secrets in code
 * - heavyweight logic inside Odoo (requests.post in models)
 * - missing spec/ssot docs
 */
class WorkspaceDoctorProvider {
    adapter;
    workspaceRoot;
    _onDidChange = new vscode.EventEmitter();
    onDidChangeTreeData = this._onDidChange.event;
    findings = [];
    constructor(adapter, workspaceRoot) {
        this.adapter = adapter;
        this.workspaceRoot = workspaceRoot;
    }
    async refresh() {
        const modules = await this.adapter.discoverModules();
        this.findings = [];
        this.findings.push(...this.checkMissingManifest(modules));
        this.findings.push(...this.checkMissingTests(modules));
        this.findings.push(...this.checkDeprecatedImports(modules));
        this.findings.push(...(await this.checkSecretsInCode()));
        this.findings.push(...(await this.checkHeavyweightLogic(modules)));
        this.findings.push(...(await this.checkMissingSpecs()));
        this._onDidChange.fire();
    }
    getTreeItem(element) {
        return element;
    }
    getChildren(element) {
        if (element) {
            return [];
        }
        if (this.findings.length === 0) {
            return [
                new DoctorTreeItem('All checks passed', 'info', vscode.TreeItemCollapsibleState.None),
            ];
        }
        const errors = this.findings.filter((f) => f.severity === 'error');
        const warnings = this.findings.filter((f) => f.severity === 'warning');
        const infos = this.findings.filter((f) => f.severity === 'info');
        const items = [];
        if (errors.length > 0) {
            items.push(new DoctorTreeItem(`Errors (${errors.length})`, 'error', vscode.TreeItemCollapsibleState.Expanded, errors));
        }
        if (warnings.length > 0) {
            items.push(new DoctorTreeItem(`Warnings (${warnings.length})`, 'warning', vscode.TreeItemCollapsibleState.Expanded, warnings));
        }
        if (infos.length > 0) {
            items.push(new DoctorTreeItem(`Info (${infos.length})`, 'info', vscode.TreeItemCollapsibleState.Collapsed, infos));
        }
        return items;
    }
    getFindings() {
        return this.findings;
    }
    // -----------------------------------------------------------------------
    // Check implementations
    // -----------------------------------------------------------------------
    checkMissingManifest(modules) {
        return modules
            .filter((m) => m.classification === 'not-a-module')
            .map((m) => ({
            module: m.name,
            check: 'missing-manifest',
            message: `${m.name} has no __manifest__.py — not a valid Odoo 18 module`,
            severity: 'warning',
            filePath: m.path,
        }));
    }
    checkMissingTests(modules) {
        return modules
            .filter((m) => m.classification === 'active' &&
            !m.hasTests &&
            m.name.startsWith('ipai_'))
            .map((m) => ({
            module: m.name,
            check: 'missing-tests',
            message: `${m.name} is active but has no tests in tests/test_*.py`,
            severity: 'warning',
            filePath: m.path,
        }));
    }
    checkDeprecatedImports(modules) {
        const deprecated = new Set(modules.filter((m) => m.classification === 'deprecated').map((m) => m.name));
        const findings = [];
        for (const mod of modules) {
            if (mod.classification === 'deprecated')
                continue;
            for (const dep of mod.ipaiDeps) {
                if (deprecated.has(dep)) {
                    findings.push({
                        module: mod.name,
                        check: 'deprecated-dependency',
                        message: `${mod.name} depends on deprecated module ${dep}`,
                        severity: 'error',
                        filePath: path.join(mod.path, '__manifest__.py'),
                    });
                }
            }
        }
        return findings;
    }
    async checkSecretsInCode() {
        const findings = [];
        const patterns = [
            /(?:password|secret|token|api_key)\s*=\s*['"][^'"]{8,}['"]/gi,
            /(?:AZURE_|AWS_|SUPABASE_)[A-Z_]+\s*=\s*['"][^'"]+['"]/gi,
        ];
        const pyFiles = await vscode.workspace.findFiles(new vscode.RelativePattern(path.join(this.workspaceRoot, 'addons/ipai'), '**/*.py'), '**/tests/**', 200);
        for (const uri of pyFiles) {
            try {
                const content = await fs.readFile(uri.fsPath, 'utf-8');
                for (const pattern of patterns) {
                    pattern.lastIndex = 0;
                    if (pattern.test(content)) {
                        findings.push({
                            module: this.moduleNameFromPath(uri.fsPath),
                            check: 'potential-secret',
                            message: `Potential hardcoded secret in ${path.basename(uri.fsPath)}`,
                            severity: 'error',
                            filePath: uri.fsPath,
                        });
                        break;
                    }
                }
            }
            catch {
                // skip unreadable files
            }
        }
        return findings;
    }
    async checkHeavyweightLogic(modules) {
        const findings = [];
        for (const mod of modules) {
            if (mod.classification !== 'active' && mod.classification !== 'bridge') {
                continue;
            }
            for (const modelFile of mod.modelFiles) {
                if (modelFile.endsWith('__init__.py'))
                    continue;
                try {
                    const content = await fs.readFile(modelFile, 'utf-8');
                    if (content.includes('requests.post') ||
                        content.includes('requests.get') ||
                        content.includes('aiohttp')) {
                        findings.push({
                            module: mod.name,
                            check: 'sync-http-in-model',
                            message: `${path.basename(modelFile)} makes synchronous HTTP calls — should use queue_job or externalize to Azure Function`,
                            severity: 'warning',
                            filePath: modelFile,
                        });
                    }
                }
                catch {
                    // skip
                }
            }
        }
        return findings;
    }
    async checkMissingSpecs() {
        const specDir = path.join(this.workspaceRoot, vscode.workspace
            .getConfiguration('ipai')
            .get('release.specPath', 'spec'));
        try {
            await fs.access(specDir);
            return [];
        }
        catch {
            return [
                {
                    module: '*',
                    check: 'missing-spec-dir',
                    message: `Spec directory not found at ${specDir}`,
                    severity: 'info',
                },
            ];
        }
    }
    moduleNameFromPath(filePath) {
        const addonsIdx = filePath.indexOf('addons/ipai/');
        if (addonsIdx < 0)
            return 'unknown';
        const rest = filePath.slice(addonsIdx + 'addons/ipai/'.length);
        return rest.split('/')[0] ?? 'unknown';
    }
}
exports.WorkspaceDoctorProvider = WorkspaceDoctorProvider;
// ---------------------------------------------------------------------------
// Tree item
// ---------------------------------------------------------------------------
class DoctorTreeItem extends vscode.TreeItem {
    severity;
    children;
    constructor(label, severity, collapsibleState, children) {
        super(label, collapsibleState);
        this.severity = severity;
        this.children = children;
        if (severity === 'error') {
            this.iconPath = new vscode.ThemeIcon('error', new vscode.ThemeColor('errorForeground'));
        }
        else if (severity === 'warning') {
            this.iconPath = new vscode.ThemeIcon('warning', new vscode.ThemeColor('editorWarning.foreground'));
        }
        else {
            this.iconPath = new vscode.ThemeIcon('info', new vscode.ThemeColor('editorInfo.foreground'));
        }
        if (children && children.length === 1) {
            this.description = children[0].message;
            if (children[0].filePath) {
                this.command = {
                    command: 'vscode.open',
                    title: 'Open',
                    arguments: [vscode.Uri.file(children[0].filePath)],
                };
            }
        }
    }
}
exports.DoctorTreeItem = DoctorTreeItem;
//# sourceMappingURL=workspaceDoctorProvider.js.map