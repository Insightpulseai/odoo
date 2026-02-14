import { createServerClient } from "@/lib/supabase";
import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

/**
 * Auth Callback Route (OAuth Code Exchange)
 *
 * Handles OAuth callback from Supabase Auth after Magic Link/OTP verification.
 * Exchanges authorization code for session and sets secure cookies.
 *
 * Flow:
 * 1. User clicks Magic Link or enters OTP
 * 2. Supabase Auth redirects to this endpoint with code
 * 3. Exchange code for session
 * 4. Set session cookie
 * 5. Redirect to app (or error page)
 */
export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url);
  const code = requestUrl.searchParams.get("code");
  const error = requestUrl.searchParams.get("error");
  const errorDescription = requestUrl.searchParams.get("error_description");

  // Handle auth errors (e.g., expired link, invalid code)
  if (error) {
    console.error("Auth callback error:", { error, errorDescription });
    return NextResponse.redirect(
      `${requestUrl.origin}/auth/error?error=${encodeURIComponent(
        errorDescription || error
      )}`
    );
  }

  // Code is required for OAuth exchange
  if (!code) {
    console.error("Auth callback: missing code parameter");
    return NextResponse.redirect(
      `${requestUrl.origin}/auth/error?error=missing_code`
    );
  }

  try {
    const supabase = createServerClient();

    // Exchange authorization code for session
    const { data, error: exchangeError } = await supabase.auth.exchangeCodeForSession(code);

    if (exchangeError) {
      console.error("Code exchange error:", exchangeError);
      return NextResponse.redirect(
        `${requestUrl.origin}/auth/error?error=${encodeURIComponent(
          exchangeError.message
        )}`
      );
    }

    if (!data.session) {
      console.error("Code exchange: no session returned");
      return NextResponse.redirect(
        `${requestUrl.origin}/auth/error?error=no_session`
      );
    }

    // Set session cookie (secure, httpOnly, sameSite)
    const response = NextResponse.redirect(`${requestUrl.origin}/dashboard`);

    response.cookies.set("sb-session", data.session.access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      maxAge: data.session.expires_in,
      path: "/",
    });

    // Optional: Set refresh token cookie
    if (data.session.refresh_token) {
      response.cookies.set("sb-refresh", data.session.refresh_token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        sameSite: "lax",
        maxAge: 60 * 60 * 24 * 7, // 7 days
        path: "/",
      });
    }

    return response;
  } catch (error) {
    console.error("Auth callback exception:", error);
    return NextResponse.redirect(
      `${requestUrl.origin}/auth/error?error=internal_error`
    );
  }
}
