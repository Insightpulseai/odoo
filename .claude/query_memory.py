#!/usr/bin/env python3
"""Query project memory from SQLite database.

Usage:
    python .claude/query_memory.py config          # Show all config
    python .claude/query_memory.py config supabase # Filter by category
    python .claude/query_memory.py arch            # Show architecture
    python .claude/query_memory.py commands        # Show commands
    python .claude/query_memory.py deprecated      # Show deprecated items
    python .claude/query_memory.py rules           # Show rules
    python .claude/query_memory.py all             # Show everything
"""

import sqlite3
import sys
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'project_memory.db')

def query(table: str, category: str = None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if table == 'config':
        if category:
            c.execute('SELECT * FROM config WHERE category = ?', (category,))
        else:
            c.execute('SELECT * FROM config ORDER BY category')
        for row in c.fetchall():
            print(f"{row['key']}={row['value']}  # {row['description']}")

    elif table == 'arch':
        c.execute('SELECT * FROM architecture ORDER BY type')
        for row in c.fetchall():
            port = f":{row['port']}" if row['port'] else ""
            deps = f" -> {row['dependencies']}" if row['dependencies'] else ""
            print(f"{row['component']}{port} ({row['type']}): {row['description']}{deps}")

    elif table == 'commands':
        c.execute('SELECT * FROM commands ORDER BY category')
        for row in c.fetchall():
            print(f"[{row['category']}] {row['name']}: {row['command']}")

    elif table == 'deprecated':
        c.execute('SELECT * FROM deprecated')
        for row in c.fetchall():
            print(f"❌ {row['id']} ({row['type']}): {row['reason']}")

    elif table == 'rules':
        c.execute('SELECT * FROM rules ORDER BY category, id')
        for row in c.fetchall():
            print(f"[{row['category']}] {row['rule']}")

    elif table == 'all':
        print("=== CONFIG ===")
        query('config')
        print("\n=== ARCHITECTURE ===")
        query('arch')
        print("\n=== COMMANDS ===")
        query('commands')
        print("\n=== DEPRECATED ===")
        query('deprecated')
        print("\n=== RULES ===")
        query('rules')

    conn.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    table = sys.argv[1]
    category = sys.argv[2] if len(sys.argv) > 2 else None
    query(table, category)
