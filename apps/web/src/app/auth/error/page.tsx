"use client";

import { useSearchParams } from "next/navigation";
import Link from "next/link";

/**
 * Auth Error Page
 *
 * Displays user-friendly error messages when authentication fails.
 * Handles errors from Magic Link expiration, invalid codes, etc.
 */
export default function AuthErrorPage() {
  const searchParams = useSearchParams();
  const error = searchParams.get("error") || "unknown_error";

  const errorMessages: Record<string, { title: string; description: string; action: string }> = {
    missing_code: {
      title: "Invalid Link",
      description: "The authentication link is missing required information.",
      action: "Request a new magic link to sign in.",
    },
    no_session: {
      title: "Session Failed",
      description: "We couldn't create your session. This might be a temporary issue.",
      action: "Please try signing in again.",
    },
    internal_error: {
      title: "Something Went Wrong",
      description: "An unexpected error occurred during authentication.",
      action: "Please try again or contact support if the issue persists.",
    },
    expired_link: {
      title: "Link Expired",
      description: "This magic link has expired. Magic links are valid for 24 hours.",
      action: "Request a new magic link to sign in.",
    },
    invalid_code: {
      title: "Invalid Code",
      description: "The verification code you entered is incorrect or has expired.",
      action: "Request a new code and try again.",
    },
  };

  const errorInfo = errorMessages[error] || {
    title: "Authentication Error",
    description: decodeURIComponent(error),
    action: "Please try signing in again.",
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full space-y-8 text-center">
        {/* Error Icon */}
        <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
          <svg
            className="w-8 h-8 text-red-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
        </div>

        {/* Error Title */}
        <h1 className="text-3xl font-bold text-gray-900">{errorInfo.title}</h1>

        {/* Error Description */}
        <p className="text-gray-600">{errorInfo.description}</p>

        {/* Action Message */}
        <p className="text-sm text-gray-500">{errorInfo.action}</p>

        {/* Actions */}
        <div className="space-y-3">
          <Link
            href="/"
            className="block w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition"
          >
            Try Again
          </Link>

          <Link
            href="/support"
            className="block w-full py-3 px-4 border border-gray-300 hover:border-gray-400 text-gray-700 font-medium rounded-lg transition"
          >
            Contact Support
          </Link>
        </div>

        {/* Debug Info (Development Only) */}
        {process.env.NODE_ENV === "development" && (
          <details className="mt-8 text-left">
            <summary className="cursor-pointer text-sm text-gray-500 hover:text-gray-700">
              Debug Information
            </summary>
            <pre className="mt-2 p-4 bg-gray-100 rounded text-xs overflow-auto">
              {JSON.stringify(
                {
                  error,
                  timestamp: new Date().toISOString(),
                  url: window.location.href,
                },
                null,
                2
              )}
            </pre>
          </details>
        )}
      </div>
    </div>
  );
}
