# Docs Assistant - Quick Deployment Guide

## 🚀 Quick Start (5 minutes)

### 1. Prerequisites
- Docker and Docker Compose installed
- Supabase PostgreSQL database (or any PostgreSQL with pgvector)
- OpenAI API key (for embeddings)
- Anthropic API key (for Claude answers)

### 2. Setup Environment
```bash
# Navigate to deployment directory
cd docs-assistant/deploy

# Copy environment template
cp .env.example .env

# Edit .env with your values
nano .env
```

### 3. Deploy Services
```bash
# Run deployment script
./deploy.sh
```

### 4. Setup Database
```bash
# Set DATABASE_URL (replace with your actual connection string)
export DATABASE_URL="postgresql://user:password@host:port/database"

# Setup database schema and create initial project
./setup-database.sh
```

### 5. Test Deployment
- **API Docs**: http://localhost/api/docs
- **Health Check**: http://localhost/api/health
- **Widget**: http://localhost/docs-assistant/docs-widget.js

## 📋 Detailed Deployment Steps

### Step 1: Environment Configuration
Create `.env` file in `docs-assistant/deploy/`:

```env
# Database Configuration
SUPABASE_HOST=db.your-project.supabase.co
SUPABASE_PORT=5432
SUPABASE_DB=postgres
SUPABASE_USER=postgres
SUPABASE_PASSWORD=your-password

# LLM API Keys
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=your-claude-key
```

### Step 2: Database Setup
Ensure your PostgreSQL database has pgvector extension:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Step 3: Deploy Services
```bash
cd docs-assistant/deploy
./deploy.sh
```

### Step 4: Initialize Database
```bash
export DATABASE_URL="postgresql://user:password@host:port/database"
./setup-database.sh
```

**Save the API key** displayed - you'll need it for widget configuration.

## 🔧 Integration

### Web Widget Integration
Add to your documentation site:
```html
<script
  src="http://localhost/docs-assistant/docs-widget.js"
  data-api-url="http://localhost/api"
  data-api-key="YOUR_API_KEY_FROM_SETUP"
  data-project-slug="odoo-ce"
  data-position="bottom-right"
  data-theme="light">
</script>
```

### MCP Integration (Claude Code)
Add to your Claude Code configuration:
```json
{
  "mcpServers": {
    "docs-assistant": {
      "command": "python",
      "args": ["/path/to/docs-assistant/mcp/docs_assistant.py"],
      "env": {
        "DOCS_ASSISTANT_API_URL": "http://localhost/api",
        "DOCS_ASSISTANT_API_KEY": "YOUR_API_KEY",
        "DOCS_ASSISTANT_PROJECT": "odoo-ce"
      }
    }
  }
}
```

### API Usage
```bash
# Test API
curl -X POST "http://localhost/api/v1/chat" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "project_slug": "odoo-ce",
    "question": "How do I create a new Odoo module?"
  }'
```

## 🛠️ Management Commands

### View Logs
```bash
cd docs-assistant/deploy
docker-compose logs -f docs-assistant-api
```

### Restart Services
```bash
cd docs-assistant/deploy
docker-compose restart
```

### Stop Services
```bash
cd docs-assistant/deploy
docker-compose down
```

### Update Services
```bash
cd docs-assistant/deploy
docker-compose pull
docker-compose up -d
```

## 🔍 Troubleshooting

### Common Issues

1. **API Health Check Fails**
   - Check database connection in `.env`
   - Verify OpenAI/Anthropic API keys
   - Check logs: `docker-compose logs docs-assistant-api`

2. **Widget Not Loading**
   - Verify widget URL: http://localhost/docs-assistant/docs-widget.js
   - Check API URL in widget configuration
   - Verify API key is correct

3. **Database Connection Issues**
   - Verify DATABASE_URL or individual connection parameters
   - Check if pgvector extension is installed
   - Ensure database user has proper permissions

4. **MCP Tool Not Working**
   - Check environment variables in MCP configuration
   - Verify API is accessible from MCP server
   - Check MCP server logs

### Health Checks
```bash
# API health
curl http://localhost/api/health

# Widget accessibility
curl -I http://localhost/docs-assistant/docs-widget.js

# Database connection (from API container)
docker-compose exec docs-assistant-api python -c "
import psycopg2
import os
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
print('✅ Database connection successful')
"
```

## 📈 Next Steps After Deployment

### 1. Add Documentation Sources
Use the API to add documentation sources:
```bash
# Example: Add GitHub source
curl -X POST "http://localhost/api/v1/ingest/github" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "project_slug": "odoo-ce",
    "repo": "jgtolentino/odoo-ce",
    "branch": "main",
    "paths": ["docs/", "README.md"]
  }'
```

### 2. Configure Analytics
Monitor usage through the database:
```sql
-- Top questions
SELECT query, COUNT(*) as frequency
FROM docs_questions
GROUP BY query
ORDER BY frequency DESC
LIMIT 10;

-- Answer quality
SELECT AVG(rating) as avg_rating, COUNT(*) as total_feedback
FROM docs_feedback;
```

### 3. Set Up Monitoring
- Monitor API response times
- Track widget usage analytics
- Set up alerts for service health

## 🎯 Production Deployment

For production deployment:
1. Use HTTPS with proper SSL certificates
2. Set up domain name (docs-api.yourdomain.com)
3. Configure proper firewall rules
4. Set up backup strategy for database
5. Configure monitoring and alerting
6. Implement rate limiting
7. Set up log aggregation

## 📞 Support

- **Documentation**: See `KAPA_STYLE_DOCS_ASSISTANT_IMPLEMENTATION.md`
- **Issues**: Check container logs with `docker-compose logs`
- **API Reference**: http://localhost/api/docs (after deployment)

---

**Deployment Status**: ✅ Ready
**Last Updated**: $(date)
