#!/usr/bin/env node
/**
 * Schema to Docs Sync
 * Generates data dictionary from SQL migrations
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

const MIGRATIONS_DIR = path.join(__dirname, '../../supabase/migrations');
const DOCS_OUTPUT = path.join(__dirname, '../../docs/data-dictionary.md');

// Parse all migrations and build complete schema
function parseAllMigrations() {
  const migrations = glob.sync(`${MIGRATIONS_DIR}/*.sql`).sort();
  const schema = {
    tables: {},
    indexes: [],
    policies: [],
    functions: []
  };

  for (const file of migrations) {
    const content = fs.readFileSync(file, 'utf-8');
    const filename = path.basename(file);

    // Parse tables
    const tables = parseTables(content, filename);
    for (const table of tables) {
      schema.tables[table.name] = table;
    }

    // Parse indexes
    schema.indexes.push(...parseIndexes(content));

    // Parse RLS policies
    schema.policies.push(...parsePolicies(content));

    // Parse functions
    schema.functions.push(...parseFunctions(content));
  }

  return schema;
}

// Parse CREATE TABLE statements
function parseTables(content, sourceFile) {
  const tables = [];
  const tableRegex = /CREATE TABLE (?:IF NOT EXISTS )?(\w+(?:\.\w+)?)\s*\(([\s\S]*?)\);/gi;
  let match;

  while ((match = tableRegex.exec(content)) !== null) {
    const tableName = match[1];
    const columnsStr = match[2];

    // Get table comment if exists
    const commentRegex = new RegExp(`COMMENT ON TABLE ${tableName} IS '([^']+)'`, 'i');
    const commentMatch = content.match(commentRegex);

    tables.push({
      name: tableName,
      columns: parseColumns(columnsStr),
      comment: commentMatch ? commentMatch[1] : extractInlineComment(content, tableName),
      sourceFile
    });
  }

  return tables;
}

// Extract inline comment before table definition
function extractInlineComment(content, tableName) {
  const regex = new RegExp(`-- ([^\n]+)\nCREATE TABLE (?:IF NOT EXISTS )?${tableName}`, 'i');
  const match = content.match(regex);
  return match ? match[1].trim() : null;
}

// Parse column definitions
function parseColumns(columnsStr) {
  const columns = [];
  const lines = columnsStr.split('\n').filter(l => l.trim() && !l.trim().startsWith('--'));

  for (const line of lines) {
    const trimmed = line.trim().replace(/,\s*$/, '');

    // Skip constraints
    if (/^(PRIMARY KEY|FOREIGN KEY|CONSTRAINT|UNIQUE|CHECK|CREATE)/i.test(trimmed)) {
      // Parse constraint for documentation
      const constraintInfo = parseConstraint(trimmed);
      if (constraintInfo) {
        // Add constraint info to relevant column
        for (const col of columns) {
          if (constraintInfo.columns.includes(col.name)) {
            col.constraints = col.constraints || [];
            col.constraints.push(constraintInfo);
          }
        }
      }
      continue;
    }

    // Parse column
    const colMatch = trimmed.match(/^(\w+)\s+(\w+(?:\([^)]+\))?)\s*(.*)/);
    if (colMatch) {
      const [, name, sqlType, rest] = colMatch;

      // Extract inline comment
      const commentMatch = rest.match(/--\s*(.+)/);
      const comment = commentMatch ? commentMatch[1].trim() : null;

      // Parse constraints from rest
      const constraints = rest.replace(/--.*/, '').trim();

      columns.push({
        name,
        type: sqlType,
        nullable: !/NOT NULL/i.test(constraints),
        isPrimaryKey: /PRIMARY KEY/i.test(constraints),
        isUnique: /UNIQUE/i.test(constraints),
        hasDefault: /DEFAULT/i.test(constraints),
        defaultValue: extractDefault(constraints),
        references: extractReference(constraints),
        check: extractCheck(constraints),
        comment
      });
    }
  }

  return columns;
}

// Extract DEFAULT value
function extractDefault(constraints) {
  const match = constraints.match(/DEFAULT\s+([^,\s]+(?:\([^)]*\))?)/i);
  return match ? match[1] : null;
}

// Extract REFERENCES
function extractReference(constraints) {
  const match = constraints.match(/REFERENCES\s+(\w+(?:\.\w+)?)\s*\((\w+)\)/i);
  return match ? { table: match[1], column: match[2] } : null;
}

// Extract CHECK constraint
function extractCheck(constraints) {
  const match = constraints.match(/CHECK\s*\(([^)]+)\)/i);
  return match ? match[1] : null;
}

// Parse constraint definitions
function parseConstraint(line) {
  // FOREIGN KEY
  let match = line.match(/FOREIGN KEY\s*\(([^)]+)\)\s*REFERENCES\s+(\w+)\s*\(([^)]+)\)/i);
  if (match) {
    return {
      type: 'FOREIGN KEY',
      columns: match[1].split(',').map(c => c.trim()),
      references: { table: match[2], columns: match[3].split(',').map(c => c.trim()) }
    };
  }

  // UNIQUE
  match = line.match(/UNIQUE\s*\(([^)]+)\)/i);
  if (match) {
    return {
      type: 'UNIQUE',
      columns: match[1].split(',').map(c => c.trim())
    };
  }

  return null;
}

// Parse CREATE INDEX statements
function parseIndexes(content) {
  const indexes = [];
  const indexRegex = /CREATE (?:UNIQUE )?INDEX (?:IF NOT EXISTS )?(\w+)\s+ON\s+(\w+)\s*\(([^)]+)\)/gi;
  let match;

  while ((match = indexRegex.exec(content)) !== null) {
    indexes.push({
      name: match[1],
      table: match[2],
      columns: match[3].split(',').map(c => c.trim())
    });
  }

  return indexes;
}

// Parse RLS policies
function parsePolicies(content) {
  const policies = [];
  const policyRegex = /CREATE POLICY\s+"([^"]+)"\s+ON\s+(\w+)\s+(?:FOR\s+(\w+)\s+)?(?:TO\s+(\w+)\s+)?(?:USING\s*\(([\s\S]*?)\))?(?:\s+WITH CHECK\s*\(([\s\S]*?)\))?;/gi;
  let match;

  while ((match = policyRegex.exec(content)) !== null) {
    policies.push({
      name: match[1],
      table: match[2],
      operation: match[3] || 'ALL',
      role: match[4] || 'public',
      using: match[5]?.trim(),
      withCheck: match[6]?.trim()
    });
  }

  return policies;
}

// Parse functions
function parseFunctions(content) {
  const functions = [];
  const funcRegex = /CREATE (?:OR REPLACE )?FUNCTION\s+(\w+)\s*\(([^)]*)\)\s*RETURNS\s+(\w+)/gi;
  let match;

  while ((match = funcRegex.exec(content)) !== null) {
    functions.push({
      name: match[1],
      parameters: match[2].trim(),
      returns: match[3]
    });
  }

  return functions;
}

// Group tables by domain
function groupTablesByDomain(tables) {
  const domains = {
    'HR': [],
    'Finance': [],
    'Knowledge Base': [],
    'Control Room': [],
    'Data': [],
    'Auth': [],
    'Other': []
  };

  for (const [name, table] of Object.entries(tables)) {
    if (name.startsWith('hr_')) domains['HR'].push(table);
    else if (name.startsWith('finance_')) domains['Finance'].push(table);
    else if (name.startsWith('kb_')) domains['Knowledge Base'].push(table);
    else if (name.startsWith('control_room_')) domains['Control Room'].push(table);
    else if (name.startsWith('data_')) domains['Data'].push(table);
    else if (name.startsWith('auth.') || name.startsWith('odoo_')) domains['Auth'].push(table);
    else domains['Other'].push(table);
  }

  // Filter empty domains
  return Object.fromEntries(
    Object.entries(domains).filter(([, tables]) => tables.length > 0)
  );
}

// Generate markdown documentation
function generateMarkdown(schema) {
  const lines = [];

  // Header
  lines.push('# Data Dictionary');
  lines.push('');
  lines.push('> Auto-generated from Supabase migrations');
  lines.push(`> Last updated: ${new Date().toISOString()}`);
  lines.push('');

  // Table of contents
  lines.push('## Table of Contents');
  lines.push('');
  const domains = groupTablesByDomain(schema.tables);

  for (const [domain, tables] of Object.entries(domains)) {
    lines.push(`- [${domain}](#${domain.toLowerCase().replace(/\s+/g, '-')})`);
    for (const table of tables) {
      lines.push(`  - [${table.name}](#${table.name.replace(/_/g, '-')})`);
    }
  }
  lines.push('');

  // Overview
  lines.push('## Overview');
  lines.push('');
  lines.push('| Domain | Tables | Description |');
  lines.push('|--------|--------|-------------|');

  for (const [domain, tables] of Object.entries(domains)) {
    const desc = getDomainDescription(domain);
    lines.push(`| ${domain} | ${tables.length} | ${desc} |`);
  }
  lines.push('');

  // Tables by domain
  for (const [domain, tables] of Object.entries(domains)) {
    lines.push(`## ${domain}`);
    lines.push('');

    for (const table of tables) {
      lines.push(`### ${table.name}`);
      lines.push('');

      if (table.comment) {
        lines.push(`> ${table.comment}`);
        lines.push('');
      }

      lines.push(`**Source:** \`${table.sourceFile}\``);
      lines.push('');

      // Columns table
      lines.push('| Column | Type | Nullable | Default | Description |');
      lines.push('|--------|------|----------|---------|-------------|');

      for (const col of table.columns) {
        const nullable = col.nullable ? 'Yes' : 'No';
        const defaultVal = col.defaultValue || '-';
        const desc = formatColumnDescription(col);
        lines.push(`| ${col.name} | \`${col.type}\` | ${nullable} | \`${defaultVal}\` | ${desc} |`);
      }
      lines.push('');

      // Foreign keys
      const fks = table.columns.filter(c => c.references);
      if (fks.length > 0) {
        lines.push('**Foreign Keys:**');
        for (const fk of fks) {
          lines.push(`- \`${fk.name}\` → \`${fk.references.table}(${fk.references.column})\``);
        }
        lines.push('');
      }
    }
  }

  // Indexes section
  if (schema.indexes.length > 0) {
    lines.push('## Indexes');
    lines.push('');
    lines.push('| Name | Table | Columns |');
    lines.push('|------|-------|---------|');

    for (const idx of schema.indexes) {
      lines.push(`| ${idx.name} | ${idx.table} | ${idx.columns.join(', ')} |`);
    }
    lines.push('');
  }

  // Policies section
  if (schema.policies.length > 0) {
    lines.push('## Row Level Security Policies');
    lines.push('');

    const policyByTable = {};
    for (const policy of schema.policies) {
      policyByTable[policy.table] = policyByTable[policy.table] || [];
      policyByTable[policy.table].push(policy);
    }

    for (const [table, policies] of Object.entries(policyByTable)) {
      lines.push(`### ${table}`);
      lines.push('');

      for (const policy of policies) {
        lines.push(`**${policy.name}** (${policy.operation})`);
        if (policy.using) {
          lines.push('```sql');
          lines.push(`USING (${policy.using})`);
          lines.push('```');
        }
        lines.push('');
      }
    }
  }

  // Functions section
  if (schema.functions.length > 0) {
    lines.push('## Functions');
    lines.push('');
    lines.push('| Function | Parameters | Returns |');
    lines.push('|----------|------------|---------|');

    for (const func of schema.functions) {
      const params = func.parameters || '-';
      lines.push(`| \`${func.name}\` | \`${params}\` | \`${func.returns}\` |`);
    }
    lines.push('');
  }

  return lines.join('\n');
}

// Get domain description
function getDomainDescription(domain) {
  const descriptions = {
    'HR': 'Employee management, leave, attendance, payroll',
    'Finance': 'Expenses, budgets, approvals, financial tasks',
    'Knowledge Base': 'Documents, artifacts, spaces, relations',
    'Control Room': 'Jobs, pipelines, monitoring',
    'Data': 'Data assets, lineage, quality',
    'Auth': 'Authentication and authorization',
    'Other': 'Miscellaneous tables'
  };
  return descriptions[domain] || '';
}

// Format column description
function formatColumnDescription(col) {
  const parts = [];

  if (col.isPrimaryKey) parts.push('**PK**');
  if (col.isUnique) parts.push('unique');
  if (col.check) parts.push(`check: ${col.check}`);
  if (col.comment) parts.push(col.comment);

  return parts.join(', ') || '-';
}

// Main sync function
async function syncSchemaToDocs() {
  console.log('Starting schema-to-docs sync...');

  const schema = parseAllMigrations();
  const tableCount = Object.keys(schema.tables).length;

  console.log(`Parsed ${tableCount} tables`);
  console.log(`Found ${schema.indexes.length} indexes`);
  console.log(`Found ${schema.policies.length} RLS policies`);
  console.log(`Found ${schema.functions.length} functions`);

  if (tableCount === 0) {
    console.log('No tables found');
    return;
  }

  const markdown = generateMarkdown(schema);

  // Ensure output directory exists
  const outputDir = path.dirname(DOCS_OUTPUT);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  fs.writeFileSync(DOCS_OUTPUT, markdown);
  console.log(`\nGenerated data dictionary with ${tableCount} tables`);
  console.log(`Output: ${DOCS_OUTPUT}`);
}

// Run if called directly
if (require.main === module) {
  syncSchemaToDocs().catch(console.error);
}

module.exports = { syncSchemaToDocs, parseAllMigrations };
