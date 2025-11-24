# Snowflake Setup Guide for Clinical Notes Demo

This guide will walk you through setting up Snowflake with the clinical notes database for the Azure AI Search demo.

## Prerequisites

- Active Snowflake trial account (sign up at https://signup.snowflake.com/)
- SQL client access (Snowflake Web UI or SnowSQL CLI)

## Overview

We'll be setting up:
- Database: `CLINICAL_NOTES_DB`
- Schema: `MEDICAL_RECORDS`
- Table: `PATIENT_CLINICAL_NOTES`
- Warehouse: `DEMO_WAREHOUSE`
- Sample data: 75 synthetic clinical notes

## Step 1: Access Snowflake

### Option A: Snowflake Web UI (Recommended for beginners)

1. Log in to your Snowflake account at `https://<your-account>.snowflakecomputing.com`
2. Click on **Worksheets** in the left navigation
3. Click **+ Worksheet** to create a new worksheet

### Option B: SnowSQL CLI

```bash
snowsql -a <account> -u <username>
```

## Step 2: Create Database Objects

Copy and paste the entire contents of `data/snowflake_schema.sql` into your Snowflake worksheet.

```sql
-- The script will:
-- 1. Create database CLINICAL_NOTES_DB
-- 2. Create schema MEDICAL_RECORDS
-- 3. Create warehouse DEMO_WAREHOUSE
-- 4. Create table PATIENT_CLINICAL_NOTES with indexes
-- 5. Create view V_RECENT_CLINICAL_NOTES
```

**Execute the script:**
- Web UI: Click **Run** (or press `Ctrl+Enter`)
- SnowSQL: Paste and press `Enter`

You should see output like:
```
Database CLINICAL_NOTES_DB successfully created.
Schema MEDICAL_RECORDS successfully created.
Warehouse DEMO_WAREHOUSE successfully created.
Table PATIENT_CLINICAL_NOTES successfully created.
```

## Step 3: Verify Database Structure

Run this query to verify the table was created:

```sql
USE DATABASE CLINICAL_NOTES_DB;
USE SCHEMA MEDICAL_RECORDS;

DESCRIBE TABLE PATIENT_CLINICAL_NOTES;
```

Expected output: You'll see all 31 columns of the table.

## Step 4: Load Sample Data

Copy and paste the contents of `data/insert_clinical_notes.sql` into your worksheet.

**Important Notes:**
- This file contains 75 INSERT statements
- Each statement inserts one clinical note
- The script is approximately 50KB in size
- Execution may take 1-2 minutes

**Execute the script:**
```sql
-- Run all INSERT statements
```

## Step 5: Verify Data Load

Check that all records were inserted:

```sql
SELECT COUNT(*) as total_notes
FROM PATIENT_CLINICAL_NOTES;
```

Expected result: `75`

View sample records:

```sql
SELECT
    note_id,
    patient_name,
    patient_age,
    patient_gender,
    encounter_date,
    diagnosis_summary,
    LEFT(full_clinical_note, 100) as note_preview
FROM PATIENT_CLINICAL_NOTES
ORDER BY encounter_date DESC
LIMIT 10;
```

## Step 6: Test Queries

Try some sample queries to explore the data:

### By Diagnosis

```sql
SELECT
    COUNT(*) as note_count,
    diagnosis_summary
FROM PATIENT_CLINICAL_NOTES
GROUP BY diagnosis_summary
ORDER BY note_count DESC;
```

### By Age Group

```sql
SELECT
    CASE
        WHEN patient_age < 18 THEN 'Pediatric (0-17)'
        WHEN patient_age BETWEEN 18 AND 35 THEN 'Young Adult (18-35)'
        WHEN patient_age BETWEEN 36 AND 55 THEN 'Middle Age (36-55)'
        WHEN patient_age BETWEEN 56 AND 70 THEN 'Senior (56-70)'
        ELSE 'Elderly (70+)'
    END as age_group,
    COUNT(*) as note_count
FROM PATIENT_CLINICAL_NOTES
GROUP BY age_group
ORDER BY age_group;
```

### Recent Notes

```sql
SELECT *
FROM V_RECENT_CLINICAL_NOTES
LIMIT 10;
```

### Search by Keywords

```sql
SELECT
    note_id,
    patient_name,
    diagnosis_summary,
    full_clinical_note
FROM PATIENT_CLINICAL_NOTES
WHERE full_clinical_note ILIKE '%diabetes%'
    OR full_clinical_note ILIKE '%hypertension%'
LIMIT 5;
```

## Step 7: Get Connection Details

You'll need these details for the Python pipeline configuration.

### Account Identifier

Found in your Snowflake URL: `https://<account>.<region>.snowflakecomputing.com`

Example: `abc12345.us-east-1`

### Connection Information

```
Account: <your-account>.<region>
User: <your-username>
Database: CLINICAL_NOTES_DB
Schema: MEDICAL_RECORDS
Warehouse: DEMO_WAREHOUSE
Role: ACCOUNTADMIN (or your assigned role)
```

## Step 8: Configure Pipeline

Update `config/.env` with your Snowflake credentials:

```bash
# Copy example file
cp config/.env.example config/.env

# Edit with your details
SNOWFLAKE_ACCOUNT=abc12345.us-east-1
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_DATABASE=CLINICAL_NOTES_DB
SNOWFLAKE_SCHEMA=MEDICAL_RECORDS
SNOWFLAKE_WAREHOUSE=DEMO_WAREHOUSE
SNOWFLAKE_ROLE=ACCOUNTADMIN
```

Also copy the config.yaml:

```bash
cp config/config.yaml.example config/config.yaml
```

The config.yaml is already set up for the clinical notes table - no changes needed!

## Data Schema Reference

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `note_id` | VARCHAR(50) | Unique identifier (e.g., NOTE00001) |
| `patient_name` | VARCHAR(200) | Anonymized patient name |
| `patient_age` | INTEGER | Patient age |
| `patient_gender` | VARCHAR(20) | Male, Female, Other |
| `encounter_date` | TIMESTAMP | Date/time of encounter |
| `encounter_type` | VARCHAR(100) | Type of visit |
| `diagnosis_summary` | VARCHAR(1000) | Primary diagnosis |
| `icd10_codes` | VARCHAR(500) | ICD-10 diagnosis codes |
| `full_clinical_note` | TEXT | Complete note (used for embedding) |
| `updated_at` | TIMESTAMP | Last update (watermark column) |

### Watermark Column

The `updated_at` column is used for incremental processing:
- First run: Processes all records
- Subsequent runs: Only processes records where `updated_at > last_checkpoint`

## Testing Incremental Updates

To test incremental processing, add new records:

```sql
INSERT INTO PATIENT_CLINICAL_NOTES (
    note_id, patient_name, patient_age, patient_gender,
    encounter_date, encounter_type, diagnosis_summary,
    icd10_codes, full_clinical_note, updated_at
) VALUES (
    'NOTE00076',
    'Test Patient',
    45,
    'Male',
    CURRENT_TIMESTAMP(),
    'Follow-up Visit',
    'Test diagnosis',
    'Z00.00',
    'This is a test clinical note added after initial load.',
    CURRENT_TIMESTAMP()
);
```

The next pipeline run will only process this new record.

## Troubleshooting

### Connection Issues

**Error: "Account not found"**
- Verify account identifier includes region (e.g., `account.region`)
- Check for typos in account name

**Error: "Authentication failed"**
- Verify username and password
- Check if user has necessary privileges

### Warehouse Issues

**Error: "Warehouse not found"**
```sql
-- Create warehouse if needed
CREATE WAREHOUSE DEMO_WAREHOUSE
    WITH WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE;
```

**Error: "Insufficient privileges"**
```sql
-- Grant necessary permissions
GRANT USAGE ON WAREHOUSE DEMO_WAREHOUSE TO ROLE YOUR_ROLE;
GRANT USAGE ON DATABASE CLINICAL_NOTES_DB TO ROLE YOUR_ROLE;
GRANT USAGE ON SCHEMA MEDICAL_RECORDS TO ROLE YOUR_ROLE;
GRANT SELECT ON ALL TABLES IN SCHEMA MEDICAL_RECORDS TO ROLE YOUR_ROLE;
```

### Data Issues

**No data returned**
```sql
-- Check table exists
SHOW TABLES IN SCHEMA MEDICAL_RECORDS;

-- Check row count
SELECT COUNT(*) FROM PATIENT_CLINICAL_NOTES;

-- Verify warehouse is running
SHOW WAREHOUSES LIKE 'DEMO_WAREHOUSE';
```

## Next Steps

Once Snowflake is set up and data is loaded:

1. ✅ Snowflake database configured
2. ✅ Sample data loaded (75 records)
3. ⏭️ Configure Azure infrastructure (see [Infrastructure Deployment](02-infrastructure.md))
4. ⏭️ Run the pipeline (see [Running the Pipeline](03-running-pipeline.md))

## Cost Management

### Snowflake Trial

- Free credits: $400 USD
- Duration: 30 days
- Warehouse costs: ~$0.06/hour for XSMALL

### Best Practices

1. **Auto-suspend**: Warehouse auto-suspends after 5 minutes of inactivity
2. **Resume**: Auto-resumes when queried
3. **Monitoring**: Check usage in Snowflake UI → Admin → Usage

### Sample Cost Calculation

For this demo:
- Warehouse: XSMALL ($2/credit per hour = ~$0.06/hour)
- Expected usage: 1-2 hours total for development/testing
- Estimated cost: $0.06 - $0.12

## Additional Resources

- [Snowflake Documentation](https://docs.snowflake.com/)
- [Snowflake Trial Guide](https://docs.snowflake.com/en/user-guide/getting-started-trial.html)
- [SQL Reference](https://docs.snowflake.com/en/sql-reference.html)

## Support

For issues specific to this demo:
- Check the main [README.md](../README.md)
- Review [Setup Guide](01-setup.md)

For Snowflake-specific issues:
- Snowflake Community: https://community.snowflake.com/
- Snowflake Support: Available with paid plans
