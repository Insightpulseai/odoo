import type { ReactNode } from "react";
import { AppShell } from "@ipai/ui/patterns/AppShell";

export const metadata = {
  title: "Diva Goals",
  description: "Goal status reviews and copilot-assisted approvals",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AppShell
          appName="Diva Goals"
          navItems={[
            { label: "Reviews", href: "/reviews" },
            { label: "Queue", href: "/queue" },
            { label: "Settings", href: "/settings" },
          ]}
        >
          {children}
        </AppShell>
      </body>
    </html>
  );
}
