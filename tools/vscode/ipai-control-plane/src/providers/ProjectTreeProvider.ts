import * as vscode from 'vscode';
import { ControlPlaneClient, Project, Environment } from '../client/ControlPlaneClient';

export class ProjectTreeProvider implements vscode.TreeDataProvider<TreeItem> {
  private _onDidChangeTreeData: vscode.EventEmitter<TreeItem | undefined | null | void> = new vscode.EventEmitter<TreeItem | undefined | null | void>();
  readonly onDidChangeTreeData: vscode.Event<TreeItem | undefined | null | void> = this._onDidChangeTreeData.event;

  constructor(private client: ControlPlaneClient) {}

  refresh(): void {
    this._onDidChangeTreeData.fire();
  }

  async getChildren(element?: TreeItem): Promise<TreeItem[]> {
    if (!element) {
      // Root: list projects
      try {
        const projects = await this.client.getProjects();
        return projects.map(p => new ProjectItem(p));
      } catch (error) {
        vscode.window.showErrorMessage(`Failed to load projects: ${error}`);
        return [];
      }
    }

    if (element instanceof ProjectItem) {
      // Project node: list environments
      try {
        const envs = await this.client.getEnvironments(element.project.id);
        return envs.map(e => new EnvironmentItem(e, element.project.id));
      } catch (error) {
        vscode.window.showErrorMessage(`Failed to load environments: ${error}`);
        return [];
      }
    }

    if (element instanceof EnvironmentItem) {
      // Environment node: show status details
      return [
        new StatusItem('Odoo Version', element.env.odoo_version, 'versions'),
        new StatusItem('Modules', `${element.env.modules_installed.length} installed`, 'package'),
        new StatusItem('Schema Hash', element.env.schema_hash.substring(0, 8), 'symbol-namespace'),
        new StatusItem('Health', element.env.health, this.getHealthIcon(element.env.health)),
        new StatusItem('Pending Migrations', `${element.env.pending_migrations.length}`, 'database')
      ];
    }

    return [];
  }

  getTreeItem(element: TreeItem): vscode.TreeItem {
    return element;
  }

  private getHealthIcon(health: string): string {
    switch (health) {
      case 'healthy': return 'pass';
      case 'degraded': return 'warning';
      case 'failed': return 'error';
      default: return 'circle-outline';
    }
  }
}

type TreeItem = ProjectItem | EnvironmentItem | StatusItem;

class ProjectItem extends vscode.TreeItem {
  constructor(public project: Project) {
    super(project.id, vscode.TreeItemCollapsibleState.Collapsed);
    this.iconPath = new vscode.ThemeIcon('database');
    this.contextValue = 'project';
    this.description = project.repo_root;
  }
}

class EnvironmentItem extends vscode.TreeItem {
  constructor(public env: Environment, public projectId: string) {
    super(env.name, vscode.TreeItemCollapsibleState.Collapsed);
    this.iconPath = this.getIcon(env.health);
    this.description = env.odoo_version;
    this.contextValue = 'environment';
  }

  private getIcon(health: string): vscode.ThemeIcon {
    switch (health) {
      case 'healthy':
        return new vscode.ThemeIcon('check', new vscode.ThemeColor('testing.iconPassed'));
      case 'degraded':
        return new vscode.ThemeIcon('warning', new vscode.ThemeColor('testing.iconQueued'));
      case 'failed':
        return new vscode.ThemeIcon('error', new vscode.ThemeColor('testing.iconFailed'));
      default:
        return new vscode.ThemeIcon('circle-outline');
    }
  }
}

class StatusItem extends vscode.TreeItem {
  constructor(label: string, value: string, iconName: string) {
    super(`${label}: ${value}`, vscode.TreeItemCollapsibleState.None);
    this.iconPath = new vscode.ThemeIcon(iconName);
  }
}
