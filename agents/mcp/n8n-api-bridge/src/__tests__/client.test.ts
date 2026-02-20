/**
 * client.test.ts - Tests for enhanced N8nClient with timeout and error handling
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { N8nClient } from '../client.js';
import type { N8nConfig } from '../types.js';

// Mock node-fetch
vi.mock('node-fetch', () => ({
  default: vi.fn(),
}));

import fetch from 'node-fetch';
const mockedFetch = vi.mocked(fetch);

describe('N8nClient (Enhanced)', () => {
  const defaultConfig: N8nConfig = {
    baseUrl: 'https://n8n.example.com',
    apiKey: 'test-api-key-456',
    allowMutations: false,
    requestTimeout: 5000,
  };

  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe('Constructor', () => {
    it('should set correct base URL with /api/v1 prefix', () => {
      const client = new N8nClient(defaultConfig);

      expect(client['baseUrl']).toBe('https://n8n.example.com/api/v1');
    });

    it('should configure correct headers', () => {
      const client = new N8nClient(defaultConfig);

      expect(client['headers']).toEqual({
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-N8N-API-KEY': 'test-api-key-456',
      });
    });

    it('should set timeout from config', () => {
      const client = new N8nClient({ ...defaultConfig, requestTimeout: 10000 });

      expect(client['timeout']).toBe(10000);
    });
  });

  describe('Request Timeout', () => {
    it('should abort request after timeout', async () => {
      const client = new N8nClient({ ...defaultConfig, requestTimeout: 1000 });

      // Mock a slow response
      mockedFetch.mockImplementationOnce(() =>
        new Promise((resolve) => {
          setTimeout(() => {
            resolve({
              ok: true,
              status: 200,
              json: async () => ({ data: [] }),
            } as any);
          }, 2000);
        })
      );

      const promise = client.listWorkflows();

      // Advance timers to trigger timeout
      vi.advanceTimersByTime(1000);

      await expect(promise).rejects.toThrow('Request timeout after 1000ms');
    });

    it('should clear timeout on successful response', async () => {
      const client = new N8nClient(defaultConfig);

      mockedFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: [] }),
      } as any);

      await client.listWorkflows();

      // Verify no timeout-related errors
      expect(mockedFetch).toHaveBeenCalledOnce();
    });
  });

  describe('HTTP Methods', () => {
    it('should make GET request', async () => {
      const client = new N8nClient(defaultConfig);

      mockedFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: [] }),
      } as any);

      await client.listWorkflows();

      expect(mockedFetch).toHaveBeenCalledWith(
        expect.stringContaining('/workflows'),
        expect.objectContaining({
          method: 'GET',
        })
      );
    });

    it('should make POST request with body', async () => {
      const config = { ...defaultConfig, allowMutations: true };
      const client = new N8nClient(config);

      mockedFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ id: 'exec-123' }),
      } as any);

      await client.triggerWorkflow('wf-123', { input: 'test' });

      expect(mockedFetch).toHaveBeenCalledWith(
        expect.stringContaining('/execute'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ input: 'test' }),
        })
      );
    });

    it('should make PATCH request', async () => {
      const config = { ...defaultConfig, allowMutations: true };
      const client = new N8nClient(config);

      mockedFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ id: 'wf-123', active: true }),
      } as any);

      await client.activateWorkflow('wf-123');

      expect(mockedFetch).toHaveBeenCalledWith(
        expect.stringContaining('/workflows/wf-123'),
        expect.objectContaining({
          method: 'PATCH',
        })
      );
    });

    it('should make DELETE request', async () => {
      const config = { ...defaultConfig, allowMutations: true };
      const client = new N8nClient(config);

      mockedFetch.mockResolvedValueOnce({
        ok: true,
        status: 204,
      } as any);

      await client.deleteExecution('exec-123');

      expect(mockedFetch).toHaveBeenCalledWith(
        expect.stringContaining('/executions/exec-123'),
        expect.objectContaining({
          method: 'DELETE',
        })
      );
    });
  });

  describe('Error Handling', () => {
    it('should extract error message from JSON response', async () => {
      const client = new N8nClient(defaultConfig);

      mockedFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        text: async () => JSON.stringify({ message: 'Invalid workflow ID' }),
      } as any);

      await expect(client.getWorkflow('invalid')).rejects.toThrow('Invalid workflow ID');
    });

    it('should use default message when response is not JSON', async () => {
      const client = new N8nClient(defaultConfig);

      mockedFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        text: async () => 'Not JSON',
      } as any);

      await expect(client.listWorkflows()).rejects.toThrow('n8n API error: 500 Internal Server Error');
    });

    it('should handle 204 No Content response', async () => {
      const config = { ...defaultConfig, allowMutations: true };
      const client = new N8nClient(config);

      mockedFetch.mockResolvedValueOnce({
        ok: true,
        status: 204,
      } as any);

      const result = await client.deleteExecution('exec-123');

      expect(result).toEqual({});
    });
  });

  describe('Mutation Guards', () => {
    it('should block activateWorkflow when mutations disabled', async () => {
      const client = new N8nClient(defaultConfig);

      await expect(client.activateWorkflow('wf-123')).rejects.toThrow('activate_workflow');
    });

    it('should block deactivateWorkflow when mutations disabled', async () => {
      const client = new N8nClient(defaultConfig);

      await expect(client.deactivateWorkflow('wf-123')).rejects.toThrow('deactivate_workflow');
    });

    it('should block triggerWorkflow when mutations disabled', async () => {
      const client = new N8nClient(defaultConfig);

      await expect(client.triggerWorkflow('wf-123')).rejects.toThrow('trigger_workflow');
    });

    it('should block deleteExecution when mutations disabled', async () => {
      const client = new N8nClient(defaultConfig);

      await expect(client.deleteExecution('exec-123')).rejects.toThrow('delete_execution');
    });

    it('should allow mutations when enabled', async () => {
      const config = { ...defaultConfig, allowMutations: true };
      const client = new N8nClient(config);

      mockedFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ id: 'wf-123', active: true }),
      } as any);

      await expect(client.activateWorkflow('wf-123')).resolves.toBeDefined();
    });
  });

  describe('Workflow API', () => {
    it('should list workflows with filters', async () => {
      const client = new N8nClient(defaultConfig);

      mockedFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: [], nextCursor: null }),
      } as any);

      await client.listWorkflows({ active: true, tags: ['prod', 'finance'], limit: 20 });

      expect(mockedFetch).toHaveBeenCalledWith(
        expect.stringContaining('active=true'),
        expect.any(Object)
      );
      expect(mockedFetch).toHaveBeenCalledWith(
        expect.stringContaining('tags=prod%2Cfinance'),
        expect.any(Object)
      );
      expect(mockedFetch).toHaveBeenCalledWith(
        expect.stringContaining('limit=20'),
        expect.any(Object)
      );
    });

    it('should get workflow by ID', async () => {
      const client = new N8nClient(defaultConfig);

      mockedFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ id: 'wf-123', name: 'Test Workflow' }),
      } as any);

      const result = await client.getWorkflow('wf-123');

      expect(result.id).toBe('wf-123');
      expect(mockedFetch).toHaveBeenCalledWith(
        'https://n8n.example.com/api/v1/workflows/wf-123',
        expect.any(Object)
      );
    });
  });

  describe('Execution API', () => {
    it('should list executions with filters', async () => {
      const client = new N8nClient(defaultConfig);

      mockedFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: [], nextCursor: null }),
      } as any);

      await client.listExecutions({ workflowId: 'wf-123', status: 'error', limit: 10 });

      expect(mockedFetch).toHaveBeenCalledWith(
        expect.stringContaining('workflowId=wf-123'),
        expect.any(Object)
      );
      expect(mockedFetch).toHaveBeenCalledWith(
        expect.stringContaining('status=error'),
        expect.any(Object)
      );
    });

    it('should get execution with data by default', async () => {
      const client = new N8nClient(defaultConfig);

      mockedFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ id: 'exec-123', data: {} }),
      } as any);

      await client.getExecution('exec-123');

      expect(mockedFetch).toHaveBeenCalledWith(
        expect.stringContaining('includeData=true'),
        expect.any(Object)
      );
    });

    it('should get execution without data when requested', async () => {
      const client = new N8nClient(defaultConfig);

      mockedFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ id: 'exec-123' }),
      } as any);

      await client.getExecution('exec-123', false);

      expect(mockedFetch).toHaveBeenCalledWith(
        expect.not.stringContaining('includeData'),
        expect.any(Object)
      );
    });
  });

  describe('Credentials API', () => {
    it('should list credentials (metadata only)', async () => {
      const client = new N8nClient(defaultConfig);

      mockedFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: [{ id: 'cred-1', name: 'API Key', type: 'httpHeaderAuth' }] }),
      } as any);

      const result = await client.listCredentials({ limit: 10 });

      expect(result.data).toHaveLength(1);
      expect(mockedFetch).toHaveBeenCalledWith(
        expect.stringContaining('/credentials'),
        expect.any(Object)
      );
    });
  });

  describe('Tags API', () => {
    it('should list tags', async () => {
      const client = new N8nClient(defaultConfig);

      mockedFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: [{ id: 'tag-1', name: 'production' }] }),
      } as any);

      const result = await client.listTags();

      expect(result.data).toHaveLength(1);
      expect(mockedFetch).toHaveBeenCalledWith(
        expect.stringContaining('/tags'),
        expect.any(Object)
      );
    });
  });
});
