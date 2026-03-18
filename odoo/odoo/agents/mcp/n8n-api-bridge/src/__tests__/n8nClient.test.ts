/**
 * n8nClient.test.ts - Tests for n8n API Client
 *
 * Tests authentication, URL construction, error normalization, and mutation guards.
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { N8nClient, N8nApiError, getN8nClient, resetN8nClient } from '../n8nClient.js';

// Mock node-fetch
vi.mock('node-fetch', () => ({
  default: vi.fn(),
}));

import fetch from 'node-fetch';
const mockedFetch = vi.mocked(fetch);

describe('N8nClient', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    // Reset environment
    process.env = {
      ...originalEnv,
      N8N_BASE_URL: 'https://n8n.example.com',
      N8N_API_KEY: 'test-api-key-123',
      ALLOW_MUTATIONS: 'false',
    };

    // Reset client singleton
    resetN8nClient();

    // Clear all mocks
    vi.clearAllMocks();
  });

  afterEach(() => {
    process.env = originalEnv;
    resetN8nClient();
  });

  describe('Constructor', () => {
    it('should throw error when N8N_BASE_URL is missing', () => {
      delete process.env.N8N_BASE_URL;

      expect(() => new N8nClient()).toThrow('N8N_BASE_URL environment variable is required');
    });

    it('should throw error when N8N_API_KEY is missing', () => {
      delete process.env.N8N_API_KEY;

      expect(() => new N8nClient()).toThrow('N8N_API_KEY environment variable is required');
    });

    it('should remove trailing slash from base URL', () => {
      process.env.N8N_BASE_URL = 'https://n8n.example.com/';
      const client = new N8nClient();

      expect(client['baseUrl']).toBe('https://n8n.example.com');
    });

    it('should set allowMutations to false by default', () => {
      delete process.env.ALLOW_MUTATIONS;
      const client = new N8nClient();

      expect(client['allowMutations']).toBe(false);
    });

    it('should set allowMutations to true when env var is "true"', () => {
      process.env.ALLOW_MUTATIONS = 'true';
      const client = new N8nClient();

      expect(client['allowMutations']).toBe(true);
    });
  });

  describe('Authentication Headers', () => {
    it('should inject X-N8N-API-KEY header in requests', async () => {
      const client = new N8nClient();

      mockedFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: [], nextCursor: null }),
      } as any);

      await client.listWorkflows();

      expect(mockedFetch).toHaveBeenCalledWith(
        'https://n8n.example.com/api/v1/workflows',
        expect.objectContaining({
          headers: expect.objectContaining({
            'X-N8N-API-KEY': 'test-api-key-123',
          }),
        })
      );
    });

    it('should include Accept header for JSON', async () => {
      const client = new N8nClient();

      mockedFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: [], nextCursor: null }),
      } as any);

      await client.listWorkflows();

      expect(mockedFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Accept': 'application/json',
          }),
        })
      );
    });

    it('should include Content-Type header when body is present', async () => {
      process.env.ALLOW_MUTATIONS = 'true';
      const client = new N8nClient();

      mockedFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ id: 'exec-123', status: 'success' }),
      } as any);

      await client.retryExecution('exec-123');

      expect(mockedFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      );
    });
  });

  describe('URL Construction', () => {
    it('should construct correct base URL path', async () => {
      const client = new N8nClient();

      mockedFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: [], nextCursor: null }),
      } as any);

      await client.listWorkflows();

      expect(mockedFetch).toHaveBeenCalledWith(
        'https://n8n.example.com/api/v1/workflows',
        expect.any(Object)
      );
    });

    it('should append query parameters correctly', async () => {
      const client = new N8nClient();

      mockedFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: [], nextCursor: null }),
      } as any);

      await client.listWorkflows({ limit: 10, cursor: 'abc123' });

      expect(mockedFetch).toHaveBeenCalledWith(
        'https://n8n.example.com/api/v1/workflows?limit=10&cursor=abc123',
        expect.any(Object)
      );
    });

    it('should construct resource-specific URLs', async () => {
      const client = new N8nClient();

      mockedFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ id: 'wf-123', name: 'Test' }),
      } as any);

      await client.getWorkflow('wf-123');

      expect(mockedFetch).toHaveBeenCalledWith(
        'https://n8n.example.com/api/v1/workflows/wf-123',
        expect.any(Object)
      );
    });
  });

  describe('Error Normalization', () => {
    it('should normalize 401 errors with authentication message', async () => {
      const client = new N8nClient();

      mockedFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        statusText: 'Unauthorized',
        json: async () => ({}),
        text: async () => '{}',
      } as any);

      await expect(client.listWorkflows()).rejects.toThrow(N8nApiError);
      await expect(client.listWorkflows()).rejects.toThrow('Authentication failed: Invalid API key');
    });

    it('should normalize 404 errors with not found message', async () => {
      const client = new N8nClient();

      mockedFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: async () => ({}),
        text: async () => '{}',
      } as any);

      await expect(client.getWorkflow('nonexistent')).rejects.toThrow(N8nApiError);
      await expect(client.getWorkflow('nonexistent')).rejects.toThrow('Resource not found');
    });

    it('should normalize 429 errors with rate limit message', async () => {
      const client = new N8nClient();

      mockedFetch.mockResolvedValueOnce({
        ok: false,
        status: 429,
        statusText: 'Too Many Requests',
        json: async () => ({}),
        text: async () => '{}',
      } as any);

      await expect(client.listWorkflows()).rejects.toThrow(N8nApiError);
      await expect(client.listWorkflows()).rejects.toThrow('Rate limit exceeded');
    });

    it('should include status code in error', async () => {
      const client = new N8nClient();

      mockedFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => ({}),
        text: async () => '{}',
      } as any);

      try {
        await client.listWorkflows();
        expect.fail('Should have thrown error');
      } catch (error) {
        expect(error).toBeInstanceOf(N8nApiError);
        expect((error as N8nApiError).statusCode).toBe(500);
      }
    });

    it('should preserve error details from response', async () => {
      const client = new N8nClient();
      const errorDetails = { message: 'Detailed error', code: 'ERR_CODE' };

      mockedFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        json: async () => errorDetails,
        text: async () => JSON.stringify(errorDetails),
      } as any);

      try {
        await client.listWorkflows();
        expect.fail('Should have thrown error');
      } catch (error) {
        expect(error).toBeInstanceOf(N8nApiError);
        expect((error as N8nApiError).details).toEqual(errorDetails);
      }
    });

    it('should handle network errors', async () => {
      const client = new N8nClient();

      mockedFetch.mockRejectedValueOnce(new Error('Network failure'));

      await expect(client.listWorkflows()).rejects.toThrow(N8nApiError);
      await expect(client.listWorkflows()).rejects.toThrow('Network error');
    });

    it('should handle JSON parse errors', async () => {
      const client = new N8nClient();

      mockedFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => { throw new Error('Invalid JSON'); },
      } as any);

      await expect(client.listWorkflows()).rejects.toThrow(N8nApiError);
      await expect(client.listWorkflows()).rejects.toThrow('Failed to parse response');
    });
  });

  describe('Mutation Guard', () => {
    it('should block mutations when ALLOW_MUTATIONS is false', async () => {
      process.env.ALLOW_MUTATIONS = 'false';
      const client = new N8nClient();

      await expect(client.retryExecution('exec-123')).rejects.toThrow(
        "Mutation operation 'retryExecution' is disabled"
      );
    });

    it('should allow mutations when ALLOW_MUTATIONS is true', async () => {
      process.env.ALLOW_MUTATIONS = 'true';
      const client = new N8nClient();

      mockedFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ id: 'exec-123', status: 'success' }),
      } as any);

      await expect(client.retryExecution('exec-123')).resolves.toBeDefined();
    });

    it('should NOT block audit operations (exempt from guard)', async () => {
      process.env.ALLOW_MUTATIONS = 'false';
      const client = new N8nClient();

      mockedFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({}),
      } as any);

      await expect(client.audit({ eventName: 'test.event' })).resolves.toBeUndefined();
    });
  });

  describe('API Methods', () => {
    describe('listWorkflows', () => {
      it('should fetch workflows without options', async () => {
        const client = new N8nClient();
        const mockData = { data: [{ id: 'wf-1', name: 'Workflow 1', active: true }], nextCursor: null };

        mockedFetch.mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => mockData,
        } as any);

        const result = await client.listWorkflows();

        expect(result).toEqual(mockData);
      });

      it('should handle pagination options', async () => {
        const client = new N8nClient();

        mockedFetch.mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => ({ data: [], nextCursor: 'next-page' }),
        } as any);

        await client.listWorkflows({ limit: 5, cursor: 'page-2' });

        expect(mockedFetch).toHaveBeenCalledWith(
          expect.stringContaining('limit=5'),
          expect.any(Object)
        );
        expect(mockedFetch).toHaveBeenCalledWith(
          expect.stringContaining('cursor=page-2'),
          expect.any(Object)
        );
      });
    });

    describe('getWorkflow', () => {
      it('should throw error for empty workflow ID', async () => {
        const client = new N8nClient();

        await expect(client.getWorkflow('')).rejects.toThrow('Workflow ID is required');
      });

      it('should fetch workflow by ID', async () => {
        const client = new N8nClient();
        const mockWorkflow = {
          id: 'wf-123',
          name: 'Test Workflow',
          active: true,
          nodes: [],
        };

        mockedFetch.mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => mockWorkflow,
        } as any);

        const result = await client.getWorkflow('wf-123');

        expect(result).toEqual(mockWorkflow);
      });
    });

    describe('getExecution', () => {
      it('should throw error for empty execution ID', async () => {
        const client = new N8nClient();

        await expect(client.getExecution('')).rejects.toThrow('Execution ID is required');
      });

      it('should fetch execution by ID', async () => {
        const client = new N8nClient();
        const mockExecution = {
          id: 'exec-123',
          workflowId: 'wf-123',
          status: 'success' as const,
        };

        mockedFetch.mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => mockExecution,
        } as any);

        const result = await client.getExecution('exec-123');

        expect(result).toEqual(mockExecution);
      });
    });

    describe('audit', () => {
      it('should throw error for missing eventName', async () => {
        const client = new N8nClient();

        await expect(client.audit({ eventName: '' })).rejects.toThrow('eventName is required');
      });

      it('should submit audit event with metadata', async () => {
        const client = new N8nClient();
        const auditEvent = {
          eventName: 'workflow.executed',
          userId: 'user-123',
          metadata: { workflowId: 'wf-123' },
        };

        mockedFetch.mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => ({}),
        } as any);

        await client.audit(auditEvent);

        expect(mockedFetch).toHaveBeenCalledWith(
          'https://n8n.example.com/api/v1/audit',
          expect.objectContaining({
            method: 'POST',
            body: JSON.stringify(auditEvent),
          })
        );
      });
    });
  });

  describe('Singleton Pattern', () => {
    it('should return same instance on multiple calls', () => {
      const client1 = getN8nClient();
      const client2 = getN8nClient();

      expect(client1).toBe(client2);
    });

    it('should create new instance after reset', () => {
      const client1 = getN8nClient();
      resetN8nClient();
      const client2 = getN8nClient();

      expect(client1).not.toBe(client2);
    });
  });
});

describe('N8nApiError', () => {
  it('includes status code and message', () => {
    const error = new N8nApiError(404, 'Not found');
    expect(error.statusCode).toBe(404);
    expect(error.message).toBe('Not found');
    expect(error.name).toBe('N8nApiError');
  });

  it('includes optional details', () => {
    const error = new N8nApiError(400, 'Bad request', { field: 'name' });
    expect(error.details).toEqual({ field: 'name' });
  });
});
