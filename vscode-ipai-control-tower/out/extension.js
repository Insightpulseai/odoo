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
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const odooRepoAdapter_js_1 = require("./adapters/odooRepoAdapter.js");
const infraRepoAdapter_js_1 = require("./adapters/infraRepoAdapter.js");
const workspaceDoctorProvider_js_1 = require("./views/workspaceDoctorProvider.js");
const odooModulesProvider_js_1 = require("./views/odooModulesProvider.js");
const azureRuntimeProvider_js_1 = require("./views/azureRuntimeProvider.js");
const releaseReadinessProvider_js_1 = require("./views/releaseReadinessProvider.js");
const doctrineDiagnostics_js_1 = require("./diagnostics/doctrineDiagnostics.js");
const testController_js_1 = require("./testing/testController.js");
const ipaiParticipant_js_1 = require("./chat/ipaiParticipant.js");
const runWorkspaceDoctor_js_1 = require("./commands/runWorkspaceDoctor.js");
const runReleaseReadiness_js_1 = require("./commands/runReleaseReadiness.js");
const runAzureRuntimeSmoke_js_1 = require("./commands/runAzureRuntimeSmoke.js");
async function activate(context) {
    const workspaceRoot = getWorkspaceRoot();
    if (!workspaceRoot) {
        vscode.window.showWarningMessage('IPAI Control Tower: No workspace folder found.');
        return;
    }
    const config = vscode.workspace.getConfiguration('ipai');
    // -----------------------------------------------------------------------
    // Adapters
    // -----------------------------------------------------------------------
    const odooAdapter = new odooRepoAdapter_js_1.OdooRepoAdapter(workspaceRoot);
    const infraAdapter = new infraRepoAdapter_js_1.InfraRepoAdapter(workspaceRoot, config.get('azure.resourceGroup', ''), config.get('azure.containerAppName', 'ipai-odoo-dev-web'));
    // -----------------------------------------------------------------------
    // Tree View Providers
    // -----------------------------------------------------------------------
    const doctorProvider = new workspaceDoctorProvider_js_1.WorkspaceDoctorProvider(odooAdapter, workspaceRoot);
    const modulesProvider = new odooModulesProvider_js_1.OdooModulesProvider(odooAdapter);
    const azureProvider = new azureRuntimeProvider_js_1.AzureRuntimeProvider(infraAdapter);
    const readinessProvider = new releaseReadinessProvider_js_1.ReleaseReadinessProvider(workspaceRoot);
    context.subscriptions.push(vscode.window.registerTreeDataProvider('ipai.workspaceDoctor', doctorProvider), vscode.window.registerTreeDataProvider('ipai.odooModules', modulesProvider), vscode.window.registerTreeDataProvider('ipai.azureRuntime', azureProvider), vscode.window.registerTreeDataProvider('ipai.releaseReadiness', readinessProvider));
    // -----------------------------------------------------------------------
    // Diagnostics
    // -----------------------------------------------------------------------
    const diagnostics = new doctrineDiagnostics_js_1.DoctrineDiagnosticsProvider();
    context.subscriptions.push(diagnostics);
    // -----------------------------------------------------------------------
    // Test Controller
    // -----------------------------------------------------------------------
    const testController = new testController_js_1.OdooTestController(workspaceRoot);
    context.subscriptions.push(testController);
    // -----------------------------------------------------------------------
    // Commands
    // -----------------------------------------------------------------------
    (0, runWorkspaceDoctor_js_1.registerDoctorCommand)(context, doctorProvider);
    (0, runReleaseReadiness_js_1.registerReadinessCommand)(context, readinessProvider);
    (0, runAzureRuntimeSmoke_js_1.registerAzureSmokeCommand)(context, azureProvider);
    // Refresh all views
    context.subscriptions.push(vscode.commands.registerCommand('ipai.refreshAll', async () => {
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'IPAI: Refreshing all views...',
            cancellable: false,
        }, async () => {
            await Promise.all([
                doctorProvider.refresh(),
                modulesProvider.refresh(),
                readinessProvider.refresh(),
            ]);
            // Update diagnostics with fresh module list
            diagnostics.setDeprecatedModules(modulesProvider.getModules());
            // Load test tree
            await testController.loadModules(modulesProvider.getModules());
        });
    }));
    // Classify current addon
    context.subscriptions.push(vscode.commands.registerCommand('ipai.classifyAddon', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active editor.');
            return;
        }
        const filePath = editor.document.uri.fsPath;
        const modules = modulesProvider.getModules();
        const mod = modules.find((m) => filePath.startsWith(m.path));
        if (!mod) {
            vscode.window.showWarningMessage('Current file is not inside an IPAI addon.');
            return;
        }
        vscode.window.showInformationMessage(`${mod.name}: ${mod.classification} | ` +
            `${mod.hasTests ? 'tested' : 'no tests'} | ` +
            `${mod.modelFiles.filter((f) => !f.endsWith('__init__.py')).length} models | ` +
            `deps: ${mod.ipaiDeps.join(', ') || 'none'}`);
    }));
    // Generate test skeleton
    context.subscriptions.push(vscode.commands.registerCommand('ipai.generateTestSkeleton', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active editor.');
            return;
        }
        const filePath = editor.document.uri.fsPath;
        const modules = modulesProvider.getModules();
        const mod = modules.find((m) => filePath.startsWith(m.path));
        if (!mod) {
            vscode.window.showWarningMessage('Current file is not inside an IPAI addon.');
            return;
        }
        const testDir = vscode.Uri.file(`${mod.path}/tests`);
        const initFile = vscode.Uri.file(`${mod.path}/tests/__init__.py`);
        const testFile = vscode.Uri.file(`${mod.path}/tests/test_${mod.name.replace('ipai_', '')}.py`);
        // Create tests directory and files
        await vscode.workspace.fs.createDirectory(testDir);
        const initContent = Buffer.from(`from . import test_${mod.name.replace('ipai_', '')}\n`, 'utf-8');
        await vscode.workspace.fs.writeFile(initFile, initContent);
        const testContent = Buffer.from(`# -*- coding: utf-8 -*-\n` +
            `from odoo.tests.common import TransactionCase\n\n\n` +
            `class Test${toPascalCase(mod.name)}(TransactionCase):\n` +
            `    """Tests for ${mod.manifest?.name ?? mod.name}."""\n\n` +
            `    @classmethod\n` +
            `    def setUpClass(cls):\n` +
            `        super().setUpClass()\n` +
            `        # TODO: set up test data\n\n` +
            `    def test_smoke_install(self):\n` +
            `        """Module installs without errors."""\n` +
            `        self.assertTrue(\n` +
            `            self.env['ir.module.module'].search([\n` +
            `                ('name', '=', '${mod.name}'),\n` +
            `                ('state', '=', 'installed'),\n` +
            `            ]),\n` +
            `            '${mod.name} should be installed',\n` +
            `        )\n`, 'utf-8');
        await vscode.workspace.fs.writeFile(testFile, testContent);
        // Open the new test file
        const doc = await vscode.workspace.openTextDocument(testFile);
        await vscode.window.showTextDocument(doc);
        vscode.window.showInformationMessage(`Test skeleton created for ${mod.name}`);
    }));
    // Open ship readiness summary
    context.subscriptions.push(vscode.commands.registerCommand('ipai.openShipReadiness', async () => {
        const checklistPath = vscode.Uri.file(`${workspaceRoot}/docs/release/FEATURE_SHIP_READINESS_CHECKLIST.md`);
        try {
            const doc = await vscode.workspace.openTextDocument(checklistPath);
            await vscode.window.showTextDocument(doc);
        }
        catch {
            vscode.window.showWarningMessage('Ship-readiness checklist not found at docs/release/FEATURE_SHIP_READINESS_CHECKLIST.md');
        }
    }));
    // Open failing item (placeholder — navigates to evidence dir)
    context.subscriptions.push(vscode.commands.registerCommand('ipai.openFailingItem', async () => {
        const report = readinessProvider.getReport();
        const failing = report?.gates.filter((g) => g.status === 'fail' && g.filePath);
        if (!failing || failing.length === 0) {
            vscode.window.showInformationMessage('No failing items with file paths.');
            return;
        }
        const items = failing.map((g) => ({
            label: `[${g.category}] ${g.name}`,
            detail: g.detail,
            filePath: g.filePath,
        }));
        const selected = await vscode.window.showQuickPick(items, {
            placeHolder: 'Select failing item to open',
        });
        if (selected) {
            const uri = vscode.Uri.file(selected.filePath);
            try {
                const doc = await vscode.workspace.openTextDocument(uri);
                await vscode.window.showTextDocument(doc);
            }
            catch {
                // might be a directory
                vscode.commands.executeCommand('revealFileInOS', uri);
            }
        }
    }));
    // -----------------------------------------------------------------------
    // Chat Participant
    // -----------------------------------------------------------------------
    context.subscriptions.push((0, ipaiParticipant_js_1.registerChatParticipant)(context, () => doctorProvider.getFindings(), () => modulesProvider.getModules(), () => azureProvider.getChecks(), () => readinessProvider.getReport()));
    // -----------------------------------------------------------------------
    // Status bar
    // -----------------------------------------------------------------------
    const statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 50);
    statusBar.command = 'ipai.refreshAll';
    statusBar.text = '$(pulse) IPAI';
    statusBar.tooltip = 'IPAI Control Tower — click to refresh';
    statusBar.show();
    context.subscriptions.push(statusBar);
    // -----------------------------------------------------------------------
    // Auto-refresh on activation
    // -----------------------------------------------------------------------
    // Run initial module discovery (non-blocking)
    modulesProvider.refresh().then(() => {
        diagnostics.setDeprecatedModules(modulesProvider.getModules());
        diagnostics.activate();
        testController.loadModules(modulesProvider.getModules());
        const modules = modulesProvider.getModules();
        const active = modules.filter((m) => m.classification === 'active').length;
        statusBar.text = `$(pulse) IPAI: ${modules.length} modules (${active} active)`;
    });
    // Watch for manifest changes
    const manifestWatcher = vscode.workspace.createFileSystemWatcher('**/__manifest__.py');
    manifestWatcher.onDidChange(() => modulesProvider.refresh());
    manifestWatcher.onDidCreate(() => modulesProvider.refresh());
    manifestWatcher.onDidDelete(() => modulesProvider.refresh());
    context.subscriptions.push(manifestWatcher);
    vscode.window.showInformationMessage('IPAI Control Tower activated for Odoo 18 on Azure');
}
function deactivate() {
    // Cleanup handled by disposables
}
// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function getWorkspaceRoot() {
    const folders = vscode.workspace.workspaceFolders;
    if (!folders || folders.length === 0)
        return undefined;
    return folders[0].uri.fsPath;
}
function toPascalCase(str) {
    return str
        .split('_')
        .map((s) => s.charAt(0).toUpperCase() + s.slice(1))
        .join('');
}
//# sourceMappingURL=extension.js.map