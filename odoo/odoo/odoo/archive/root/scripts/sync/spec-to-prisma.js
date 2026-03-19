#!/usr/bin/env node
/**
 * Spec to Prisma Schema Sync
 * Parses spec PRD files and generates Prisma schema models
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

const SPEC_DIR = path.join(__dirname, '../../spec');
const PRISMA_SCHEMA = path.join(__dirname, '../../prisma/schema.prisma');

// Parse entity definitions from PRD markdown
function parseEntitiesFromPRD(content) {
  const entities = [];

  // Match table definitions in markdown code blocks
  const tableRegex = /```(?:sql|prisma)?\n([\s\S]*?)```/g;
  let match;

  while ((match = tableRegex.exec(content)) !== null) {
    const block = match[1];

    // Parse CREATE TABLE statements
    const createTableRegex = /CREATE TABLE (?:IF NOT EXISTS )?(\w+)\s*\(([\s\S]*?)\);/gi;
    let tableMatch;

    while ((tableMatch = createTableRegex.exec(block)) !== null) {
      const tableName = tableMatch[1];
      const columnsStr = tableMatch[2];

      entities.push({
        name: toPascalCase(tableName),
        tableName,
        fields: parseColumns(columnsStr)
      });
    }
  }

  // Also parse data model sections
  const modelRegex = /### (\w+)\s*\n([\s\S]*?)(?=###|$)/g;
  while ((match = modelRegex.exec(content)) !== null) {
    const modelName = match[1];
    const modelContent = match[2];

    // Parse field lists
    const fieldRegex = /[-*]\s*`?(\w+)`?\s*[:-]\s*(.+)/g;
    const fields = [];
    let fieldMatch;

    while ((fieldMatch = fieldRegex.exec(modelContent)) !== null) {
      const fieldName = fieldMatch[1];
      const fieldDesc = fieldMatch[2];

      fields.push({
        name: toCamelCase(fieldName),
        type: inferPrismaType(fieldDesc),
        description: fieldDesc
      });
    }

    if (fields.length > 0) {
      entities.push({
        name: toPascalCase(modelName),
        tableName: toSnakeCase(modelName),
        fields
      });
    }
  }

  return entities;
}

// Parse SQL column definitions
function parseColumns(columnsStr) {
  const fields = [];
  const lines = columnsStr.split('\n').filter(l => l.trim());

  for (const line of lines) {
    const trimmed = line.trim().replace(/,\s*$/, '');

    // Skip constraints
    if (/^(PRIMARY KEY|FOREIGN KEY|CONSTRAINT|UNIQUE|CHECK|INDEX)/i.test(trimmed)) {
      continue;
    }

    // Parse column: name TYPE [constraints]
    const colMatch = trimmed.match(/^(\w+)\s+(\w+(?:\([^)]+\))?)\s*(.*)/);
    if (colMatch) {
      const [, colName, sqlType, constraints] = colMatch;

      fields.push({
        name: toCamelCase(colName),
        dbName: colName,
        type: sqlTypeToPrisma(sqlType),
        isOptional: !/NOT NULL/i.test(constraints) && !/PRIMARY KEY/i.test(constraints),
        isId: /PRIMARY KEY/i.test(constraints),
        hasDefault: /DEFAULT/i.test(constraints),
        isUnique: /UNIQUE/i.test(constraints)
      });
    }
  }

  return fields;
}

// Convert SQL types to Prisma types
function sqlTypeToPrisma(sqlType) {
  const typeMap = {
    'uuid': 'String @db.Uuid',
    'text': 'String',
    'varchar': 'String',
    'int': 'Int',
    'integer': 'Int',
    'bigint': 'BigInt',
    'decimal': 'Decimal',
    'numeric': 'Decimal',
    'boolean': 'Boolean',
    'bool': 'Boolean',
    'date': 'DateTime @db.Date',
    'timestamp': 'DateTime',
    'timestamptz': 'DateTime',
    'jsonb': 'Json',
    'json': 'Json',
    'inet': 'String'
  };

  const baseType = sqlType.toLowerCase().replace(/\([^)]+\)/, '');
  return typeMap[baseType] || 'String';
}

// Infer Prisma type from description
function inferPrismaType(description) {
  const desc = description.toLowerCase();

  if (desc.includes('id') || desc.includes('uuid')) return 'String @db.Uuid';
  if (desc.includes('date') || desc.includes('time')) return 'DateTime';
  if (desc.includes('number') || desc.includes('count') || desc.includes('amount')) return 'Int';
  if (desc.includes('decimal') || desc.includes('price') || desc.includes('money')) return 'Decimal';
  if (desc.includes('boolean') || desc.includes('flag') || desc.includes('is_')) return 'Boolean';
  if (desc.includes('json') || desc.includes('object') || desc.includes('array')) return 'Json';

  return 'String';
}

// String utilities
function toPascalCase(str) {
  return str
    .replace(/_/g, ' ')
    .replace(/\w+/g, w => w[0].toUpperCase() + w.slice(1).toLowerCase())
    .replace(/\s/g, '');
}

function toCamelCase(str) {
  const pascal = toPascalCase(str);
  return pascal[0].toLowerCase() + pascal.slice(1);
}

function toSnakeCase(str) {
  return str
    .replace(/([A-Z])/g, '_$1')
    .toLowerCase()
    .replace(/^_/, '');
}

// Generate Prisma model
function generatePrismaModel(entity) {
  const lines = [`model ${entity.name} {`];

  for (const field of entity.fields) {
    let line = `  ${field.name}`;
    line += ` ${field.type}`;

    if (field.isId) line += ' @id';
    if (field.isOptional) line += '?';
    if (field.hasDefault) line += ' @default(...)';
    if (field.isUnique) line += ' @unique';
    if (field.dbName && field.dbName !== field.name) {
      line += ` @map("${field.dbName}")`;
    }

    lines.push(line);
  }

  if (entity.tableName !== entity.name) {
    lines.push(`  @@map("${entity.tableName}")`);
  }

  lines.push('}');
  lines.push('');

  return lines.join('\n');
}

// Main sync function
async function syncSpecToPrisma() {
  console.log('Starting spec-to-prisma sync...');

  // Find all PRD files
  const prdFiles = glob.sync(`${SPEC_DIR}/**/prd.md`);
  console.log(`Found ${prdFiles.length} PRD files`);

  const allEntities = [];

  for (const file of prdFiles) {
    const content = fs.readFileSync(file, 'utf-8');
    const entities = parseEntitiesFromPRD(content);

    if (entities.length > 0) {
      console.log(`  ${path.relative(SPEC_DIR, file)}: ${entities.length} entities`);
      allEntities.push(...entities);
    }
  }

  if (allEntities.length === 0) {
    console.log('No entities found in spec files');
    return;
  }

  // Generate Prisma schema header
  const header = `// Generated by spec-to-prisma sync
// Last updated: ${new Date().toISOString()}
// DO NOT EDIT MANUALLY - changes will be overwritten

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

`;

  // Generate all models
  const models = allEntities.map(generatePrismaModel).join('\n');

  // Write schema
  const schemaContent = header + models;

  // Ensure directory exists
  const prismaDir = path.dirname(PRISMA_SCHEMA);
  if (!fs.existsSync(prismaDir)) {
    fs.mkdirSync(prismaDir, { recursive: true });
  }

  fs.writeFileSync(PRISMA_SCHEMA, schemaContent);
  console.log(`\nGenerated Prisma schema with ${allEntities.length} models`);
  console.log(`Output: ${PRISMA_SCHEMA}`);
}

// Run if called directly
if (require.main === module) {
  syncSpecToPrisma().catch(console.error);
}

module.exports = { syncSpecToPrisma, parseEntitiesFromPRD };
