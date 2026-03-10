// src/app/logout/page.tsx
import { logoutAction } from "./server-actions";

export default function LogoutPage() {
  return (
    <main style={{ maxWidth: 420, margin: "64px auto", fontFamily: "system-ui" }}>
      <h1 style={{ fontSize: 24, marginBottom: 8 }}>Sign out</h1>
      <form action={logoutAction}>
        <button type="submit" style={{ padding: 10, cursor: "pointer" }}>
          Confirm sign out
        </button>
      </form>
    </main>
  );
}
