import * as vscode from 'vscode';
import { ControlPlaneClient } from '../client/ControlPlaneClient';

export class DiagnosticProvider {
  private diagnostics: vscode.DiagnosticCollection;
  private client: ControlPlaneClient;
  private watchers: vscode.FileSystemWatcher[] = [];

  constructor(client: ControlPlaneClient) {
    this.client = client;
    this.diagnostics = vscode.languages.createDiagnosticCollection('ipai');

    // Watch for file changes
    const manifestWatcher = vscode.workspace.createFileSystemWatcher('**/__manifest__.py');
    manifestWatcher.onDidChange(uri => this.validateManifest(uri));
    manifestWatcher.onDidCreate(uri => this.validateManifest(uri));
    this.watchers.push(manifestWatcher);

    const xmlWatcher = vscode.workspace.createFileSystemWatcher('**/*.xml');
    xmlWatcher.onDidChange(uri => this.validateXml(uri));
    xmlWatcher.onDidCreate(uri => this.validateXml(uri));
    this.watchers.push(xmlWatcher);
  }

  async validateManifest(uri: vscode.Uri) {
    const autoRun = vscode.workspace.getConfiguration('ipai').get<boolean>('validation.autoRun', true);
    if (!autoRun) { return; }

    try {
      const result = await this.client.validateManifest(uri.fsPath);
      const diagnostics = this.convertToDiagnostics(result.issues);
      this.diagnostics.set(uri, diagnostics);
    } catch (error) {
      console.error(`Manifest validation failed: ${error}`);
    }
  }

  async validateXml(uri: vscode.Uri) {
    const autoRun = vscode.workspace.getConfiguration('ipai').get<boolean>('validation.autoRun', true);
    if (!autoRun) { return; }

    try {
      const result = await this.client.validateXml(uri.fsPath);
      const diagnostics = this.convertToDiagnostics(result.issues);
      this.diagnostics.set(uri, diagnostics);
    } catch (error) {
      console.error(`XML validation failed: ${error}`);
    }
  }

  private convertToDiagnostics(issues: any[]): vscode.Diagnostic[] {
    return issues.map(issue => {
      const line = (issue.line || 1) - 1;
      const range = new vscode.Range(line, issue.column || 0, line, 999);

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
  }

  dispose() {
    this.diagnostics.dispose();
    this.watchers.forEach(w => w.dispose());
  }
}
