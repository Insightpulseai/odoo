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
exports.ReleaseReadinessProvider = void 0;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
const fs = __importStar(require("fs/promises"));
/**
 * Release Readiness tree view — checks the 5-gate ship-readiness protocol.
 *
 * Gates: Product, Correctness, Runtime, Safety, Evidence
 * Reads existing repo artifacts — does NOT own business logic.
 */
class ReleaseReadinessProvider {
    workspaceRoot;
    _onDidChange = new vscode.EventEmitter();
    onDidChangeTreeData = this._onDidChange.event;
    report = null;
    constructor(workspaceRoot) {
        this.workspaceRoot = workspaceRoot;
    }
    async refresh() {
        const branch = await this.getCurrentBranch();
        const gates = await this.evaluateGates();
        this.report = {
            branch,
            timestamp: new Date(),
            gates,
            allPassed: gates.every((g) => g.status === 'pass'),
        };
        this._onDidChange.fire();
    }
    getTreeItem(element) {
        return element;
    }
    getChildren(element) {
        if (element)
            return [];
        if (!this.report) {
            const item = new ReadinessTreeItem('Run Release Readiness Audit to populate', vscode.TreeItemCollapsibleState.None);
            item.iconPath = new vscode.ThemeIcon('info');
            item.command = {
                command: 'ipai.runReleaseReadiness',
                title: 'Run Audit',
            };
            return [item];
        }
        const header = new ReadinessTreeItem(this.report.allPassed
            ? `Ship-Ready (${this.report.branch})`
            : `NOT Ready (${this.report.branch})`, vscode.TreeItemCollapsibleState.None);
        header.iconPath = this.report.allPassed
            ? new vscode.ThemeIcon('rocket', new vscode.ThemeColor('testing.iconPassed'))
            : new vscode.ThemeIcon('shield', new vscode.ThemeColor('testing.iconFailed'));
        const gateItems = this.report.gates.map((gate) => {
            const item = new ReadinessTreeItem(`[${gate.category.toUpperCase()}] ${gate.name}`, vscode.TreeItemCollapsibleState.None);
            item.description = gate.detail;
            item.iconPath = gateIcon(gate.status);
            if (gate.filePath) {
                item.command = {
                    command: 'vscode.open',
                    title: 'Open',
                    arguments: [vscode.Uri.file(gate.filePath)],
                };
            }
            return item;
        });
        const footer = new ReadinessTreeItem(`Checked: ${this.report.timestamp.toLocaleTimeString()}`, vscode.TreeItemCollapsibleState.None);
        footer.iconPath = new vscode.ThemeIcon('clock');
        return [header, ...gateItems, footer];
    }
    getReport() {
        return this.report;
    }
    // -----------------------------------------------------------------------
    // Gate evaluations
    // -----------------------------------------------------------------------
    async evaluateGates() {
        return [
            await this.checkSpecPresent(),
            await this.checkTestsExist(),
            await this.checkEvidencePresent(),
            await this.checkShipReadinessChecklist(),
            await this.checkSsotValidationMatrix(),
        ];
    }
    async checkSpecPresent() {
        const specDir = path.join(this.workspaceRoot, vscode.workspace
            .getConfiguration('ipai')
            .get('release.specPath', 'spec'));
        const exists = await this.dirExists(specDir);
        let specCount = 0;
        if (exists) {
            const entries = await fs.readdir(specDir, { withFileTypes: true });
            specCount = entries.filter((e) => e.isDirectory()).length;
        }
        return {
            name: 'Spec bundles present',
            category: 'product',
            status: specCount > 0 ? 'pass' : 'fail',
            detail: exists ? `${specCount} spec bundles` : 'spec/ directory not found',
            filePath: exists ? specDir : undefined,
        };
    }
    async checkTestsExist() {
        const testFiles = await vscode.workspace.findFiles(new vscode.RelativePattern(path.join(this.workspaceRoot, 'addons/ipai'), '**/tests/test_*.py'), undefined, 200);
        return {
            name: 'Odoo 18 tests present',
            category: 'correctness',
            status: testFiles.length > 0 ? 'pass' : 'fail',
            detail: `${testFiles.length} test files across modules`,
        };
    }
    async checkEvidencePresent() {
        const evidencePath = path.join(this.workspaceRoot, vscode.workspace
            .getConfiguration('ipai')
            .get('release.evidencePath', 'docs/evidence'));
        const exists = await this.dirExists(evidencePath);
        if (!exists) {
            return {
                name: 'Evidence packs present',
                category: 'evidence',
                status: 'fail',
                detail: 'docs/evidence/ directory not found',
            };
        }
        const entries = await fs.readdir(evidencePath, { withFileTypes: true });
        const stampDirs = entries.filter((e) => e.isDirectory() && /^\d{8}/.test(e.name));
        return {
            name: 'Evidence packs present',
            category: 'evidence',
            status: stampDirs.length > 0 ? 'pass' : 'fail',
            detail: `${stampDirs.length} evidence pack(s)`,
            filePath: evidencePath,
        };
    }
    async checkShipReadinessChecklist() {
        const checklistPath = path.join(this.workspaceRoot, 'docs/release/FEATURE_SHIP_READINESS_CHECKLIST.md');
        const exists = await this.fileExists(checklistPath);
        return {
            name: 'Ship-readiness checklist',
            category: 'safety',
            status: exists ? 'pass' : 'fail',
            detail: exists ? 'Checklist file present' : 'Checklist not found',
            filePath: exists ? checklistPath : undefined,
        };
    }
    async checkSsotValidationMatrix() {
        const matrixPath = path.join(this.workspaceRoot, 'ssot/docs/odoo_on_azure_validation_matrix.yaml');
        const exists = await this.fileExists(matrixPath);
        return {
            name: 'SSOT validation matrix',
            category: 'runtime',
            status: exists ? 'pass' : 'not-checked',
            detail: exists ? 'Matrix present' : 'Matrix file not found',
            filePath: exists ? matrixPath : undefined,
        };
    }
    // -----------------------------------------------------------------------
    // Helpers
    // -----------------------------------------------------------------------
    async getCurrentBranch() {
        try {
            const gitExt = vscode.extensions.getExtension('vscode.git');
            if (gitExt?.isActive) {
                const git = gitExt.exports.getAPI(1);
                const repo = git.repositories[0];
                return repo?.state.HEAD?.name ?? 'unknown';
            }
        }
        catch {
            // fallback
        }
        return 'unknown';
    }
    async dirExists(dirPath) {
        try {
            const stat = await fs.stat(dirPath);
            return stat.isDirectory();
        }
        catch {
            return false;
        }
    }
    async fileExists(filePath) {
        try {
            await fs.access(filePath);
            return true;
        }
        catch {
            return false;
        }
    }
}
exports.ReleaseReadinessProvider = ReleaseReadinessProvider;
function gateIcon(status) {
    switch (status) {
        case 'pass':
            return new vscode.ThemeIcon('pass', new vscode.ThemeColor('testing.iconPassed'));
        case 'fail':
            return new vscode.ThemeIcon('error', new vscode.ThemeColor('testing.iconFailed'));
        default:
            return new vscode.ThemeIcon('circle-outline');
    }
}
class ReadinessTreeItem extends vscode.TreeItem {
}
//# sourceMappingURL=releaseReadinessProvider.js.map