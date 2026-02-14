import * as vscode from 'vscode';
import { ControlPlaneClient } from '../client/ControlPlaneClient';

export class EvidenceTreeProvider implements vscode.TreeDataProvider<vscode.TreeItem> {
  private _onDidChangeTreeData: vscode.EventEmitter<vscode.TreeItem | undefined | null | void> = new vscode.EventEmitter<vscode.TreeItem | undefined | null | void>();
  readonly onDidChangeTreeData: vscode.Event<vscode.TreeItem | undefined | null | void> = this._onDidChangeTreeData.event;

  constructor(private client: ControlPlaneClient) {}

  refresh(): void {
    this._onDidChangeTreeData.fire();
  }

  getTreeItem(element: vscode.TreeItem): vscode.TreeItem {
    return element;
  }

  async getChildren(): Promise<vscode.TreeItem[]> {
    try {
      // Get evidence bundles for default project
      const bundles = await this.client.getEvidenceBundles('default');

      if (bundles.length === 0) {
        const item = new vscode.TreeItem('No evidence bundles yet', vscode.TreeItemCollapsibleState.None);
        item.description = 'Operations will appear here';
        return [item];
      }

      return bundles.map(bundle => {
        const item = new vscode.TreeItem(
          bundle.operation || 'Operation',
          vscode.TreeItemCollapsibleState.None
        );

        item.description = `${bundle.timestamp} - ${bundle.status}`;
        item.iconPath = this.getStatusIcon(bundle.status);
        item.tooltip = `Bundle: ${bundle.bundle_id}\nEnvironment: ${bundle.target_env || 'N/A'}`;
        item.contextValue = 'evidenceBundle';

        return item;
      });
    } catch (error) {
      console.error('Failed to load evidence bundles:', error);
      const item = new vscode.TreeItem('Failed to load', vscode.TreeItemCollapsibleState.None);
      item.description = 'Check control plane server';
      return [item];
    }
  }

  private getStatusIcon(status: string): vscode.ThemeIcon {
    switch (status) {
      case 'success':
      case 'succeeded':
        return new vscode.ThemeIcon('check', new vscode.ThemeColor('testing.iconPassed'));
      case 'failed':
        return new vscode.ThemeIcon('error', new vscode.ThemeColor('testing.iconFailed'));
      case 'running':
      case 'pending':
        return new vscode.ThemeIcon('sync~spin', new vscode.ThemeColor('testing.iconQueued'));
      default:
        return new vscode.ThemeIcon('circle-outline');
    }
  }
}
