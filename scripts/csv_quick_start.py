#!/usr/bin/env python3
"""
Quick Start - CSV Data Processing

Minimal dependencies version for immediate use with your CSV files.
"""

import pandas as pd
import json
from pathlib import Path
import ast
import re

print("=" * 80)
print("Resume Ranking System - CSV Quick Start")
print("=" * 80)
print()

# Load resume CSV
print("📊 Loading resume_data.csv...")
resume_df = pd.read_csv("resume_data.csv")
print(f"   Found {len(resume_df)} resumes")

# Process first 400 resumes for better evaluation
print("\n🔄 Processing resumes (using 400 for robust evaluation)...")
resumes = []

for idx, row in resume_df.head(400).iterrows():
    # Build resume text
    sections = []
    
    # Career objective
    if pd.notna(row.get('career_objective')):
        sections.append(f"SUMMARY:\n{row['career_objective']}\n")
    
    # Skills
    try:
        skills = ast.literal_eval(str(row.get('skills', '[]'))) if pd.notna(row.get('skills')) else []
        if skills:
            sections.append(f"SKILLS:\n{', '.join(skills)}\n")
    except:
        skills = []
    
    # Experience
    try:
        companies = ast.literal_eval(str(row.get('professional_company_names', '[]')))
        positions = ast.literal_eval(str(row.get('positions', '[]')))
        
        if companies or positions:
            sections.append("EXPERIENCE:")
            for i in range(max(len(companies) if isinstance(companies, list) else 0, 
                              len(positions) if isinstance(positions, list) else 0)):
                exp_line = []
                if isinstance(positions, list) and i < len(positions):
                    exp_line.append(positions[i])
                if isinstance(companies, list) and i < len(companies):
                    exp_line.append(f"at {companies[i]}")
                if exp_line:
                    sections.append(" ".join(exp_line))
    except:
        pass
    
    text = "\n".join(sections)
    
    resume = {
        "id": f"resume_{idx:06d}",
        "text": text,
        "skills": skills if isinstance(skills, list) else [],
    }
    
    resumes.append(resume)

# Save resumes
Path("data/processed").mkdir(parents=True, exist_ok=True)
with open("data/processed/resumes.json", "w") as f:
    json.dump(resumes, f, indent=2)

print(f"✅ Processed {len(resumes)} resumes")
print(f"   Saved to: data/processed/resumes.json")

# Load job description CSV
print("\n📊 Loading job_title_des.csv...")
jd_df = pd.read_csv("job_title_des.csv")
print(f"   Found {len(jd_df)} job descriptions")

# Process first 100 job descriptions for better coverage
print("\n🔄 Processing job descriptions (using 100 for diversity)...")
job_descriptions = []

for idx, row in jd_df.head(100).iterrows():
    title = row.get('Job Title', '')
    description = row.get('Job Description', '')
    
    text = f"{title}\n\n{description}" if title else description
    
    jd = {
        "id": f"jd_{idx:06d}",
        "text": text,
        "title": title,
        "required_skills": [],
    }
    
    job_descriptions.append(jd)

# Save job descriptions
with open("data/processed/job_descriptions.json", "w") as f:
    json.dump(job_descriptions, f, indent=2)

print(f"✅ Processed {len(job_descriptions)} job descriptions")
print(f"   Saved to: data/processed/job_descriptions.json")

print("\n" + "=" * 80)
print("✅ Data preparation complete!")
print()
print("📊 Dataset Summary:")
print(f"   - Resumes: {len(resumes)}")
print(f"   - Job Descriptions: {len(job_descriptions)}")
print()
print("🚀 Next step: Run evaluation")
print("   python3 scripts/run_evaluation.py")
print("=" * 80)
