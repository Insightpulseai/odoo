#!/usr/bin/env node
/**
 * Docs to KB Sync
 * Syncs markdown documentation to Supabase KB artifacts
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');
const crypto = require('crypto');

const DOCS_DIR = path.join(__dirname, '../../docs');
const SUPABASE_URL = process.env.SUPABASE_URL || 'https://spdtwktxdalcfigzeqrz.supabase.co';
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_KEY;

// Parse markdown frontmatter
function parseFrontmatter(content) {
  const match = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);

  if (!match) {
    return { frontmatter: {}, content };
  }

  const frontmatter = {};
  const lines = match[1].split('\n');

  for (const line of lines) {
    const [key, ...valueParts] = line.split(':');
    if (key && valueParts.length > 0) {
      let value = valueParts.join(':').trim();

      // Parse arrays
      if (value.startsWith('[') && value.endsWith(']')) {
        value = value.slice(1, -1).split(',').map(v => v.trim().replace(/["']/g, ''));
      }
      // Remove quotes
      else if ((value.startsWith('"') && value.endsWith('"')) ||
               (value.startsWith("'") && value.endsWith("'"))) {
        value = value.slice(1, -1);
      }

      frontmatter[key.trim()] = value;
    }
  }

  return { frontmatter, content: match[2] };
}

// Extract title from markdown
function extractTitle(content) {
  const match = content.match(/^#\s+(.+)/m);
  return match ? match[1].trim() : null;
}

// Determine artifact kind from path/content
function determineKind(filePath, content) {
  const pathParts = filePath.toLowerCase();

  if (pathParts.includes('prd') || pathParts.includes('spec')) return 'prd';
  if (pathParts.includes('architecture') || pathParts.includes('design')) return 'architecture';
  if (pathParts.includes('runbook') || pathParts.includes('ops')) return 'runbook';
  if (pathParts.includes('api') || pathParts.includes('reference')) return 'api_reference';
  if (pathParts.includes('dictionary') || pathParts.includes('data')) return 'data_dictionary';
  if (pathParts.includes('readme')) return 'readme';
  if (pathParts.includes('changelog')) return 'changelog';

  return 'documentation';
}

// Extract tags from content
function extractTags(content, filePath) {
  const tags = new Set();

  // Add path-based tags
  const pathParts = filePath.split('/');
  for (const part of pathParts) {
    if (part !== 'docs' && part !== 'md' && !part.includes('.')) {
      tags.add(part.toLowerCase());
    }
  }

  // Extract technology mentions
  const techPatterns = [
    /\b(supabase|postgres|postgresql)\b/gi,
    /\b(react|next\.?js|typescript)\b/gi,
    /\b(n8n|workflow|automation)\b/gi,
    /\b(odoo|erp)\b/gi,
    /\b(databricks|spark|delta)\b/gi,
    /\b(api|rest|graphql)\b/gi
  ];

  for (const pattern of techPatterns) {
    const matches = content.match(pattern);
    if (matches) {
      for (const match of matches) {
        tags.add(match.toLowerCase().replace(/\./g, ''));
      }
    }
  }

  return Array.from(tags).slice(0, 10); // Limit to 10 tags
}

// Determine personas from content
function determinePersonas(content, kind) {
  const personas = new Set();

  // Default personas by kind
  const kindPersonas = {
    'prd': ['product', 'engineering'],
    'architecture': ['engineering', 'devops'],
    'runbook': ['devops', 'sre'],
    'api_reference': ['engineering', 'integration'],
    'data_dictionary': ['data', 'engineering'],
    'readme': ['engineering'],
    'documentation': ['engineering']
  };

  personas.add(...(kindPersonas[kind] || ['engineering']));

  // Add based on content
  if (/\b(budget|cost|finance|expense)\b/i.test(content)) personas.add('finance');
  if (/\b(hr|employee|payroll|leave)\b/i.test(content)) personas.add('hr');
  if (/\b(deploy|ci\/cd|pipeline|infrastructure)\b/i.test(content)) personas.add('devops');
  if (/\b(metric|dashboard|report|analytics)\b/i.test(content)) personas.add('analytics');

  return Array.from(personas);
}

// Calculate content hash for change detection
function calculateHash(content) {
  return crypto.createHash('md5').update(content).digest('hex');
}

// Process a single markdown file
function processMarkdownFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const relativePath = path.relative(DOCS_DIR, filePath);
  const { frontmatter, content: body } = parseFrontmatter(content);

  const title = frontmatter.title || extractTitle(body) || path.basename(filePath, '.md');
  const kind = frontmatter.kind || determineKind(relativePath, body);
  const tags = frontmatter.tags || extractTags(body, relativePath);
  const personas = frontmatter.personas || determinePersonas(body, kind);

  return {
    source_path: relativePath,
    title,
    kind,
    content: body,
    content_hash: calculateHash(content),
    tags,
    personas,
    metadata: {
      ...frontmatter,
      file_size: content.length,
      last_modified: fs.statSync(filePath).mtime.toISOString()
    }
  };
}

// Sync to Supabase
async function syncToSupabase(artifacts) {
  if (!SUPABASE_KEY) {
    console.log('SUPABASE_SERVICE_KEY not set - running in dry-run mode');
    console.log(`Would sync ${artifacts.length} artifacts`);
    return { inserted: 0, updated: 0, unchanged: 0 };
  }

  const stats = { inserted: 0, updated: 0, unchanged: 0 };

  for (const artifact of artifacts) {
    try {
      // Check if artifact exists
      const checkResponse = await fetch(
        `${SUPABASE_URL}/rest/v1/kb_artifacts?source_path=eq.${encodeURIComponent(artifact.source_path)}&select=id,content_hash`,
        {
          headers: {
            'apikey': SUPABASE_KEY,
            'Authorization': `Bearer ${SUPABASE_KEY}`
          }
        }
      );

      const existing = await checkResponse.json();

      if (existing.length > 0) {
        // Check if content changed
        if (existing[0].content_hash === artifact.content_hash) {
          stats.unchanged++;
          continue;
        }

        // Update existing
        await fetch(
          `${SUPABASE_URL}/rest/v1/kb_artifacts?id=eq.${existing[0].id}`,
          {
            method: 'PATCH',
            headers: {
              'apikey': SUPABASE_KEY,
              'Authorization': `Bearer ${SUPABASE_KEY}`,
              'Content-Type': 'application/json',
              'Prefer': 'return=minimal'
            },
            body: JSON.stringify({
              ...artifact,
              updated_at: new Date().toISOString()
            })
          }
        );
        stats.updated++;
      } else {
        // Insert new
        await fetch(
          `${SUPABASE_URL}/rest/v1/kb_artifacts`,
          {
            method: 'POST',
            headers: {
              'apikey': SUPABASE_KEY,
              'Authorization': `Bearer ${SUPABASE_KEY}`,
              'Content-Type': 'application/json',
              'Prefer': 'return=minimal'
            },
            body: JSON.stringify(artifact)
          }
        );
        stats.inserted++;
      }
    } catch (error) {
      console.error(`Error syncing ${artifact.source_path}:`, error.message);
    }
  }

  return stats;
}

// Main sync function
async function syncDocsToKB() {
  console.log('Starting docs-to-kb sync...');

  // Find all markdown files
  const files = glob.sync(`${DOCS_DIR}/**/*.md`);
  console.log(`Found ${files.length} markdown files`);

  // Process all files
  const artifacts = [];
  for (const file of files) {
    try {
      const artifact = processMarkdownFile(file);
      artifacts.push(artifact);
      console.log(`  Processed: ${artifact.source_path} (${artifact.kind})`);
    } catch (error) {
      console.error(`  Error processing ${file}:`, error.message);
    }
  }

  // Sync to Supabase
  console.log('\nSyncing to Supabase KB...');
  const stats = await syncToSupabase(artifacts);

  console.log('\nSync complete:');
  console.log(`  Inserted: ${stats.inserted}`);
  console.log(`  Updated: ${stats.updated}`);
  console.log(`  Unchanged: ${stats.unchanged}`);
}

// Run if called directly
if (require.main === module) {
  syncDocsToKB().catch(console.error);
}

module.exports = { syncDocsToKB, processMarkdownFile };
