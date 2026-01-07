#!/usr/bin/env python
"""
Data preparation script.

Processes raw resume PDFs and job descriptions into structured JSON format.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import yaml
import json
from src.data.parser import ResumeParser, JobDescriptionParser
from src.data.preprocessor import TextPreprocessor
from src.data.privacy import PIIRedactor


def prepare_resumes(raw_dir: Path, preprocessor: TextPreprocessor, redactor: PIIRedactor) -> list:
    """Prepare resume data.

    Args:
        raw_dir: Directory containing resume PDFs
        preprocessor: Text preprocessor
        redactor: PII redactor

    Returns:
        List of processed resume dictionaries
    """
    parser = ResumeParser(use_pdfplumber=True)
    resumes = []

    pdf_files = list(raw_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"Warning: No PDF files found in {raw_dir}")
        return []

    print(f"Processing {len(pdf_files)} resumes...")

    for i, pdf_path in enumerate(pdf_files, 1):
        try:
            # Parse PDF
            text = parser.parse_pdf(pdf_path)

            # Clean text
            text = preprocessor.clean(text)

            # Redact PII
            text = redactor.redact(text)

            # Extract sections and skills
            sections = parser.extract_sections(text)
            skills = parser.extract_skills(text)
            years_exp = parser.extract_years_experience(text)

            resume = {
                "id": f"resume_{i:04d}",
                "filename": pdf_path.name,
                "text": text,
                "sections": sections,
                "skills": skills,
                "years_experience": years_exp,
            }

            resumes.append(resume)

            if i % 10 == 0:
                print(f"  Processed {i}/{len(pdf_files)} resumes...")

        except Exception as e:
            print(f"  Error processing {pdf_path.name}: {e}")
            continue

    return resumes


def prepare_job_descriptions(raw_dir: Path, preprocessor: TextPreprocessor) -> list:
    """Prepare job description data.

    Args:
        raw_dir: Directory containing job description files
        preprocessor: Text preprocessor

    Returns:
        List of processed job description dictionaries
    """
    job_descriptions = []

    # Support both .txt and .pdf files
    files = list(raw_dir.glob("*.txt")) + list(raw_dir.glob("*.pdf"))

    if not files:
        print(f"Warning: No job description files found in {raw_dir}")
        return []

    print(f"Processing {len(files)} job descriptions...")

    for i, file_path in enumerate(files, 1):
        try:
            # Parse file
            text = JobDescriptionParser.parse(file_path)

            # Clean text
            text = preprocessor.clean(text)

            # Extract required skills
            required_skills = JobDescriptionParser.extract_required_skills(text)

            jd = {
                "id": f"jd_{i:04d}",
                "filename": file_path.name,
                "text": text,
                "required_skills": required_skills,
            }

            job_descriptions.append(jd)

        except Exception as e:
            print(f"  Error processing {file_path.name}: {e}")
            continue

    return job_descriptions


def main():
    """Run data preparation."""
    print("=" * 80)
    print("Resume Ranking System - Data Preparation")
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

    # Prepare resumes
    raw_resume_dir = Path(config["data"]["raw_resumes"])
    resumes = prepare_resumes(raw_resume_dir, preprocessor, redactor)

    if resumes:
        # Save resumes
        output_path = Path(config["data"]["processed_resumes"])
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(resumes, f, indent=2)

        print(f"\n✓ Processed {len(resumes)} resumes")
        print(f"  Saved to: {output_path}")
    else:
        print("\n⚠ No resumes processed")

    # Prepare job descriptions
    raw_jd_dir = Path(config["data"]["raw_job_descriptions"])
    job_descriptions = prepare_job_descriptions(raw_jd_dir, preprocessor)

    if job_descriptions:
        # Save job descriptions
        output_path = Path(config["data"]["processed_job_descriptions"])
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(job_descriptions, f, indent=2)

        print(f"\n✓ Processed {len(job_descriptions)} job descriptions")
        print(f"  Saved to: {output_path}")
    else:
        print("\n⚠ No job descriptions processed")

    print("\n" + "=" * 80)
    print("Data preparation complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
