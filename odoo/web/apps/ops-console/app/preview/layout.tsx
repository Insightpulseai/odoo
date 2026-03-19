"use client"

import { PreviewShellProvider, PreviewShell, DevToolbar, DiagnosticsPanel, usePreviewShell } from "@ipai/platform-shell"

function PreviewLayoutInner({ children }: { children: React.ReactNode }) {
  const { entries, diagnosticsOpen, toggleDiagnostics, clearDiagnostics } = usePreviewShell()

  return (
    <div style={{ position: "fixed", inset: 0, zIndex: 100, background: "var(--background, #0a0a0a)" }}>
      <PreviewShell
        toolbar={
          <DevToolbar
            environment={process.env.NODE_ENV === "production" ? "production" : "dev"}
            diagnosticCount={entries.length}
            onToggleDiagnostics={toggleDiagnostics}
            onClearDiagnostics={clearDiagnostics}
            buildSha={process.env.NEXT_PUBLIC_BUILD_SHA}
          />
        }
        preview={children}
        diagnostics={<DiagnosticsPanel entries={entries} onClear={clearDiagnostics} />}
        diagnosticsOpen={diagnosticsOpen}
      />
    </div>
  )
}

export default function PreviewLayout({ children }: { children: React.ReactNode }) {
  return (
    <PreviewShellProvider>
      <PreviewLayoutInner>{children}</PreviewLayoutInner>
    </PreviewShellProvider>
  )
}
