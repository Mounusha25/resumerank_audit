"""Resume Ranking System - ML Evaluation & Auditing Framework

This package provides tools for evaluating and auditing resume ranking models
with a focus on fairness, explainability, and stability.

⚠️ IMPORTANT: This is NOT a hiring decision tool.
This system is designed for evaluation and research purposes only.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__license__ = "MIT"

# Ethical disclaimer
DISCLAIMER = """
This software is for educational and research purposes only.
It is NOT validated for employment decisions and should NOT be used
to make hiring recommendations without proper legal review and compliance validation.
"""


def print_disclaimer():
    """Print ethical disclaimer when package is imported."""
    print("=" * 80)
    print(DISCLAIMER)
    print("=" * 80)
