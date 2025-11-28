/**
 * Semantic Search API Client
 *
 * Provides natural language search over monthly revenue insights
 * using vector embeddings stored in Supabase.
 *
 * @module semantic-search/api
 */

/**
 * Configuration for the semantic search API
 * These should be set via Odoo system parameters or environment
 */
const CONFIG = {
    // Default Supabase project URL - should be overridden in production
    SUPABASE_PROJECT_REF: 'spdtwktxdalcfigzeqrz',
    get SUPABASE_FUNCTIONS_URL() {
        return `https://${this.SUPABASE_PROJECT_REF}.functions.supabase.co`;
    },
    DEFAULT_MATCH_COUNT: 10,
    DEFAULT_MAX_DISTANCE: 1.5,
};

/**
 * @typedef {Object} SearchResult
 * @property {number} id - Record ID
 * @property {number} company_id - Company ID
 * @property {string} month - Month date (ISO format)
 * @property {string} revenue - Revenue amount
 * @property {string} summary - AI-generated summary
 * @property {number} distance - Vector distance (lower = more similar)
 */

/**
 * @typedef {Object} SearchResponse
 * @property {SearchResult[]} results - Array of search results
 * @property {Object} meta - Search metadata
 * @property {string} meta.query - Original query
 * @property {number} meta.companyId - Company ID searched
 * @property {number} meta.matchCount - Number of results returned
 * @property {number} meta.maxDistance - Maximum distance threshold used
 */

/**
 * Search monthly revenue insights using natural language
 *
 * @param {Object} params - Search parameters
 * @param {number} params.companyId - Company ID to search within
 * @param {string} params.query - Natural language search query
 * @param {number} [params.matchCount=10] - Maximum number of results
 * @param {number} [params.maxDistance=1.5] - Maximum vector distance threshold
 * @param {string} [params.authToken] - Optional auth token for protected endpoints
 * @returns {Promise<SearchResult[]>} Array of matching revenue records
 * @throws {Error} If the search fails
 *
 * @example
 * const results = await searchMonthlyRevenueInsights({
 *     companyId: 1,
 *     query: "months where revenue dipped after a spike",
 *     matchCount: 5
 * });
 */
export async function searchMonthlyRevenueInsights(params) {
    const {
        companyId,
        query,
        matchCount = CONFIG.DEFAULT_MATCH_COUNT,
        maxDistance = CONFIG.DEFAULT_MAX_DISTANCE,
        authToken = null,
    } = params;

    if (!companyId || typeof companyId !== 'number') {
        throw new Error('companyId is required and must be a number');
    }

    if (!query || typeof query !== 'string' || query.trim().length === 0) {
        throw new Error('query is required and must be a non-empty string');
    }

    const headers = {
        'Content-Type': 'application/json',
    };

    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }

    const response = await fetch(
        `${CONFIG.SUPABASE_FUNCTIONS_URL}/search-monthly-revenue`,
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
        throw new Error(errorData.error || `Search failed: ${response.status}`);
    }

    const data = await response.json();
    return data.results || [];
}

/**
 * Format revenue amount for display
 *
 * @param {string|number} revenue - Revenue amount
 * @param {string} [currency='PHP'] - Currency code
 * @returns {string} Formatted revenue string
 */
export function formatRevenue(revenue, currency = 'PHP') {
    const amount = typeof revenue === 'string' ? parseFloat(revenue) : revenue;

    if (isNaN(amount)) {
        return revenue;
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
 * @param {string} month - Month date in ISO format
 * @returns {string} Formatted month string (e.g., "November 2024")
 */
export function formatMonth(month) {
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
 * Calculate relevance score from distance
 *
 * @param {number} distance - Vector distance (L2)
 * @param {number} [maxDistance=1.5] - Maximum distance threshold
 * @returns {number} Relevance score (0-100, higher = more relevant)
 */
export function calculateRelevance(distance, maxDistance = 1.5) {
    if (distance <= 0) return 100;
    if (distance >= maxDistance) return 0;

    // Linear interpolation, inverted
    return Math.round((1 - distance / maxDistance) * 100);
}

// Export configuration for customization
export { CONFIG as SemanticSearchConfig };
