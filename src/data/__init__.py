"""Data processing and preparation module.

Handles:
- PDF resume parsing
- Text cleaning and normalization
- PII redaction
- Structured field extraction
- Data splitting
"""

from .loader import load_resumes, load_job_descriptions
from .parser import ResumeParser
from .preprocessor import TextPreprocessor
from .privacy import PIIRedactor

__all__ = [
    "load_resumes",
    "load_job_descriptions",
    "ResumeParser",
    "TextPreprocessor",
    "PIIRedactor",
]
