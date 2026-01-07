#!/usr/bin/env python
"""
Data preparation script for CSV datasets.

Processes CSV files containing resumes and job descriptions.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import yaml
import json
from src.data.csv_loader import CSVResumeLoader, CSVJobDescriptionLoader
from src.data.preprocessor import TextPreprocessor
from src.data.privacy import PIIRedactor


def main():
    """Run CSV data preparation."""
    print("=" * 80)
    print("Resume Ranking System - CSV Data Preparation")
    print("=" * 80)
    print()

    # Load configuration
    with open("config/config.yaml", "r") as f:
        config = yaml.safe_load(f)

    # Initialize processors
    preprocessor = TextPreprocessor(
        lowercase=False,
        remove_special_chars=True,
    )

    redactor = PIIRedactor(
        redact_names=config["privacy"]["anonymize_names"],
        redact_contact=config["privacy"]["redact_pii"],
    )

    # Process resumes from CSV
    resume_csv_path = "resume_data.csv"
    
    if Path(resume_csv_path).exists():
        print(f"Processing resumes from {resume_csv_path}...")
        
        resume_loader = CSVResumeLoader(resume_csv_path)
        resumes = resume_loader.process_to_dict(max_resumes=1000)  # Limit for initial testing
        
        # Apply preprocessing and PII redaction
        for resume in resumes:
            # Clean text
            resume["text"] = preprocessor.clean(resume["text"])
            
            # Redact PII
            resume["text"] = redactor.redact(resume["text"])
        
        # Save processed resumes
        output_path = Path(config["data"]["processed_resumes"])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w") as f:
            json.dump(resumes, f, indent=2)
        
        print(f"\n✓ Processed {len(resumes)} resumes")
        print(f"  Saved to: {output_path}")
    else:
        print(f"\n⚠ Resume CSV not found: {resume_csv_path}")
        print("  Please ensure resume_data.csv is in the project root")

    # Process job descriptions from CSV
    jd_csv_path = "job_title_des.csv"
    
    if Path(jd_csv_path).exists():
        print(f"\nProcessing job descriptions from {jd_csv_path}...")
        
        jd_loader = CSVJobDescriptionLoader(jd_csv_path)
        job_descriptions = jd_loader.process_to_dict(max_jobs=100)  # Limit for initial testing
        
        # Apply preprocessing
        for jd in job_descriptions:
            jd["text"] = preprocessor.clean(jd["text"])
        
        # Save processed job descriptions
        output_path = Path(config["data"]["processed_job_descriptions"])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w") as f:
            json.dump(job_descriptions, f, indent=2)
        
        print(f"\n✓ Processed {len(job_descriptions)} job descriptions")
        print(f"  Saved to: {output_path}")
    else:
        print(f"\n⚠ Job description CSV not found: {jd_csv_path}")
        print("  Please ensure job_title_des.csv is in the project root")

    print("\n" + "=" * 80)
    print("CSV data preparation complete!")
    print("\nNext step: Run evaluation")
    print("  python scripts/run_evaluation.py")
    print("=" * 80)


if __name__ == "__main__":
    main()
