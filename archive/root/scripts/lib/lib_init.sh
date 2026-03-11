#!/bin/bash
set -e

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
LIB_DIR="$REPO_ROOT/.lib"
LIB_DB="$LIB_DIR/lib.db"

echo "Initializing LIB (Local Intelligence Brain)..."

# Create .lib directory
mkdir -p "$LIB_DIR"

# Initialize database schema
python3 "$REPO_ROOT/scripts/lib/lib_db.py" init --db-path "$LIB_DB"

# Create default config
cat > "$LIB_DIR/lib.config.json" <<EOF
{
  "version": "1.0.0",
  "database": {
    "path": "./.lib/lib.db",
    "wal_mode": true,
    "synchronous": "NORMAL",
    "busy_timeout_ms": 5000
  },
  "scanner": {
    "scan_roots": ["$REPO_ROOT"],
    "auto_scan_on_startup": true,
    "content_extraction": {
      "enabled": true,
      "max_size_kb": 50,
      "extensions": [".py", ".js", ".ts", ".md", ".txt", ".json", ".sql", ".yaml", ".yml", ".sh"]
    }
  },
  "fts5": {
    "enabled": true
  }
}
EOF

# Add to .gitignore if not already present
if ! grep -q "^.lib/" "$REPO_ROOT/.gitignore" 2>/dev/null; then
    echo -e "\n# LIB (Local Intelligence Brain)\n.lib/" >> "$REPO_ROOT/.gitignore"
fi

echo "✅ LIB initialized at $LIB_DIR"
echo "   Database: $LIB_DB"
echo "   Config: $LIB_DIR/lib.config.json"
echo ""
echo "Next steps:"
echo "   1. Test scanner: cd scripts/lib && python3 lib_scan.py --scan-root $REPO_ROOT/addons --db-path $LIB_DB --verbose"
echo "   2. Setup MCP server: cd mcp/servers/lib-mcp-server && python -m uvicorn src.server:app"
