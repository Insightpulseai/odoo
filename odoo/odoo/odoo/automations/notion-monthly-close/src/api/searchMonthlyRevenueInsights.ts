/**
 * Semantic Search API Client (TypeScript)
 *
 * Provides natural language search over monthly revenue insights
 * using vector embeddings stored in Supabase.
 *
 * @example
 * ```ts
 * import { searchMonthlyRevenueInsights } from './api/searchMonthlyRevenueInsights';
 *
 * const results = await searchMonthlyRevenueInsights({
 *   companyId: 1,
 *   query: "months where revenue dipped after a spike",
 *   matchCount: 10
 * });
 * ```
 */

// Configuration - should be set via environment variables
const SUPABASE_PROJECT_REF = process.env.NEXT_PUBLIC_SUPABASE_PROJECT_REF || 'spdtwktxdalcfigzeqrz';
const SUPABASE_FUNCTIONS_URL = `https://${SUPABASE_PROJECT_REF}.functions.supabase.co`;

/**
 * Search result from the semantic search
 */
export interface SearchResult {
  id: number;
  company_id: number;
  month: string;
  revenue: string;
  summary: string;
  distance: number;
}

/**
 * Parameters for the search function
 */
export interface SearchParams {
  companyId: number;
  query: string;
  matchCount?: number;
  maxDistance?: number;
  authToken?: string;
}

/**
 * Search response from the API
 */
export interface SearchResponse {
  results: SearchResult[];
  meta: {
    query: string;
    companyId: number;
    matchCount: number;
    maxDistance: number;
  };
}

/**
 * Search monthly revenue insights using natural language
 *
 * @param params - Search parameters
 * @returns Array of matching revenue records sorted by relevance
 * @throws Error if the search fails
 */
export async function searchMonthlyRevenueInsights(
  params: SearchParams
): Promise<SearchResult[]> {
  const {
    companyId,
    query,
    matchCount = 10,
    maxDistance = 1.5,
    authToken,
  } = params;

  if (!companyId || typeof companyId !== 'number') {
    throw new Error('companyId is required and must be a number');
  }

  if (!query || typeof query !== 'string' || query.trim().length === 0) {
    throw new Error('query is required and must be a non-empty string');
  }

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }

  const response = await fetch(
    `${SUPABASE_FUNCTIONS_URL}/search-monthly-revenue`,
    {
      method: 'POST',
      headers,
      body: JSON.stringify({
        companyId,
        query: query.trim(),
        matchCount,
        maxDistance,
      }),
    }
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      (errorData as { error?: string }).error || `Search failed: ${response.status}`
    );
  }

  const data: SearchResponse = await response.json();
  return data.results || [];
}

/**
 * Format revenue amount for display
 *
 * @param revenue - Revenue amount (string or number)
 * @param currency - Currency code (default: PHP)
 * @returns Formatted revenue string
 */
export function formatRevenue(
  revenue: string | number,
  currency: string = 'PHP'
): string {
  const amount = typeof revenue === 'string' ? parseFloat(revenue) : revenue;

  if (isNaN(amount)) {
    return String(revenue);
  }

  const formatter = new Intl.NumberFormat('en-PH', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  });

  return formatter.format(amount);
}

/**
 * Format month date for display
 *
 * @param month - Month date in ISO format
 * @returns Formatted month string (e.g., "November 2024")
 */
export function formatMonth(month: string): string {
  const date = new Date(month);

  if (isNaN(date.getTime())) {
    return month;
  }

  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
  });
}

/**
 * Calculate relevance score from vector distance
 *
 * @param distance - Vector distance (L2)
 * @param maxDistance - Maximum distance threshold
 * @returns Relevance score (0-100, higher = more relevant)
 */
export function calculateRelevance(
  distance: number,
  maxDistance: number = 1.5
): number {
  if (distance <= 0) return 100;
  if (distance >= maxDistance) return 0;

  // Linear interpolation, inverted
  return Math.round((1 - distance / maxDistance) * 100);
}
