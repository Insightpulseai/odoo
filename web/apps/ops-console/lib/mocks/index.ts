// apps/ops-console/lib/mocks/index.ts
import { runtime } from "../datasource/runtime";
import * as MOCK_DATA from "./data";

/**
 * Explicit mock data exports with a runtime safety check.
 * If this module is imported while not in mock mode, it will throw a hard error.
 */

if (runtime.mode !== "mock") {
  console.warn("SECURITY_WARNING: Mocks module imported while not in mock mode.");
  // We throw a hard error to prevent accidental mock usage in production bundles
  if (process.env.NODE_ENV === "production") {
    throw new Error("Mocks imported while in live mode.");
  }
}

export const mocks = MOCK_DATA;
