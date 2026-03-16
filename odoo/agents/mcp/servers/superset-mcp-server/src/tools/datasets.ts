/**
 * Dataset management tools
 */

import { SupersetClient } from "../superset-client.js";

export async function listDatasets(
  client: SupersetClient,
  databaseId?: number
): Promise<unknown> {
  return client.listDatasets(databaseId);
}

export async function getDataset(
  client: SupersetClient,
  id: number
): Promise<unknown> {
  return client.getDataset(id);
}

interface CreateDatasetOptions {
  database_id: number;
  table_name?: string;
  schema?: string;
  sql?: string;
}

export async function createDataset(
  client: SupersetClient,
  options: CreateDatasetOptions
): Promise<unknown> {
  const data: Record<string, unknown> = {
    database: options.database_id,
  };

  if (options.sql) {
    // Virtual dataset from SQL
    data.sql = options.sql;
    data.table_name = options.table_name || "virtual_dataset";
  } else if (options.table_name) {
    // Physical table
    data.table_name = options.table_name;
    if (options.schema) {
      data.schema = options.schema;
    }
  }

  return client.createDataset(data);
}

export async function syncDatasetColumns(
  client: SupersetClient,
  id: number
): Promise<unknown> {
  return client.refreshDatasetColumns(id);
}
