# LIB MCP Server - Claude Code Configuration

Complete setup guide for integrating LIB (Local Intelligence Brain) with Claude Code.

## Installation

### 1. Initialize LIB Database

```bash
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo
chmod +x scripts/lib/lib_init.sh
./scripts/lib/lib_init.sh
```

**Expected Output:**
```
✅ LIB database initialized at .lib/lib.db
   Schema: lib_files, lib_runs, lib_files_fts
   6 indexes created
   FTS5 triggers active
   WAL mode enabled
```

### 2. Install Python Dependencies

```bash
cd mcp/servers/lib-mcp-server
pip install -r requirements.txt
```

**Dependencies:**
- `fastapi`
- `uvicorn[standard]`
- `aiosqlite`
- `pydantic`
- `pydantic-settings`

### 3. Configure Environment Variables

**Option A: Environment variables** (`.env` file in `mcp/servers/lib-mcp-server/`):

```bash
LIB_SQLITE_PATH=../../../.lib/lib.db
LIB_SCAN_ROOTS=["/Users/tbwa/Documents/GitHub/Insightpulseai/odoo"]
LIB_AUTO_SCAN_ON_STARTUP=true
LIB_FTS5_ENABLED=true
LIB_HOST=localhost
LIB_PORT=8765
LIB_LOG_LEVEL=info
```

**Option B: Configuration file** (`.lib/lib.config.json`):

```json
{
  "database": {
    "path": ".lib/lib.db",
    "journal_mode": "WAL",
    "synchronous": "NORMAL",
    "cache_size_mb": 64
  },
  "scanner": {
    "scan_roots": ["/Users/tbwa/Documents/GitHub/Insightpulseai/odoo"],
    "auto_scan_on_startup": true,
    "ignore_patterns": [
      "node_modules",
      "__pycache__",
      ".git",
      "build",
      "dist",
      ".venv"
    ],
    "content_extraction": {
      "enabled": true,
      "max_size_kb": 50,
      "text_extensions": [
        ".py",
        ".js",
        ".ts",
        ".md",
        ".txt",
        ".json",
        ".yaml",
        ".sql",
        ".sh"
      ]
    }
  },
  "fts5": {
    "enabled": true,
    "snippet_length": 32
  },
  "server": {
    "host": "localhost",
    "port": 8765,
    "log_level": "info"
  }
}
```

### 4. Start MCP Server

```bash
cd mcp/servers/lib-mcp-server
python -m uvicorn src.server:app --host localhost --port 8765 --reload
```

**Expected Output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Initializing LIB database at ../../../.lib/lib.db
INFO:     Starting auto-scan on startup...
INFO:     Auto-scan completed: {'scanned': 1234, 'new': 1234, 'updated': 0, 'deleted': 0}
INFO:     Application startup complete.
INFO:     Uvicorn running on http://localhost:8765
```

### 5. Verify MCP Server

```bash
# Health check
curl http://localhost:8765/health

# List available tools
curl http://localhost:8765/tools/list

# Test metadata search
curl -X POST "http://localhost:8765/tools/lib_search_files" \
  -H "Content-Type: application/json" \
  -d '{"ext": ".py", "limit": 10}'

# Test FTS5 search
curl -X POST "http://localhost:8765/tools/lib_fts_search" \
  -H "Content-Type: application/json" \
  -d '{"query": "def scan_repository", "limit": 10}'
```

## Claude Code MCP Configuration

### Add to `~/.claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "lib": {
      "url": "http://localhost:8765",
      "type": "sse",
      "description": "Local Intelligence Brain - Filesystem metadata and content search",
      "enabled": true
    }
  }
}
```

**Alternative: Direct command launch** (if using stdio transport):

```json
{
  "mcpServers": {
    "lib": {
      "command": "python",
      "args": [
        "-m",
        "uvicorn",
        "src.server:app",
        "--host",
        "localhost",
        "--port",
        "8765"
      ],
      "cwd": "/Users/tbwa/Documents/GitHub/Insightpulseai/odoo/mcp/servers/lib-mcp-server",
      "env": {
        "LIB_SQLITE_PATH": "../../../.lib/lib.db",
        "LIB_AUTO_SCAN_ON_STARTUP": "true"
      }
    }
  }
}
```

## Sample Prompts for Claude Code

### 1. Find Python Files

**Prompt:**
```
Use the lib_search_files tool to find all Python files in the repository.
```

**Expected Response:**
Claude Code will call:
```json
{
  "name": "lib_search_files",
  "arguments": {
    "ext": ".py",
    "limit": 1000
  }
}
```

### 2. Search for Specific Function

**Prompt:**
```
Use lib_fts_search to find all files containing the function "scan_repository".
```

**Expected Response:**
Claude Code will call:
```json
{
  "name": "lib_fts_search",
  "arguments": {
    "query": "def scan_repository",
    "limit": 50
  }
}
```

### 3. Get File Details

**Prompt:**
```
Use lib_get_file_info to get metadata for scripts/lib/lib_scan.py
```

**Expected Response:**
Claude Code will call:
```json
{
  "name": "lib_get_file_info",
  "arguments": {
    "path": "scripts/lib/lib_scan.py"
  }
}
```

### 4. Scan New Directory

**Prompt:**
```
Use lib_scan_directory to index the addons/ipai/ directory.
```

**Expected Response:**
Claude Code will call:
```json
{
  "name": "lib_scan_directory",
  "arguments": {
    "path": "addons/ipai/"
  }
}
```

### 5. View Scan History

**Prompt:**
```
Use lib_query_runs to show the last 5 scan operations.
```

**Expected Response:**
Claude Code will call:
```json
{
  "name": "lib_query_runs",
  "arguments": {
    "limit": 5
  }
}
```

## Advanced Usage Patterns

### Compound Queries

**Prompt:**
```
Find all Python files in the addons/ directory that contain "odoo" in their content.
```

**Workflow:**
1. Claude Code calls `lib_search_files` with `query="addons/"` and `ext=".py"`
2. For files with content, calls `lib_fts_search` with `query="odoo"`
3. Returns intersection of results

### Performance Analysis

**Prompt:**
```
Analyze the repository structure: How many files of each type? What's the total size?
```

**Workflow:**
1. Claude Code calls `lib_search_files` multiple times with different `ext` filters
2. Aggregates results by extension
3. Presents summary statistics

### Content Discovery

**Prompt:**
```
Find all files that import "aiosqlite" and show code snippets.
```

**Workflow:**
1. Claude Code calls `lib_fts_search` with `query="import aiosqlite"`
2. Returns files with highlighted snippets using `<mark>` tags
3. Presents formatted results with file paths and line context

## Troubleshooting

### Server Won't Start

**Issue:** Port already in use

**Solution:**
```bash
# Find process using port 8765
lsof -i :8765

# Kill process
kill -9 <PID>

# Or use different port
export LIB_PORT=8766
python -m uvicorn src.server:app --port 8766
```

### Auto-Scan Fails

**Issue:** Scan roots not accessible

**Solution:**
```bash
# Verify scan roots exist
ls -la /Users/tbwa/Documents/GitHub/Insightpulseai/odoo

# Update configuration with valid paths
export LIB_SCAN_ROOTS='["/path/to/valid/directory"]'
```

### FTS5 Not Working

**Issue:** SQLite version too old

**Solution:**
```bash
# Check SQLite version (requires >= 3.9.0)
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"

# Upgrade SQLite if needed (macOS)
brew upgrade sqlite

# Verify FTS5 enabled
sqlite3 .lib/lib.db "SELECT * FROM pragma_compile_options WHERE compile_options LIKE '%FTS5%';"
```

### Database Locked

**Issue:** Another process holding database lock

**Solution:**
```bash
# Check for stale locks
rm .lib/lib.db-shm .lib/lib.db-wal

# Verify WAL mode
sqlite3 .lib/lib.db "PRAGMA journal_mode;"
# Should return: wal
```

## Performance Tuning

### Optimize Scan Performance

```bash
# Reduce content extraction size
export LIB_CONTENT_MAX_SIZE_KB=25

# Disable content extraction entirely (faster, no FTS5)
export LIB_CONTENT_EXTRACTION_ENABLED=false

# Increase ignore patterns
# Edit .lib/lib.config.json and add to ignore_patterns
```

### Optimize Search Performance

```bash
# Increase SQLite cache size
# Edit .lib/lib.config.json:
{
  "database": {
    "cache_size_mb": 128  # Default: 64
  }
}
```

### Monitor Performance

```bash
# Run benchmark script
python3 scripts/lib/lib_benchmark.py \
  --db-path .lib/bench.db \
  --scan-root /Users/tbwa/Documents/GitHub/Insightpulseai/odoo

# Check database size
du -h .lib/lib.db

# Count indexed files
sqlite3 .lib/lib.db "SELECT COUNT(*) FROM lib_files WHERE deleted_at IS NULL;"

# Check FTS5 index size
sqlite3 .lib/lib.db "SELECT COUNT(*) FROM lib_files_fts;"
```

## Next Steps

1. **Baseline Performance:** Run `lib_benchmark.py` to establish performance baseline
2. **MCP Integration:** Add LIB server to Claude Code MCP configuration
3. **Test Prompts:** Try sample prompts to verify integration
4. **Custom Workflows:** Create domain-specific prompts for your codebase
5. **Monitor Usage:** Track scan frequency and search patterns

## Resources

- **Documentation:** `mcp/servers/lib-mcp-server/README.md`
- **Implementation Plan:** `docs/ai/LIB_IMPLEMENTATION.md`
- **Database Schema:** `scripts/lib/lib_db.py` (lines 28-93)
- **Scanner Logic:** `scripts/lib/lib_scan.py`
- **MCP Tools:** `mcp/servers/lib-mcp-server/src/tools.py`

---

**Status:** LIB v1.0 Complete | Ready for Claude Code MCP Integration
