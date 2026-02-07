# External Memory (Just-in-Time Retrieval)
> Extracted from root CLAUDE.md. See [CLAUDE.md](../../CLAUDE.md) for authoritative rules.

---

Project configuration is stored in SQLite to reduce context usage:

```bash
python .claude/query_memory.py config       # Supabase/DB config
python .claude/query_memory.py arch         # Architecture components
python .claude/query_memory.py commands     # All commands
python .claude/query_memory.py rules        # Project rules
python .claude/query_memory.py deprecated   # Deprecated items
python .claude/query_memory.py all          # Everything
```
