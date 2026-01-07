"""Resume and job description parser.

Extracts text from PDFs and structures the content.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional
import PyPDF2
import pdfplumber


class ResumeParser:
    """Parse resume PDFs and extract structured information."""

    def __init__(self, use_pdfplumber: bool = True):
        """Initialize parser.

        Args:
            use_pdfplumber: If True, use pdfplumber (better quality).
                           If False, use PyPDF2 (faster).
        """
        self.use_pdfplumber = use_pdfplumber

    def parse_pdf(self, pdf_path: Path) -> str:
        """Extract text from PDF file.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text content
        """
        if self.use_pdfplumber:
            return self._parse_with_pdfplumber(pdf_path)
        else:
            return self._parse_with_pypdf2(pdf_path)

    def _parse_with_pdfplumber(self, pdf_path: Path) -> str:
        """Extract text using pdfplumber (better quality)."""
        text_content = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
        except Exception as e:
            raise ValueError(f"Error parsing PDF {pdf_path}: {e}")

        return "\n\n".join(text_content)

    def _parse_with_pypdf2(self, pdf_path: Path) -> str:
        """Extract text using PyPDF2 (faster)."""
        text_content = []

        try:
            with open(pdf_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
        except Exception as e:
            raise ValueError(f"Error parsing PDF {pdf_path}: {e}")

        return "\n\n".join(text_content)

    def extract_sections(self, text: str) -> Dict[str, str]:
        """Extract common resume sections.

        Args:
            text: Resume text

        Returns:
            Dictionary of section_name -> section_content
        """
        sections = {
            "summary": "",
            "experience": "",
            "education": "",
            "skills": "",
            "other": "",
        }

        # Common section headers
        section_patterns = {
            "summary": r"(?i)(summary|objective|profile|about)",
            "experience": r"(?i)(experience|employment|work history)",
            "education": r"(?i)(education|academic|qualifications)",
            "skills": r"(?i)(skills|technical skills|competencies)",
        }

        # Split text by common section markers
        lines = text.split("\n")
        current_section = "other"

        for line in lines:
            line_lower = line.lower().strip()

            # Check if line is a section header
            for section_name, pattern in section_patterns.items():
                if re.match(pattern, line_lower) and len(line_lower) < 50:
                    current_section = section_name
                    break
            else:
                # Add line to current section
                sections[current_section] += line + "\n"

        return {k: v.strip() for k, v in sections.items() if v.strip()}

    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text.

        Args:
            text: Resume text

        Returns:
            List of extracted skills
        """
        # Common skill keywords (this is simplified - expand as needed)
        skill_keywords = [
            "python",
            "java",
            "javascript",
            "c++",
            "sql",
            "machine learning",
            "deep learning",
            "nlp",
            "data analysis",
            "project management",
            "leadership",
            "communication",
            "agile",
            "scrum",
            "aws",
            "azure",
            "docker",
            "kubernetes",
            "git",
            "react",
            "node.js",
            "tensorflow",
            "pytorch",
        ]

        text_lower = text.lower()
        found_skills = []

        for skill in skill_keywords:
            if skill in text_lower:
                found_skills.append(skill)

        return found_skills

    def extract_years_experience(self, text: str) -> Optional[int]:
        """Estimate years of experience from resume.

        Args:
            text: Resume text

        Returns:
            Estimated years of experience, or None if not found
        """
        # Look for patterns like "5 years", "5+ years", "2019-2023"
        year_patterns = [
            r"(\d+)\+?\s*years?",
            r"(\d{4})\s*-\s*(\d{4}|present|current)",
        ]

        years = []

        for pattern in year_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    if len(match) == 2:
                        # Date range
                        try:
                            start = int(match[0])
                            end = 2026 if match[1].lower() in ["present", "current"] else int(match[1])
                            years.append(end - start)
                        except ValueError:
                            continue
                else:
                    # Direct year mention
                    try:
                        years.append(int(match))
                    except ValueError:
                        continue

        return max(years) if years else None


class JobDescriptionParser:
    """Parse job descriptions from text files or PDFs."""

    @staticmethod
    def parse(file_path: Path) -> str:
        """Parse job description from file.

        Args:
            file_path: Path to job description file

        Returns:
            Job description text
        """
        if file_path.suffix.lower() == ".pdf":
            parser = ResumeParser()
            return parser.parse_pdf(file_path)
        else:
            # Plain text file
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()

    @staticmethod
    def extract_required_skills(jd_text: str) -> List[str]:
        """Extract required skills from job description.

        Args:
            jd_text: Job description text

        Returns:
            List of required skills
        """
        # Look for common JD sections
        required_section = re.search(
            r"(?i)(required|requirements|qualifications).*?(?=\n\n|\Z)",
            jd_text,
            re.DOTALL,
        )

        if required_section:
            section_text = required_section.group(0)
            # Extract bullet points or comma-separated items
            skills = re.findall(r"[•\-\*]\s*(.+?)(?=\n|$)", section_text)
            return [s.strip() for s in skills if len(s.strip()) > 3]

        return []
