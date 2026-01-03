#!/usr/bin/env node
/**
 * Odoo ERP MCP Server
 *
 * Model Context Protocol (MCP) server for Odoo CE 18.0 integration
 * Supports 50+ tools across accounting, BIR compliance, partners, and projects
 *
 * @see https://github.com/jgtolentino/odoo-ce/spec/odoo-mcp-server
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

import { OdooClient } from './odoo-client.js';
import { EmployeeResolver } from './utils/employee-resolver.js';
import { registerAccountTools } from './tools/account.js';
import { registerBIRTools } from './tools/bir.js';

// Load environment configuration
const config = {
  url: process.env.ODOO_URL || 'http://localhost:8069',
  db: process.env.ODOO_DB || 'production',
  username: process.env.ODOO_USERNAME || 'admin',
  password: process.env.ODOO_PASSWORD || '',
};

if (!config.password) {
  console.error('Error: ODOO_PASSWORD environment variable is required');
  process.exit(1);
}

// Initialize MCP server
const server = new Server(
  {
    name: process.env.MCP_SERVER_NAME || 'odoo-erp-server',
    version: process.env.MCP_SERVER_VERSION || '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Initialize Odoo client
const odoo = new OdooClient(config);
const employeeResolver = new EmployeeResolver(odoo);

// Register all tools
const allTools = [
  ...registerAccountTools(odoo, employeeResolver),
  ...registerBIRTools(odoo, employeeResolver),
  // TODO: Add more tool categories
  // ...registerPartnerTools(odoo, employeeResolver),
  // ...registerProjectTools(odoo, employeeResolver),
];

console.error(`Registered ${allTools.length} tools`);

// Handle tool listing
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: allTools.map(tool => ({
    name: tool.name,
    description: tool.description,
    inputSchema: tool.inputSchema,
  })),
}));

// Handle tool execution
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const tool = allTools.find((t) => t.name === request.params.name);

  if (!tool) {
    throw new Error(`Tool not found: ${request.params.name}`);
  }

  try {
    return await tool.handler(request.params.arguments || {});
  } catch (error: any) {
    return {
      content: [
        {
          type: 'text',
          text: `❌ Tool execution error:\n${error.message}`,
        },
      ],
      isError: true,
    };
  }
});

// Main entry point
async function main() {
  // Test Odoo connection
  console.error('Testing Odoo connection...');
  const connected = await odoo.testConnection();

  if (!connected) {
    console.error('❌ Failed to connect to Odoo');
    console.error(`URL: ${config.url}`);
    console.error(`DB: ${config.db}`);
    console.error(`User: ${config.username}`);
    process.exit(1);
  }

  console.error('✅ Connected to Odoo successfully');
  console.error(`URL: ${config.url}`);
  console.error(`DB: ${config.db}`);

  // Start MCP server
  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error('🚀 Odoo ERP MCP server running on stdio');
  console.error(`Tools available: ${allTools.length}`);
  console.error(`Employee codes: ${employeeResolver.getValidCodes().join(', ')}`);
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
