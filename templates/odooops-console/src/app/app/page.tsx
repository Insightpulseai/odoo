// src/app/app/page.tsx
import { createSupabaseServerClient } from "@/lib/supabase/server";

export default async function AppHome() {
  const supabase = createSupabaseServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  return (
    <section>
      <h1 style={{ fontSize: 22, marginBottom: 8 }}>Dashboard</h1>
      <p style={{ marginTop: 0, opacity: 0.8 }}>
        Authenticated as <code>{user?.email}</code>
      </p>

      <h2 style={{ fontSize: 18, marginTop: 24 }}>Audit test</h2>
      <form action="/api/audit" method="post" style={{ display: "grid", gap: 10, maxWidth: 520 }}>
        <input type="hidden" name="action" value="app.viewed_dashboard" />
        <input type="hidden" name="env" value="prod" />
        <label style={{ display: "grid", gap: 6 }}>
          Org ID (uuid)
          <input name="org_id" placeholder="(optional) uuid" style={{ padding: 10 }} />
        </label>
        <label style={{ display: "grid", gap: 6 }}>
          Metadata (JSON)
          <textarea
            name="metadata_json"
            placeholder='{"route":"/app","note":"hello"}'
            style={{ padding: 10, minHeight: 80 }}
          />
        </label>
        <button type="submit" style={{ padding: 10, cursor: "pointer" }}>
          Write audit event
        </button>
      </form>
    </section>
  );
}
