-- IBVAP Database Schema Initialization
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    fullname VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    gender VARCHAR(20),
    profile_pic TEXT,
    role VARCHAR(20) DEFAULT 'operator',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Cameras Table
CREATE TABLE IF NOT EXISTS cameras (
    id SERIAL PRIMARY KEY,
    camera_id VARCHAR(50) UNIQUE DEFAULT ('CAM-' || substring(gen_random_uuid()::text, 1, 8)),
    camera_name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    rtsp_url TEXT NOT NULL UNIQUE,
    status VARCHAR(20) DEFAULT 'online',
    virtual_fence JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Alerts Table
CREATE TABLE IF NOT EXISTS alerts (
    alert_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    camera_id VARCHAR(50) NOT NULL,
    event_timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    object_type VARCHAR(50) NOT NULL,
    tracking_id INTEGER NOT NULL DEFAULT 1,
    confidence NUMERIC(5,2) NOT NULL DEFAULT 0.85,
    spatial_coordinates JSONB NOT NULL DEFAULT '[]'::jsonb,
    snapshot_data TEXT NOT NULL DEFAULT '',
    alert_status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(event_timestamp, camera_id);

-- Compatibility view for intrusion_alerts
CREATE OR REPLACE VIEW intrusion_alerts AS SELECT * FROM alerts;

-- Seed initial test cameras if none exist
INSERT INTO cameras (camera_name, location, rtsp_url, status)
VALUES 
  ('Border Sector North - Cam 1', 'Northern Perimeter Post A', 'videos/test.mp4', 'online'),
  ('Border Sector West - Cam 2', 'Western Gate Bunker 3', 'rtsp://mock/stream2', 'online'),
  ('Command Outpost East - Cam 3', 'East Tower Watch', 'rtsp://mock/stream3', 'online'),
  ('Southern Buffer Zone - Cam 4', 'Sector 4 Barricade', 'rtsp://mock/stream4', 'offline')
ON CONFLICT (rtsp_url) DO NOTHING;
