#!/usr/bin/env node
/**
 * Superset MCP Server
 *
 * Tools for managing Apache Superset BI platform:
 * - Dashboards: list, export, import, refresh
 * - Charts: list, get details, update SQL
 * - Datasets: list, create, sync columns
 * - Databases: list connections
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import { SupersetClient } from "./superset-client.js";
import * as dashboardTools from "./tools/dashboards.js";
import * as datasetTools from "./tools/datasets.js";
import * as chartTools from "./tools/charts.js";

const SUPERSET_URL = process.env.SUPERSET_URL;
const SUPERSET_USERNAME = process.env.SUPERSET_USERNAME;
const SUPERSET_PASSWORD = process.env.SUPERSET_PASSWORD;

if (!SUPERSET_URL || !SUPERSET_USERNAME || !SUPERSET_PASSWORD) {
  console.error(
    "Error: SUPERSET_URL, SUPERSET_USERNAME, SUPERSET_PASSWORD required"
  );
  process.exit(1);
}

const client = new SupersetClient(SUPERSET_URL, SUPERSET_USERNAME, SUPERSET_PASSWORD);

const tools: Tool[] = [
  // Dashboard tools
  {
    name: "list_dashboards",
    description: "List all dashboards",
    inputSchema: {
      type: "object",
      properties: {
        page: { type: "number", description: "Page number" },
        page_size: { type: "number", description: "Items per page" },
      },
    },
  },
  {
    name: "get_dashboard",
    description: "Get dashboard details",
    inputSchema: {
      type: "object",
      properties: {
        dashboard_id: { type: "number", description: "Dashboard ID" },
      },
      required: ["dashboard_id"],
    },
  },
  {
    name: "export_dashboard_yaml",
    description: "Export dashboard as YAML for version control",
    inputSchema: {
      type: "object",
      properties: {
        dashboard_id: { type: "number", description: "Dashboard ID" },
      },
      required: ["dashboard_id"],
    },
  },
  {
    name: "refresh_dashboard",
    description: "Refresh all charts in a dashboard",
    inputSchema: {
      type: "object",
      properties: {
        dashboard_id: { type: "number", description: "Dashboard ID" },
      },
      required: ["dashboard_id"],
    },
  },
  // Chart tools
  {
    name: "list_charts",
    description: "List all charts",
    inputSchema: {
      type: "object",
      properties: {
        dashboard_id: { type: "number", description: "Filter by dashboard" },
      },
    },
  },
  {
    name: "get_chart",
    description: "Get chart details including SQL query",
    inputSchema: {
      type: "object",
      properties: {
        chart_id: { type: "number", description: "Chart ID" },
      },
      required: ["chart_id"],
    },
  },
  {
    name: "update_chart_sql",
    description: "Update the SQL query for a chart",
    inputSchema: {
      type: "object",
      properties: {
        chart_id: { type: "number", description: "Chart ID" },
        sql: { type: "string", description: "New SQL query" },
      },
      required: ["chart_id", "sql"],
    },
  },
  // Dataset tools
  {
    name: "list_datasets",
    description: "List all datasets",
    inputSchema: {
      type: "object",
      properties: {
        database_id: { type: "number", description: "Filter by database" },
      },
    },
  },
  {
    name: "get_dataset",
    description: "Get dataset details and columns",
    inputSchema: {
      type: "object",
      properties: {
        dataset_id: { type: "number", description: "Dataset ID" },
      },
      required: ["dataset_id"],
    },
  },
  {
    name: "create_dataset",
    description: "Create a new dataset from a table or SQL",
    inputSchema: {
      type: "object",
      properties: {
        database_id: { type: "number", description: "Database connection ID" },
        table_name: { type: "string", description: "Table name" },
        schema: { type: "string", description: "Schema name" },
        sql: { type: "string", description: "Custom SQL (for virtual dataset)" },
      },
      required: ["database_id"],
    },
  },
  {
    name: "sync_dataset_columns",
    description: "Sync dataset columns from source",
    inputSchema: {
      type: "object",
      properties: {
        dataset_id: { type: "number", description: "Dataset ID" },
      },
      required: ["dataset_id"],
    },
  },
  // Database tools
  {
    name: "list_databases",
    description: "List database connections",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
  {
    name: "test_database_connection",
    description: "Test a database connection",
    inputSchema: {
      type: "object",
      properties: {
        database_id: { type: "number", description: "Database ID" },
      },
      required: ["database_id"],
    },
  },
];

const server = new Server(
  {
    name: "superset-mcp-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools,
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    await client.ensureAuthenticated();
    let result: unknown;

    switch (name) {
      case "list_dashboards":
        result = await dashboardTools.listDashboards(
          client,
          args?.page as number,
          args?.page_size as number
        );
        break;
      case "get_dashboard":
        result = await dashboardTools.getDashboard(
          client,
          args.dashboard_id as number
        );
        break;
      case "export_dashboard_yaml":
        result = await dashboardTools.exportDashboard(
          client,
          args.dashboard_id as number
        );
        break;
      case "refresh_dashboard":
        result = await dashboardTools.refreshDashboard(
          client,
          args.dashboard_id as number
        );
        break;
      case "list_charts":
        result = await chartTools.listCharts(
          client,
          args?.dashboard_id as number
        );
        break;
      case "get_chart":
        result = await chartTools.getChart(client, args.chart_id as number);
        break;
      case "update_chart_sql":
        result = await chartTools.updateChartSql(
          client,
          args.chart_id as number,
          args.sql as string
        );
        break;
      case "list_datasets":
        result = await datasetTools.listDatasets(
          client,
          args?.database_id as number
        );
        break;
      case "get_dataset":
        result = await datasetTools.getDataset(
          client,
          args.dataset_id as number
        );
        break;
      case "create_dataset":
        result = await datasetTools.createDataset(client, {
          database_id: args.database_id as number,
          table_name: args.table_name as string,
          schema: args.schema as string,
          sql: args.sql as string,
        });
        break;
      case "sync_dataset_columns":
        result = await datasetTools.syncDatasetColumns(
          client,
          args.dataset_id as number
        );
        break;
      case "list_databases":
        result = await client.listDatabases();
        break;
      case "test_database_connection":
        result = await client.testDatabaseConnection(
          args.database_id as number
        );
        break;
      default:
        throw new Error(`Unknown tool: ${name}`);
    }

    return {
      content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return {
      content: [{ type: "text", text: `Error: ${message}` }],
      isError: true,
    };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Superset MCP Server running on stdio");
}

main().catch(console.error);
