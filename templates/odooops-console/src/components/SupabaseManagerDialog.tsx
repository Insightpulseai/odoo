"use client";

import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";

// TODO: Replace with @supabase/platform-kit-nextjs when it ships on npm.
// The package does not exist yet — using a placeholder embed.
function PlatformKit({ projectRef, className }: {
  projectRef: string;
  apiUrl: string;
  className?: string;
}) {
  return (
    <div className={className}>
      <p className="text-sm text-muted-foreground mb-2">
        Supabase project: <code>{projectRef}</code>
      </p>
      <iframe
        src={`https://supabase.com/dashboard/project/${projectRef}`}
        className="w-full h-full border rounded"
        title="Supabase Dashboard"
      />
    </div>
  );
}

interface SupabaseManagerDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  projectRef: string;
}

export function SupabaseManagerDialog({
  open,
  onOpenChange,
  projectRef,
}: SupabaseManagerDialogProps) {
  if (!projectRef) {
    return null;
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-[95vw] h-[90vh] p-0">
        <DialogHeader className="p-6 pb-0">
          <DialogTitle>Manage Supabase Project</DialogTitle>
        </DialogHeader>
        <div className="flex-1 overflow-hidden p-6">
          <PlatformKit
            projectRef={projectRef}
            apiUrl={`/api/supabase-proxy/${projectRef}`}
            className="w-full h-full"
          />
        </div>
      </DialogContent>
    </Dialog>
  );
}
