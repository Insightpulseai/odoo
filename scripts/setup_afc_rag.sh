#!/bin/bash
# AFC RAG Setup Script
# Configures Supabase connection and OpenAI API for AFC RAG service

set -e

echo "🔧 AFC RAG Service Configuration"
echo "=================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."

# Check if psycopg2 is installed
if ! python3 -c "import psycopg2" 2>/dev/null; then
    echo "⚠️  psycopg2 not found. Installing..."
    pip install psycopg2-binary
    echo "✅ psycopg2-binary installed"
else
    echo "✅ psycopg2 already installed"
fi

# Check environment variables
echo ""
echo "Checking environment variables..."

if [ -z "$POSTGRES_HOST" ]; then
    echo "⚠️  POSTGRES_HOST not set"
    echo "   Expected: db.spdtwktxdalcfigzeqrz.supabase.co"
else
    echo "✅ POSTGRES_HOST: ${POSTGRES_HOST:0:30}..."
fi

if [ -z "$POSTGRES_PASSWORD" ]; then
    echo "⚠️  POSTGRES_PASSWORD not set"
else
    echo "✅ POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:0:10}***"
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set (optional)"
else
    echo "✅ OPENAI_API_KEY: ${OPENAI_API_KEY:0:10}***"
fi

# Test Supabase connection
echo ""
echo "Testing Supabase connection..."

if psql "$POSTGRES_URL_NON_POOLING" -c "SELECT COUNT(*) FROM afc.document_chunks;" > /dev/null 2>&1; then
    CHUNK_COUNT=$(psql "$POSTGRES_URL_NON_POOLING" -t -c "SELECT COUNT(*) FROM afc.document_chunks;")
    echo "✅ Supabase connection successful"
    echo "   Document chunks: $CHUNK_COUNT"
else
    echo "❌ Supabase connection failed"
    echo "   Check your POSTGRES_URL_NON_POOLING environment variable"
    exit 1
fi

# Test embeddings table
echo ""
echo "Testing embeddings table..."

if psql "$POSTGRES_URL_NON_POOLING" -c "SELECT COUNT(*) FROM afc.chunk_embeddings;" > /dev/null 2>&1; then
    EMBEDDING_COUNT=$(psql "$POSTGRES_URL_NON_POOLING" -t -c "SELECT COUNT(*) FROM afc.chunk_embeddings;")
    echo "✅ Embeddings table accessible"
    echo "   Embeddings: $EMBEDDING_COUNT"
else
    echo "❌ Embeddings table not found"
    exit 1
fi

# Summary
echo ""
echo "=================================="
echo "Configuration Summary"
echo "=================================="
echo ""
echo "Database:"
echo "  Host: $POSTGRES_HOST"
echo "  Database: postgres"
echo "  Port: 5432"
echo "  Chunks: $CHUNK_COUNT"
echo "  Embeddings: $EMBEDDING_COUNT"
echo ""

if [ -n "$OPENAI_API_KEY" ]; then
    echo "OpenAI API: ✅ Configured"
    echo "  Model: text-embedding-3-large"
else
    echo "OpenAI API: ⚠️  Not configured (using placeholder embeddings)"
fi

echo ""
echo "=================================="
echo "Next Steps"
echo "=================================="
echo ""
echo "1. Start Odoo:"
echo "   docker compose up -d"
echo ""
echo "2. Install/Upgrade module:"
echo "   docker compose exec web odoo -d production -u ipai_ask_ai --stop-after-init"
echo ""
echo "3. Update System Parameters (if not using env vars):"
echo "   Settings → Technical → Parameters → System Parameters"
echo "   - afc.supabase.db_password = [from POSTGRES_PASSWORD]"
echo "   - openai.api_key = [from OPENAI_API_KEY]"
echo ""
echo "4. Test AFC RAG service:"
echo "   python3 scripts/test_afc_rag.py"
echo ""
