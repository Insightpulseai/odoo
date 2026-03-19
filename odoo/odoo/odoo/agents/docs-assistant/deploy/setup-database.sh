#!/bin/bash

# Database Setup Script for Docs Assistant
set -e

echo "🗄️ Setting up Docs Assistant Database..."

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL environment variable not set"
    echo "Please set DATABASE_URL to your Supabase PostgreSQL connection string"
    echo "Example: postgresql://user:password@host:port/database"
    exit 1
fi

# Apply schema
echo "📋 Applying database schema..."
psql "$DATABASE_URL" -f ../supabase/schema.sql

# Create initial project and API key
echo "🔑 Creating initial project and API key..."

# Generate a random API key
API_KEY=$(openssl rand -hex 32)
API_KEY_HASH=$(echo -n "$API_KEY" | shasum -a 256 | cut -d' ' -f1)

# SQL to create initial setup
SQL=$(cat << EOF
-- Create initial project
INSERT INTO docs_projects (name, slug, description)
VALUES ('Odoo CE Documentation', 'odoo-ce', 'Odoo Community Edition Documentation Assistant')
ON CONFLICT (slug) DO NOTHING;

-- Create API key for the project
INSERT INTO docs_api_keys (project_id, key_hash, label)
SELECT id, '$API_KEY_HASH', 'Initial API Key'
FROM docs_projects
WHERE slug = 'odoo-ce'
ON CONFLICT DO NOTHING;

-- Create default source group
INSERT INTO docs_source_groups (project_id, name, description, is_default)
SELECT id, 'default', 'Default documentation sources', true
FROM docs_projects
WHERE slug = 'odoo-ce'
ON CONFLICT DO NOTHING;

-- Display created resources
SELECT
    p.name as project_name,
    p.slug as project_slug,
    ak.id as api_key_id,
    'API Key: $API_KEY' as api_key_value
FROM docs_projects p
LEFT JOIN docs_api_keys ak ON p.id = ak.project_id
WHERE p.slug = 'odoo-ce';
EOF
)

# Execute the SQL
echo "$SQL" | psql "$DATABASE_URL" --quiet

echo ""
echo "✅ Database setup complete!"
echo ""
echo "📋 Created Resources:"
echo "   Project: Odoo CE Documentation (odoo-ce)"
echo "   API Key: $API_KEY"
echo ""
echo "🔧 Next Steps:"
echo "   1. Save the API key above - you won't see it again!"
echo "   2. Configure your widget with this API key"
echo "   3. Add documentation sources using the API"
echo ""
echo "📝 Example widget configuration:"
echo '<script src="http://localhost/docs-assistant/docs-widget.js"'
echo "  data-api-url=\"http://localhost/api\""
echo "  data-api-key=\"$API_KEY\""
echo "  data-project-slug=\"odoo-ce\">"
echo '</script>'
