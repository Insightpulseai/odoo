"use client";

import SupabaseManagerDialogKit from "@/platform/platform-kit-nextjs/components/supabase-manager";

interface SupabaseManagerDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  projectRef: string;
  isMobile?: boolean;
}

export function SupabaseManagerDialog({
  open,
  onOpenChange,
  projectRef,
  isMobile = false,
}: SupabaseManagerDialogProps) {
  if (!projectRef) {
    return null;
  }

  return (
    <SupabaseManagerDialogKit
      projectRef={projectRef}
      open={open}
      onOpenChange={onOpenChange}
      isMobile={isMobile}
    />
  );
}
