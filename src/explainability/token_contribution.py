"""Token contribution analysis for explainability."""

from typing import List, Tuple, Dict, Any
import numpy as np
import re


class TokenContributionAnalyzer:
    """Analyze token-level contributions to ranking scores."""

    def __init__(self, ranker: Any):
        """Initialize token contribution analyzer.

        Args:
            ranker: Ranking model with score() method
        """
        self.ranker = ranker

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization.

        Args:
            text: Input text

        Returns:
            List of tokens
        """
        # Split on whitespace and punctuation
        tokens = re.findall(r'\b\w+\b', text.lower())
        return tokens

    def analyze_token_removal(
        self,
        resume: Dict[str, Any],
        job_description: str,
        top_k: int = 10,
    ) -> List[Tuple[str, float]]:
        """Analyze impact of removing individual tokens.

        Args:
            resume: Resume dictionary
            job_description: Job description text
            top_k: Number of top contributing tokens to return

        Returns:
            List of (token, contribution) tuples
        """
        baseline_score = self.ranker.score(resume, job_description)

        tokens = self._tokenize(resume["text"])
        unique_tokens = list(set(tokens))

        contributions = []

        for token in unique_tokens:
            # Remove token from text
            modified_text = re.sub(
                rf'\b{re.escape(token)}\b',
                '',
                resume["text"],
                flags=re.IGNORECASE
            )

            modified_resume = {**resume, "text": modified_text}

            # Get new score
            new_score = self.ranker.score(modified_resume, job_description)

            # Contribution is drop in score
            contribution = baseline_score - new_score

            if contribution > 0.001:  # Only keep meaningful contributions
                contributions.append((token, float(contribution)))

        # Sort by contribution
        contributions.sort(key=lambda x: x[1], reverse=True)

        return contributions[:top_k]

    def find_matching_keywords(
        self,
        resume: Dict[str, Any],
        job_description: str,
    ) -> List[str]:
        """Find keywords that appear in both resume and job description.

        Args:
            resume: Resume dictionary
            job_description: Job description text

        Returns:
            List of matching keywords
        """
        resume_tokens = set(self._tokenize(resume["text"]))
        jd_tokens = set(self._tokenize(job_description))

        matching = list(resume_tokens & jd_tokens)

        # Filter out very common words
        stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"}
        matching = [token for token in matching if token not in stopwords]

        return sorted(matching)

    def get_skill_overlap(
        self,
        resume_skills: List[str],
        job_skills: List[str],
    ) -> Dict[str, List[str]]:
        """Analyze skill overlap.

        Args:
            resume_skills: Skills from resume
            job_skills: Required skills from job

        Returns:
            Dictionary with matched, missing, and extra skills
        """
        resume_set = {s.lower() for s in resume_skills}
        job_set = {s.lower() for s in job_skills}

        return {
            "matched": sorted(list(resume_set & job_set)),
            "missing": sorted(list(job_set - resume_set)),
            "extra": sorted(list(resume_set - job_set)),
        }

    def explain_score(
        self,
        resume: Dict[str, Any],
        job_description: str,
    ) -> Dict[str, Any]:
        """Comprehensive explanation of ranking score.

        Args:
            resume: Resume dictionary
            job_description: Job description text

        Returns:
            Explanation dictionary
        """
        score = self.ranker.score(resume, job_description)

        # Top contributing tokens
        top_tokens = self.analyze_token_removal(resume, job_description, top_k=10)

        # Matching keywords
        matching_keywords = self.find_matching_keywords(resume, job_description)

        return {
            "score": float(score),
            "top_contributing_tokens": top_tokens,
            "matching_keywords": matching_keywords,
            "num_matching_keywords": len(matching_keywords),
        }
