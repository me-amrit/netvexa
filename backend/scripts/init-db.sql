-- Create user if not exists (PostgreSQL 9.5+)
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_user
      WHERE  usename = 'netvexa') THEN
      CREATE USER netvexa WITH PASSWORD 'netvexa_password';
   END IF;
END
$do$;

-- Grant permissions
ALTER USER netvexa CREATEDB;

-- Enable pgvector extension (must be done as superuser)
CREATE EXTENSION IF NOT EXISTS vector;

-- Grant usage on schema
GRANT ALL ON SCHEMA public TO netvexa;