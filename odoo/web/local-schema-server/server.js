import express from 'express';
import cors from 'cors';
import { readFileSync, readdirSync, statSync } from 'fs';
import { join, dirname, extname, basename } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..', '..');

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.SCHEMA_PORT || 8765;

// Schema file locations
const SCHEMA_PATHS = {
  dbml: join(ROOT, 'docs/data-model'),
  sql: join(ROOT, 'db/schema'),
  migrations: join(ROOT, 'db/migrations'),
  supabase: join(ROOT, 'supabase/migrations'),
};

// List all schema files
function listSchemaFiles(dir, ext) {
  try {
    return readdirSync(dir)
      .filter(f => extname(f).toLowerCase() === ext)
      .map(f => ({
        name: f,
        path: join(dir, f),
        size: statSync(join(dir, f)).size,
      }));
  } catch {
    return [];
  }
}

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'local-schema-server', timestamp: new Date().toISOString() });
});

// List all available schemas
app.get('/schemas', (req, res) => {
  res.json({
    dbml: listSchemaFiles(SCHEMA_PATHS.dbml, '.dbml'),
    sql: listSchemaFiles(SCHEMA_PATHS.sql, '.sql'),
    migrations: listSchemaFiles(SCHEMA_PATHS.migrations, '.sql'),
    supabase: listSchemaFiles(SCHEMA_PATHS.supabase, '.sql'),
  });
});

// Get canonical DBML schema (main entry point)
app.get('/schema/canonical', (req, res) => {
  try {
    const content = readFileSync(join(SCHEMA_PATHS.dbml, 'insightpulse_canonical.dbml'), 'utf-8');
    res.type('text/plain').send(content);
  } catch (err) {
    res.status(404).json({ error: 'Canonical schema not found', details: err.message });
  }
});

// Get Odoo canonical schema
app.get('/schema/odoo', (req, res) => {
  try {
    const content = readFileSync(join(SCHEMA_PATHS.dbml, 'ODOO_CANONICAL_SCHEMA.dbml'), 'utf-8');
    res.type('text/plain').send(content);
  } catch (err) {
    res.status(404).json({ error: 'Odoo schema not found', details: err.message });
  }
});

// Get any schema file by name
app.get('/schema/:type/:name', (req, res) => {
  const { type, name } = req.params;
  const basePath = SCHEMA_PATHS[type];

  if (!basePath) {
    return res.status(400).json({ error: `Invalid schema type: ${type}` });
  }

  try {
    const filePath = join(basePath, name);
    const content = readFileSync(filePath, 'utf-8');
    res.type('text/plain').send(content);
  } catch (err) {
    res.status(404).json({ error: `Schema not found: ${name}`, details: err.message });
  }
});

// Get control plane SQL schema
app.get('/schema/control-plane', (req, res) => {
  try {
    const content = readFileSync(join(SCHEMA_PATHS.sql, 'control_plane_schema.sql'), 'utf-8');
    res.type('text/plain').send(content);
  } catch (err) {
    res.status(404).json({ error: 'Control plane schema not found', details: err.message });
  }
});

// JSON endpoint for schema metadata
app.get('/schema/canonical.json', (req, res) => {
  try {
    const content = readFileSync(join(SCHEMA_PATHS.dbml, 'insightpulse_canonical.dbml'), 'utf-8');
    const tables = content.match(/Table\s+(\w+)\s*\{/g)?.map(t => t.match(/Table\s+(\w+)/)[1]) || [];
    res.json({
      name: 'insightpulse_canonical',
      format: 'dbml',
      tables,
      tableCount: tables.length,
    });
  } catch (err) {
    res.status(404).json({ error: 'Canonical schema not found', details: err.message });
  }
});

app.listen(PORT, () => {
  console.log(`Schema server running at http://localhost:${PORT}`);
  console.log(`\nEndpoints:`);
  console.log(`  GET /health              - Health check`);
  console.log(`  GET /schemas             - List all schemas`);
  console.log(`  GET /schema/canonical    - InsightPulse canonical DBML`);
  console.log(`  GET /schema/odoo         - Odoo canonical DBML`);
  console.log(`  GET /schema/control-plane - Control plane SQL`);
  console.log(`  GET /schema/:type/:name  - Get specific schema file`);
});
