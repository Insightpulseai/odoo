-- Odoo Copilot: BIR document types for RAG pipeline
-- Inserts BIR-specific document types into kb.document_types

-- Ensure kb schema exists
CREATE SCHEMA IF NOT EXISTS kb;

-- Create document_types table if not exists
CREATE TABLE IF NOT EXISTS kb.document_types (
  id serial PRIMARY KEY,
  type_key text UNIQUE NOT NULL,
  display_name text NOT NULL,
  description text,
  created_at timestamptz DEFAULT now()
);

-- Insert BIR document types
INSERT INTO kb.document_types (type_key, display_name, description) VALUES
  ('bir_revenue_regulation', 'BIR Revenue Regulation', 'Revenue Regulations issued by the Bureau of Internal Revenue'),
  ('bir_revenue_memorandum', 'BIR Revenue Memorandum', 'Revenue Memorandum Orders and Circulars'),
  ('bir_tax_form_guide', 'BIR Tax Form Guide', 'Instructions and guides for BIR tax forms'),
  ('bir_train_law', 'TRAIN Law Provision', 'Tax Reform for Acceleration and Inclusion (TRAIN) law provisions'),
  ('bir_filing_calendar', 'BIR Filing Calendar', 'Tax filing deadlines and calendar')
ON CONFLICT (type_key) DO NOTHING;
