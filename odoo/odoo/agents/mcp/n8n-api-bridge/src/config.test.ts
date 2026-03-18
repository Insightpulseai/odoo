/**
 * Configuration loader tests
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { loadN8nConfig, loadMcpConfig } from './config.js';
import { ConfigurationError } from './types.js';

describe('loadN8nConfig', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    process.env = { ...originalEnv };
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  it('should load valid configuration', () => {
    process.env['N8N_BASE_URL'] = 'https://n8n.example.com';
    process.env['N8N_API_KEY'] = 'test-key-123';
    process.env['ALLOW_MUTATIONS'] = 'true';
    process.env['REQUEST_TIMEOUT'] = '5000';

    const config = loadN8nConfig();

    expect(config.baseUrl).toBe('https://n8n.example.com');
    expect(config.apiKey).toBe('test-key-123');
    expect(config.allowMutations).toBe(true);
    expect(config.requestTimeout).toBe(5000);
  });

  it('should remove trailing slash from base URL', () => {
    process.env['N8N_BASE_URL'] = 'https://n8n.example.com/';
    process.env['N8N_API_KEY'] = 'test-key';

    const config = loadN8nConfig();
    expect(config.baseUrl).toBe('https://n8n.example.com');
  });

  it('should default allowMutations to false', () => {
    process.env['N8N_BASE_URL'] = 'https://n8n.example.com';
    process.env['N8N_API_KEY'] = 'test-key';

    const config = loadN8nConfig();
    expect(config.allowMutations).toBe(false);
  });

  it('should default requestTimeout to 30000', () => {
    process.env['N8N_BASE_URL'] = 'https://n8n.example.com';
    process.env['N8N_API_KEY'] = 'test-key';

    const config = loadN8nConfig();
    expect(config.requestTimeout).toBe(30000);
  });

  it('should throw ConfigurationError if N8N_BASE_URL is missing', () => {
    delete process.env['N8N_BASE_URL'];
    process.env['N8N_API_KEY'] = 'test-key';

    expect(() => loadN8nConfig()).toThrow(ConfigurationError);
    expect(() => loadN8nConfig()).toThrow('N8N_BASE_URL is required');
  });

  it('should throw ConfigurationError if N8N_API_KEY is missing', () => {
    process.env['N8N_BASE_URL'] = 'https://n8n.example.com';
    delete process.env['N8N_API_KEY'];

    expect(() => loadN8nConfig()).toThrow(ConfigurationError);
    expect(() => loadN8nConfig()).toThrow('N8N_API_KEY is required');
  });

  it('should throw ConfigurationError if N8N_API_KEY is placeholder', () => {
    process.env['N8N_BASE_URL'] = 'https://n8n.example.com';
    process.env['N8N_API_KEY'] = '__REPLACE_WITH_YOUR_API_KEY__';

    expect(() => loadN8nConfig()).toThrow(ConfigurationError);
    expect(() => loadN8nConfig()).toThrow('N8N_API_KEY is required');
  });

  it('should throw ConfigurationError for invalid URL', () => {
    process.env['N8N_BASE_URL'] = 'not-a-valid-url';
    process.env['N8N_API_KEY'] = 'test-key';

    expect(() => loadN8nConfig()).toThrow(ConfigurationError);
    expect(() => loadN8nConfig()).toThrow('Invalid N8N_BASE_URL');
  });

  it('should throw ConfigurationError for invalid timeout', () => {
    process.env['N8N_BASE_URL'] = 'https://n8n.example.com';
    process.env['N8N_API_KEY'] = 'test-key';
    process.env['REQUEST_TIMEOUT'] = '500'; // Less than 1000ms

    expect(() => loadN8nConfig()).toThrow(ConfigurationError);
    expect(() => loadN8nConfig()).toThrow('Invalid REQUEST_TIMEOUT');
  });
});

describe('loadMcpConfig', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    process.env = { ...originalEnv };
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  it('should load valid configuration', () => {
    process.env['MCP_PORT'] = '4000';
    process.env['MCP_LOG_LEVEL'] = 'debug';

    const config = loadMcpConfig();

    expect(config.port).toBe(4000);
    expect(config.logLevel).toBe('debug');
  });

  it('should default port to 3100', () => {
    delete process.env['MCP_PORT'];

    const config = loadMcpConfig();
    expect(config.port).toBe(3100);
  });

  it('should default logLevel to info', () => {
    delete process.env['MCP_LOG_LEVEL'];

    const config = loadMcpConfig();
    expect(config.logLevel).toBe('info');
  });

  it('should throw ConfigurationError for invalid port', () => {
    process.env['MCP_PORT'] = '99999';

    expect(() => loadMcpConfig()).toThrow(ConfigurationError);
    expect(() => loadMcpConfig()).toThrow('Invalid MCP_PORT');
  });

  it('should throw ConfigurationError for invalid log level', () => {
    process.env['MCP_LOG_LEVEL'] = 'invalid';

    expect(() => loadMcpConfig()).toThrow(ConfigurationError);
    expect(() => loadMcpConfig()).toThrow('Invalid MCP_LOG_LEVEL');
  });
});
