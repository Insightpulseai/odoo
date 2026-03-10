"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { loginAction } from "./server-actions";

export default function LoginForm({ next }: { next: string }) {
  // const searchParams = useSearchParams(); // Removed, passed from parent
  // const next = searchParams.get("next") || "/app"; // Removed


  return (
    <main style={{ maxWidth: 420, margin: "64px auto", fontFamily: "system-ui" }}>
      <h1 style={{ fontSize: 24, marginBottom: 8 }}>Sign in</h1>
      <p style={{ marginTop: 0, marginBottom: 24, opacity: 0.8 }}>
        OdooOps Console uses Supabase Auth.
      </p>

      <form action={loginAction} style={{ display: "grid", gap: 12 }}>
        <input type="hidden" name="next" value={next} />
        <label style={{ display: "grid", gap: 6 }}>
          Email
          <input
            name="email"
            type="email"
            required
            autoComplete="email"
            placeholder="you@company.com"
            style={{ padding: 10 }}
          />
        </label>

        <label style={{ display: "grid", gap: 6 }}>
          Password
          <input
            name="password"
            type="password"
            required
            autoComplete="current-password"
            placeholder="••••••••"
            style={{ padding: 10 }}
          />
        </label>

        <button type="submit" style={{ padding: 10, cursor: "pointer" }}>
          Sign in
        </button>

        <div style={{ display: "flex", justifyContent: "space-between", opacity: 0.8 }}>
          <Link href="/">Home</Link>
          <Link href="/logout">Sign out</Link>
        </div>
      </form>
    </main>
  );
}
