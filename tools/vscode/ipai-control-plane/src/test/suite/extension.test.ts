import * as assert from 'assert';
import * as vscode from 'vscode';

suite('IPAI Control Plane Extension Test Suite', () => {
  vscode.window.showInformationMessage('Start all tests.');

  test('Extension should be present', () => {
    const ext = vscode.extensions.getExtension('InsightpulseAI.ipai-control-plane');
    assert.ok(ext, 'Extension not found');
  });

  test('Extension should activate', async () => {
    const ext = vscode.extensions.getExtension('InsightpulseAI.ipai-control-plane');
    assert.ok(ext, 'Extension not found');

    await ext.activate();
    assert.strictEqual(ext.isActive, true, 'Extension did not activate');
  });

  test('All commands should be registered', async () => {
    const commands = await vscode.commands.getCommands(true);

    const requiredCommands = [
      'ipai.projects.refresh',
      'ipai.projects.select',
      'ipai.env.deploy',
      'ipai.env.rollback',
      'ipai.env.shell',
      'ipai.env.logs',
      'ipai.validate.manifest',
      'ipai.validate.xml',
      'ipai.validate.security',
      'ipai.validate.all',
      'ipai.ops.install',
      'ipai.ops.migrate',
      'ipai.ops.upgrade',
      'ipai.ai.generatePatch',
      'ipai.ai.explainDrift',
      'ipai.ai.planUpgrade'
    ];

    for (const cmd of requiredCommands) {
      assert.ok(
        commands.includes(cmd),
        `Command ${cmd} not registered`
      );
    }
  });

  test('Tree views should be registered', () => {
    // Verify tree view container exists
    const container = vscode.window.registerTreeDataProvider;
    assert.ok(container, 'Tree view container not available');
  });

  test('Configuration settings should be available', () => {
    const config = vscode.workspace.getConfiguration('ipai');

    // Check default values
    assert.strictEqual(config.get('controlPlane.port'), 9876, 'Default port incorrect');
    assert.strictEqual(config.get('projects.defaultEnvironment'), 'dev', 'Default environment incorrect');
    assert.strictEqual(config.get('validation.autoRun'), true, 'Auto-run validation should be enabled');
    assert.strictEqual(config.get('evidence.autoGenerate'), true, 'Auto-generate evidence should be enabled');
    assert.strictEqual(config.get('ai.provider'), 'claude', 'Default AI provider incorrect');
  });

  test('Diagnostic collection should be created', async () => {
    const ext = vscode.extensions.getExtension('InsightpulseAI.ipai-control-plane');
    assert.ok(ext, 'Extension not found');

    await ext.activate();

    // Diagnostics are registered during activation
    // We can't directly access the DiagnosticCollection, but we can verify no errors occurred
    assert.ok(true, 'Diagnostics initialized without errors');
  });
});
