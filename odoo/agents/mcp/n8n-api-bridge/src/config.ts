/**
 * Configuration loader and validator
 */

import { config as loadEnv } from 'dotenv';
import { ConfigurationError, N8nConfig, McpServerConfig } from './types.js';

// Load environment variables
loadEnv();

/**
 * Load and validate n8n API configuration
 */
export function loadN8nConfig(): N8nConfig {
  const baseUrl = process.env['N8N_BASE_URL'];
  const apiKey = process.env['N8N_API_KEY'];
  const allowMutations = process.env['ALLOW_MUTATIONS'] === 'true';
  const requestTimeout = parseInt(process.env['REQUEST_TIMEOUT'] ?? '30000', 10);

  if (!baseUrl) {
    throw new ConfigurationError('N8N_BASE_URL is required');
  }

  if (!apiKey || apiKey === '__REPLACE_WITH_YOUR_API_KEY__') {
    throw new ConfigurationError(
      'N8N_API_KEY is required. Set a valid API key in .env file.'
    );
  }

  // Validate URL format
  try {
    new URL(baseUrl);
  } catch {
    throw new ConfigurationError(`Invalid N8N_BASE_URL: ${baseUrl}`);
  }

  if (isNaN(requestTimeout) || requestTimeout < 1000) {
    throw new ConfigurationError(
      `Invalid REQUEST_TIMEOUT: ${process.env['REQUEST_TIMEOUT']}. Must be >= 1000ms`
    );
  }

  return {
    baseUrl: baseUrl.replace(/\/$/, ''), // Remove trailing slash
    apiKey,
    allowMutations,
    requestTimeout,
  };
}

/**
 * Load and validate MCP server configuration
 */
export function loadMcpConfig(): McpServerConfig {
  const port = parseInt(process.env['MCP_PORT'] ?? '3100', 10);
  const logLevel = (process.env['MCP_LOG_LEVEL'] ?? 'info') as McpServerConfig['logLevel'];

  if (isNaN(port) || port < 1 || port > 65535) {
    throw new ConfigurationError(
      `Invalid MCP_PORT: ${process.env['MCP_PORT']}. Must be 1-65535`
    );
  }

  if (!['debug', 'info', 'warn', 'error'].includes(logLevel)) {
    throw new ConfigurationError(
      `Invalid MCP_LOG_LEVEL: ${logLevel}. Must be debug|info|warn|error`
    );
  }

  return { port, logLevel };
}
