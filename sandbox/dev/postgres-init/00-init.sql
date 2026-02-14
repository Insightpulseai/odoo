-- IPAI Dev Workspace: Initialize databases
-- Creates separate databases for Odoo and Superset

CREATE DATABASE odoo_dev;
CREATE DATABASE superset;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE odoo_dev TO dev;
GRANT ALL PRIVILEGES ON DATABASE superset TO dev;

-- Enable extensions commonly needed
\c odoo_dev
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

\c superset
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
