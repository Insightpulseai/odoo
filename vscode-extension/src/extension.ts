import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import {exec} from 'child_process';
import {promisify} from 'util';

const execAsync = promisify(exec);

interface SandboxState {
  repoRoot: string;
  sandboxPath: string;
  composeFile: string;
  branch: string;
  commit: string;
  containers: {name: string; status: string; ports: string}[];
  dbTarget: string | null;
  addonsPath: string | null;
  health: 'healthy' | 'degraded' | 'down' | 'unknown';
  timestamp: string;
}

let outputChannel: vscode.OutputChannel;
let statusBarItem: vscode.StatusBarItem;

export function activate(context: vscode.ExtensionContext) {
  outputChannel = vscode.window.createOutputChannel('Odoo Live Sandbox');
  statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
  statusBarItem.command = 'odoo-live-sandbox.showStatus';
  context.subscriptions.push(statusBarItem);

  // Auto-detect on activation
  const config = vscode.workspace.getConfiguration('odooLiveSandbox');
  if (config.get('autoDetect')) {
    detectAndShowStatus(config.get('showBanner', true));
  }

  // Register commands
  context.subscriptions.push(
    vscode.commands.registerCommand('odoo-live-sandbox.showStatus', showStatus),
    vscode.commands.registerCommand('odoo-live-sandbox.sandboxUp', sandboxUp),
    vscode.commands.registerCommand('odoo-live-sandbox.sandboxDown', sandboxDown),
    vscode.commands.registerCommand('odoo-live-sandbox.sandboxRestart', sandboxRestart),
    vscode.commands.registerCommand('odoo-live-sandbox.showLogs', showLogs),
    vscode.commands.registerCommand('odoo-live-sandbox.dbShell', dbShell),
    vscode.commands.registerCommand('odoo-live-sandbox.odooShell', odooShell),
    vscode.commands.registerCommand('odoo-live-sandbox.updateAppsList', updateAppsList),
    vscode.commands.registerCommand('odoo-live-sandbox.installModule', installModule),
    vscode.commands.registerCommand('odoo-live-sandbox.rebuildAssets', rebuildAssets),
    vscode.commands.registerCommand('odoo-live-sandbox.runHealthCheck', runHealthCheck),
    vscode.commands.registerCommand('odoo-live-sandbox.exportState', exportState)
  );
}

async function detectAndShowStatus(showBanner: boolean) {
  const state = await detectSandboxState();
  if (!state) {
    statusBarItem.text = '$(error) Odoo: Not detected';
    statusBarItem.show();
    return;
  }

  // Update status bar
  const healthIcon = state.health === 'healthy' ? '$(check)' : state.health === 'degraded' ? '$(warning)' : '$(x)';
  statusBarItem.text = `${healthIcon} Odoo: ${state.health}`;
  statusBarItem.show();

  if (showBanner) {
    printCanonicalBanner(state);
  }
}

async function detectSandboxState(): Promise<SandboxState | null> {
  const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
  if (!workspaceFolder) {
    return null;
  }

  const repoRoot = workspaceFolder.uri.fsPath;
  const config = vscode.workspace.getConfiguration('odooLiveSandbox');
  const sandboxPath = path.join(repoRoot, config.get('sandboxPath', 'sandbox/dev'));

  // Check if sandbox exists
  if (!fs.existsSync(sandboxPath)) {
    return null;
  }

  try {
    // Detect git branch/commit
    const {stdout: branch} = await execAsync('git branch --show-current', {cwd: repoRoot});
    const {stdout: commit} = await execAsync('git rev-parse --short HEAD', {cwd: repoRoot});

    // Detect compose file
    const composeFile = fs.existsSync(path.join(sandboxPath, 'docker-compose.yml'))
      ? 'docker-compose.yml'
      : fs.existsSync(path.join(sandboxPath, 'docker-compose.production.yml'))
      ? 'docker-compose.production.yml'
      : 'unknown';

    // Detect running containers
    const {stdout: containersOutput} = await execAsync(
      `docker compose -f ${composeFile} ps --format json`,
      {cwd: sandboxPath}
    ).catch(() => ({stdout: '[]'}));

    const containers = containersOutput
      .trim()
      .split('\n')
      .filter(line => line)
      .map(line => {
        try {
          const c = JSON.parse(line);
          return {
            name: c.Name || c.name || 'unknown',
            status: c.State || c.status || 'unknown',
            ports: c.Publishers?.map((p: any) => `${p.PublishedPort}→${p.TargetPort}`).join(',') || ''
          };
        } catch {
          return {name: 'parse-error', status: 'unknown', ports: ''};
        }
      });

    // Detect DB target
    let dbTarget: string | null = null;
    const envFile = path.join(sandboxPath, '.env');
    if (fs.existsSync(envFile)) {
      const envContent = fs.readFileSync(envFile, 'utf-8');
      const dbMatch = envContent.match(/DB_HOST=([^\n]+)/);
      if (dbMatch) {
        dbTarget = dbMatch[1].includes('supabase') || dbMatch[1].includes('do-db')
          ? 'production (DO Managed)'
          : 'local';
      }
    }

    // Detect addons path
    let addonsPath: string | null = null;
    const odooConf = path.join(sandboxPath, 'odoo.conf');
    if (fs.existsSync(odooConf)) {
      const confContent = fs.readFileSync(odooConf, 'utf-8');
      const pathMatch = confContent.match(/addons_path\s*=\s*([^\n]+)/);
      if (pathMatch) {
        addonsPath = pathMatch[1].trim();
      }
    }

    // Determine health
    const runningContainers = containers.filter(c => c.status.includes('running') || c.status.includes('Up'));
    const health: SandboxState['health'] =
      runningContainers.length === 0 ? 'down' :
      runningContainers.length < containers.length ? 'degraded' :
      'healthy';

    return {
      repoRoot,
      sandboxPath,
      composeFile,
      branch: branch.trim(),
      commit: commit.trim(),
      containers,
      dbTarget,
      addonsPath,
      health,
      timestamp: new Date().toISOString()
    };
  } catch (error) {
    outputChannel.appendLine(`Detection error: ${error}`);
    return null;
  }
}

function printCanonicalBanner(state: SandboxState) {
  const banner = `
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 Odoo Live Sandbox - Canonical Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 Environment
   Repo:    ${state.repoRoot}
   Sandbox: ${state.sandboxPath}
   Compose: ${state.composeFile}
   Branch:  ${state.branch} (${state.commit})

🐳 Containers (${state.containers.length} detected)
${state.containers.map(c => `   ${c.status.includes('running') ? '✅' : '❌'} ${c.name.padEnd(20)} ${c.status.padEnd(15)} ${c.ports}`).join('\n') || '   No containers found'}

💾 Database
   Target: ${state.dbTarget || 'Not detected'}

📂 Addons Path
   ${state.addonsPath ? state.addonsPath.split(',').join('\n   ') : 'Not detected'}

🏥 Health: ${state.health.toUpperCase()}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Quick Actions (Cmd+Shift+P):
   • Odoo Live Sandbox: Up/Down/Restart
   • Odoo Live Sandbox: Tail Odoo Logs
   • Odoo Live Sandbox: Install/Upgrade Module
   • Odoo Live Sandbox: Run Health Check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`;

  outputChannel.clear();
  outputChannel.appendLine(banner);
  outputChannel.show(true);
}

async function showStatus() {
  await detectAndShowStatus(true);
}

async function sandboxUp() {
  const state = await detectSandboxState();
  if (!state) {
    vscode.window.showErrorMessage('Sandbox not detected');
    return;
  }

  const terminal = vscode.window.createTerminal({
    name: 'Odoo Sandbox Up',
    cwd: state.sandboxPath
  });
  terminal.sendText(`docker compose up -d`);
  terminal.show();

  // Refresh status after 5 seconds
  setTimeout(() => detectAndShowStatus(false), 5000);
}

async function sandboxDown() {
  const state = await detectSandboxState();
  if (!state) {
    vscode.window.showErrorMessage('Sandbox not detected');
    return;
  }

  const answer = await vscode.window.showWarningMessage(
    'Stop sandbox containers?',
    {modal: true},
    'Stop', 'Stop & Remove Volumes (DANGER)'
  );

  if (!answer) {
    return;
  }

  const terminal = vscode.window.createTerminal({
    name: 'Odoo Sandbox Down',
    cwd: state.sandboxPath
  });

  if (answer === 'Stop & Remove Volumes (DANGER)') {
    terminal.sendText(`docker compose down -v --remove-orphans`);
  } else {
    terminal.sendText(`docker compose down`);
  }

  terminal.show();
  setTimeout(() => detectAndShowStatus(false), 3000);
}

async function sandboxRestart() {
  const state = await detectSandboxState();
  if (!state) {
    vscode.window.showErrorMessage('Sandbox not detected');
    return;
  }

  const terminal = vscode.window.createTerminal({
    name: 'Odoo Sandbox Restart',
    cwd: state.sandboxPath
  });
  terminal.sendText(`docker compose restart odoo`);
  terminal.show();
}

async function showLogs() {
  const state = await detectSandboxState();
  if (!state) {
    vscode.window.showErrorMessage('Sandbox not detected');
    return;
  }

  const terminal = vscode.window.createTerminal({
    name: 'Odoo Logs',
    cwd: state.sandboxPath
  });
  terminal.sendText(`docker compose logs -f --tail=200 odoo`);
  terminal.show();
}

async function dbShell() {
  const state = await detectSandboxState();
  if (!state) {
    vscode.window.showErrorMessage('Sandbox not detected');
    return;
  }

  const terminal = vscode.window.createTerminal({
    name: 'DB Shell',
    cwd: state.sandboxPath
  });
  terminal.sendText(`docker compose exec db psql -U odoo -d odoo`);
  terminal.show();
}

async function odooShell() {
  const state = await detectSandboxState();
  if (!state) {
    vscode.window.showErrorMessage('Sandbox not detected');
    return;
  }

  const terminal = vscode.window.createTerminal({
    name: 'Odoo Shell',
    cwd: state.sandboxPath
  });
  terminal.sendText(`docker compose exec odoo odoo shell -d odoo`);
  terminal.show();
}

async function updateAppsList() {
  const state = await detectSandboxState();
  if (!state) {
    vscode.window.showErrorMessage('Sandbox not detected');
    return;
  }

  const terminal = vscode.window.createTerminal({
    name: 'Update Apps List',
    cwd: state.sandboxPath
  });
  terminal.sendText(`docker compose exec -T odoo odoo -d odoo --update-apps-list --stop-after-init`);
  terminal.show();

  vscode.window.showInformationMessage('Updating apps list (hot reload safe)...');
}

async function installModule() {
  const state = await detectSandboxState();
  if (!state) {
    vscode.window.showErrorMessage('Sandbox not detected');
    return;
  }

  const moduleName = await vscode.window.showInputBox({
    prompt: 'Enter module name to install/upgrade',
    placeHolder: 'e.g., ipai_finance_ppm',
    validateInput: (value) => value.trim() ? null : 'Module name required'
  });

  if (!moduleName) {
    return;
  }

  const action = await vscode.window.showQuickPick(['Install (-i)', 'Upgrade (-u)'], {
    placeHolder: 'Install or upgrade?'
  });

  if (!action) {
    return;
  }

  const flag = action.startsWith('Install') ? '-i' : '-u';

  const terminal = vscode.window.createTerminal({
    name: `${action} ${moduleName}`,
    cwd: state.sandboxPath
  });
  terminal.sendText(`docker compose exec -T odoo odoo -d odoo ${flag} ${moduleName} --stop-after-init`);
  terminal.show();

  vscode.window.showInformationMessage(`${action} ${moduleName} (hot reload safe)...`);
}

async function rebuildAssets() {
  const state = await detectSandboxState();
  if (!state) {
    vscode.window.showErrorMessage('Sandbox not detected');
    return;
  }

  const answer = await vscode.window.showWarningMessage(
    'Rebuild assets? This will restart Odoo.',
    {modal: true},
    'Rebuild'
  );

  if (!answer) {
    return;
  }

  const terminal = vscode.window.createTerminal({
    name: 'Rebuild Assets',
    cwd: state.sandboxPath
  });
  terminal.sendText(`docker compose restart odoo`);
  terminal.show();

  vscode.window.showInformationMessage('Rebuilding assets (Odoo restarting)...');
}

async function runHealthCheck() {
  const state = await detectSandboxState();
  if (!state) {
    vscode.window.showErrorMessage('Sandbox not detected');
    return;
  }

  const healthScript = path.join(state.repoRoot, 'scripts/healthcheck_odoo_login.sh');

  if (!fs.existsSync(healthScript)) {
    vscode.window.showWarningMessage('Health check script not found: scripts/healthcheck_odoo_login.sh');
    return;
  }

  const terminal = vscode.window.createTerminal({
    name: 'Health Check',
    cwd: state.repoRoot
  });
  terminal.sendText(`./scripts/healthcheck_odoo_login.sh`);
  terminal.show();
}

async function exportState() {
  const state = await detectSandboxState();
  if (!state) {
    vscode.window.showErrorMessage('Sandbox not detected');
    return;
  }

  const stateFile = path.join(state.sandboxPath, 'sandbox_state.json');
  fs.writeFileSync(stateFile, JSON.stringify(state, null, 2));

  outputChannel.appendLine(`\nRuntime state exported to: ${stateFile}`);
  outputChannel.appendLine(JSON.stringify(state, null, 2));
  outputChannel.show();

  vscode.window.showInformationMessage(`State exported: ${stateFile}`);
}

export function deactivate() {
  if (outputChannel) {
    outputChannel.dispose();
  }
  if (statusBarItem) {
    statusBarItem.dispose();
  }
}
