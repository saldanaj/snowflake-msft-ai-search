-- Simple Snowflake Schema for Clinical Notes Demo
-- Run this entire script in a Snowflake worksheet

-- Create and use database
CREATE DATABASE IF NOT EXISTS CLINICAL_NOTES_DB;
USE DATABASE CLINICAL_NOTES_DB;

-- Create and use schema
CREATE SCHEMA IF NOT EXISTS MEDICAL_RECORDS;
USE SCHEMA MEDICAL_RECORDS;

-- Create warehouse
CREATE WAREHOUSE IF NOT EXISTS DEMO_WAREHOUSE
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE;

-- Use the warehouse
USE WAREHOUSE DEMO_WAREHOUSE;

-- Drop table if exists
DROP TABLE IF EXISTS PATIENT_CLINICAL_NOTES;

-- Create simple clinical notes table
CREATE TABLE PATIENT_CLINICAL_NOTES (
    note_id VARCHAR(50),
    patient_name VARCHAR(200),
    patient_age INTEGER,
    patient_gender VARCHAR(20),
    encounter_date TIMESTAMP_NTZ,
    encounter_type VARCHAR(100),
    chief_complaint TEXT,
    medical_history TEXT,
    bp_systolic INTEGER,
    bp_diastolic INTEGER,
    temperature_f FLOAT,
    weight_lbs FLOAT,
    heart_rate INTEGER,
    vitals_text VARCHAR(500),
    physical_exam TEXT,
    lab_results TEXT,
    assessment TEXT,
    icd10_codes VARCHAR(500),
    diagnosis_summary VARCHAR(1000),
    treatment_plan TEXT,
    medications_prescribed TEXT,
    procedures_planned VARCHAR(500),
    referrals VARCHAR(500),
    follow_up_weeks INTEGER,
    full_clinical_note TEXT,
    provider_name VARCHAR(200),
    department VARCHAR(100),
    note_status VARCHAR(50),
    created_at TIMESTAMP_NTZ,
    updated_at TIMESTAMP_NTZ,
    created_by VARCHAR(100)
);

-- Verify table was created
SELECT COUNT(*) as row_count FROM PATIENT_CLINICAL_NOTES;
