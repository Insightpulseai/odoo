"use client";

import { ThemeProvider } from "next-themes";
import { TooltipProvider } from "@/common/tooltip";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider enableSystem attribute="class" defaultTheme="light">
      <TooltipProvider>{children}</TooltipProvider>
    </ThemeProvider>
  );
}
