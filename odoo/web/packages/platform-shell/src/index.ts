// Console bridge (diagnostic engine)
export { createConsoleBridge } from './console-bridge';
export type { DiagnosticEntry, ConsoleBridge } from './console-bridge';

// Components
export { DiagnosticsPanel } from './DiagnosticsPanel';
export { ErrorOverlay } from './ErrorOverlay';
export { DevToolbar } from './DevToolbar';
export { HotPreviewFrame } from './HotPreviewFrame';
export { PreviewShell } from './PreviewShell';

// Provider + hook
export { PreviewShellProvider, usePreviewShell } from './PreviewShellProvider';
