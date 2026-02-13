/**
 * Test file for env.ts resolver
 * Run: deno test supabase/functions/_shared/env_test.ts
 */

import { assertEquals, assertThrows } from "https://deno.land/std@0.208.0/assert/mod.ts";
import { envPrefix, getEnvironment, getEnvSecret, isStaging, isProduction } from "./env.ts";

Deno.test("envPrefix throws without ENVIRONMENT", () => {
  const originalEnv = Deno.env.get("ENVIRONMENT");
  Deno.env.delete("ENVIRONMENT");

  assertThrows(
    () => envPrefix(),
    Error,
    "ENVIRONMENT must be set"
  );

  if (originalEnv) Deno.env.set("ENVIRONMENT", originalEnv);
});

Deno.test("envPrefix returns STAGE__ for staging", () => {
  const originalEnv = Deno.env.get("ENVIRONMENT");
  Deno.env.set("ENVIRONMENT", "staging");

  assertEquals(envPrefix(), "STAGE__");

  if (originalEnv) {
    Deno.env.set("ENVIRONMENT", originalEnv);
  } else {
    Deno.env.delete("ENVIRONMENT");
  }
});

Deno.test("envPrefix returns PROD__ for prod", () => {
  const originalEnv = Deno.env.get("ENVIRONMENT");
  Deno.env.set("ENVIRONMENT", "prod");

  assertEquals(envPrefix(), "PROD__");

  if (originalEnv) {
    Deno.env.set("ENVIRONMENT", originalEnv);
  } else {
    Deno.env.delete("ENVIRONMENT");
  }
});

Deno.test("getEnvSecret resolves prefixed secret", () => {
  const originalEnv = Deno.env.get("ENVIRONMENT");
  Deno.env.set("ENVIRONMENT", "staging");
  Deno.env.set("STAGE__TEST_KEY", "test-value");

  assertEquals(getEnvSecret("TEST_KEY"), "test-value");

  Deno.env.delete("STAGE__TEST_KEY");
  if (originalEnv) {
    Deno.env.set("ENVIRONMENT", originalEnv);
  } else {
    Deno.env.delete("ENVIRONMENT");
  }
});

Deno.test("isStaging returns true in staging", () => {
  const originalEnv = Deno.env.get("ENVIRONMENT");
  Deno.env.set("ENVIRONMENT", "staging");

  assertEquals(isStaging(), true);
  assertEquals(isProduction(), false);

  if (originalEnv) {
    Deno.env.set("ENVIRONMENT", originalEnv);
  } else {
    Deno.env.delete("ENVIRONMENT");
  }
});
