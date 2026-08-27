-- =========================================
-- DATABASE SCHEMA
-- =========================================

-- Create a new table 'cameras' with a primary key and columns
CREATE TABLE cameras (
    camera_id VARCHAR(50) PRIMARY KEY,
    location_name TEXT NOT NULL CHECK (LENGTH(location_name) <= 100),
rtsp_url TEXT NOT NULL CHECK (LENGTH(rtsp_url) <= 500),
    status_cam VARCHAR(20) DEFAULT 'online'
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

-- Index to speed up sorting and filtering by date/time
CREATE INDEX idx_alerts_timestamp ON intrusion_alerts(event_timestamp);

-- Index to speed up finding alerts for a specific camera
CREATE INDEX idx_alerts_camera ON intrusion_alerts(camera_id);

