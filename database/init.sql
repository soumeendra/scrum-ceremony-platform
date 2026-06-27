-- Initialize SCP database with required extensions and RLS policies

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";  -- pgvector for embeddings

-- Create application role (used by the API)
CREATE ROLE scp_app_user WITH LOGIN PASSWORD 'scp_dev_password';
GRANT CONNECT ON DATABASE scp_platform TO scp_app_user;
GRANT USAGE ON SCHEMA public TO scp_app_user;

-- Note: Table-specific grants and RLS policies are managed by Alembic migrations
-- This file only sets up the database-level prerequisites

-- Verify extensions
SELECT extname, extversion FROM pg_extension WHERE extname IN ('uuid-ossp', 'pgcrypto', 'vector');
