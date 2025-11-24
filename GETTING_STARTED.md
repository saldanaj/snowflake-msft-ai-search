# Getting Started - What's Ready and What to Do Next

## Summary

✅ **All data preparation is complete!** You now have everything needed to run the demo.

## What's Been Created

### 1. Database Schema and Data ✅
- **Snowflake DDL:** `data/snowflake_schema.sql` - Creates database, schema, warehouse, and table
- **Sample Data:** `data/insert_clinical_notes.sql` - 75 realistic clinical notes ready to load
- **JSON Export:** `data/synthetic_clinical_notes.json` - Data in JSON format for review

### 2. Complete Pipeline Infrastructure ✅
- **Snowflake Extractor:** Pulls clinical notes with incremental support
- **Azure OpenAI Embedder:** Generates embeddings with batching
- **Azure AI Search Indexer:** Creates vector search index
- **Pipeline Orchestrator:** Coordinates the entire flow

### 3. Configuration Files ✅
- **Environment Config:** `config/.env.example` - Pre-configured for clinical notes
- **Pipeline Config:** `config/config.yaml.example` - Schema-aligned settings
- **Requirements:** `requirements.txt` - All dependencies listed

### 4. Documentation ✅
- **Quick Start:** `QUICKSTART.md` - 30-minute end-to-end guide
- **Snowflake Setup:** `docs/SNOWFLAKE_SETUP.md` - Detailed database setup
- **Infrastructure:** `docs/02-infrastructure.md` - Azure deployment
- **Pipeline Operations:** `docs/03-running-pipeline.md` - How to run
- **Summary:** `DATA_PREPARATION_SUMMARY.md` - What was accomplished

### 5. Helper Scripts ✅
- **Data Generator:** `scripts/generate_synthetic_notes.py`
- **Pipeline Runner:** `scripts/run_pipeline.py`
- **Environment Setup:** `scripts/install_requirements.ps1/sh`

## Important: Use Virtual Environment

All required packages are in `requirements.txt`:
- pandas, numpy - Data processing
- openpyxl, xlrd - Excel file support
- snowflake-connector-python - Snowflake connectivity
- azure-identity, azure-search-documents - Azure AI Search
- openai - Azure OpenAI embeddings
- pyyaml, python-dotenv - Configuration
- structlog - Logging

**To install all dependencies in your venv:**

### Windows
```powershell
.\scripts\install_requirements.ps1
```

### Linux/Mac
```bash
chmod +x scripts/install_requirements.sh
./scripts/install_requirements.sh
```

**Or manually:**
```bash
# Activate venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac

# Install all requirements
pip install -r requirements.txt
```

## Your Next Steps (Choose Your Starting Point)

### Option 1: Follow the Quick Start (Recommended)

Open `QUICKSTART.md` for a 30-minute guided setup that covers:
1. Loading data into Snowflake (10 min)
2. Deploying Azure infrastructure (10 min)
3. Configuring and running pipeline (10 min)

### Option 2: Step-by-Step Approach

1. **Set up Snowflake first:**
   - Read `docs/SNOWFLAKE_SETUP.md`
   - Run the SQL scripts
   - Test connection

2. **Deploy Azure services:**
   - Read `docs/02-infrastructure.md`
   - Deploy using Bicep scripts
   - Get API keys

3. **Configure pipeline:**
   - Copy config files
   - Fill in credentials
   - Verify setup

4. **Run pipeline:**
   - Read `docs/03-running-pipeline.md`
   - Execute first run
   - Test incremental updates

## File Locations Quick Reference

### Data Files
```
data/
├── snowflake_schema.sql              ← Run this first in Snowflake
├── insert_clinical_notes.sql         ← Run this second in Snowflake
└── synthetic_clinical_notes.json     ← Review generated data
```

### Configuration
```
config/
├── .env.example                      ← Copy to .env and fill in
└── config.yaml.example               ← Copy to config.yaml (ready to use)
```

### Scripts
```
scripts/
├── install_requirements.ps1/sh       ← Install dependencies
├── run_pipeline.py                   ← Main pipeline execution
└── generate_synthetic_notes.py       ← Regenerate data if needed
```

### Documentation
```
QUICKSTART.md                         ← Start here for 30-min setup
DATA_PREPARATION_SUMMARY.md          ← What was accomplished
docs/
├── SNOWFLAKE_SETUP.md               ← Snowflake detailed guide
├── 02-infrastructure.md              ← Azure deployment
└── 03-running-pipeline.md            ← Pipeline operations
```

## Quick Validation Checklist

Before starting, verify you have:

- [ ] Snowflake trial account created
- [ ] Azure subscription with OpenAI access
- [ ] Python 3.10+ installed
- [ ] Virtual environment exists (`venv/` directory)
- [ ] All requirements installed in venv
- [ ] Azure CLI installed (for infrastructure deployment)

## Sample Commands

### Test Environment
```bash
# Activate venv
.\venv\Scripts\Activate.ps1

# Verify packages installed
pip list

# Should see: pandas, snowflake-connector-python, azure-search-documents, openai, etc.
```

### Configure
```bash
# Copy config files
cp config/.env.example config/.env
cp config/config.yaml.example config/config.yaml

# Edit config/.env with your credentials
```

### Run Pipeline
```bash
# First run - create index and load all data
python scripts/run_pipeline.py --full --recreate-index

# Incremental run - only new/updated records
python scripts/run_pipeline.py --incremental
```

## What You'll Have After Setup

1. ✅ **Snowflake:** Database with 75 clinical notes
2. ✅ **Azure OpenAI:** Text embedding generation
3. ✅ **Azure AI Search:** Vector search index with semantic capabilities
4. ✅ **Pipeline:** Automated data flow with incremental updates
5. ✅ **Searchable Data:** Clinical notes ready for conversational AI

## Data Overview

**75 synthetic clinical notes covering:**
- Chronic conditions (diabetes, hypertension, etc.)
- Mental health (anxiety, depression)
- Pain management (back pain, arthritis)
- Pulmonary (COPD, asthma)
- Routine care (physicals, pre-op)

**Patient demographics:**
- Ages: 3-85 years
- Both genders
- Realistic vital signs
- Authentic ICD-10 codes
- Common medications

## Example Clinical Note

```
Daniel Martin, a 77-year-old male, presents today for chronic knee/hip pain.
The patient reports joint pain and stiffness, worse in morning, improves with
activity. BP 137/84 | Temp 97.7 °F | Wt 194 lb | HR 81. Physical exam reveals
joint crepitus noted, mild effusion, reduced range of motion, no erythema.
Labs show X-ray shows joint space narrowing and osteophyte formation.
Assessment: Osteoarthritis of knee/hip (M17.11, M16.11). Plan: Prescribe
celecoxib 200 mg daily, acetaminophen 1000 mg TID, and glucosamine 1500 mg
daily. Follow up in 16 weeks.
```

## Key Features of This Demo

1. **Production-Ready Code**
   - Error handling and retries
   - Structured logging
   - Incremental processing
   - Batch operations

2. **Scalable Architecture**
   - Modular components
   - Configuration-driven
   - Easy to extend
   - Container-ready

3. **Comprehensive Documentation**
   - Step-by-step guides
   - Troubleshooting help
   - Cost estimates
   - Best practices

4. **Real-World Scenarios**
   - Authentic medical data patterns
   - Common clinical workflows
   - Incremental updates
   - Search and retrieval

## Support Resources

- **Quick Start:** See `QUICKSTART.md`
- **Detailed Setup:** See `docs/SNOWFLAKE_SETUP.md`
- **Infrastructure:** See `docs/02-infrastructure.md`
- **Pipeline Help:** See `docs/03-running-pipeline.md`
- **Future Ideas:** See `docs/04-future-enhancements.md`

## Questions?

- Review the documentation in `docs/` folder
- Check `QUICKSTART.md` for step-by-step instructions
- Verify all prerequisites are met
- Ensure virtual environment is activated

## Ready to Start?

1. Install requirements: `.\scripts\install_requirements.ps1`
2. Open `QUICKSTART.md`
3. Follow Phase 1 (Snowflake Setup)

Good luck with your demo! 🚀
