# LIB MCP Server - Local Intelligence Brain

Fast, deterministic filesystem metadata and content search for agent workflows.

## Features

- **SQLite-based storage** - Local-only, zero infrastructure
- **Auto-scan on startup** - Filesystem indexed automatically
- **Full-text search (FTS5)** - Search across file content
- **Multi-repository support** - Single database for multiple repos
- **Soft delete** - Preserve history of deleted files
- **WAL mode** - High-performance concurrent access

## Quick Start

### 1. Initialize Database

```bash
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo
chmod +x scripts/lib/lib_init.sh
./scripts/lib/lib_init.sh
```

### 2. Install Dependencies

```bash
cd mcp/servers/lib-mcp-server
pip install -r requirements.txt
```

### 3. Configure

Edit `.lib/lib.config.json`:

```json
{
  "scanner": {
    "scan_roots": ["/Users/tbwa/Documents/GitHub/Insightpulseai/odoo"],
    "auto_scan_on_startup": true
  }
}
```

Or set environment variables:

```bash
export LIB_SQLITE_PATH="./.lib/lib.db"
export LIB_SCAN_ROOTS="/Users/tbwa/Documents/GitHub/Insightpulseai/odoo"
export LIB_AUTO_SCAN_ON_STARTUP=true
```

### 4. Start Server

```bash
python -m uvicorn src.server:app --reload
```

Server starts on `http://localhost:8000`

## MCP Tools

### 1. `lib_search_files` - Search by metadata

```json
{
  "name": "lib_search_files",
  "arguments": {
    "ext": ".py",
    "limit": 50
  }
}
```

### 2. `lib_get_file_info` - Get file details

```json
{
  "name": "lib_get_file_info",
  "arguments": {
    "path": "/path/to/file.py"
  }
}
```

### 3. `lib_scan_directory` - Manual scan

```json
{
  "name": "lib_scan_directory",
  "arguments": {
    "path": "/path/to/directory"
  }
}
```

### 4. `lib_query_runs` - Scan history

```json
{
  "name": "lib_query_runs",
  "arguments": {
    "limit": 10
  }
}
```

### 5. `lib_fts_search` - Full-text search

```json
{
  "name": "lib_fts_search",
  "arguments": {
    "query": "def scan_repository",
    "limit": 50
  }
}
```

## HTTP Endpoints

### Health Check

```bash
curl http://localhost:8000/health
```

### Search Files

```bash
curl -X POST "http://localhost:8000/tools/lib_search_files" \
  -H "Content-Type: application/json" \
  -d '{"ext": ".py", "limit": 10}'
```

### FTS5 Search

```bash
curl -X POST "http://localhost:8000/tools/lib_fts_search" \
  -H "Content-Type: application/json" \
  -d '{"query": "def scan_repository", "limit": 10}'
```

## Performance

- **Scan speed**: 1,000 files in <5 seconds
- **Search latency**: <50ms for metadata search
- **FTS5 latency**: <100ms for content search
- **Database size**: ~50KB per file with content extraction

## Architecture

```
.lib/
├── lib.db                  # SQLite database (WAL mode)
├── lib.db-shm             # Shared memory (WAL)
├── lib.db-wal             # Write-ahead log
└── lib.config.json        # Configuration

scripts/lib/
├── lib_db.py              # Database layer
├── lib_scan.py            # Scanner
└── lib_init.sh            # Initialization

mcp/servers/lib-mcp-server/
├── src/
│   ├── server.py          # FastAPI server
│   ├── tools.py           # MCP tool definitions
│   └── config.py          # Configuration loader
└── requirements.txt
```

## Configuration

### Database Settings

- **Path**: `.lib/lib.db` (configurable)
- **Journal mode**: WAL
- **Synchronous**: NORMAL
- **Busy timeout**: 5000ms
- **Cache size**: 64MB

### Scanner Settings

- **Auto-scan**: Enabled by default
- **Content extraction**: First 50KB of text files
- **Supported extensions**: `.py`, `.js`, `.ts`, `.md`, `.txt`, `.json`, `.sql`, `.yaml`, `.yml`, `.sh`
- **Ignored paths**: `node_modules`, `__pycache__`, `.git`, `build`, `dist`, `.venv`, `.cache`, `.next`

### FTS5 Settings

- **Enabled**: Yes
- **Indexed fields**: `path`, `ext`, `mime`, `content`
- **Snippet length**: 32 words
- **Snippet markers**: `<mark>...</mark>`

## Troubleshooting

### Database locked

Ensure no other processes are holding the database. Check for stale locks:

```bash
rm .lib/lib.db-shm .lib/lib.db-wal
```

### Scan too slow

Reduce `scan_roots` or disable `content_extraction`:

```json
{
  "scanner": {
    "content_extraction": {
      "enabled": false
    }
  }
}
```

### FTS5 not working

Verify SQLite version supports FTS5:

```bash
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
```

Requires SQLite >= 3.9.0

## Development

### Run tests

```bash
pytest tests/
```

### Manual scan

```bash
cd scripts/lib
python3 lib_scan.py --scan-root /path/to/repo --db-path ../../.lib/lib.db --verbose
```

### Database inspection

```bash
sqlite3 .lib/lib.db ".schema lib_files"
sqlite3 .lib/lib.db "SELECT COUNT(*) FROM lib_files WHERE deleted_at IS NULL"
```

## License

MIT
