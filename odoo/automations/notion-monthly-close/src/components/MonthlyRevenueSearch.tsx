/**
 * MonthlyRevenueSearch Component (Standalone React)
 *
 * A natural language search interface for monthly revenue insights.
 * Can be embedded in any React application (Next.js, Superset proxy, etc.)
 *
 * @example
 * ```tsx
 * import { MonthlyRevenueSearch } from './components/MonthlyRevenueSearch';
 *
 * function Dashboard() {
 *   return <MonthlyRevenueSearch companyId={1} />;
 * }
 * ```
 */

import React, { useState, useCallback } from 'react';
import {
  searchMonthlyRevenueInsights,
  formatRevenue,
  formatMonth,
  calculateRelevance,
  type SearchResult,
} from '../api/searchMonthlyRevenueInsights';

interface MonthlyRevenueSearchProps {
  /** Company ID to search within */
  companyId: number;
  /** Optional className for styling */
  className?: string;
  /** Optional auth token for protected endpoints */
  authToken?: string;
}

interface EnhancedResult extends SearchResult {
  formattedMonth: string;
  formattedRevenue: string;
  relevance: number;
}

/**
 * MonthlyRevenueSearch - Natural language search for revenue insights
 */
export function MonthlyRevenueSearch({
  companyId,
  className = '',
  authToken,
}: MonthlyRevenueSearchProps): React.ReactElement {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<EnhancedResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = useCallback(async () => {
    const trimmedQuery = query.trim();
    if (!trimmedQuery) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await searchMonthlyRevenueInsights({
        companyId,
        query: trimmedQuery,
        matchCount: 10,
        authToken,
      });

      setResults(
        data.map((r) => ({
          ...r,
          formattedMonth: formatMonth(r.month),
          formattedRevenue: formatRevenue(r.revenue),
          relevance: calculateRelevance(r.distance),
        }))
      );
      setHasSearched(true);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Search failed';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [companyId, query, authToken]);

  const handleClear = useCallback(() => {
    setQuery('');
    setResults([]);
    setHasSearched(false);
    setError(null);
  }, []);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSearch();
      } else if (e.key === 'Escape') {
        handleClear();
      }
    },
    [handleSearch, handleClear]
  );

  const getRelevanceBadgeClass = (relevance: number): string => {
    if (relevance >= 80) return 'bg-green-500 text-white';
    if (relevance >= 50) return 'bg-yellow-500 text-black';
    return 'bg-gray-400 text-white';
  };

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Header */}
      <div className="p-4 border-b bg-gray-50">
        <h4 className="text-lg font-semibold mb-1">Revenue Insights Search</h4>
        <p className="text-sm text-gray-500">
          Search monthly revenue data using natural language queries
        </p>
      </div>

      {/* Search Form */}
      <div className="p-4 border-b">
        <div className="flex gap-2">
          <input
            type="text"
            className="flex-1 border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., months where revenue dipped after a spike..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
          />
          <button
            type="button"
            className="px-4 py-2 rounded bg-blue-600 text-white text-sm hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            onClick={handleSearch}
            disabled={loading || !query.trim()}
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
          <button
            type="button"
            className="px-3 py-2 rounded border text-gray-600 hover:bg-gray-100 disabled:opacity-50"
            onClick={handleClear}
            disabled={loading}
          >
            Clear
          </button>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="mx-4 mt-4 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Results */}
      <div className="flex-1 overflow-auto p-4">
        {/* Empty State - Before Search */}
        {!hasSearched && !loading && (
          <div className="text-center text-gray-400 py-12">
            <div className="text-4xl mb-4">&#128161;</div>
            <p className="mb-2">Try searching for insights like:</p>
            <ul className="text-sm space-y-1">
              <li>"Months with highest revenue growth"</li>
              <li>"Revenue dips in Q3"</li>
              <li>"Best performing months last year"</li>
            </ul>
          </div>
        )}

        {/* Empty State - No Results */}
        {hasSearched && results.length === 0 && !loading && (
          <div className="text-center text-gray-400 py-12">
            <div className="text-4xl mb-4">&#128269;</div>
            <p>No matching revenue records found.</p>
            <p className="text-sm mt-1">Try a different query or broader search terms.</p>
          </div>
        )}

        {/* Results List */}
        {results.length > 0 && (
          <>
            <p className="text-sm text-gray-500 mb-4">
              Found <strong>{results.length}</strong> matching records
            </p>

            <div className="space-y-3">
              {results.map((result) => (
                <div
                  key={result.id}
                  className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex justify-between items-start mb-2">
                    <h6 className="font-medium text-gray-800">
                      {result.formattedMonth}
                    </h6>
                    <div className="flex items-center gap-2">
                      <span
                        className={`text-xs px-2 py-1 rounded ${getRelevanceBadgeClass(
                          result.relevance
                        )}`}
                      >
                        {result.relevance}% match
                      </span>
                      <span className="text-lg font-bold text-green-600">
                        {result.formattedRevenue}
                      </span>
                    </div>
                  </div>

                  {result.summary && (
                    <p className="text-sm text-gray-600 italic">
                      "{result.summary}"
                    </p>
                  )}
                </div>
              ))}
            </div>
          </>
        )}
      </div>

      {/* Footer */}
      <div className="p-2 border-t bg-gray-50 text-center">
        <small className="text-gray-400">
          Powered by semantic vector search &#9889;
        </small>
      </div>
    </div>
  );
}

export default MonthlyRevenueSearch;
