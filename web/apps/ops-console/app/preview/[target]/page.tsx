"use client"

import { useParams } from "next/navigation"
import { HotPreviewFrame, usePreviewShell } from "@ipai/platform-shell"

function ComponentsPreview() {
  return (
    <div className="p-8 space-y-8">
      <h2 className="text-lg font-semibold">Component Library</h2>
      <p className="text-sm text-muted-foreground">
        Browse and test components with live diagnostics. Errors and warnings appear in the right panel.
      </p>

      <div className="grid grid-cols-2 gap-4">
        <div className="border border-border rounded-lg p-4">
          <h3 className="text-sm font-medium mb-3">Buttons</h3>
          <div className="flex gap-2 flex-wrap">
            <button className="px-3 py-1.5 bg-primary text-primary-foreground rounded-md text-sm">Primary</button>
            <button className="px-3 py-1.5 bg-secondary text-secondary-foreground rounded-md text-sm">Secondary</button>
            <button className="px-3 py-1.5 border border-border rounded-md text-sm">Outline</button>
            <button className="px-3 py-1.5 text-sm text-muted-foreground hover:text-foreground">Ghost</button>
          </div>
        </div>

        <div className="border border-border rounded-lg p-4">
          <h3 className="text-sm font-medium mb-3">Test Diagnostics</h3>
          <div className="flex gap-2 flex-wrap">
            <button
              className="px-3 py-1.5 bg-red-500/10 text-red-600 rounded-md text-sm"
              onClick={() => console.error("Test error from Preview Shell")}
            >
              Trigger Error
            </button>
            <button
              className="px-3 py-1.5 bg-yellow-500/10 text-yellow-600 rounded-md text-sm"
              onClick={() => console.warn("Test warning from Preview Shell")}
            >
              Trigger Warning
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

function PagesPreview() {
  return (
    <div className="p-8">
      <h2 className="text-lg font-semibold">Page Preview</h2>
      <p className="text-sm text-muted-foreground mt-1">
        Navigate ops-console pages with diagnostics panel open to catch runtime errors.
      </p>
      <div className="mt-6 border border-border rounded-lg overflow-hidden">
        <HotPreviewFrame src="/">
          <div className="p-8 text-center text-muted-foreground">
            Page preview loads the ops-console root in an embedded frame.
          </div>
        </HotPreviewFrame>
      </div>
    </div>
  )
}

function NotFound({ target }: { target: string }) {
  return (
    <div className="p-8 text-center">
      <h2 className="text-lg font-semibold">Preview target not found</h2>
      <p className="text-sm text-muted-foreground mt-1">
        &quot;{target}&quot; is not a recognized preview target.
      </p>
    </div>
  )
}

const targets: Record<string, React.ComponentType> = {
  components: ComponentsPreview,
  pages: PagesPreview,
}

export default function PreviewTargetPage() {
  const params = useParams()
  const target = params.target as string
  const { reportError } = usePreviewShell()

  const Target = targets[target]

  if (!Target) {
    return <NotFound target={target} />
  }

  return (
    <HotPreviewFrame onError={reportError}>
      <Target />
    </HotPreviewFrame>
  )
}
