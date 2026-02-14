import * as vscode from 'vscode';
import { ControlPlaneClient } from '../client/ControlPlaneClient';

interface Providers {
  projectTreeProvider: any;
  validationTreeProvider: any;
  evidenceTreeProvider: any;
}

export async function installModulesCommand(
  client: ControlPlaneClient,
  environmentItem: any,
  providers: Providers
) {
  try {
    // Get project and environment context
    const projectId = environmentItem?.projectId || 'default';
    const environment = environmentItem?.env?.name || 'dev';

    // Prompt for modules to install
    const modulesInput = await vscode.window.showInputBox({
      prompt: 'Enter module names to install (comma-separated)',
      placeHolder: 'sale,account,stock',
      validateInput: (value) => {
        if (!value || value.trim().length === 0) {
          return 'Please enter at least one module name';
        }
        return null;
      }
    });

    if (!modulesInput) {
      return; // User cancelled
    }

    const modules = modulesInput.split(',').map(m => m.trim()).filter(m => m.length > 0);

    // Show progress
    await vscode.window.withProgress({
      location: vscode.ProgressLocation.Notification,
      title: 'Planning module installation',
      cancellable: false
    }, async (progress) => {
      progress.report({ message: 'Generating diffs...' });

      // Step 1: Plan operation
      const plan = await client.planOperation('install_modules', {
        environment,
        modules,
        project_id: projectId
      });

      // Check for validation failures
      const failedChecks = plan.checks.filter(c => c.status === 'fail');
      if (failedChecks.length > 0) {
        const errors = failedChecks.map(c => c.message).join('\n');
        vscode.window.showErrorMessage(
          `Installation validation failed:\n${errors}`
        );
        return;
      }

      progress.report({ message: 'Showing diff preview...' });

      // Step 2: Show diff preview
      const approved = await showDiffPreview(plan);
      if (!approved) {
        return; // User cancelled
      }

      progress.report({ message: 'Executing operation...' });

      // Step 3: Execute operation
      const execution = await client.executeOperation(plan.op_id);

      progress.report({ message: 'Waiting for completion...' });

      // Step 4: Poll for completion (simple polling)
      let status = await client.getOperationStatus(execution.op_id);
      let attempts = 0;
      while (status.status === 'running' && attempts < 30) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        status = await client.getOperationStatus(execution.op_id);
        attempts++;
      }

      if (status.status === 'succeeded') {
        vscode.window.showInformationMessage(
          `✅ Modules installed successfully!\nEvidence: ${execution.bundle_id}`
        );

        // Refresh tree views
        providers.projectTreeProvider.refresh();
        providers.evidenceTreeProvider.refresh();
      } else {
        vscode.window.showErrorMessage(
          `❌ Installation failed (status: ${status.status})`
        );
      }
    });

  } catch (error: any) {
    vscode.window.showErrorMessage(
      `Installation failed: ${error.message || error}`
    );
  }
}

async function showDiffPreview(plan: any): Promise<boolean> {
  // Create webview panel for diff preview
  const panel = vscode.window.createWebviewPanel(
    'diffPreview',
    'Module Installation Preview',
    vscode.ViewColumn.One,
    {
      enableScripts: true
    }
  );

  // Generate HTML content
  panel.webview.html = generateDiffPreviewHtml(plan);

  // Wait for user decision
  return new Promise<boolean>((resolve) => {
    panel.webview.onDidReceiveMessage(
      message => {
        if (message.command === 'approve') {
          panel.dispose();
          resolve(true);
        } else if (message.command === 'cancel') {
          panel.dispose();
          resolve(false);
        }
      }
    );

    panel.onDidDispose(() => {
      resolve(false);
    });
  });
}

function generateDiffPreviewHtml(plan: any): string {
  const diffsHtml = plan.diffs.map((diff: any) => `
    <div class="diff">
      <h3>${diff.type.toUpperCase()}: ${diff.path}</h3>
      <p>${diff.summary}</p>
      <pre><code>${escapeHtml(diff.patch)}</code></pre>
    </div>
  `).join('');

  const checksHtml = plan.checks.map((check: any) => {
    const icon = check.status === 'pass' ? '✅' : check.status === 'warn' ? '⚠️' : '❌';
    return `<div class="check ${check.status}">${icon} ${check.message}</div>`;
  }).join('');

  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body {
      font-family: var(--vscode-font-family);
      padding: 20px;
      color: var(--vscode-foreground);
      background-color: var(--vscode-editor-background);
    }
    h1 {
      color: var(--vscode-titleBar-activeForeground);
    }
    .diff {
      margin: 20px 0;
      padding: 15px;
      border: 1px solid var(--vscode-panel-border);
      border-radius: 4px;
      background-color: var(--vscode-editor-background);
    }
    .diff h3 {
      margin-top: 0;
      color: var(--vscode-textLink-foreground);
    }
    pre {
      background-color: var(--vscode-textCodeBlock-background);
      padding: 10px;
      border-radius: 4px;
      overflow-x: auto;
    }
    code {
      font-family: var(--vscode-editor-font-family);
      font-size: var(--vscode-editor-font-size);
    }
    .checks {
      margin: 20px 0;
      padding: 15px;
      background-color: var(--vscode-editor-background);
      border: 1px solid var(--vscode-panel-border);
      border-radius: 4px;
    }
    .check {
      padding: 5px 0;
    }
    .check.fail {
      color: var(--vscode-errorForeground);
    }
    .check.warn {
      color: var(--vscode-warningForeground);
    }
    .check.pass {
      color: var(--vscode-testing-iconPassed);
    }
    .actions {
      margin-top: 30px;
      display: flex;
      gap: 10px;
    }
    button {
      padding: 10px 20px;
      font-size: 14px;
      cursor: pointer;
      border: none;
      border-radius: 4px;
    }
    .approve {
      background-color: var(--vscode-button-background);
      color: var(--vscode-button-foreground);
    }
    .approve:hover {
      background-color: var(--vscode-button-hoverBackground);
    }
    .cancel {
      background-color: var(--vscode-button-secondaryBackground);
      color: var(--vscode-button-secondaryForeground);
    }
    .cancel:hover {
      background-color: var(--vscode-button-secondaryHoverBackground);
    }
  </style>
</head>
<body>
  <h1>Module Installation Preview</h1>

  <h2>Validation Checks</h2>
  <div class="checks">
    ${checksHtml}
  </div>

  <h2>Changes</h2>
  ${diffsHtml}

  <div class="actions">
    <button class="approve" onclick="approve()">✅ Install Modules</button>
    <button class="cancel" onclick="cancel()">❌ Cancel</button>
  </div>

  <script>
    const vscode = acquireVsCodeApi();

    function approve() {
      vscode.postMessage({ command: 'approve' });
    }

    function cancel() {
      vscode.postMessage({ command: 'cancel' });
    }
  </script>
</body>
</html>
  `;
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
