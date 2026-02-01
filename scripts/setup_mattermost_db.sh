#!/usr/bin/env bash
set -euo pipefail

# Mattermost Database Setup Script
# Run this on your production droplet (159.223.75.148)

echo "🔧 Setting up Mattermost database..."

# Database configuration
DB_HOST="localhost"
DB_PORT="5432"
DB_USER="odoo"
DB_NAME="mattermost"
MM_USER="mmuser"
MM_PASSWORD="mm_password"

echo "📦 Creating Mattermost database and user..."

# Create database and user
docker exec odoo_prod_db_1 psql -U "$DB_USER" -d postgres -c "
  CREATE DATABASE $DB_NAME;
  CREATE USER $MM_USER WITH PASSWORD '$MM_PASSWORD';
  GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $MM_USER;
"

echo "✅ Database created: $DB_NAME"
echo "✅ User created: $MM_USER"
echo "🔐 Password set for Mattermost user"

# Verify the setup
echo "🔍 Verifying database setup..."
docker exec odoo_prod_db_1 psql -U "$DB_USER" -d postgres -c "
  SELECT datname FROM pg_database WHERE datname = '$DB_NAME';
"

echo "🎉 Mattermost database setup complete!"
echo ""
echo "Next steps:"
echo "1. Update your docker-compose.prod.yml with Mattermost service"
echo "2. Deploy: docker compose -f docker-compose.prod.yml up -d mattermost"
echo "3. Access: https://chat.insightpulseai.com"
