/**
 * integration.test.ts - Integration tests for n8n MCP Bridge
 *
 * These tests connect to a real n8n instance if credentials are provided.
 * They are skipped in CI if N8N_TEST_BASE_URL is not set.
 */

import { describe, it, expect, beforeAll } from 'vitest';
import { N8nClient } from '../client.js';
import type { N8nConfig } from '../types.js';

// Skip all tests if no test credentials provided
const skipIntegration = !process.env.N8N_TEST_BASE_URL || !process.env.N8N_TEST_API_KEY;

describe.skipIf(skipIntegration)('Integration Tests', () => {
  let client: N8nClient;
  let config: N8nConfig;

  beforeAll(() => {
    config = {
      baseUrl: process.env.N8N_TEST_BASE_URL!,
      apiKey: process.env.N8N_TEST_API_KEY!,
      allowMutations: process.env.ALLOW_MUTATIONS === 'true',
      requestTimeout: 10000, // 10 seconds for integration tests
    };

    client = new N8nClient(config);
  });

  describe('Smoke Tests', () => {
    it('should connect to n8n instance', async () => {
      // Simple health check - list workflows should not throw
      await expect(client.listWorkflows({ limit: 1 })).resolves.toBeDefined();
    });

    it('should list workflows with pagination', async () => {
      const result = await client.listWorkflows({ limit: 5 });

      expect(result).toHaveProperty('data');
      expect(Array.isArray(result.data)).toBe(true);

      // If there are workflows, verify structure
      if (result.data.length > 0) {
        const workflow = result.data[0]!;
        expect(workflow).toHaveProperty('id');
        expect(workflow).toHaveProperty('name');
        expect(workflow).toHaveProperty('active');
      }
    });

    it('should get workflow details if any exist', async () => {
      const list = await client.listWorkflows({ limit: 1 });

      if (list.data.length === 0) {
        console.log('No workflows found, skipping workflow detail test');
        return;
      }

      const workflowId = list.data[0]!.id;
      const workflow = await client.getWorkflow(workflowId);

      expect(workflow.id).toBe(workflowId);
      expect(workflow).toHaveProperty('name');
      expect(workflow).toHaveProperty('nodes');
    });

    it('should list executions', async () => {
      const result = await client.listExecutions({ limit: 5 });

      expect(result).toHaveProperty('data');
      expect(Array.isArray(result.data)).toBe(true);

      // If there are executions, verify structure
      if (result.data.length > 0) {
        const execution = result.data[0]!;
        expect(execution).toHaveProperty('id');
        expect(execution).toHaveProperty('workflowId');
        expect(execution).toHaveProperty('status');
      }
    });

    it('should list credentials (metadata only)', async () => {
      const result = await client.listCredentials({ limit: 5 });

      expect(result).toHaveProperty('data');
      expect(Array.isArray(result.data)).toBe(true);

      // Credentials should NOT contain sensitive data
      if (result.data.length > 0) {
        const credential = result.data[0]!;
        expect(credential).toHaveProperty('id');
        expect(credential).toHaveProperty('name');
        expect(credential).toHaveProperty('type');
        expect(credential).not.toHaveProperty('data'); // No sensitive data
      }
    });

    it('should list tags', async () => {
      const result = await client.listTags({ limit: 10 });

      expect(result).toHaveProperty('data');
      expect(Array.isArray(result.data)).toBe(true);

      // If there are tags, verify structure
      if (result.data.length > 0) {
        const tag = result.data[0]!;
        expect(tag).toHaveProperty('id');
        expect(tag).toHaveProperty('name');
      }
    });
  });

  describe('Error Handling', () => {
    it('should handle 404 for non-existent workflow', async () => {
      await expect(client.getWorkflow('non-existent-workflow-id')).rejects.toThrow();
    });

    it('should handle 404 for non-existent execution', async () => {
      await expect(client.getExecution('non-existent-execution-id')).rejects.toThrow();
    });
  });

  describe('Pagination', () => {
    it('should respect limit parameter', async () => {
      const result = await client.listWorkflows({ limit: 3 });

      expect(result.data.length).toBeLessThanOrEqual(3);
    });

    it('should handle cursor-based pagination', async () => {
      const firstPage = await client.listWorkflows({ limit: 2 });

      if (firstPage.nextCursor) {
        const secondPage = await client.listWorkflows({
          limit: 2,
          cursor: firstPage.nextCursor,
        });

        expect(secondPage).toHaveProperty('data');
        // Second page should have different items (if available)
        if (secondPage.data.length > 0 && firstPage.data.length > 0) {
          expect(secondPage.data[0]!.id).not.toBe(firstPage.data[0]!.id);
        }
      }
    });
  });

  describe('Filters', () => {
    it('should filter workflows by active status', async () => {
      const activeWorkflows = await client.listWorkflows({ active: true, limit: 10 });
      const inactiveWorkflows = await client.listWorkflows({ active: false, limit: 10 });

      // All active workflows should have active=true
      for (const workflow of activeWorkflows.data) {
        expect(workflow.active).toBe(true);
      }

      // All inactive workflows should have active=false
      for (const workflow of inactiveWorkflows.data) {
        expect(workflow.active).toBe(false);
      }
    });

    it('should filter executions by workflow ID', async () => {
      const workflows = await client.listWorkflows({ limit: 1 });

      if (workflows.data.length === 0) {
        console.log('No workflows found, skipping execution filter test');
        return;
      }

      const workflowId = workflows.data[0]!.id;
      const executions = await client.listExecutions({ workflowId, limit: 5 });

      // All executions should belong to the specified workflow
      for (const execution of executions.data) {
        expect(execution.workflowId).toBe(workflowId);
      }
    });

    it('should filter executions by status', async () => {
      const successExecutions = await client.listExecutions({ status: 'success', limit: 5 });

      // All executions should have success status
      for (const execution of successExecutions.data) {
        expect(execution.status).toBe('success');
      }
    });
  });

  describe.skipIf(!config.allowMutations)('Mutation Operations', () => {
    it('should activate and deactivate workflow', async () => {
      const workflows = await client.listWorkflows({ active: false, limit: 1 });

      if (workflows.data.length === 0) {
        console.log('No inactive workflows found, skipping mutation test');
        return;
      }

      const workflowId = workflows.data[0]!.id;

      // Activate
      const activated = await client.activateWorkflow(workflowId);
      expect(activated.active).toBe(true);

      // Deactivate (cleanup)
      const deactivated = await client.deactivateWorkflow(workflowId);
      expect(deactivated.active).toBe(false);
    });
  });
});

describe('Integration Test Setup', () => {
  it('should show how to configure integration tests', () => {
    if (skipIntegration) {
      console.log(`
Integration tests are SKIPPED.

To run integration tests, set these environment variables:

  export N8N_TEST_BASE_URL="https://your-n8n-instance.com"
  export N8N_TEST_API_KEY="your-api-key"
  export ALLOW_MUTATIONS="false"  # Set to "true" for mutation tests

Then run:

  pnpm test

Note: Integration tests connect to a real n8n instance.
      `);
    }

    expect(true).toBe(true); // Always pass
  });
});
