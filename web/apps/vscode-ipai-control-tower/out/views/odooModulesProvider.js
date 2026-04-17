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
exports.ModuleTreeItem = exports.OdooModulesProvider = void 0;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
/**
 * Odoo Modules tree view — shows all ipai_* modules grouped by classification.
 *
 * For each module shows:
 * - installability
 * - dependency count
 * - test presence
 * - model/view/security file counts
 * - consolidation target (if in plan)
 */
class OdooModulesProvider {
    adapter;
    _onDidChange = new vscode.EventEmitter();
    onDidChangeTreeData = this._onDidChange.event;
    modules = [];
    plan = null;
    constructor(adapter) {
        this.adapter = adapter;
    }
    async refresh() {
        this.modules = await this.adapter.discoverModules();
        this.plan = await this.adapter.loadConsolidationPlan();
        this._onDidChange.fire();
    }
    getTreeItem(element) {
        return element;
    }
    getChildren(element) {
        if (!element) {
            return this.getRootGroups();
        }
        if (element.contextValue === 'group') {
            return this.getModulesForGroup(element.classification);
        }
        if (element.contextValue === 'module') {
            return this.getModuleDetails(element.module);
        }
        return [];
    }
    getModules() {
        return this.modules;
    }
    // -----------------------------------------------------------------------
    // Tree construction
    // -----------------------------------------------------------------------
    getRootGroups() {
        const groups = [
            { label: 'Active', classification: 'active', icon: 'check' },
            { label: 'Bridge', classification: 'bridge', icon: 'plug' },
            { label: 'Stub', classification: 'stub', icon: 'circle-outline' },
            { label: 'Deprecated', classification: 'deprecated', icon: 'trash' },
            { label: 'Not a Module', classification: 'not-a-module', icon: 'question' },
        ];
        return groups
            .map((g) => {
            const count = this.modules.filter((m) => m.classification === g.classification).length;
            if (count === 0)
                return null;
            const item = new ModuleTreeItem(`${g.label} (${count})`, vscode.TreeItemCollapsibleState.Collapsed);
            item.contextValue = 'group';
            item.classification = g.classification;
            item.iconPath = new vscode.ThemeIcon(g.icon);
            return item;
        })
            .filter(Boolean);
    }
    getModulesForGroup(classification) {
        return this.modules
            .filter((m) => m.classification === classification)
            .map((m) => {
            const consolidationTarget = this.plan?.entries.find((e) => e.source === m.name);
            const description = [
                m.hasTests ? 'tested' : 'no tests',
                `${m.modelFiles.filter((f) => !f.endsWith('__init__.py')).length} models`,
                `${m.viewFiles.length} views`,
                m.ipaiDeps.length > 0 ? `deps: ${m.ipaiDeps.join(', ')}` : undefined,
                consolidationTarget
                    ? `-> ${consolidationTarget.target} (${consolidationTarget.status})`
                    : undefined,
            ]
                .filter(Boolean)
                .join(' | ');
            const item = new ModuleTreeItem(m.name, vscode.TreeItemCollapsibleState.Collapsed);
            item.contextValue = 'module';
            item.module = m;
            item.description = description;
            item.tooltip = new vscode.MarkdownString(`**${m.name}** (${m.classification})\n\n` +
                `- Version: ${m.manifest?.version ?? 'N/A'}\n` +
                `- License: ${m.manifest?.license ?? 'N/A'}\n` +
                `- Tests: ${m.hasTests ? m.testFiles.length + ' files' : 'none'}\n` +
                `- Depends: ${m.manifest?.depends.join(', ') ?? 'none'}\n` +
                (consolidationTarget
                    ? `\n**Consolidation:** ${consolidationTarget.action} -> ${consolidationTarget.target}`
                    : ''));
            if (m.hasTests) {
                item.iconPath = new vscode.ThemeIcon('beaker', new vscode.ThemeColor('testing.iconPassed'));
            }
            else {
                item.iconPath = new vscode.ThemeIcon('package');
            }
            item.command = {
                command: 'vscode.open',
                title: 'Open Manifest',
                arguments: [
                    vscode.Uri.file(path.join(m.path, '__manifest__.py')),
                ],
            };
            return item;
        });
    }
    getModuleDetails(mod) {
        const items = [];
        if (mod.modelFiles.length > 0) {
            for (const f of mod.modelFiles) {
                if (f.endsWith('__init__.py'))
                    continue;
                const item = new ModuleTreeItem(path.basename(f), vscode.TreeItemCollapsibleState.None);
                item.iconPath = new vscode.ThemeIcon('symbol-class');
                item.command = {
                    command: 'vscode.open',
                    title: 'Open',
                    arguments: [vscode.Uri.file(f)],
                };
                items.push(item);
            }
        }
        if (mod.testFiles.length > 0) {
            for (const f of mod.testFiles) {
                const item = new ModuleTreeItem(path.basename(f), vscode.TreeItemCollapsibleState.None);
                item.iconPath = new vscode.ThemeIcon('beaker');
                item.command = {
                    command: 'vscode.open',
                    title: 'Open',
                    arguments: [vscode.Uri.file(f)],
                };
                items.push(item);
            }
        }
        if (mod.reverseDeps.length > 0) {
            const item = new ModuleTreeItem(`Used by: ${mod.reverseDeps.join(', ')}`, vscode.TreeItemCollapsibleState.None);
            item.iconPath = new vscode.ThemeIcon('references');
            items.push(item);
        }
        return items;
    }
}
exports.OdooModulesProvider = OdooModulesProvider;
// ---------------------------------------------------------------------------
// Tree item
// ---------------------------------------------------------------------------
class ModuleTreeItem extends vscode.TreeItem {
    classification;
    module;
}
exports.ModuleTreeItem = ModuleTreeItem;
//# sourceMappingURL=odooModulesProvider.js.map