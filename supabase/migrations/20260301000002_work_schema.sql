-- =============================================================================
-- Migration: work.* schema — Notion-like System of Work (SoW)
-- Owner: Supabase (SSOT for workspace knowledge + collaboration)
-- Boundary: SoW can READ from ops.* and via curated views from Odoo
--           SoW must NEVER write to Odoo SoR directly
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS work;

-- Extension: full-text search + vectors
CREATE EXTENSION IF NOT EXISTS pg_trgm;    -- trigram similarity
CREATE EXTENSION IF NOT EXISTS vector;     -- pgvector (embeddings, optional)

-- =============================================================================
-- Enum types
-- =============================================================================

DO $$ BEGIN
  CREATE TYPE work.block_type AS ENUM (
    'paragraph', 'heading_1', 'heading_2', 'heading_3',
    'bullet_list_item', 'numbered_list_item', 'toggle',
    'code', 'quote', 'callout', 'divider',
    'image', 'file', 'embed',
    'table', 'table_row',
    'odoo_embed', 'chart_embed', 'artifact_embed'
  );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  CREATE TYPE work.page_status AS ENUM ('draft', 'published', 'archived');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  CREATE TYPE work.col_type AS ENUM (
    'text', 'number', 'boolean', 'date', 'datetime',
    'select', 'multi_select', 'url', 'email', 'phone',
    'relation', 'rollup', 'formula'
  );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  CREATE TYPE work.permission_level AS ENUM ('viewer', 'commenter', 'editor', 'admin');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- =============================================================================
-- work.spaces — Top-level workspaces (like Notion workspaces / Confluence spaces)
-- =============================================================================
CREATE TABLE IF NOT EXISTS work.spaces (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  slug         text NOT NULL UNIQUE,
  name         text NOT NULL,
  description  text,
  icon         text,                         -- emoji or icon URL
  created_by   uuid REFERENCES auth.users(id),
  created_at   timestamptz DEFAULT now(),
  updated_at   timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_spaces_slug ON work.spaces (slug);

-- =============================================================================
-- work.pages — Wiki pages, docs, runbooks, specs
-- =============================================================================
CREATE TABLE IF NOT EXISTS work.pages (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  space_id     uuid REFERENCES work.spaces(id) ON DELETE CASCADE,
  parent_id    uuid REFERENCES work.pages(id),  -- nested pages
  title        text NOT NULL,
  icon         text,
  cover_url    text,
  status       work.page_status NOT NULL DEFAULT 'draft',
  sort_order   integer NOT NULL DEFAULT 0,

  -- Full-text search (auto-maintained by trigger)
  search_vec   tsvector GENERATED ALWAYS AS (
    to_tsvector('english', coalesce(title, ''))
  ) STORED,

  created_by   uuid REFERENCES auth.users(id),
  updated_by   uuid REFERENCES auth.users(id),
  created_at   timestamptz DEFAULT now(),
  updated_at   timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_pages_space    ON work.pages (space_id);
CREATE INDEX IF NOT EXISTS idx_pages_parent   ON work.pages (parent_id);
CREATE INDEX IF NOT EXISTS idx_pages_status   ON work.pages (status);
CREATE INDEX IF NOT EXISTS idx_pages_search   ON work.pages USING GIN (search_vec);
CREATE INDEX IF NOT EXISTS idx_pages_updated  ON work.pages (updated_at DESC);

-- =============================================================================
-- work.blocks — Block-based content (mirrors Notion's block model)
-- =============================================================================
CREATE TABLE IF NOT EXISTS work.blocks (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  page_id      uuid REFERENCES work.pages(id) ON DELETE CASCADE,
  parent_id    uuid REFERENCES work.blocks(id),  -- nested blocks
  type         work.block_type NOT NULL DEFAULT 'paragraph',
  content      jsonb NOT NULL DEFAULT '{}',      -- {text, checked, url, language, ...}
  sort_order   integer NOT NULL DEFAULT 0,

  -- Full-text search
  search_vec   tsvector GENERATED ALWAYS AS (
    to_tsvector('english', coalesce(content->>'text', ''))
  ) STORED,

  created_by   uuid REFERENCES auth.users(id),
  created_at   timestamptz DEFAULT now(),
  updated_at   timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_blocks_page    ON work.blocks (page_id, sort_order);
CREATE INDEX IF NOT EXISTS idx_blocks_parent  ON work.blocks (parent_id);
CREATE INDEX IF NOT EXISTS idx_blocks_search  ON work.blocks USING GIN (search_vec);

-- =============================================================================
-- work.databases — Structured knowledge tables (Notion database equivalent)
-- =============================================================================
CREATE TABLE IF NOT EXISTS work.databases (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  space_id     uuid REFERENCES work.spaces(id) ON DELETE CASCADE,
  page_id      uuid REFERENCES work.pages(id),   -- embedding page (optional)
  name         text NOT NULL,
  description  text,
  icon         text,
  created_by   uuid REFERENCES auth.users(id),
  created_at   timestamptz DEFAULT now(),
  updated_at   timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_databases_space ON work.databases (space_id);

-- =============================================================================
-- work.db_columns — Column schema for databases
-- =============================================================================
CREATE TABLE IF NOT EXISTS work.db_columns (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  database_id  uuid REFERENCES work.databases(id) ON DELETE CASCADE,
  name         text NOT NULL,
  type         work.col_type NOT NULL DEFAULT 'text',
  options      jsonb DEFAULT '{}',               -- select options, relation config, formula, etc.
  sort_order   integer NOT NULL DEFAULT 0,
  is_primary   boolean NOT NULL DEFAULT false,   -- the "title" column
  created_at   timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_db_columns_db ON work.db_columns (database_id, sort_order);

-- =============================================================================
-- work.db_rows — Rows in a database
-- =============================================================================
CREATE TABLE IF NOT EXISTS work.db_rows (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  database_id  uuid REFERENCES work.databases(id) ON DELETE CASCADE,
  page_id      uuid REFERENCES work.pages(id),   -- linked page (row as page)
  data         jsonb NOT NULL DEFAULT '{}',       -- { column_id: value }
  sort_order   integer NOT NULL DEFAULT 0,

  -- Full-text on all text values (trigger-maintained)
  search_vec   tsvector,

  created_by   uuid REFERENCES auth.users(id),
  created_at   timestamptz DEFAULT now(),
  updated_at   timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_db_rows_db      ON work.db_rows (database_id, sort_order);
CREATE INDEX IF NOT EXISTS idx_db_rows_search  ON work.db_rows USING GIN (search_vec);

-- Trigger: maintain search_vec for db_rows
CREATE OR REPLACE FUNCTION work.update_row_search_vec()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  NEW.search_vec := to_tsvector('english',
    coalesce(array_to_string(ARRAY(
      SELECT value::text FROM jsonb_each_text(NEW.data)
    ), ' '), ''));
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_row_search ON work.db_rows;
CREATE TRIGGER trg_row_search
  BEFORE INSERT OR UPDATE ON work.db_rows
  FOR EACH ROW EXECUTE FUNCTION work.update_row_search_vec();

-- =============================================================================
-- work.relations — Page ↔ page and row ↔ row links
-- =============================================================================
CREATE TABLE IF NOT EXISTS work.relations (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  src_type     text NOT NULL,                    -- 'page' | 'db_row'
  src_id       uuid NOT NULL,
  dst_type     text NOT NULL,
  dst_id       uuid NOT NULL,
  rel_type     text NOT NULL DEFAULT 'reference', -- 'reference' | 'child' | 'related'
  created_by   uuid REFERENCES auth.users(id),
  created_at   timestamptz DEFAULT now(),
  UNIQUE (src_type, src_id, dst_type, dst_id, rel_type)
);

CREATE INDEX IF NOT EXISTS idx_relations_src ON work.relations (src_type, src_id);
CREATE INDEX IF NOT EXISTS idx_relations_dst ON work.relations (dst_type, dst_id);

-- =============================================================================
-- work.comments — Inline and block-level comments
-- =============================================================================
CREATE TABLE IF NOT EXISTS work.comments (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  page_id      uuid REFERENCES work.pages(id) ON DELETE CASCADE,
  block_id     uuid REFERENCES work.blocks(id) ON DELETE CASCADE,
  parent_id    uuid REFERENCES work.comments(id), -- threaded replies
  body         text NOT NULL,
  resolved     boolean NOT NULL DEFAULT false,
  created_by   uuid REFERENCES auth.users(id),
  created_at   timestamptz DEFAULT now(),
  updated_at   timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_comments_page  ON work.comments (page_id);
CREATE INDEX IF NOT EXISTS idx_comments_block ON work.comments (block_id);

-- =============================================================================
-- work.attachments — Supabase Storage pointers
-- =============================================================================
CREATE TABLE IF NOT EXISTS work.attachments (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  page_id      uuid REFERENCES work.pages(id) ON DELETE CASCADE,
  block_id     uuid REFERENCES work.blocks(id),
  name         text NOT NULL,
  mime_type    text,
  size_bytes   bigint,
  storage_path text NOT NULL,                    -- Supabase Storage object path
  created_by   uuid REFERENCES auth.users(id),
  created_at   timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_attachments_page ON work.attachments (page_id);

-- =============================================================================
-- work.permissions — Space/page RBAC (supplements RLS)
-- =============================================================================
CREATE TABLE IF NOT EXISTS work.permissions (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  space_id     uuid REFERENCES work.spaces(id) ON DELETE CASCADE,
  page_id      uuid REFERENCES work.pages(id) ON DELETE CASCADE,
  user_id      uuid REFERENCES auth.users(id),
  level        work.permission_level NOT NULL DEFAULT 'viewer',
  granted_by   uuid REFERENCES auth.users(id),
  created_at   timestamptz DEFAULT now(),
  CONSTRAINT perm_scope CHECK (
    (space_id IS NOT NULL AND page_id IS NULL) OR
    (space_id IS NULL AND page_id IS NOT NULL)
  )
);

CREATE INDEX IF NOT EXISTS idx_permissions_space ON work.permissions (space_id, user_id);
CREATE INDEX IF NOT EXISTS idx_permissions_page  ON work.permissions (page_id, user_id);
CREATE INDEX IF NOT EXISTS idx_permissions_user  ON work.permissions (user_id);

-- =============================================================================
-- work.templates — Page and database templates
-- =============================================================================
CREATE TABLE IF NOT EXISTS work.templates (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  space_id     uuid REFERENCES work.spaces(id),
  name         text NOT NULL,
  description  text,
  kind         text NOT NULL DEFAULT 'page',     -- 'page' | 'database'
  body         jsonb NOT NULL DEFAULT '{}',      -- serialised page/blocks structure
  is_global    boolean NOT NULL DEFAULT false,   -- available across spaces
  created_by   uuid REFERENCES auth.users(id),
  created_at   timestamptz DEFAULT now()
);

-- =============================================================================
-- work.search_index — Denormalised full-text + embedding index
-- Populated by workspace-indexer Edge Function
-- =============================================================================
CREATE TABLE IF NOT EXISTS work.search_index (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  source_type  text NOT NULL,                    -- 'page' | 'block' | 'db_row'
  source_id    uuid NOT NULL,
  space_id     uuid REFERENCES work.spaces(id) ON DELETE CASCADE,
  title        text,
  snippet      text,
  search_vec   tsvector,
  embedding    vector(1536),                     -- OpenAI text-embedding-3-small
  indexed_at   timestamptz DEFAULT now(),
  UNIQUE (source_type, source_id)
);

CREATE INDEX IF NOT EXISTS idx_search_space   ON work.search_index (space_id);
CREATE INDEX IF NOT EXISTS idx_search_vec     ON work.search_index USING GIN (search_vec);
CREATE INDEX IF NOT EXISTS idx_search_embed   ON work.search_index USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

-- =============================================================================
-- RLS Policies
-- =============================================================================
ALTER TABLE work.spaces      ENABLE ROW LEVEL SECURITY;
ALTER TABLE work.pages       ENABLE ROW LEVEL SECURITY;
ALTER TABLE work.blocks      ENABLE ROW LEVEL SECURITY;
ALTER TABLE work.databases   ENABLE ROW LEVEL SECURITY;
ALTER TABLE work.db_columns  ENABLE ROW LEVEL SECURITY;
ALTER TABLE work.db_rows     ENABLE ROW LEVEL SECURITY;
ALTER TABLE work.relations   ENABLE ROW LEVEL SECURITY;
ALTER TABLE work.comments    ENABLE ROW LEVEL SECURITY;
ALTER TABLE work.attachments ENABLE ROW LEVEL SECURITY;
ALTER TABLE work.permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE work.templates   ENABLE ROW LEVEL SECURITY;
ALTER TABLE work.search_index ENABLE ROW LEVEL SECURITY;

-- Service role: full access (Edge Functions + server-side routes)
DO $$
DECLARE t text;
BEGIN
  FOREACH t IN ARRAY ARRAY[
    'spaces','pages','blocks','databases','db_columns','db_rows',
    'relations','comments','attachments','permissions','templates','search_index'
  ] LOOP
    EXECUTE format(
      'CREATE POLICY "svc_all" ON work.%I FOR ALL TO service_role USING (true) WITH CHECK (true)',
      t
    );
  END LOOP;
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- Authenticated: spaces they have a permission row for
CREATE POLICY "auth_read_spaces" ON work.spaces
  FOR SELECT TO authenticated USING (
    id IN (SELECT space_id FROM work.permissions WHERE user_id = auth.uid())
    OR created_by = auth.uid()
  );

-- Authenticated: pages in spaces they can access
CREATE POLICY "auth_read_pages" ON work.pages
  FOR SELECT TO authenticated USING (
    space_id IN (SELECT space_id FROM work.permissions WHERE user_id = auth.uid())
    OR created_by = auth.uid()
  );

-- Authenticated: blocks on pages they can read
CREATE POLICY "auth_read_blocks" ON work.blocks
  FOR SELECT TO authenticated USING (
    page_id IN (
      SELECT id FROM work.pages WHERE
        space_id IN (SELECT space_id FROM work.permissions WHERE user_id = auth.uid())
        OR created_by = auth.uid()
    )
  );

-- Authenticated: comments on pages they can read
CREATE POLICY "auth_read_comments" ON work.comments
  FOR SELECT TO authenticated USING (
    page_id IN (
      SELECT id FROM work.pages WHERE
        space_id IN (SELECT space_id FROM work.permissions WHERE user_id = auth.uid())
        OR created_by = auth.uid()
    )
  );

-- search_index: space-scoped
CREATE POLICY "auth_read_search" ON work.search_index
  FOR SELECT TO authenticated USING (
    space_id IN (SELECT space_id FROM work.permissions WHERE user_id = auth.uid())
  );

-- =============================================================================
-- RPC helpers
-- =============================================================================

-- Full-text search across pages, blocks, and db_rows
CREATE OR REPLACE FUNCTION work.work_search(
  query_text   text,
  p_space_id   uuid DEFAULT NULL,
  p_limit      int DEFAULT 20
)
RETURNS TABLE (
  source_type  text,
  source_id    uuid,
  space_id     uuid,
  title        text,
  snippet      text,
  rank         real
)
LANGUAGE sql STABLE SECURITY DEFINER
AS $$
  SELECT
    source_type, source_id, space_id, title,
    ts_headline('english', coalesce(snippet, title, ''), plainto_tsquery('english', query_text),
      'StartSel=<mark>, StopSel=</mark>, MaxWords=35, MinWords=15') AS snippet,
    ts_rank(search_vec, plainto_tsquery('english', query_text)) AS rank
  FROM work.search_index
  WHERE
    search_vec @@ plainto_tsquery('english', query_text)
    AND (p_space_id IS NULL OR space_id = p_space_id)
  ORDER BY rank DESC
  LIMIT p_limit;
$$;

GRANT EXECUTE ON FUNCTION work.work_search TO service_role, authenticated;

-- Create a page with initial paragraph block
CREATE OR REPLACE FUNCTION work.create_page(
  p_space_id   uuid,
  p_title      text,
  p_parent_id  uuid DEFAULT NULL,
  p_icon       text DEFAULT NULL,
  p_status     work.page_status DEFAULT 'draft'
)
RETURNS uuid LANGUAGE plpgsql SECURITY DEFINER AS $$
DECLARE
  v_page_id uuid;
BEGIN
  INSERT INTO work.pages (space_id, parent_id, title, icon, status, created_by, updated_by)
  VALUES (p_space_id, p_parent_id, p_title, p_icon, p_status, auth.uid(), auth.uid())
  RETURNING id INTO v_page_id;

  -- Add empty first block
  INSERT INTO work.blocks (page_id, type, content, sort_order, created_by)
  VALUES (v_page_id, 'paragraph', '{"text": ""}', 0, auth.uid());

  RETURN v_page_id;
END;
$$;

GRANT EXECUTE ON FUNCTION work.create_page TO service_role, authenticated;

-- Upsert a db_row (idempotent by id)
CREATE OR REPLACE FUNCTION work.upsert_row(
  p_database_id uuid,
  p_row_id      uuid DEFAULT NULL,
  p_data        jsonb DEFAULT '{}'
)
RETURNS uuid LANGUAGE plpgsql SECURITY DEFINER AS $$
DECLARE
  v_row_id uuid;
BEGIN
  IF p_row_id IS NOT NULL THEN
    UPDATE work.db_rows SET data = p_data, updated_at = now()
    WHERE id = p_row_id AND database_id = p_database_id
    RETURNING id INTO v_row_id;
  END IF;

  IF v_row_id IS NULL THEN
    INSERT INTO work.db_rows (id, database_id, data, created_by)
    VALUES (coalesce(p_row_id, gen_random_uuid()), p_database_id, p_data, auth.uid())
    RETURNING id INTO v_row_id;
  END IF;

  RETURN v_row_id;
END;
$$;

GRANT EXECUTE ON FUNCTION work.upsert_row TO service_role, authenticated;

-- =============================================================================
-- Grants
-- =============================================================================
GRANT USAGE ON SCHEMA work TO service_role, authenticated;
GRANT ALL   ON ALL TABLES IN SCHEMA work TO service_role;
GRANT SELECT ON ALL TABLES IN SCHEMA work TO authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA work TO service_role, authenticated;

-- =============================================================================
-- Seed: default space
-- =============================================================================
INSERT INTO work.spaces (slug, name, description, icon)
VALUES ('ipai', 'IPAI Workspace', 'Main InsightPulse AI knowledge base', '🧠')
ON CONFLICT (slug) DO NOTHING;
