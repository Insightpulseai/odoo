-- Kapa.ai-style Documentation Assistant - Supabase Schema
-- Self-hosted RAG system for technical documentation Q&A

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Projects / tenants
CREATE TABLE docs_projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- API keys bound to projects
CREATE TABLE docs_api_keys (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES docs_projects(id) ON DELETE CASCADE,
  key_hash TEXT NOT NULL,            -- store hash, never raw key
  label TEXT,
  permissions JSONB DEFAULT '{"chat": true, "search": true, "ingest": false}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  revoked_at TIMESTAMPTZ,
  last_used_at TIMESTAMPTZ
);

-- Sources & source groups (versions/products)
CREATE TABLE docs_sources (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES docs_projects(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  kind TEXT NOT NULL,                -- 'github', 'notion', 's3', 'markdown', 'odoo', 'n8n'
  config JSONB NOT NULL,             -- source-specific configuration
  sync_schedule TEXT DEFAULT 'daily', -- 'hourly', 'daily', 'weekly', 'manual'
  last_sync_at TIMESTAMPTZ,
  sync_status TEXT DEFAULT 'pending', -- 'pending', 'syncing', 'success', 'error'
  error_message TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Source groups for versioning/product segmentation
CREATE TABLE docs_source_groups (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES docs_projects(id) ON DELETE CASCADE,
  name TEXT NOT NULL,                -- e.g. 'v1', 'v2', 'cloud', 'self-hosted'
  description TEXT,
  is_default BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE docs_source_group_members (
  source_id UUID REFERENCES docs_sources(id) ON DELETE CASCADE,
  group_id UUID REFERENCES docs_source_groups(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (source_id, group_id)
);

-- Documents & chunks
CREATE TABLE docs_documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES docs_projects(id) ON DELETE CASCADE,
  source_id UUID REFERENCES docs_sources(id) ON DELETE CASCADE,
  external_id TEXT,                  -- URL, doc ID, file path, etc.
  path TEXT,                         -- file path or URL path
  title TEXT,
  content_hash TEXT,                 -- for change detection
  metadata JSONB DEFAULT '{}'::jsonb, -- source-specific metadata
  lang TEXT DEFAULT 'en',
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(project_id, source_id, external_id)
);

CREATE TABLE docs_chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID REFERENCES docs_documents(id) ON DELETE CASCADE,
  project_id UUID REFERENCES docs_projects(id) ON DELETE CASCADE,
  source_id UUID REFERENCES docs_sources(id) ON DELETE CASCADE,
  ordinal INTEGER NOT NULL,          -- order within document
  content TEXT NOT NULL,
  heading TEXT,                      -- section heading
  section_path TEXT[],               -- ["Getting Started", "Installation"]
  token_count INTEGER,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vector embeddings for semantic search
CREATE TABLE docs_chunk_embeddings (
  chunk_id UUID PRIMARY KEY REFERENCES docs_chunks(id) ON DELETE CASCADE,
  embedding VECTOR(1536),            -- OpenAI/Claude compatible
  model TEXT NOT NULL DEFAULT 'text-embedding-3-large',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Q&A conversation logging
CREATE TABLE docs_questions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES docs_projects(id) ON DELETE CASCADE,
  api_key_id UUID REFERENCES docs_api_keys(id),
  user_id TEXT,                      -- optional external user ID
  session_id TEXT,                   -- for conversation continuity
  channel TEXT NOT NULL,             -- 'widget', 'slack', 'mattermost', 'api', 'mcp'
  query TEXT NOT NULL,
  metadata JSONB DEFAULT '{}'::jsonb, -- user agent, IP, etc.
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE docs_answers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  question_id UUID REFERENCES docs_questions(id) ON DELETE CASCADE,
  project_id UUID REFERENCES docs_projects(id) ON DELETE CASCADE,
  model TEXT NOT NULL,               -- 'claude-3-sonnet', 'gpt-4', etc.
  answer TEXT NOT NULL,
  latency_ms INTEGER,
  token_in INTEGER,
  token_out INTEGER,
  grounded BOOLEAN,                  -- true if fully covered by context
  confidence_score REAL,             -- 0-1 confidence in answer
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Citations linking answers to source chunks
CREATE TABLE docs_answer_citations (
  answer_id UUID REFERENCES docs_answers(id) ON DELETE CASCADE,
  chunk_id UUID REFERENCES docs_chunks(id) ON DELETE CASCADE,
  relevance_score REAL,              -- 0-1 relevance score
  citation_text TEXT,                -- snippet used in answer
  created_at TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (answer_id, chunk_id)
);

-- User feedback for quality improvement
CREATE TABLE docs_feedback (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  answer_id UUID REFERENCES docs_answers(id) ON DELETE CASCADE,
  rating INTEGER CHECK (rating BETWEEN 1 AND 5),
  comment TEXT,
  user_id TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Analytics events for tracking usage
CREATE TABLE docs_analytics_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES docs_projects(id) ON DELETE CASCADE,
  event_type TEXT NOT NULL,          -- 'question_asked', 'answer_received', 'source_clicked', 'feedback_given'
  user_id TEXT,
  session_id TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Knowledge gaps - questions that couldn't be answered well
CREATE TABLE docs_knowledge_gaps (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES docs_projects(id) ON DELETE CASCADE,
  question TEXT NOT NULL,
  frequency INTEGER DEFAULT 1,       -- how many times this gap was encountered
  suggested_topics TEXT[],           -- potential topics to document
  status TEXT DEFAULT 'open',        -- 'open', 'in_progress', 'resolved'
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_docs_chunks_project_id ON docs_chunks(project_id);
CREATE INDEX idx_docs_chunks_source_id ON docs_chunks(source_id);
CREATE INDEX idx_docs_questions_project_id ON docs_questions(project_id);
CREATE INDEX idx_docs_questions_created_at ON docs_questions(created_at);
CREATE INDEX idx_docs_answers_question_id ON docs_answers(question_id);
CREATE INDEX idx_docs_chunk_embeddings_embedding ON docs_chunk_embeddings USING ivfflat (embedding vector_cosine_ops);

-- Row Level Security (RLS) policies
ALTER TABLE docs_projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE docs_api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE docs_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE docs_source_groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE docs_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE docs_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE docs_chunk_embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE docs_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE docs_answers ENABLE ROW LEVEL SECURITY;
ALTER TABLE docs_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE docs_analytics_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE docs_knowledge_gaps ENABLE ROW LEVEL SECURITY;

-- RLS Policies (simplified - adjust based on your auth system)
CREATE POLICY "Users can view their own projects" ON docs_projects
  FOR SELECT USING (auth.uid() IN (
    SELECT user_id FROM project_members WHERE project_id = docs_projects.id
  ));

-- Functions for common operations
CREATE OR REPLACE FUNCTION docs_search_chunks(
  query_embedding VECTOR(1536),
  match_count INTEGER DEFAULT 10,
  project_id_filter UUID DEFAULT NULL,
  source_group_ids UUID[] DEFAULT NULL
)
RETURNS TABLE(
  chunk_id UUID,
  content TEXT,
  heading TEXT,
  section_path TEXT[],
  document_title TEXT,
  source_name TEXT,
  similarity_score FLOAT
)
LANGUAGE SQL
AS $$
  SELECT 
    c.id,
    c.content,
    c.heading,
    c.section_path,
    d.title as document_title,
    s.name as source_name,
    1 - (ce.embedding <=> query_embedding) as similarity_score
  FROM docs_chunks c
  JOIN docs_chunk_embeddings ce ON c.id = ce.chunk_id
  JOIN docs_documents d ON c.document_id = d.id
  JOIN docs_sources s ON c.source_id = s.id
  WHERE c.project_id = project_id_filter
    AND (source_group_ids IS NULL OR 
         s.id IN (SELECT source_id FROM docs_source_group_members WHERE group_id = ANY(source_group_ids)))
  ORDER BY ce.embedding <=> query_embedding
  LIMIT match_count;
$$;

-- Update timestamps trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_docs_projects_updated_at BEFORE UPDATE ON docs_projects
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_docs_sources_updated_at BEFORE UPDATE ON docs_sources
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_docs_documents_updated_at BEFORE UPDATE ON docs_documents
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_docs_knowledge_gaps_updated_at BEFORE UPDATE ON docs_knowledge_gaps
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
