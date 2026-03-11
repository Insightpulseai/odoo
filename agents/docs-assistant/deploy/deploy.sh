#!/bin/bash

# Docs Assistant Deployment Script
set -e

echo "🚀 Starting Docs Assistant Deployment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create .env file with required variables."
    echo "Required variables:"
    echo "SUPABASE_HOST=your-supabase-host"
    echo "SUPABASE_PORT=5432"
    echo "SUPABASE_DB=your-database"
    echo "SUPABASE_USER=your-user"
    echo "SUPABASE_PASSWORD=your-password"
    echo "OPENAI_API_KEY=your-openai-key"
    echo "ANTHROPIC_API_KEY=your-claude-key"
    exit 1
fi

# Load environment variables
source .env

# Check required variables
required_vars=("SUPABASE_HOST" "SUPABASE_DB" "SUPABASE_USER" "SUPABASE_PASSWORD" "OPENAI_API_KEY" "ANTHROPIC_API_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Missing required environment variable: $var"
        exit 1
    fi
done

echo "✅ Environment variables loaded"

# Create nginx configuration directory
mkdir -p nginx/conf.d
mkdir -p nginx/ssl

# Create nginx configuration
cat > nginx/conf.d/docs-assistant.conf << 'EOF'
server {
    listen 80;
    server_name localhost;

    # API proxy
    location /api/ {
        proxy_pass http://docs-assistant-api:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # CORS headers
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization,X-API-Key' always;
        add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range' always;

        if ($request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' '*';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
            add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization,X-API-Key';
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Content-Type' 'text/plain; charset=utf-8';
            add_header 'Content-Length' 0;
            return 204;
        }
    }

    # Widget static files
    location /docs-assistant/ {
        alias /var/www/html/docs-assistant/;
        add_header 'Access-Control-Allow-Origin' '*';
        add_header 'Cache-Control' 'public, max-age=3600';
    }

    # Health check
    location /health {
        proxy_pass http://docs-assistant-api:8000/health;
        proxy_set_header Host $host;
    }

    # Root redirect to API docs
    location / {
        return 302 /api/docs;
    }
}
EOF

echo "✅ Nginx configuration created"

# Build and start services
echo "📦 Building and starting Docker services..."
docker-compose up -d --build

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check API health
API_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/api/health || echo "000")

if [ "$API_HEALTH" = "200" ]; then
    echo "✅ Docs Assistant API is healthy"
else
    echo "❌ Docs Assistant API health check failed (HTTP $API_HEALTH)"
    echo "📋 Checking container logs..."
    docker-compose logs docs-assistant-api
    exit 1
fi

# Check widget accessibility
WIDGET_ACCESS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/docs-assistant/docs-widget.js || echo "000")

if [ "$WIDGET_ACCESS" = "200" ]; then
    echo "✅ Widget static files are accessible"
else
    echo "⚠️  Widget static files not accessible (HTTP $WIDGET_ACCESS)"
fi

echo ""
echo "🎉 Docs Assistant Deployment Complete!"
echo ""
echo "📊 Services Status:"
echo "   API: http://localhost/api/docs"
echo "   Widget: http://localhost/docs-assistant/docs-widget.js"
echo "   Health: http://localhost/api/health"
echo ""
echo "🔑 Next Steps:"
echo "   1. Apply database schema: psql \$DATABASE_URL -f ../supabase/schema.sql"
echo "   2. Create initial project and API key"
echo "   3. Configure widget on your documentation site"
echo ""
echo "📝 Example widget integration:"
echo '<script src="http://localhost/docs-assistant/docs-widget.js"'
echo '  data-api-url="http://localhost/api"'
echo '  data-api-key="your-api-key"'
echo '  data-project-slug="odoo-ce">'
echo '</script>'
