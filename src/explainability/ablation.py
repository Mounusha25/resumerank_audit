"""Ablation-based explainability.

Explains rankings by removing sections and measuring impact.
"""

from typing import Dict, Any, List
import re


class AblationExplainer:
    """Explain rankings using ablation studies."""

    def __init__(self, ranker: Any):
        """Initialize ablation explainer.

        Args:
            ranker: Ranking model with score() method
        """
        self.ranker = ranker

    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract a specific section from resume text.

        Args:
            text: Resume text
            section_name: Section to extract

        Returns:
            Section text
        """
        # Common section patterns
        patterns = {
            "skills": r"(?i)(skills|technical skills|competencies)(.*?)(?=\n\n|\Z)",
            "experience": r"(?i)(experience|employment|work history)(.*?)(?=\n\n|\Z)",
            "education": r"(?i)(education|academic)(.*?)(?=\n\n|\Z)",
            "summary": r"(?i)(summary|objective|profile)(.*?)(?=\n\n|\Z)",
        }

        pattern = patterns.get(section_name)
        if not pattern:
            return ""

        match = re.search(pattern, text, re.DOTALL)
        return match.group(0) if match else ""

    def _remove_section(self, text: str, section_name: str) -> str:
        """Remove a section from resume text.

        Args:
            text: Resume text
            section_name: Section to remove

        Returns:
            Text with section removed
        """
        section_text = self._extract_section(text, section_name)

        if section_text:
            return text.replace(section_text, "").strip()

        return text

    def explain(
        self,
        resume: Dict[str, Any],
        job_description: str,
        sections: List[str] = None,
    ) -> Dict[str, float]:
        """Explain ranking by ablating sections.

        Args:
            resume: Resume dictionary with 'text' key
            job_description: Job description text
            sections: List of sections to ablate

        Returns:
            Dictionary of section_name -> contribution score
        """
        if sections is None:
            sections = ["skills", "experience", "education", "summary"]

        # Get baseline score
        baseline_score = self.ranker.score(resume, job_description)

        contributions = {}

        for section in sections:
            # Remove section
            modified_text = self._remove_section(resume["text"], section)
            modified_resume = {**resume, "text": modified_text}

            # Get new score
            new_score = self.ranker.score(modified_resume, job_description)

            # Contribution is drop in score
            contribution = baseline_score - new_score

            contributions[section] = float(contribution)

        return contributions

    def explain_batch(
        self,
        resumes: List[Dict[str, Any]],
        job_description: str,
    ) -> Dict[str, Dict[str, float]]:
        """Explain rankings for multiple resumes.

        Args:
            resumes: List of resume dictionaries
            job_description: Job description text

        Returns:
            Dictionary of resume_id -> contributions
        """
        results = {}

        for resume in resumes:
            contributions = self.explain(resume, job_description)
            results[resume["id"]] = contributions

        return results

    def get_most_important_section(
        self,
        resume: Dict[str, Any],
        job_description: str,
    ) -> str:
        """Get the most important section for ranking.

        Args:
            resume: Resume dictionary
            job_description: Job description text

        Returns:
            Name of most important section
        """
        contributions = self.explain(resume, job_description)

        if not contributions:
            return "unknown"

        return max(contributions.items(), key=lambda x: x[1])[0]
