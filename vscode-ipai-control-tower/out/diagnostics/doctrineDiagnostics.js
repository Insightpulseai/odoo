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
exports.DoctrineDiagnosticsProvider = void 0;
const vscode = __importStar(require("vscode"));
/**
 * Doctrine diagnostics — emits inline warnings for:
 *
 * 1. Importing from deprecated modules
 * 2. Synchronous HTTP calls in Odoo models (requests.post/get)
 * 3. Odoo 18 breaking patterns (states= attribute, <tree> in XML, group_operator)
 * 4. Hardcoded secrets patterns
 */
class DoctrineDiagnosticsProvider {
    collection;
    disposables = [];
    deprecatedModules = new Set();
    constructor() {
        this.collection = vscode.languages.createDiagnosticCollection('ipai-doctrine');
    }
    /**
     * Set the list of deprecated module names for import checking.
     */
    setDeprecatedModules(modules) {
        this.deprecatedModules = new Set(modules
            .filter((m) => m.classification === 'deprecated')
            .map((m) => m.name));
    }
    /**
     * Start watching open documents for doctrine violations.
     */
    activate() {
        // Analyze on open/change
        this.disposables.push(vscode.workspace.onDidOpenTextDocument((doc) => this.analyzeDocument(doc)), vscode.workspace.onDidChangeTextDocument((e) => this.analyzeDocument(e.document)), vscode.workspace.onDidCloseTextDocument((doc) => this.collection.delete(doc.uri)));
        // Analyze all currently open documents
        for (const doc of vscode.workspace.textDocuments) {
            this.analyzeDocument(doc);
        }
    }
    analyzeDocument(document) {
        if (!this.isRelevant(document))
            return;
        const diagnostics = [];
        if (document.languageId === 'python') {
            diagnostics.push(...this.checkPython(document));
        }
        else if (document.languageId === 'xml') {
            diagnostics.push(...this.checkXml(document));
        }
        this.collection.set(document.uri, diagnostics);
    }
    // -----------------------------------------------------------------------
    // Python checks
    // -----------------------------------------------------------------------
    checkPython(document) {
        const diagnostics = [];
        const text = document.getText();
        const lines = text.split('\n');
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            // Check deprecated module imports
            for (const dep of this.deprecatedModules) {
                if (line.includes(`from ${dep}`) || line.includes(`import ${dep}`)) {
                    diagnostics.push(this.createDiagnostic(i, line.indexOf(dep), dep.length, `Import from deprecated module '${dep}'. Check consolidation plan for migration target.`, vscode.DiagnosticSeverity.Warning, 'deprecated-import'));
                }
            }
            // Check synchronous HTTP calls in model files
            if (document.uri.fsPath.includes('/models/')) {
                const httpPatterns = [
                    { pattern: 'requests.post', msg: 'Synchronous requests.post in Odoo model' },
                    { pattern: 'requests.get', msg: 'Synchronous requests.get in Odoo model' },
                    { pattern: 'requests.put', msg: 'Synchronous requests.put in Odoo model' },
                    { pattern: 'requests.delete', msg: 'Synchronous requests.delete in Odoo model' },
                ];
                for (const { pattern, msg } of httpPatterns) {
                    const idx = line.indexOf(pattern);
                    if (idx >= 0) {
                        diagnostics.push(this.createDiagnostic(i, idx, pattern.length, `${msg} — should use queue_job for async processing or externalize to Azure Function.`, vscode.DiagnosticSeverity.Warning, 'sync-http-in-model'));
                    }
                }
            }
            // Check Odoo 18 breaking: states= attribute on fields
            const statesMatch = line.match(/states\s*=\s*\{/);
            if (statesMatch && statesMatch.index !== undefined) {
                diagnostics.push(this.createDiagnostic(i, statesMatch.index, statesMatch[0].length, 'Odoo 18 breaking change: states= attribute is removed. Use readonly/invisible expressions in XML views instead.', vscode.DiagnosticSeverity.Error, 'odoo18-states-removed'));
            }
            // Check Odoo 18 breaking: group_operator (renamed to aggregator)
            const groupOpMatch = line.match(/group_operator\s*=/);
            if (groupOpMatch && groupOpMatch.index !== undefined) {
                diagnostics.push(this.createDiagnostic(i, groupOpMatch.index, groupOpMatch[0].length, 'Odoo 18 breaking change: group_operator is renamed to aggregator.', vscode.DiagnosticSeverity.Error, 'odoo18-group-operator'));
            }
            // Check potential hardcoded secrets
            const secretMatch = line.match(/(?:password|secret|api_key|token)\s*=\s*['"][^'"]{8,}['"]/i);
            if (secretMatch &&
                secretMatch.index !== undefined &&
                !line.trimStart().startsWith('#') &&
                !line.includes('os.environ') &&
                !line.includes('getenv')) {
                diagnostics.push(this.createDiagnostic(i, secretMatch.index, secretMatch[0].length, 'Potential hardcoded secret. Use environment variables or Azure Key Vault.', vscode.DiagnosticSeverity.Error, 'hardcoded-secret'));
            }
        }
        return diagnostics;
    }
    // -----------------------------------------------------------------------
    // XML checks
    // -----------------------------------------------------------------------
    checkXml(document) {
        const diagnostics = [];
        const lines = document.getText().split('\n');
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            // Check Odoo 18 breaking: <tree> should be <list>
            const treeMatch = line.match(/<tree\s/);
            if (treeMatch && treeMatch.index !== undefined) {
                diagnostics.push(this.createDiagnostic(i, treeMatch.index, treeMatch[0].length, 'Odoo 18 breaking change: <tree> is renamed to <list>.', vscode.DiagnosticSeverity.Error, 'odoo18-tree-to-list'));
            }
            // Check deprecated attrs= syntax (Odoo 18 uses inline expressions)
            const attrsMatch = line.match(/attrs\s*=\s*['"]\{/);
            if (attrsMatch && attrsMatch.index !== undefined) {
                diagnostics.push(this.createDiagnostic(i, attrsMatch.index, attrsMatch[0].length, 'Odoo 18: attrs= dict syntax is deprecated. Use inline expressions: invisible="condition", readonly="condition".', vscode.DiagnosticSeverity.Warning, 'odoo18-attrs-deprecated'));
            }
        }
        return diagnostics;
    }
    // -----------------------------------------------------------------------
    // Helpers
    // -----------------------------------------------------------------------
    isRelevant(document) {
        const path = document.uri.fsPath;
        return ((document.languageId === 'python' || document.languageId === 'xml') &&
            (path.includes('addons/ipai') || path.includes('addons/oca')));
    }
    createDiagnostic(line, col, length, message, severity, code) {
        const range = new vscode.Range(line, col, line, col + length);
        const diag = new vscode.Diagnostic(range, message, severity);
        diag.code = code;
        diag.source = 'IPAI Control Tower';
        return diag;
    }
    dispose() {
        this.collection.dispose();
        for (const d of this.disposables) {
            d.dispose();
        }
    }
}
exports.DoctrineDiagnosticsProvider = DoctrineDiagnosticsProvider;
//# sourceMappingURL=doctrineDiagnostics.js.map