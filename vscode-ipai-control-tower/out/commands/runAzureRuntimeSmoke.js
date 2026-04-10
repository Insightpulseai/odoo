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
exports.registerAzureSmokeCommand = registerAzureSmokeCommand;
const vscode = __importStar(require("vscode"));
function registerAzureSmokeCommand(context, provider) {
    context.subscriptions.push(vscode.commands.registerCommand('ipai.runAzureRuntimeSmoke', async () => {
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'IPAI: Running Azure Runtime Smoke...',
            cancellable: false,
        }, async () => {
            await provider.refresh();
            const checks = provider.getChecks();
            const passing = checks.filter((c) => c.status === 'pass').length;
            const failing = checks.filter((c) => c.status === 'fail').length;
            if (failing === 0) {
                vscode.window.showInformationMessage(`IPAI Azure Runtime: All ${passing} checks passed`);
            }
            else {
                vscode.window.showWarningMessage(`IPAI Azure Runtime: ${passing} pass, ${failing} fail`);
            }
        });
    }));
}
//# sourceMappingURL=runAzureRuntimeSmoke.js.map