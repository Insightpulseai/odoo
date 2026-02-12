// src/app/app/layout.tsx
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const supabase = createSupabaseServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  // Defense-in-depth: middleware already blocks, but keep server check
  if (!user) redirect("/login?next=/app");

  return (
    <div style={{ fontFamily: "system-ui" }}>
      <header style={{ padding: 16, borderBottom: "1px solid #eee" }}>
        <strong>OdooOps Console</strong>
        <span style={{ marginLeft: 12, opacity: 0.7 }}>{user.email}</span>
        <a href="/logout" style={{ float: "right" }}>
          Sign out
        </a>
      </header>
      <main style={{ padding: 16 }}>{children}</main>
    </div>
  );
}
