import * as vscode from 'vscode';
import { ControlPlaneClient } from '../client/ControlPlaneClient';
import { ProjectTreeProvider } from '../providers/ProjectTreeProvider';
import { ValidationTreeProvider } from '../providers/ValidationTreeProvider';
import { EvidenceTreeProvider } from '../providers/EvidenceTreeProvider';
import { installModulesCommand } from './operations';

interface Providers {
  projectTreeProvider: ProjectTreeProvider;
  validationTreeProvider: ValidationTreeProvider;
  evidenceTreeProvider: EvidenceTreeProvider;
}

export function registerCommands(
  context: vscode.ExtensionContext,
  client: ControlPlaneClient,
  providers: Providers
) {
  // Project commands
  context.subscriptions.push(
    vscode.commands.registerCommand('ipai.projects.refresh', () => {
      providers.projectTreeProvider.refresh();
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('ipai.projects.select', async () => {
      const projects = await client.getProjects();
      const selected = await vscode.window.showQuickPick(
        projects.map(p => ({ label: p.id, description: p.repo_root })),
        { placeHolder: 'Select a project' }
      );
      if (selected) {
        vscode.window.showInformationMessage(`Selected project: ${selected.label}`);
      }
    })
  );

  // Environment commands
  context.subscriptions.push(
    vscode.commands.registerCommand('ipai.env.deploy', async () => {
      vscode.window.showInformationMessage('Deploy: Not implemented yet');
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('ipai.env.rollback', async () => {
      vscode.window.showInformationMessage('Rollback: Not implemented yet');
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('ipai.env.shell', async () => {
      vscode.window.showInformationMessage('Shell: Not implemented yet');
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('ipai.env.logs', async () => {
      vscode.window.showInformationMessage('Logs: Not implemented yet');
    })
  );

  // Validation commands
  context.subscriptions.push(
    vscode.commands.registerCommand('ipai.validate.manifest', async () => {
      vscode.window.showInformationMessage('Validate Manifest: Not implemented yet');
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('ipai.validate.xml', async () => {
      vscode.window.showInformationMessage('Validate XML: Not implemented yet');
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('ipai.validate.security', async () => {
      vscode.window.showInformationMessage('Validate Security: Not implemented yet');
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('ipai.validate.all', async () => {
      vscode.window.showInformationMessage('Validate All: Not implemented yet');
    })
  );

  // Operation commands
  context.subscriptions.push(
    vscode.commands.registerCommand('ipai.ops.install', async (environmentItem?: any) => {
      await installModulesCommand(client, environmentItem, providers);
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('ipai.ops.migrate', async () => {
      vscode.window.showInformationMessage('Run Migration: Not implemented yet');
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('ipai.ops.upgrade', async () => {
      vscode.window.showInformationMessage('Upgrade Odoo: Not implemented yet');
    })
  );

  // AI commands
  context.subscriptions.push(
    vscode.commands.registerCommand('ipai.ai.generatePatch', async () => {
      vscode.window.showInformationMessage('AI Generate Patch: Not implemented yet');
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('ipai.ai.explainDrift', async () => {
      vscode.window.showInformationMessage('AI Explain Drift: Not implemented yet');
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('ipai.ai.planUpgrade', async () => {
      vscode.window.showInformationMessage('AI Plan Upgrade: Not implemented yet');
    })
  );
}
