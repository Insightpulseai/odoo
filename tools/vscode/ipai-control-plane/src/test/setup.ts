import { vi } from "vitest";

// Mock the vscode module for unit tests
vi.mock("vscode", () => ({
  window: {
    showInformationMessage: vi.fn(),
    showErrorMessage: vi.fn(),
    showWarningMessage: vi.fn(),
    showInputBox: vi.fn(),
    showQuickPick: vi.fn(),
    createOutputChannel: vi.fn(() => ({
      appendLine: vi.fn(),
      show: vi.fn(),
      clear: vi.fn(),
      dispose: vi.fn()
    })),
    createTreeView: vi.fn(),
    createWebviewPanel: vi.fn(),
    withProgress: vi.fn()
  },
  commands: {
    registerCommand: vi.fn(),
    executeCommand: vi.fn()
  },
  workspace: {
    getConfiguration: vi.fn(() => ({
      get: vi.fn(),
      update: vi.fn()
    })),
    workspaceFolders: [],
    onDidChangeConfiguration: vi.fn(),
    fs: {
      readFile: vi.fn(),
      writeFile: vi.fn()
    }
  },
  Uri: {
    file: vi.fn((path) => ({ fsPath: path, path, scheme: "file" })),
    parse: vi.fn((str) => ({ fsPath: str, path: str, scheme: "file" }))
  },
  TreeItem: class TreeItem {
    constructor(public label: string, public collapsibleState?: number) {}
  },
  TreeItemCollapsibleState: {
    None: 0,
    Collapsed: 1,
    Expanded: 2
  },
  EventEmitter: class EventEmitter {
    fire() {}
    event = vi.fn()
  },
  DiagnosticSeverity: {
    Error: 0,
    Warning: 1,
    Information: 2,
    Hint: 3
  },
  languages: {
    createDiagnosticCollection: vi.fn(() => ({
      set: vi.fn(),
      delete: vi.fn(),
      clear: vi.fn(),
      dispose: vi.fn()
    }))
  },
  Range: class Range {
    constructor(public start: any, public end: any) {}
  },
  Position: class Position {
    constructor(public line: number, public character: number) {}
  },
  Diagnostic: class Diagnostic {
    constructor(public range: any, public message: string, public severity: number) {}
  }
}));
