#!/bin/bash
# AFC RAG Deployment Script
# Automated deployment of AFC RAG integration to Odoo CE 18.0

set -e

echo "=========================================="
echo "AFC RAG Deployment - Odoo CE 18.0"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check prerequisites
echo "Step 1: Checking prerequisites..."
echo ""

# Check psycopg2
if python3 -c "import psycopg2" 2>/dev/null; then
    echo -e "${GREEN}✅ psycopg2-binary installed${NC}"
else
    echo -e "${YELLOW}⚠️  psycopg2-binary not found. Installing...${NC}"
    pip install psycopg2-binary
    echo -e "${GREEN}✅ psycopg2-binary installed${NC}"
fi

# Check environment variables
if [ -z "$POSTGRES_PASSWORD" ]; then
    echo -e "${RED}❌ POSTGRES_PASSWORD not set${NC}"
    echo "   Set environment variable: export POSTGRES_PASSWORD=..."
    exit 1
else
    echo -e "${GREEN}✅ POSTGRES_PASSWORD set${NC}"
fi

# Check Docker
if docker ps > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Docker is running${NC}"
else
    echo -e "${YELLOW}⚠️  Docker is not running${NC}"
    echo "   Start Docker/Colima: colima start"
    echo ""
    echo "Alternative: Manual deployment via Odoo UI"
    echo "  1. Copy addons/ipai_ask_ai to your Odoo addons path"
    echo "  2. Restart Odoo"
    echo "  3. Apps → Update Apps List"
    echo "  4. Search 'IPAI Ask AI' → Install"
    exit 1
fi

# Step 2: Start Odoo stack
echo ""
echo "Step 2: Starting Odoo Docker stack..."
echo ""

docker compose up -d

# Wait for Odoo to be ready
echo "Waiting for Odoo to start (30 seconds)..."
sleep 30

# Check if Odoo is running
if docker compose ps | grep -q "web.*running"; then
    echo -e "${GREEN}✅ Odoo is running${NC}"
else
    echo -e "${RED}❌ Odoo failed to start${NC}"
    docker compose logs web | tail -50
    exit 1
fi

# Step 3: Install/Upgrade module
echo ""
echo "Step 3: Installing/Upgrading ipai_ask_ai module..."
echo ""

docker compose exec -T web odoo -d production -u ipai_ask_ai --stop-after-init

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Module upgraded successfully${NC}"
else
    echo -e "${RED}❌ Module upgrade failed${NC}"
    echo "Check Odoo logs: docker compose logs web | tail -100"
    exit 1
fi

# Step 4: Restart Odoo
echo ""
echo "Step 4: Restarting Odoo..."
echo ""

docker compose restart web

echo "Waiting for Odoo to restart (20 seconds)..."
sleep 20

# Step 5: Configure System Parameters
echo ""
echo "Step 5: Configuring System Parameters..."
echo ""

echo -e "${YELLOW}⚠️  Manual configuration required:${NC}"
echo ""
echo "1. Open Odoo: http://localhost:8069"
echo "2. Login with your admin credentials"
echo "3. Navigate to: Settings → Technical → Parameters → System Parameters"
echo "4. Update the following parameters:"
echo ""
echo "   afc.supabase.db_password = [from \$POSTGRES_PASSWORD]"
echo "   openai.api_key = [optional, for actual embeddings]"
echo ""
echo "5. Save changes"
echo ""

# Step 6: Test AFC RAG service
echo ""
echo "Step 6: Testing AFC RAG service..."
echo ""

python3 scripts/test_afc_rag.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ AFC RAG service tests passed${NC}"
else
    echo -e "${YELLOW}⚠️  Some tests failed (expected if knowledge base is empty)${NC}"
fi

# Step 7: Verify module in Odoo
echo ""
echo "Step 7: Verifying module installation..."
echo ""

# Check if module is installed via Odoo xmlrpc
cat > /tmp/check_module.py << 'EOF'
#!/usr/bin/env python3
import xmlrpc.client
import os

url = os.getenv("ODOO_URL", "http://localhost:8069")
db = os.getenv("ODOO_DB", "production")
username = os.getenv("ODOO_USERNAME", "admin")
password = os.getenv("ODOO_PASSWORD", "admin")

common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})

if uid:
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    module = models.execute_kw(db, uid, password,
        'ir.module.module', 'search_read',
        [[('name', '=', 'ipai_ask_ai')]],
        {'fields': ['name', 'state']})

    if module and module[0]['state'] == 'installed':
        print("✅ ipai_ask_ai module is installed")
        exit(0)
    else:
        print("❌ ipai_ask_ai module not installed or not active")
        exit(1)
else:
    print("❌ Failed to authenticate with Odoo")
    exit(1)
EOF

python3 /tmp/check_module.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Module verification successful${NC}"
else
    echo -e "${YELLOW}⚠️  Module verification failed (check Odoo credentials)${NC}"
fi

# Final summary
echo ""
echo "=========================================="
echo "Deployment Summary"
echo "=========================================="
echo ""
echo -e "${GREEN}✅ Prerequisites checked${NC}"
echo -e "${GREEN}✅ Odoo stack started${NC}"
echo -e "${GREEN}✅ Module upgraded${NC}"
echo -e "${YELLOW}⚠️  System Parameters require manual configuration${NC}"
echo -e "${GREEN}✅ Tests executed${NC}"
echo ""
echo "Next Steps:"
echo "1. Configure System Parameters (see Step 5 above)"
echo "2. Test AI Assistant widget in Odoo UI"
echo "3. Submit test query: 'What is the BIR 1601-C filing deadline?'"
echo "4. Verify AFC query routing and response format"
echo ""
echo "Documentation:"
echo "  - README_AFC_RAG.md - Comprehensive deployment guide"
echo "  - DEPLOYMENT_STATUS.md - Current deployment status"
echo "  - CHANGES.md - Complete change summary"
echo ""
echo "Support:"
echo "  - Test suite: python3 scripts/test_afc_rag.py"
echo "  - Setup validation: ./scripts/setup_afc_rag.sh"
echo "  - Odoo logs: docker compose logs web -f"
echo ""
