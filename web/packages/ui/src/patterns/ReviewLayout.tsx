import type { ReactNode } from "react";

interface ReviewLayoutProps {
  main: ReactNode;
  side: ReactNode;
}

export function ReviewLayout({ main, side }: ReviewLayoutProps) {
  return (
    <div className="flex h-full">
      {/* Main content column */}
      <div className="flex-1 overflow-auto p-6">{main}</div>

      {/* Side panel column */}
      <div className="w-96 border-l bg-white overflow-auto">{side}</div>
    </div>
  );
}
