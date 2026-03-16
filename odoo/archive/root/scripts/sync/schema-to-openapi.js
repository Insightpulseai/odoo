#!/usr/bin/env node
/**
 * Schema to OpenAPI Sync
 * Parses SQL migrations and generates OpenAPI specification
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');
const yaml = require('js-yaml');

const MIGRATIONS_DIR = path.join(__dirname, '../../supabase/migrations');
const OPENAPI_OUTPUT = path.join(__dirname, '../../docs/api/openapi.yaml');

// Parse SQL migration files
function parseMigrations() {
  const migrations = glob.sync(`${MIGRATIONS_DIR}/*.sql`);
  const tables = {};

  for (const file of migrations) {
    const content = fs.readFileSync(file, 'utf-8');
    const parsed = parseSQLSchema(content);

    for (const table of parsed) {
      tables[table.name] = table;
    }
  }

  return tables;
}

// Parse SQL CREATE TABLE statements
function parseSQLSchema(content) {
  const tables = [];

  // Match CREATE TABLE statements
  const tableRegex = /CREATE TABLE (?:IF NOT EXISTS )?(\w+)\s*\(([\s\S]*?)\);/gi;
  let match;

  while ((match = tableRegex.exec(content)) !== null) {
    const tableName = match[1];
    const columnsStr = match[2];

    // Skip auth and system tables
    if (tableName.startsWith('auth.') || tableName.startsWith('pg_')) {
      continue;
    }

    const columns = parseColumns(columnsStr);

    tables.push({
      name: tableName,
      columns,
      primaryKey: columns.find(c => c.isPrimaryKey)?.name || 'id'
    });
  }

  return tables;
}

// Parse column definitions
function parseColumns(columnsStr) {
  const columns = [];
  const lines = columnsStr.split('\n').filter(l => l.trim());

  for (const line of lines) {
    const trimmed = line.trim().replace(/,\s*$/, '');

    // Skip constraints
    if (/^(PRIMARY KEY|FOREIGN KEY|CONSTRAINT|UNIQUE|CHECK|INDEX|CREATE)/i.test(trimmed)) {
      continue;
    }

    // Parse column
    const colMatch = trimmed.match(/^(\w+)\s+(\w+(?:\([^)]+\))?)\s*(.*)/);
    if (colMatch) {
      const [, name, sqlType, constraints] = colMatch;

      columns.push({
        name,
        type: sqlToOpenAPIType(sqlType),
        format: sqlToOpenAPIFormat(sqlType),
        nullable: !/NOT NULL/i.test(constraints) && !/PRIMARY KEY/i.test(constraints),
        isPrimaryKey: /PRIMARY KEY/i.test(constraints),
        description: extractComment(constraints)
      });
    }
  }

  return columns;
}

// Convert SQL type to OpenAPI type
function sqlToOpenAPIType(sqlType) {
  const type = sqlType.toLowerCase().replace(/\([^)]+\)/, '');

  const typeMap = {
    'uuid': 'string',
    'text': 'string',
    'varchar': 'string',
    'char': 'string',
    'int': 'integer',
    'integer': 'integer',
    'bigint': 'integer',
    'smallint': 'integer',
    'decimal': 'number',
    'numeric': 'number',
    'real': 'number',
    'double': 'number',
    'boolean': 'boolean',
    'bool': 'boolean',
    'date': 'string',
    'timestamp': 'string',
    'timestamptz': 'string',
    'time': 'string',
    'timetz': 'string',
    'jsonb': 'object',
    'json': 'object',
    'inet': 'string',
    'uuid[]': 'array'
  };

  return typeMap[type] || 'string';
}

// Get OpenAPI format for SQL type
function sqlToOpenAPIFormat(sqlType) {
  const type = sqlType.toLowerCase().replace(/\([^)]+\)/, '');

  const formatMap = {
    'uuid': 'uuid',
    'date': 'date',
    'timestamp': 'date-time',
    'timestamptz': 'date-time',
    'time': 'time',
    'inet': 'ipv4',
    'bigint': 'int64'
  };

  return formatMap[type];
}

// Extract comment from constraints
function extractComment(constraints) {
  const commentMatch = constraints.match(/--\s*(.+)/);
  return commentMatch ? commentMatch[1].trim() : undefined;
}

// Convert table name to resource name
function toResourceName(tableName) {
  // Remove common prefixes
  const prefixes = ['hr_', 'finance_', 'kb_', 'control_room_'];
  let name = tableName;

  for (const prefix of prefixes) {
    if (name.startsWith(prefix)) {
      name = name.slice(prefix.length);
      break;
    }
  }

  return name;
}

// Convert to PascalCase
function toPascalCase(str) {
  return str
    .replace(/_/g, ' ')
    .replace(/\w+/g, w => w[0].toUpperCase() + w.slice(1).toLowerCase())
    .replace(/\s/g, '');
}

// Generate OpenAPI schema for a table
function generateSchema(table) {
  const properties = {};
  const required = [];

  for (const col of table.columns) {
    const prop = {
      type: col.type
    };

    if (col.format) prop.format = col.format;
    if (col.description) prop.description = col.description;

    if (col.type === 'array') {
      prop.items = { type: 'string', format: 'uuid' };
    }

    properties[col.name] = prop;

    if (!col.nullable && !col.isPrimaryKey) {
      required.push(col.name);
    }
  }

  return {
    type: 'object',
    properties,
    required: required.length > 0 ? required : undefined
  };
}

// Generate OpenAPI paths for a table
function generatePaths(table) {
  const resource = toResourceName(table.name);
  const schemaRef = `#/components/schemas/${toPascalCase(table.name)}`;

  return {
    [`/${resource}`]: {
      get: {
        summary: `List ${resource}`,
        operationId: `list${toPascalCase(table.name)}`,
        tags: [getTag(table.name)],
        parameters: [
          { $ref: '#/components/parameters/offset' },
          { $ref: '#/components/parameters/limit' },
          { $ref: '#/components/parameters/order' }
        ],
        responses: {
          '200': {
            description: `List of ${resource}`,
            content: {
              'application/json': {
                schema: {
                  type: 'array',
                  items: { $ref: schemaRef }
                }
              }
            }
          },
          '401': { $ref: '#/components/responses/Unauthorized' }
        },
        security: [{ bearerAuth: [] }]
      },
      post: {
        summary: `Create ${resource}`,
        operationId: `create${toPascalCase(table.name)}`,
        tags: [getTag(table.name)],
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: { $ref: schemaRef }
            }
          }
        },
        responses: {
          '201': {
            description: `Created ${resource}`,
            content: {
              'application/json': {
                schema: { $ref: schemaRef }
              }
            }
          },
          '401': { $ref: '#/components/responses/Unauthorized' },
          '400': { $ref: '#/components/responses/BadRequest' }
        },
        security: [{ bearerAuth: [] }]
      }
    },
    [`/${resource}/{id}`]: {
      get: {
        summary: `Get ${resource} by ID`,
        operationId: `get${toPascalCase(table.name)}`,
        tags: [getTag(table.name)],
        parameters: [
          { $ref: '#/components/parameters/id' }
        ],
        responses: {
          '200': {
            description: `Single ${resource}`,
            content: {
              'application/json': {
                schema: { $ref: schemaRef }
              }
            }
          },
          '404': { $ref: '#/components/responses/NotFound' }
        },
        security: [{ bearerAuth: [] }]
      },
      patch: {
        summary: `Update ${resource}`,
        operationId: `update${toPascalCase(table.name)}`,
        tags: [getTag(table.name)],
        parameters: [
          { $ref: '#/components/parameters/id' }
        ],
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: { $ref: schemaRef }
            }
          }
        },
        responses: {
          '200': {
            description: `Updated ${resource}`,
            content: {
              'application/json': {
                schema: { $ref: schemaRef }
              }
            }
          },
          '404': { $ref: '#/components/responses/NotFound' }
        },
        security: [{ bearerAuth: [] }]
      },
      delete: {
        summary: `Delete ${resource}`,
        operationId: `delete${toPascalCase(table.name)}`,
        tags: [getTag(table.name)],
        parameters: [
          { $ref: '#/components/parameters/id' }
        ],
        responses: {
          '204': { description: 'Deleted' },
          '404': { $ref: '#/components/responses/NotFound' }
        },
        security: [{ bearerAuth: [] }]
      }
    }
  };
}

// Get tag from table name
function getTag(tableName) {
  const prefixes = {
    'hr_': 'HR',
    'finance_': 'Finance',
    'kb_': 'Knowledge Base',
    'control_room_': 'Control Room',
    'data_': 'Data',
    'approval_': 'Approvals'
  };

  for (const [prefix, tag] of Object.entries(prefixes)) {
    if (tableName.startsWith(prefix)) return tag;
  }

  return 'General';
}

// Generate complete OpenAPI spec
function generateOpenAPISpec(tables) {
  const schemas = {};
  let paths = {};

  for (const [name, table] of Object.entries(tables)) {
    schemas[toPascalCase(name)] = generateSchema(table);
    paths = { ...paths, ...generatePaths(table) };
  }

  return {
    openapi: '3.0.3',
    info: {
      title: 'InsightPulse API',
      description: 'Auto-generated API from Supabase schema',
      version: '1.0.0',
      contact: {
        name: 'InsightPulse Team'
      }
    },
    servers: [
      {
        url: 'https://spdtwktxdalcfigzeqrz.supabase.co/rest/v1',
        description: 'Supabase REST API'
      }
    ],
    paths,
    components: {
      schemas,
      parameters: {
        id: {
          name: 'id',
          in: 'path',
          required: true,
          schema: { type: 'string', format: 'uuid' }
        },
        offset: {
          name: 'offset',
          in: 'query',
          schema: { type: 'integer', default: 0 }
        },
        limit: {
          name: 'limit',
          in: 'query',
          schema: { type: 'integer', default: 100, maximum: 1000 }
        },
        order: {
          name: 'order',
          in: 'query',
          schema: { type: 'string' },
          description: 'Column to order by (e.g., created_at.desc)'
        }
      },
      responses: {
        Unauthorized: {
          description: 'Authentication required',
          content: {
            'application/json': {
              schema: {
                type: 'object',
                properties: {
                  message: { type: 'string' }
                }
              }
            }
          }
        },
        NotFound: {
          description: 'Resource not found'
        },
        BadRequest: {
          description: 'Invalid request'
        }
      },
      securitySchemes: {
        bearerAuth: {
          type: 'http',
          scheme: 'bearer',
          bearerFormat: 'JWT'
        }
      }
    },
    tags: [
      { name: 'HR', description: 'Human Resources operations' },
      { name: 'Finance', description: 'Finance and expense operations' },
      { name: 'Knowledge Base', description: 'KB artifact operations' },
      { name: 'Control Room', description: 'Control Room job operations' },
      { name: 'Data', description: 'Data asset operations' },
      { name: 'Approvals', description: 'Approval workflow operations' }
    ]
  };
}

// Main sync function
async function syncSchemaToOpenAPI() {
  console.log('Starting schema-to-openapi sync...');

  const tables = parseMigrations();
  const tableCount = Object.keys(tables).length;
  console.log(`Parsed ${tableCount} tables from migrations`);

  if (tableCount === 0) {
    console.log('No tables found');
    return;
  }

  const spec = generateOpenAPISpec(tables);

  // Ensure output directory exists
  const outputDir = path.dirname(OPENAPI_OUTPUT);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // Write YAML
  const yamlContent = `# Generated by schema-to-openapi sync
# Last updated: ${new Date().toISOString()}
# DO NOT EDIT MANUALLY

${yaml.dump(spec, { lineWidth: 120, noRefs: true })}`;

  fs.writeFileSync(OPENAPI_OUTPUT, yamlContent);
  console.log(`\nGenerated OpenAPI spec with ${tableCount} schemas`);
  console.log(`Output: ${OPENAPI_OUTPUT}`);
}

// Run if called directly
if (require.main === module) {
  syncSchemaToOpenAPI().catch(console.error);
}

module.exports = { syncSchemaToOpenAPI, parseMigrations };
