-- db/init.sql
-- This script runs automatically when the PostgreSQL container boots up for the first time.
-- It demonstrates explicit table modeling and the use of JSONB for AI outputs.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS extractions (
    extraction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    original_file_reference VARCHAR(500) NOT NULL,
    
    -- Using JSONB to store highly dynamic AI structured outputs efficiently
    extracted_data JSONB NOT NULL,
    
    status VARCHAR(50) DEFAULT 'SUCCESS',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexing deeply nested JSONB structures is a great practice for performance
CREATE INDEX idx_extractions_data ON extractions USING GIN (extracted_data);
CREATE INDEX idx_extractions_user ON extractions(user_id);
