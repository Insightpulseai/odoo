#!/usr/bin/env bash
set -euo pipefail

# Keycloak Database Setup Script
# Run this on your production droplet (159.223.75.148)

echo "🔧 Setting up Keycloak database..."

# Database configuration
DB_HOST="localhost"
DB_PORT="5432"
DB_USER="odoo"
DB_NAME="keycloak"
KC_USER="keycloak"
KC_PASSWORD="keycloak_password"

echo "📦 Creating Keycloak database and user..."

# Create database and user
docker exec odoo_prod_db_1 psql -U "$DB_USER" -d postgres -c "
  CREATE DATABASE $DB_NAME;
  CREATE USER $KC_USER WITH PASSWORD '$KC_PASSWORD';
  GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $KC_USER;
  GRANT CREATE ON DATABASE $DB_NAME TO $KC_USER;
"

echo "✅ Database created: $DB_NAME"
echo "✅ User created: $KC_USER"
echo "🔐 Password set for Keycloak user"

# Verify the setup
echo "🔍 Verifying database setup..."
docker exec odoo_prod_db_1 psql -U "$DB_USER" -d postgres -c "
  SELECT datname FROM pg_database WHERE datname = '$DB_NAME';
"

echo "🎉 Keycloak database setup complete!"
echo ""
echo "Next steps:"
echo "1. Update your docker-compose.prod.yml with Keycloak service"
echo "2. Set KEYCLOAK_ADMIN_PASSWORD to a secure value"
echo "3. Deploy: docker compose -f docker-compose.prod.yml up -d keycloak"
echo "4. Access: https://auth.insightpulseai.net"
echo "5. Create 'insightpulse' realm and configure clients"
