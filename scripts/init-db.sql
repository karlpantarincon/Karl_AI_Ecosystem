-- Initialize Karl AI Ecosystem Database
-- This script runs when the PostgreSQL container starts

-- Create database if it doesn't exist
SELECT 'CREATE DATABASE karl_ecosystem'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'karl_ecosystem')\gexec

-- Connect to the database
\c karl_ecosystem;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create initial system flags
INSERT INTO flags (key, value, description, updated_at) 
VALUES 
    ('system_paused', 'false', 'System pause flag', NOW()),
    ('maintenance_mode', 'false', 'Maintenance mode flag', NOW()),
    ('debug_mode', 'false', 'Debug mode flag', NOW())
ON CONFLICT (key) DO NOTHING;

-- Create initial admin user (if needed in the future)
-- INSERT INTO users (id, username, email, role, created_at) 
-- VALUES (uuid_generate_v4(), 'admin', 'admin@karl-ai.com', 'admin', NOW())
-- ON CONFLICT (email) DO NOTHING;

-- Log initialization
INSERT INTO events (agent, type, payload, created_at)
VALUES ('system', 'database_initialized', 
        '{"message": "Database initialized successfully", "version": "0.1.0"}', 
        NOW());
