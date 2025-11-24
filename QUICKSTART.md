# Quick Start Guide - Clinical Notes Demo

This guide will get you up and running with the Snowflake to Azure AI Search demo in ~30 minutes.

## What You'll Build

A pipeline that:
1. Extracts clinical notes from Snowflake
2. Generates embeddings using Azure OpenAI
3. Indexes data in Azure AI Search for conversational AI

## Prerequisites Checklist

- [ ] Snowflake trial account (sign up: https://signup.snowflake.com/)
- [ ] Azure subscription with:
  - [ ] Azure OpenAI access (apply: https://aka.ms/oai/access)
  - [ ] Contributor permissions
- [ ] Python 3.10+ installed
- [ ] Git installed
- [ ] Azure CLI installed (for infrastructure deployment)

## Phase 1: Snowflake Setup (10 minutes)

### 1.1 Access Snowflake

Log in to your Snowflake account and open a new worksheet.

### 1.2 Create Database and Load Data

**Step 1:** Run the schema creation script

- Open `data/snowflake_schema.sql`
- Copy entire contents
- Paste into Snowflake worksheet
- Click **Run**

Expected output: Database, schema, warehouse, and table created successfully.

**Step 2:** Load sample data

- Open `data/insert_clinical_notes.sql`
- Copy entire contents
- Paste into Snowflake worksheet
- Click **Run** (may take 1-2 minutes)

**Step 3:** Verify data

```sql
SELECT COUNT(*) FROM PATIENT_CLINICAL_NOTES;
-- Should return: 75

SELECT * FROM PATIENT_CLINICAL_NOTES LIMIT 5;
-- Should show 5 clinical notes
```

### 1.3 Note Connection Details

You'll need these for configuration:

```
Account: <from your Snowflake URL>
Example: abc12345.us-east-1.snowflakecomputing.com
       → abc12345.us-east-1

Username: <your Snowflake username>
Password: <your Snowflake password>
Database: CLINICAL_NOTES_DB
Schema: MEDICAL_RECORDS
Warehouse: DEMO_WAREHOUSE
```

✅ **Checkpoint:** You should have 75 clinical notes in Snowflake.

For detailed instructions, see [Snowflake Setup Guide](docs/SNOWFLAKE_SETUP.md).

## Phase 2: Azure Infrastructure (10 minutes)

### 2.1 Login to Azure

```bash
az login
```

### 2.2 Deploy Infrastructure

**Windows:**
```powershell
.\scripts\deploy_infrastructure.ps1 `
    -ResourceGroupName "rg-clinical-notes-demo" `
    -Location "eastus" `
    -Environment "dev"
```

**Linux/Mac:**
```bash
chmod +x scripts/deploy_infrastructure.sh
./scripts/deploy_infrastructure.sh \
    --resource-group "rg-clinical-notes-demo" \
    --location "eastus" \
    --environment "dev"
```

### 2.3 Retrieve API Keys

**Azure AI Search:**
```bash
az search admin-key show \
    --resource-group "rg-clinical-notes-demo" \
    --service-name "<search-service-name>" \
    --query "primaryKey" -o tsv
```

**Azure OpenAI:**
```bash
az cognitiveservices account keys list \
    --resource-group "rg-clinical-notes-demo" \
    --name "<openai-service-name>" \
    --query "key1" -o tsv
```

✅ **Checkpoint:** You should have Azure OpenAI and AI Search endpoints + API keys.

For detailed instructions, see [Infrastructure Deployment](docs/02-infrastructure.md).

## Phase 3: Pipeline Configuration (5 minutes)

### 3.1 Set Up Python Environment

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3.2 Configure Environment

```bash
# Copy example files
cp config/.env.example config/.env
cp config/config.yaml.example config/config.yaml
```

### 3.3 Edit config/.env

Open `config/.env` and fill in your credentials:

```bash
# Snowflake Configuration
SNOWFLAKE_ACCOUNT=abc12345.us-east-1
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_DATABASE=CLINICAL_NOTES_DB
SNOWFLAKE_SCHEMA=MEDICAL_RECORDS
SNOWFLAKE_WAREHOUSE=DEMO_WAREHOUSE
SNOWFLAKE_ROLE=ACCOUNTADMIN

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=your_openai_api_key
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
AZURE_OPENAI_API_VERSION=2024-02-01

# Azure AI Search Configuration
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_API_KEY=your_search_api_key
AZURE_SEARCH_INDEX_NAME=clinical-notes-index
```

✅ **Checkpoint:** Configuration files are set up with your credentials.

## Phase 4: Run the Pipeline (5 minutes)

### 4.1 First Run - Full Index

```bash
python scripts/run_pipeline.py --full --recreate-index
```

Expected output:
```
Pipeline execution started
Step 1: Extracting data from Snowflake
  Data extraction completed: 75 rows
Step 2: Generating embeddings
  Batch 1/1 processed successfully
  Embedding generation completed: 75 rows
Step 3: Setting up Azure AI Search index
  Index created successfully
Step 4: Indexing documents
  Document indexing completed: 75 rows

==================================================
Pipeline Execution Summary
==================================================
Rows extracted: 75
Rows embedded: 75
Rows indexed: 75
Total documents in index: 75
Duration: 45.23 seconds
==================================================
```

### 4.2 Test Incremental Update

Add a new record to Snowflake:

```sql
INSERT INTO PATIENT_CLINICAL_NOTES (
    note_id, patient_name, patient_age, patient_gender,
    encounter_date, encounter_type, diagnosis_summary,
    icd10_codes, full_clinical_note, updated_at
) VALUES (
    'NOTE00076',
    'Jane Test',
    55,
    'Female',
    CURRENT_TIMESTAMP(),
    'Follow-up Visit',
    'Hypertension follow-up',
    'I10',
    'Jane Test, a 55-year-old female, presents for hypertension follow-up. BP 140/85. Continue lisinopril 10mg daily.',
    CURRENT_TIMESTAMP()
);
```

Run incremental pipeline:

```bash
python scripts/run_pipeline.py --incremental
```

Expected output:
```
Rows extracted: 1
Rows embedded: 1
Rows indexed: 1
Total documents in index: 76
```

✅ **Checkpoint:** Pipeline successfully indexes clinical notes from Snowflake to Azure AI Search.

## Phase 5: Verify Search (5 minutes)

### 5.1 Test in Azure Portal

1. Open Azure Portal
2. Navigate to your Azure AI Search resource
3. Click "Search explorer"
4. Try searches:
   - `diabetes`
   - `hypertension`
   - `chronic pain`

### 5.2 Test with Python

Create `test_search.py`:

```python
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
import os
from dotenv import load_dotenv

load_dotenv("config/.env")

# Initialize client
client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY"))
)

# Search
query = "diabetes hypertension"
results = client.search(search_text=query, top=5)

print(f"\nSearch results for: '{query}'\n")
for i, result in enumerate(results, 1):
    print(f"{i}. Patient: {result['id']}")
    print(f"   Content: {result['content'][:150]}...")
    print(f"   Score: {result['@search.score']:.2f}\n")
```

Run it:
```bash
python test_search.py
```

✅ **Checkpoint:** You can search clinical notes using Azure AI Search!

## What You've Accomplished

1. ✅ Set up Snowflake with 75 synthetic clinical notes
2. ✅ Deployed Azure infrastructure (OpenAI + AI Search)
3. ✅ Configured the pipeline
4. ✅ Indexed clinical notes with embeddings
5. ✅ Tested incremental updates
6. ✅ Verified search functionality

## Next Steps

### Customize for Your Use Case

1. **Add Real Data**
   - Replace synthetic notes with your data
   - Update schema if needed
   - Run pipeline with your data

2. **Enhance Pipeline**
   - Add data quality checks
   - Implement error notifications
   - Set up monitoring

3. **Build Conversational AI**
   - Implement RAG (Retrieval Augmented Generation)
   - Create chat interface
   - Deploy to Azure Container Apps

### Learn More

- [Snowflake Setup Details](docs/SNOWFLAKE_SETUP.md)
- [Infrastructure Guide](docs/02-infrastructure.md)
- [Pipeline Operations](docs/03-running-pipeline.md)
- [Future Enhancements](docs/04-future-enhancements.md)

## Troubleshooting

### Snowflake Connection Fails

Check:
- Account identifier format (include region)
- Username and password
- Warehouse is running

### Azure Deployment Fails

Check:
- Azure OpenAI access approved
- Sufficient permissions
- Region availability

### Pipeline Errors

Common issues:
- Missing environment variables → Check config/.env
- API rate limits → Reduce batch size
- Schema mismatch → Verify table columns

### Getting Help

1. Check documentation in `docs/` folder
2. Review error messages carefully
3. Verify all prerequisites are met

## Cost Estimates

**Development/Testing (1 month):**
- Snowflake Trial: $0 (free credits)
- Azure AI Search (Basic): ~$75/month
- Azure OpenAI: ~$5-10 (embedding generation)
- **Total: ~$80-85/month**

**Important:** Remember to delete resources when done!

```bash
az group delete --name "rg-clinical-notes-demo" --yes
```

## Demo Scenarios

### Scenario 1: Find Similar Cases

"Show me all cases similar to a patient with diabetes and hypertension"
→ Uses vector similarity search with embeddings

### Scenario 2: Medication Search

"Find all notes mentioning metformin or insulin"
→ Uses keyword search across clinical notes

### Scenario 3: Diagnostic Patterns

"What are common comorbidities with COPD?"
→ Search + aggregation across diagnoses

### Scenario 4: Real-time Updates

Add new clinical note → Auto-indexes → Searchable immediately

## Congratulations!

You've successfully built a production-ready pipeline that:
- Extracts data from Snowflake
- Generates embeddings with Azure OpenAI
- Enables semantic search with Azure AI Search
- Supports incremental updates
- Can scale to millions of records

This forms the foundation for conversational AI applications!
