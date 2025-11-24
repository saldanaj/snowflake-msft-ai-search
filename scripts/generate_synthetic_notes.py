#!/usr/bin/env python3
"""
Generate synthetic clinical notes for the demo.

This script creates realistic clinical notes based on common medical scenarios.
"""

import random
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configuration
NUM_RECORDS = 75  # Generate 75 records
OUTPUT_DIR = project_root / "data"
OUTPUT_FILE = OUTPUT_DIR / "synthetic_clinical_notes.json"
SQL_FILE = OUTPUT_DIR / "insert_clinical_notes.sql"

# Data for generating realistic notes
FIRST_NAMES_M = ["John", "Robert", "Michael", "James", "David", "William", "Richard", "Joseph", "Charles", "Thomas",
                  "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Joshua", "Kenneth"]
FIRST_NAMES_F = ["Mary", "Patricia", "Jennifer", "Linda", "Barbara", "Elizabeth", "Susan", "Jessica", "Sarah", "Karen",
                  "Nancy", "Lisa", "Betty", "Margaret", "Sandra", "Ashley", "Kimberly", "Emily", "Donna", "Michelle"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
               "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
               "Lee", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker"]

# Clinical scenarios with realistic data
CLINICAL_SCENARIOS = [
    {
        "condition": "Hypertension and Type 2 Diabetes",
        "age_range": (45, 75),
        "chief_complaint": "follow-up of chronic conditions",
        "history": "reports compliance with medications but notes occasional headaches",
        "vitals": {"bp": (135, 155, 85, 95), "temp": (97.0, 98.5), "weight": (180, 250), "hr": (70, 90)},
        "physical_exam": "no acute distress, heart RRR with no murmurs, lungs clear bilaterally",
        "labs": "fasting glucose: 145-165 mg/dL, HbA1c: 7.5-9.0%, LDL 110-140 mg/dL, HDL 35-45 mg/dL",
        "diagnosis": "Essential hypertension, Type 2 diabetes",
        "icd10": "I10, E11.65",
        "medications": ["metformin 1000 mg BID", "lisinopril 10-20 mg daily", "atorvastatin 20 mg daily"],
        "follow_up": [8, 12, 16],
        "encounter_type": "Follow-up Visit"
    },
    {
        "condition": "Anxiety and Depression",
        "age_range": (25, 50),
        "chief_complaint": "follow-up on anxiety and depression",
        "history": "mentions worsening anxiety episodes triggered by work stress, denies suicidal ideation",
        "vitals": {"bp": (110, 130, 70, 85), "temp": (97.5, 98.5), "weight": (120, 180), "hr": (65, 85)},
        "physical_exam": "no acute distress, engages cooperatively in conversation, appropriate affect",
        "labs": "PHQ-9 score: 10-16 (moderate depression), GAD-7 score: 8-12 (mild-moderate anxiety)",
        "diagnosis": "Major depressive disorder, Generalized anxiety disorder",
        "icd10": "F33.1, F41.1",
        "medications": ["sertraline 50-150 mg daily", "buspirone 15 mg BID", "hydroxyzine 25 mg PRN anxiety"],
        "follow_up": [4, 6, 8],
        "encounter_type": "Mental Health Follow-up"
    },
    {
        "condition": "Chronic Low Back Pain",
        "age_range": (35, 65),
        "chief_complaint": "evaluation of chronic back pain",
        "history": "reports pain intensity 5-7/10, exacerbated with prolonged sitting, occasional radiation to leg",
        "vitals": {"bp": (125, 145, 75, 90), "temp": (97.8, 98.6), "weight": (200, 280), "hr": (72, 88)},
        "physical_exam": "neurologically intact, tenderness over lumbar spine, mild restriction in forward flexion",
        "labs": "MRI lumbar spine shows L4-L5 or L5-S1 degenerative disc changes",
        "diagnosis": "Chronic low back pain, lumbar spondylosis",
        "icd10": "M54.5, M47.816",
        "medications": ["gabapentin 300-600 mg TID", "meloxicam 15 mg daily", "cyclobenzaprine 10 mg TID PRN"],
        "follow_up": [6, 8, 12],
        "encounter_type": "Pain Management"
    },
    {
        "condition": "COPD and CHF",
        "age_range": (65, 85),
        "chief_complaint": "routine follow-up for COPD and heart failure",
        "history": "experiences dyspnea on exertion, denies chest pain, reports mild peripheral edema",
        "vitals": {"bp": (130, 150, 70, 85), "temp": (97.5, 98.5), "weight": (160, 200), "hr": (80, 100)},
        "physical_exam": "bilateral crackles at lung bases, S3 heart sound, mild peripheral edema (+1 to +2)",
        "labs": "BNP elevated at 300-450 pg/mL, creatinine stable at 1.0-1.5 mg/dL, oxygen saturation 88-92%",
        "diagnosis": "CHF exacerbation, COPD",
        "icd10": "I50.9, J44.9",
        "medications": ["furosemide 40-80 mg daily", "tiotropium inhaled daily", "carvedilol 12.5 mg BID"],
        "follow_up": [2, 4, 6],
        "encounter_type": "Cardiopulmonary Follow-up"
    },
    {
        "condition": "Asthma",
        "age_range": (5, 45),
        "chief_complaint": "follow-up for asthma management",
        "history": "reports occasional wheezing during colds, uses rescue inhaler 2-3 times per week",
        "vitals": {"bp": (105, 125, 65, 80), "temp": (97.5, 98.5), "weight": (100, 180), "hr": (70, 95)},
        "physical_exam": "lung auscultation reveals occasional expiratory wheezes, no respiratory distress",
        "labs": "Peak flow: 75-85% of predicted, spirometry shows mild obstruction",
        "diagnosis": "Moderate persistent asthma",
        "icd10": "J45.40",
        "medications": ["fluticasone/salmeterol 250/50 mcg BID", "albuterol inhaler PRN", "montelukast 10 mg daily"],
        "follow_up": [12, 16, 24],
        "encounter_type": "Pulmonary Follow-up"
    },
    {
        "condition": "Osteoarthritis",
        "age_range": (55, 80),
        "chief_complaint": "chronic knee/hip pain",
        "history": "reports joint pain and stiffness, worse in morning, improves with activity",
        "vitals": {"bp": (130, 145, 75, 88), "temp": (97.5, 98.5), "weight": (170, 240), "hr": (68, 82)},
        "physical_exam": "joint crepitus noted, mild effusion, reduced range of motion, no erythema",
        "labs": "X-ray shows joint space narrowing and osteophyte formation",
        "diagnosis": "Osteoarthritis of knee/hip",
        "icd10": "M17.11, M16.11",
        "medications": ["celecoxib 200 mg daily", "acetaminophen 1000 mg TID", "glucosamine 1500 mg daily"],
        "follow_up": [12, 16, 24],
        "encounter_type": "Orthopedic Follow-up"
    },
    {
        "condition": "Hypothyroidism",
        "age_range": (30, 70),
        "chief_complaint": "thyroid disorder follow-up",
        "history": "reports fatigue and weight gain, compliant with thyroid medication",
        "vitals": {"bp": (115, 135, 70, 85), "temp": (97.0, 98.0), "weight": (140, 200), "hr": (60, 75)},
        "physical_exam": "thyroid non-palpable, no nodules, normal cardiovascular exam",
        "labs": "TSH: 5.5-8.5 mIU/L, Free T4: 0.7-0.9 ng/dL",
        "diagnosis": "Hypothyroidism",
        "icd10": "E03.9",
        "medications": ["levothyroxine 75-125 mcg daily"],
        "follow_up": [12, 16, 24],
        "encounter_type": "Endocrine Follow-up"
    },
    {
        "condition": "Migraine Headaches",
        "age_range": (20, 55),
        "chief_complaint": "recurrent migraine headaches",
        "history": "reports 3-5 headaches per month, photophobia and nausea with attacks",
        "vitals": {"bp": (110, 130, 70, 80), "temp": (97.8, 98.6), "weight": (120, 180), "hr": (65, 80)},
        "physical_exam": "neurological exam normal, no focal deficits",
        "labs": "No labs indicated, clinical diagnosis",
        "diagnosis": "Migraine without aura",
        "icd10": "G43.009",
        "medications": ["sumatriptan 100 mg PRN", "propranolol 80 mg daily", "topiramate 50 mg BID"],
        "follow_up": [8, 12, 16],
        "encounter_type": "Neurology Follow-up"
    },
    {
        "condition": "Pre-surgical Evaluation",
        "age_range": (3, 75),
        "chief_complaint": "pre-surgical evaluation",
        "history": "scheduled for elective surgery, no recent illnesses",
        "vitals": {"bp": (110, 140, 65, 85), "temp": (97.5, 98.5), "weight": (100, 220), "hr": (70, 90)},
        "physical_exam": "general health good, cardiovascular and pulmonary systems stable",
        "labs": "CBC, CMP, PT/INR within normal limits",
        "diagnosis": "Pre-operative evaluation",
        "icd10": "Z01.818",
        "medications": ["Hold aspirin 7 days prior", "Continue home medications"],
        "follow_up": [1, 2],
        "encounter_type": "Pre-operative Visit"
    },
    {
        "condition": "Annual Physical",
        "age_range": (25, 75),
        "chief_complaint": "annual physical examination",
        "history": "feels well, exercises regularly, balanced diet, no current complaints",
        "vitals": {"bp": (110, 130, 65, 80), "temp": (97.8, 98.6), "weight": (120, 190), "hr": (60, 80)},
        "physical_exam": "unremarkable, clear lungs, RRR heart sounds, normal neurological function",
        "labs": "CBC, CMP, lipid panel within normal limits",
        "diagnosis": "Health maintenance",
        "icd10": "Z00.00",
        "medications": ["Continue current regimen"],
        "follow_up": [52],  # 1 year
        "encounter_type": "Annual Physical"
    }
]

def generate_vitals(vitals_template):
    """Generate realistic vital signs."""
    bp_sys = random.randint(vitals_template["bp"][0], vitals_template["bp"][1])
    bp_dia = random.randint(vitals_template["bp"][2], vitals_template["bp"][3])
    temp = round(random.uniform(vitals_template["temp"][0], vitals_template["temp"][1]), 1)
    weight = random.randint(vitals_template["weight"][0], vitals_template["weight"][1])
    hr = random.randint(vitals_template["hr"][0], vitals_template["hr"][1]) if "hr" in vitals_template else None

    vitals_text = f"BP {bp_sys}/{bp_dia} | Temp {temp} °F | Wt {weight} lb"
    if hr:
        vitals_text += f" | HR {hr}"

    return {
        "bp_systolic": bp_sys,
        "bp_diastolic": bp_dia,
        "temperature_f": temp,
        "weight_lbs": weight,
        "heart_rate": hr,
        "vitals_text": vitals_text
    }

def generate_clinical_note(note_id, scenario, patient_name, age, gender, encounter_date):
    """Generate a complete clinical note."""

    vitals = generate_vitals(scenario["vitals"])
    medications = random.sample(scenario["medications"], min(len(scenario["medications"]), random.randint(1, 3)))
    follow_up_weeks = random.choice(scenario["follow_up"])

    # Build the full clinical note
    full_note = f"""{patient_name}, a {age}-year-old {gender.lower()}, presents today for {scenario["chief_complaint"]}. """
    full_note += f"""The patient {scenario["history"]}. """
    full_note += f"""Personal, social, and family histories have been reviewed and updated in EMR. """

    # Add vitals
    full_note += f"""{vitals["vitals_text"]}. """

    # Physical exam
    full_note += f"""Physical exam reveals {scenario["physical_exam"]}. """

    # Labs
    if scenario["labs"] != "No labs indicated, clinical diagnosis":
        full_note += f"""Labs show {scenario["labs"]}. """

    # Assessment
    full_note += f"""Assessment: {scenario["diagnosis"]} ({scenario["icd10"]}). """

    # Plan
    full_note += f"""Plan: """
    for i, med in enumerate(medications):
        if i == 0:
            full_note += f"""Prescribe {med}"""
        elif i == len(medications) - 1:
            full_note += f""", and {med}"""
        else:
            full_note += f""", {med}"""
    full_note += f""". Follow up in {follow_up_weeks} weeks."""

    return {
        "note_id": note_id,
        "patient_name": patient_name,
        "patient_age": age,
        "patient_gender": gender,
        "encounter_date": encounter_date.isoformat(),
        "encounter_type": scenario["encounter_type"],
        "chief_complaint": scenario["chief_complaint"],
        "medical_history": scenario["history"],
        "bp_systolic": vitals["bp_systolic"],
        "bp_diastolic": vitals["bp_diastolic"],
        "temperature_f": vitals["temperature_f"],
        "weight_lbs": vitals["weight_lbs"],
        "heart_rate": vitals["heart_rate"],
        "vitals_text": vitals["vitals_text"],
        "physical_exam": scenario["physical_exam"],
        "lab_results": scenario["labs"],
        "assessment": scenario["diagnosis"],
        "icd10_codes": scenario["icd10"],
        "diagnosis_summary": scenario["diagnosis"],
        "treatment_plan": f"""Medications: {', '.join(medications)}. Follow-up in {follow_up_weeks} weeks.""",
        "medications_prescribed": ', '.join(medications),
        "procedures_planned": "",
        "referrals": "",
        "follow_up_weeks": follow_up_weeks,
        "full_clinical_note": full_note,
        "provider_name": f"Dr. {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Davis'])}",
        "department": random.choice(["Internal Medicine", "Family Medicine", "Cardiology", "Pulmonology", "Orthopedics"]),
        "note_status": "FINAL",
        "created_at": encounter_date.isoformat(),
        "updated_at": encounter_date.isoformat()
    }

def generate_all_notes(num_records=NUM_RECORDS):
    """Generate all clinical notes."""
    notes = []

    for i in range(num_records):
        # Select random scenario
        scenario = random.choice(CLINICAL_SCENARIOS)

        # Generate patient demographics
        gender = random.choice(["Male", "Female"])
        first_name = random.choice(FIRST_NAMES_M if gender == "Male" else FIRST_NAMES_F)
        last_name = random.choice(LAST_NAMES)
        patient_name = f"{first_name} {last_name}"

        age = random.randint(scenario["age_range"][0], scenario["age_range"][1])

        # Generate encounter date (within last 2 years)
        days_ago = random.randint(0, 730)
        encounter_date = datetime.now() - timedelta(days=days_ago)

        note_id = f"NOTE{i+1:05d}"

        note = generate_clinical_note(note_id, scenario, patient_name, age, gender, encounter_date)
        notes.append(note)

    return notes

def save_to_json(notes, output_file):
    """Save notes to JSON file."""
    with open(output_file, 'w') as f:
        json.dump(notes, f, indent=2)
    print(f"[OK] Saved {len(notes)} notes to {output_file}")

def generate_sql_insert(notes, sql_file):
    """Generate SQL INSERT statements."""
    with open(sql_file, 'w') as f:
        f.write("-- =============================================\n")
        f.write("-- Insert Clinical Notes Data\n")
        f.write("-- =============================================\n\n")
        f.write("USE DATABASE CLINICAL_NOTES_DB;\n")
        f.write("USE SCHEMA MEDICAL_RECORDS;\n")
        f.write("USE WAREHOUSE DEMO_WAREHOUSE;\n\n")

        for note in notes:
            # Escape single quotes in text fields
            def escape_sql(text):
                if text is None:
                    return "NULL"
                return f"'{str(text).replace(chr(39), chr(39)+chr(39))}'"

            f.write(f"""INSERT INTO PATIENT_CLINICAL_NOTES (
    note_id, patient_name, patient_age, patient_gender, encounter_date, encounter_type,
    chief_complaint, medical_history, bp_systolic, bp_diastolic, temperature_f, weight_lbs, heart_rate, vitals_text,
    physical_exam, lab_results, assessment, icd10_codes, diagnosis_summary,
    treatment_plan, medications_prescribed, procedures_planned, referrals, follow_up_weeks,
    full_clinical_note, provider_name, department, note_status, created_at, updated_at
) VALUES (
    {escape_sql(note['note_id'])},
    {escape_sql(note['patient_name'])},
    {note['patient_age']},
    {escape_sql(note['patient_gender'])},
    '{note['encounter_date']}'::TIMESTAMP_NTZ,
    {escape_sql(note['encounter_type'])},
    {escape_sql(note['chief_complaint'])},
    {escape_sql(note['medical_history'])},
    {note['bp_systolic']},
    {note['bp_diastolic']},
    {note['temperature_f']},
    {note['weight_lbs']},
    {note['heart_rate'] if note['heart_rate'] else 'NULL'},
    {escape_sql(note['vitals_text'])},
    {escape_sql(note['physical_exam'])},
    {escape_sql(note['lab_results'])},
    {escape_sql(note['assessment'])},
    {escape_sql(note['icd10_codes'])},
    {escape_sql(note['diagnosis_summary'])},
    {escape_sql(note['treatment_plan'])},
    {escape_sql(note['medications_prescribed'])},
    {escape_sql(note['procedures_planned'])},
    {escape_sql(note['referrals'])},
    {note['follow_up_weeks']},
    {escape_sql(note['full_clinical_note'])},
    {escape_sql(note['provider_name'])},
    {escape_sql(note['department'])},
    {escape_sql(note['note_status'])},
    '{note['created_at']}'::TIMESTAMP_NTZ,
    '{note['updated_at']}'::TIMESTAMP_NTZ
);\n\n""")

        f.write("\n-- Verify data insertion\n")
        f.write("SELECT COUNT(*) as total_notes FROM PATIENT_CLINICAL_NOTES;\n")
        f.write("SELECT * FROM PATIENT_CLINICAL_NOTES LIMIT 5;\n")

    print(f"[OK] Generated SQL script: {sql_file}")

def main():
    """Main execution function."""
    print("="*80)
    print("Synthetic Clinical Notes Generator")
    print("="*80)
    print(f"\nGenerating {NUM_RECORDS} clinical notes...")

    # Generate notes
    notes = generate_all_notes(NUM_RECORDS)

    # Save to JSON
    save_to_json(notes, OUTPUT_FILE)

    # Generate SQL
    generate_sql_insert(notes, SQL_FILE)

    print("\n" + "="*80)
    print("Generation Complete!")
    print("="*80)
    print(f"\nGenerated files:")
    print(f"  - JSON: {OUTPUT_FILE}")
    print(f"  - SQL:  {SQL_FILE}")
    print(f"\nNext steps:")
    print("  1. Review the generated data in the JSON file")
    print("  2. Run snowflake_schema.sql in Snowflake to create tables")
    print("  3. Run insert_clinical_notes.sql to load data")
    print()

if __name__ == "__main__":
    main()
