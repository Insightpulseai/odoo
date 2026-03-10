// apps/ops-console/lib/datasource/guard.ts
import { assertLive } from "./runtime";

/**
 * Execute the live assertion guard.
 * This should be imported at the very top of the app entry point.
 */
if (typeof window !== "undefined") {
  try {
    assertLive();
  } catch (error) {
    // Render a fatal error overlay if possible, or just kill the app
    document.body.innerHTML = `
      <div style="background: #1a1a1a; color: #ef4444; height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; font-family: sans-serif; padding: 20px; text-align: center;">
        <h1 style="font-size: 24px; margin-bottom: 16px;">🚨 Data Source Security Failure</h1>
        <p style="color: #a1a1aa; max-width: 500px;">
          Mock mode is active in a production environment. For security reasons, the application has been halted.
        </p>
        <pre style="background: #000; padding: 12px; border-radius: 4px; border: 1px solid #333; margin-top: 24px; color: #ef4444;">${error instanceof Error ? error.message : "Internal Error"}</pre>
      </div>
    `;
    throw error;
  }
} else {
  // Server-side guard
  assertLive();
}
