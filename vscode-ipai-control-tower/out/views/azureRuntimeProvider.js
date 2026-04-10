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
exports.AzureRuntimeProvider = void 0;
const vscode = __importStar(require("vscode"));
/**
 * Azure Runtime tree view — live status panel for the current environment.
 *
 * Shows: Container Apps, revisions, Front Door, PostgreSQL, MI, Foundry endpoint.
 */
class AzureRuntimeProvider {
    adapter;
    _onDidChange = new vscode.EventEmitter();
    onDidChangeTreeData = this._onDidChange.event;
    checks = [];
    lastRun = null;
    constructor(adapter) {
        this.adapter = adapter;
    }
    async refresh() {
        this.checks = await this.adapter.runAllChecks();
        this.lastRun = new Date();
        this._onDidChange.fire();
    }
    getTreeItem(element) {
        return element;
    }
    getChildren(element) {
        if (element)
            return [];
        if (this.checks.length === 0) {
            const item = new AzureTreeItem('Run Azure Runtime Smoke to populate', vscode.TreeItemCollapsibleState.None);
            item.iconPath = new vscode.ThemeIcon('info');
            item.command = {
                command: 'ipai.runAzureRuntimeSmoke',
                title: 'Run Smoke',
            };
            return [item];
        }
        const items = this.checks.map((check) => {
            const item = new AzureTreeItem(check.name, vscode.TreeItemCollapsibleState.None);
            item.description = check.detail;
            item.iconPath = statusIcon(check.status);
            item.tooltip = new vscode.MarkdownString(`**${check.name}**\n\n` +
                `- Category: ${check.category}\n` +
                `- Status: ${check.status}\n` +
                `- Detail: ${check.detail}\n` +
                `- Checked: ${check.timestamp.toISOString()}`);
            return item;
        });
        if (this.lastRun) {
            const footer = new AzureTreeItem(`Last checked: ${this.lastRun.toLocaleTimeString()}`, vscode.TreeItemCollapsibleState.None);
            footer.iconPath = new vscode.ThemeIcon('clock');
            items.push(footer);
        }
        return items;
    }
    getChecks() {
        return this.checks;
    }
}
exports.AzureRuntimeProvider = AzureRuntimeProvider;
function statusIcon(status) {
    switch (status) {
        case 'pass':
            return new vscode.ThemeIcon('pass', new vscode.ThemeColor('testing.iconPassed'));
        case 'fail':
            return new vscode.ThemeIcon('error', new vscode.ThemeColor('testing.iconFailed'));
        case 'skipped':
            return new vscode.ThemeIcon('debug-step-over');
        default:
            return new vscode.ThemeIcon('question');
    }
}
class AzureTreeItem extends vscode.TreeItem {
}
//# sourceMappingURL=azureRuntimeProvider.js.map