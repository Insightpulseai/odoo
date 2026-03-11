// apps/ops-console/lib/http/fetcher.ts
import { runtime } from "../datasource/runtime";

export interface FetchOptions extends RequestInit {
  params?: Record<string, string>;
}

/**
 * Enhanced fetch wrapper that adds audit headers and latency logging.
 */
export async function fetchJson<T>(url: string, options: FetchOptions = {}): Promise<T> {
  const start = performance.now();
  const { params, ...init } = options;

  // Append query params if present
  const fullUrl = new URL(url, typeof window !== "undefined" ? window.location.origin : undefined);
  if (params) {
    Object.entries(params).forEach(([key, value]) => fullUrl.searchParams.append(key, value));
  }

  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  headers.set("x-datasource-mode", runtime.mode);
  headers.set("x-odooops-client", runtime.buildSha);

  try {
    const response = await fetch(fullUrl.toString(), {
      ...init,
      headers,
    });

    const duration = performance.now() - start;

    if (process.env.NEXT_PUBLIC_DEBUG_DATASOURCES === "1") {
      console.log(`[Fetcher] ${init.method || "GET"} ${fullUrl.hostname} - ${response.status} (${duration.toFixed(0)}ms)`);
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: response.statusText }));
      throw new Error(error.message || `HTTP ${response.status}`);
    }

    return response.json();
  } catch (error) {
    console.error(`[Fetcher Error] ${url}:`, error);
    throw error;
  }
}
