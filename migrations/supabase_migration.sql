-- ExposeChain Supabase Migration Script
-- This script creates the necessary tables in your Supabase PostgreSQL database

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create scan_records table
CREATE TABLE IF NOT EXISTS scan_records (
    id SERIAL PRIMARY KEY,
    scan_id VARCHAR(255) UNIQUE NOT NULL,
    target VARCHAR(255) NOT NULL,
    scan_type VARCHAR(50) NOT NULL,
    dns_results JSONB,
    whois_results JSONB,
    geolocation_results JSONB,
    ssl_results JSONB,
    ai_analysis JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_scan_records_scan_id ON scan_records(scan_id);
CREATE INDEX IF NOT EXISTS idx_scan_records_target ON scan_records(target);
CREATE INDEX IF NOT EXISTS idx_scan_records_created_at ON scan_records(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_scan_records_scan_type ON scan_records(scan_type);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for updated_at
DROP TRIGGER IF EXISTS update_scan_records_updated_at ON scan_records;
CREATE TRIGGER update_scan_records_updated_at
    BEFORE UPDATE ON scan_records
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Optional: Create a view for recent scans (last 30 days)
CREATE OR REPLACE VIEW recent_scans AS
SELECT
    scan_id,
    target,
    scan_type,
    created_at,
    (ai_analysis->>'overall_risk_score')::numeric AS risk_score,
    ai_analysis->>'threat_level' AS threat_level
FROM scan_records
WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '30 days'
ORDER BY created_at DESC;

-- Grant permissions (adjust as needed for your Supabase setup)
-- These will be handled by Supabase's RLS (Row Level Security) policies
