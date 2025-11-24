# Setup Guide

This guide walks you through setting up the Snowflake to Azure AI Search demo environment.

## Prerequisites

Before you begin, ensure you have the following:

### Required Software
- Python 3.10 or higher
- Git
- Azure CLI (for infrastructure deployment)

### Required Accounts
- Azure subscription with:
  - Azure OpenAI service access (requires application approval)
  - Permissions to create resources
- Snowflake trial account (can be created at https://signup.snowflake.com/)

## Step 1: Clone the Repository

```bash
git clone <repository-url>
cd snowflake-msft-ai-search
```

## Step 2: Set Up Python Environment

### Windows

```powershell
# Run the setup script
.\scripts\setup_env.ps1

# Or manually:
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Linux/Mac

```bash
# Run the setup script
chmod +x scripts/setup_env.sh
./scripts/setup_env.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Step 3: Set Up Snowflake

1. Create a Snowflake trial account at https://signup.snowflake.com/

2. Log in to your Snowflake account

3. Create a database and schema for your data:

```sql
-- Create database
CREATE DATABASE DEMO_DB;

-- Create schema
CREATE SCHEMA DEMO_DB.DEMO_SCHEMA;

-- Create warehouse
CREATE WAREHOUSE DEMO_WAREHOUSE
    WITH WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE;

-- Use the database and schema
USE DATABASE DEMO_DB;
USE SCHEMA DEMO_SCHEMA;
USE WAREHOUSE DEMO_WAREHOUSE;
```

4. Create a sample table and load data:

```sql
-- Create sample table
CREATE TABLE CUSTOMER_DATA (
    id VARCHAR(50) PRIMARY KEY,
    text_content VARCHAR(10000),
    category VARCHAR(100),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Insert sample data
INSERT INTO CUSTOMER_DATA (id, text_content, category)
VALUES
    ('1', 'Our new product line includes innovative AI-powered tools for data analysis.', 'product'),
    ('2', 'Customer satisfaction has increased by 25% after implementing our new support system.', 'support'),
    ('3', 'The quarterly financial report shows strong growth in cloud services revenue.', 'finance');
```

5. Note your Snowflake connection details:
   - Account identifier (e.g., `abc12345.us-east-1`)
   - Username
   - Password
   - Database name
   - Schema name
   - Warehouse name

## Step 4: Configure Environment Variables

1. Copy the example configuration files:

```bash
# Windows
Copy-Item config\.env.example config\.env
Copy-Item config\config.yaml.example config\config.yaml

# Linux/Mac
cp config/.env.example config/.env
cp config/config.yaml.example config/config.yaml
```

2. Edit `config/.env` with your Snowflake credentials:

```bash
# Snowflake Configuration
SNOWFLAKE_ACCOUNT=your_account.region
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_DATABASE=DEMO_DB
SNOWFLAKE_SCHEMA=DEMO_SCHEMA
SNOWFLAKE_WAREHOUSE=DEMO_WAREHOUSE
SNOWFLAKE_ROLE=ACCOUNTADMIN

# Note: Azure credentials will be added after infrastructure deployment
```

3. Edit `config/config.yaml` to match your Snowflake table structure:

```yaml
pipeline:
  source:
    table_name: "CUSTOMER_DATA"
    columns:
      - id
      - text_content
      - category
      - created_at
      - updated_at
    watermark_column: "updated_at"
    initial_watermark: null

  embedding:
    text_field: "text_content"
    # ... rest of config
```

## Step 5: Verify Setup

Test your Snowflake connection:

```python
# Create a test script: test_connection.py
from src.utils.config import Config
from src.extractors.snowflake_extractor import SnowflakeExtractor

config = Config()
extractor = SnowflakeExtractor(config)

with extractor:
    count = extractor.get_row_count("CUSTOMER_DATA")
    print(f"Successfully connected! Found {count} rows.")
```

Run the test:

```bash
python test_connection.py
```

## Next Steps

Once setup is complete, proceed to:
- [Infrastructure Deployment](02-infrastructure.md) to deploy Azure resources
- [Running the Pipeline](03-running-pipeline.md) to execute the data pipeline

## Troubleshooting

### Python Version Issues
Ensure you're using Python 3.10 or higher:
```bash
python --version
```

### Snowflake Connection Issues
- Verify your account identifier format (should include region)
- Ensure your IP is whitelisted if network policies are enabled
- Check that your user has appropriate permissions

### Virtual Environment Issues
If activation fails, try:
```bash
# Windows
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Linux/Mac
Make sure the script has execute permissions:
chmod +x scripts/setup_env.sh
```
