import * as vscode from 'vscode';
import { ControlPlaneClient } from './client/ControlPlaneClient';
import { ProjectTreeProvider } from './providers/ProjectTreeProvider';
import { ValidationTreeProvider } from './providers/ValidationTreeProvider';
import { EvidenceTreeProvider } from './providers/EvidenceTreeProvider';
import { DiagnosticProvider } from './providers/DiagnosticProvider';
import { registerCommands } from './commands';

let client: ControlPlaneClient;

export async function activate(context: vscode.ExtensionContext) {
  console.log('IPAI Control Plane activating...');

  // Initialize control plane client
  const port = vscode.workspace.getConfiguration('ipai').get<number>('controlPlane.port', 9876);
  client = new ControlPlaneClient(`http://127.0.0.1:${port}`);

  // Check if control plane is running
  const isReady = await client.healthCheck();
  if (!isReady) {
    vscode.window.showWarningMessage(
      'IPAI Control Plane server not running. Some features will be unavailable.',
      'Start Server'
    ).then(selection => {
      if (selection === 'Start Server') {
        vscode.commands.executeCommand('ipai.controlPlane.start');
      }
    });
  }

  // Register tree providers
  const projectTreeProvider = new ProjectTreeProvider(client);
  const validationTreeProvider = new ValidationTreeProvider(client);
  const evidenceTreeProvider = new EvidenceTreeProvider(client);

  vscode.window.registerTreeDataProvider('ipaiProjects', projectTreeProvider);
  vscode.window.registerTreeDataProvider('ipaiValidation', validationTreeProvider);
  vscode.window.registerTreeDataProvider('ipaiEvidence', evidenceTreeProvider);

  // Register diagnostic provider
  const diagnosticProvider = new DiagnosticProvider(client);
  context.subscriptions.push(diagnosticProvider);

  // Register all commands
  registerCommands(context, client, {
    projectTreeProvider,
    validationTreeProvider,
    evidenceTreeProvider
  });

  console.log('IPAI Control Plane activated');
}

export function deactivate() {
  console.log('IPAI Control Plane deactivating...');
}

export { client };
