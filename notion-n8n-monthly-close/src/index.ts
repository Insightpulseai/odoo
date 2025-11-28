/**
 * Notion-n8n Monthly Close - Semantic Query Layer
 *
 * This module provides natural language search capabilities over
 * monthly revenue insights using vector embeddings.
 *
 * @module notion-n8n-monthly-close
 */

// API Client
export {
  searchMonthlyRevenueInsights,
  formatRevenue,
  formatMonth,
  calculateRelevance,
  type SearchResult,
  type SearchParams,
  type SearchResponse,
} from './api/searchMonthlyRevenueInsights';

// React Components
export { MonthlyRevenueSearch } from './components/MonthlyRevenueSearch';
