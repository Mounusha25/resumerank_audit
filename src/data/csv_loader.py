"""CSV data loader for resume and job description datasets.

Handles CSV format datasets instead of PDF files.
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re


class CSVResumeLoader:
    """Load and process resume data from CSV."""

    def __init__(self, csv_path: str):
        """Initialize CSV loader.

        Args:
            csv_path: Path to resume CSV file
        """
        self.csv_path = Path(csv_path)
        self.df = None

    def load(self) -> pd.DataFrame:
        """Load CSV file.

        Returns:
            Pandas DataFrame
        """
        print(f"Loading resume CSV from {self.csv_path}...")
        self.df = pd.read_csv(self.csv_path)
        print(f"  Loaded {len(self.df)} resumes")
        print(f"  Columns: {list(self.df.columns[:10])}...")
        return self.df

    def _safe_parse_list(self, value: Any) -> List[str]:
        """Safely parse string representation of list.

        Args:
            value: Value to parse

        Returns:
            List of strings
        """
        if pd.isna(value) or value == 'N/A':
            return []

        if isinstance(value, list):
            return value

        if isinstance(value, str):
            try:
                # Try to parse as Python literal
                parsed = ast.literal_eval(value)
                if isinstance(parsed, list):
                    return [str(item) for item in parsed if item]
                return [value]
            except (ValueError, SyntaxError):
                # If parsing fails, treat as single item
                return [value] if value.strip() else []

        return []

    def _build_resume_text(self, row: pd.Series) -> str:
        """Build full resume text from CSV row.

        Args:
            row: DataFrame row

        Returns:
            Formatted resume text
        """
        sections = []

        # Career Objective / Summary
        if pd.notna(row.get('career_objective')):
            sections.append(f"SUMMARY:\n{row['career_objective']}\n")

        # Skills
        skills = self._safe_parse_list(row.get('skills'))
        if skills:
            sections.append(f"SKILLS:\n{', '.join(skills)}\n")

        # Education
        institutions = self._safe_parse_list(row.get('educational_institution_name'))
        degrees = self._safe_parse_list(row.get('degree_names'))
        majors = self._safe_parse_list(row.get('major_field_of_studies'))
        years = self._safe_parse_list(row.get('passing_years'))

        if institutions or degrees:
            sections.append("EDUCATION:")
            for i in range(max(len(institutions), len(degrees))):
                edu_parts = []
                if i < len(degrees):
                    edu_parts.append(degrees[i])
                if i < len(majors) and majors[i]:
                    edu_parts.append(f"in {majors[i]}")
                if i < len(institutions):
                    edu_parts.append(f"from {institutions[i]}")
                if i < len(years) and years[i] != 'N/A':
                    edu_parts.append(f"({years[i]})")

                if edu_parts:
                    sections.append(" ".join(edu_parts))
            sections.append("")

        # Experience
        companies = self._safe_parse_list(row.get('professional_company_names'))
        positions = self._safe_parse_list(row.get('positions'))
        start_dates = self._safe_parse_list(row.get('start_dates'))
        end_dates = self._safe_parse_list(row.get('end_dates'))
        responsibilities = self._safe_parse_list(row.get('responsibilities'))

        if companies or positions:
            sections.append("EXPERIENCE:")
            for i in range(max(len(companies), len(positions))):
                exp_parts = []
                if i < len(positions):
                    exp_parts.append(positions[i])
                if i < len(companies):
                    exp_parts.append(f"at {companies[i]}")
                if i < len(start_dates) and i < len(end_dates):
                    exp_parts.append(f"({start_dates[i]} - {end_dates[i]})")

                if exp_parts:
                    sections.append(" ".join(exp_parts))

                if i < len(responsibilities) and responsibilities[i]:
                    sections.append(f"  {responsibilities[i]}")

            sections.append("")

        # Languages
        languages = self._safe_parse_list(row.get('languages'))
        if languages:
            sections.append(f"LANGUAGES:\n{', '.join(languages)}\n")

        # Certifications
        cert_providers = self._safe_parse_list(row.get('certification_providers'))
        cert_skills = self._safe_parse_list(row.get('certification_skills'))

        if cert_providers:
            sections.append("CERTIFICATIONS:")
            for i, provider in enumerate(cert_providers):
                cert_text = provider
                if i < len(cert_skills) and cert_skills[i]:
                    cert_text += f" - {cert_skills[i]}"
                sections.append(cert_text)
            sections.append("")

        return "\n".join(sections)

    def process_to_dict(
        self,
        max_resumes: Optional[int] = None,
        clean_text: bool = True,
    ) -> List[Dict[str, Any]]:
        """Process CSV into resume dictionaries.

        Args:
            max_resumes: Maximum number of resumes to process
            clean_text: Whether to clean text

        Returns:
            List of resume dictionaries
        """
        if self.df is None:
            self.load()

        # Limit number of resumes if specified
        df_subset = self.df.head(max_resumes) if max_resumes else self.df

        resumes = []

        for idx, row in df_subset.iterrows():
            # Build full resume text
            text = self._build_resume_text(row)

            # Extract skills
            skills = self._safe_parse_list(row.get('skills'))

            # Calculate years of experience
            years_exp = self._calculate_experience(row)

            resume = {
                "id": f"resume_{idx:06d}",
                "text": text,
                "skills": skills,
                "years_experience": years_exp,
                "career_objective": row.get('career_objective', ''),
                "education": {
                    "institutions": self._safe_parse_list(row.get('educational_institution_name')),
                    "degrees": self._safe_parse_list(row.get('degree_names')),
                    "majors": self._safe_parse_list(row.get('major_field_of_studies')),
                },
                "experience": {
                    "companies": self._safe_parse_list(row.get('professional_company_names')),
                    "positions": self._safe_parse_list(row.get('positions')),
                },
            }

            resumes.append(resume)

            if (idx + 1) % 100 == 0:
                print(f"  Processed {idx + 1} resumes...")

        return resumes

    def _calculate_experience(self, row: pd.Series) -> Optional[int]:
        """Calculate years of experience from dates.

        Args:
            row: DataFrame row

        Returns:
            Years of experience or None
        """
        start_dates = self._safe_parse_list(row.get('start_dates'))
        end_dates = self._safe_parse_list(row.get('end_dates'))

        if not start_dates or not end_dates:
            return None

        total_years = 0

        for start, end in zip(start_dates, end_dates):
            try:
                # Extract year from date strings
                start_year = int(re.search(r'\d{4}', str(start)).group()) if re.search(r'\d{4}', str(start)) else None
                if 'till date' in str(end).lower() or 'present' in str(end).lower():
                    end_year = 2026
                else:
                    end_year = int(re.search(r'\d{4}', str(end)).group()) if re.search(r'\d{4}', str(end)) else None

                if start_year and end_year:
                    total_years += (end_year - start_year)
            except (AttributeError, ValueError):
                continue

        return total_years if total_years > 0 else None


class CSVJobDescriptionLoader:
    """Load and process job descriptions from CSV."""

    def __init__(self, csv_path: str):
        """Initialize CSV loader.

        Args:
            csv_path: Path to job description CSV file
        """
        self.csv_path = Path(csv_path)
        self.df = None

    def load(self) -> pd.DataFrame:
        """Load CSV file.

        Returns:
            Pandas DataFrame
        """
        print(f"Loading job description CSV from {self.csv_path}...")
        self.df = pd.read_csv(self.csv_path)
        print(f"  Loaded {len(self.df)} job descriptions")
        return self.df

    def process_to_dict(
        self,
        max_jobs: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Process CSV into job description dictionaries.

        Args:
            max_jobs: Maximum number of jobs to process

        Returns:
            List of job description dictionaries
        """
        if self.df is None:
            self.load()

        # Limit number of jobs if specified
        df_subset = self.df.head(max_jobs) if max_jobs else self.df

        job_descriptions = []

        for idx, row in df_subset.iterrows():
            # Get job title and description
            title = row.get('Job Title', row.get('job_title', ''))
            description = row.get('Job Description', row.get('job_description', ''))

            # Build full text
            text = f"{title}\n\n{description}" if title else description

            # Extract skills if available
            skills_required = []
            if 'skills_required' in row and pd.notna(row['skills_required']):
                try:
                    skills_required = ast.literal_eval(str(row['skills_required']))
                    if not isinstance(skills_required, list):
                        skills_required = [str(skills_required)]
                except (ValueError, SyntaxError):
                    skills_required = []

            jd = {
                "id": f"jd_{idx:06d}",
                "text": text,
                "title": title,
                "description": description,
                "required_skills": skills_required,
            }

            job_descriptions.append(jd)

        return job_descriptions
