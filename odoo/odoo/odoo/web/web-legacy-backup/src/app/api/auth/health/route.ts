import { createServerClient } from "@/lib/supabase";
import { NextResponse } from "next/server";

/**
 * Auth Health Check Endpoint
 *
 * Verifies Supabase Auth connectivity and configuration.
 * Used by monitoring systems and CI smoke tests.
 *
 * Returns:
 * - 200: Auth is healthy and reachable
 * - 500: Auth is degraded or unreachable
 */
export async function GET() {
  try {
    const supabase = createServerClient();

    // Test 1: Verify Supabase client initialized
    if (!supabase) {
      return NextResponse.json(
        {
          status: "error",
          message: "Supabase client not initialized",
          timestamp: new Date().toISOString(),
        },
        { status: 500 }
      );
    }

    // Test 2: Check Auth service health
    const startTime = Date.now();
    const { data, error } = await supabase.auth.getSession();
    const latency = Date.now() - startTime;

    if (error) {
      console.error("Auth health check failed:", error);
      return NextResponse.json(
        {
          status: "degraded",
          message: error.message,
          latency_ms: latency,
          timestamp: new Date().toISOString(),
        },
        { status: 500 }
      );
    }

    // Test 3: Verify environment variables
    const envCheck = {
      SUPABASE_URL: !!process.env.NEXT_PUBLIC_SUPABASE_URL,
      SUPABASE_ANON_KEY: !!process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
      SUPABASE_SERVICE_ROLE_KEY: !!process.env.SUPABASE_SERVICE_ROLE_KEY,
    };

    const allEnvPresent = Object.values(envCheck).every((v) => v);

    if (!allEnvPresent) {
      return NextResponse.json(
        {
          status: "degraded",
          message: "Missing required environment variables",
          env_check: envCheck,
          timestamp: new Date().toISOString(),
        },
        { status: 500 }
      );
    }

    // All checks passed
    return NextResponse.json({
      status: "healthy",
      latency_ms: latency,
      session_active: !!data.session,
      env_check: envCheck,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error("Auth health check exception:", error);
    return NextResponse.json(
      {
        status: "error",
        message: error instanceof Error ? error.message : "Unknown error",
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    );
  }
}
