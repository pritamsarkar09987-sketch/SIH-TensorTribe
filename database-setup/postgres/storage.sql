-- =========================================
-- DATABASE SCHEMA
-- =========================================

--States
CREATE TYPE status_cam AS ENUM ('online', 'offline', 'maintenance');
CREATE TYPE alert_status AS ENUM ('active', 'resolved', 'false_positive');
CREATE TYPE user_role AS ENUM ('admin', 'operator');


CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    fullname VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    gender VARCHAR(20),
    rank VARCHAR(100) DEFAULT 'Captain',
    profile_pic TEXT,
    role VARCHAR(20) DEFAULT 'operator',         
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Dynamic User-Linked Cameras
CREATE TABLE IF NOT EXISTS user_cameras (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    camera_name VARCHAR(100) NOT NULL DEFAULT 'Tactical Perimeter Cam',
    rtsp_link TEXT NOT NULL,
    location VARCHAR(100) DEFAULT 'Perimeter Point',
    status VARCHAR(20) DEFAULT 'online',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create a new table 'intrusion_alerts' with a primary key and columns
CREATE TABLE IF NOT EXISTS intrusion_alerts (
    alert_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),--UUID is a universally unique identifier that can be used as a primary key for the table
    camera_id VARCHAR(50) NOT NULL REFERENCES cameras(camera_id),
    event_timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,--Timestamp of the event
    object_type VARCHAR(50) NOT NULL,--human, vehicle, animal, etc.
    tracking_id INTEGER NOT NULL,
    confidence NUMERIC(5,2) NOT NULL,--Numeric value representing the confidence level of the detection / 5,2 represents a number with 5 digits in total, 2 of which are after the decimal point
    spatial_coordinates JSONB NOT NULL,--JSONB data type to store spatial coordinates in a flexible format
    snapshot_data TEXT NOT NULL,--Text is  used to store the snapshot data as a base64 encoded string
    alert_status VARCHAR(20) DEFAULT'active' --active, resolved, false_positive
);

-- Index to speed up sorting and filtering by date/time wrt camera_id
CREATE INDEX idx_alerts_timestamp ON intrusion_alerts(event_timestamp,camera_id);



