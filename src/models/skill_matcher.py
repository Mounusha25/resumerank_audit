"""Skill-based matching model."""

from typing import List, Tuple, Dict, Any, Set


class SkillMatcher:
    """Rank resumes based on skill overlap with job description."""

    def __init__(self, case_sensitive: bool = False):
        """Initialize skill matcher.

        Args:
            case_sensitive: Whether skill matching is case-sensitive
        """
        self.case_sensitive = case_sensitive

    def _normalize_skill(self, skill: str) -> str:
        """Normalize skill string.

        Args:
            skill: Skill string

        Returns:
            Normalized skill
        """
        skill = skill.strip()
        if not self.case_sensitive:
            skill = skill.lower()
        return skill

    def _extract_skills(self, skills: List[str]) -> Set[str]:
        """Extract and normalize skills.

        Args:
            skills: List of skill strings

        Returns:
            Set of normalized skills
        """
        return {self._normalize_skill(s) for s in skills}

    def jaccard_similarity(
        self,
        skills1: Set[str],
        skills2: Set[str],
    ) -> float:
        """Compute Jaccard similarity between skill sets.

        Args:
            skills1: First skill set
            skills2: Second skill set

        Returns:
            Jaccard similarity score
        """
        if not skills1 or not skills2:
            return 0.0

        intersection = len(skills1 & skills2)
        union = len(skills1 | skills2)

        return intersection / union if union > 0 else 0.0

    def overlap_coefficient(
        self,
        skills1: Set[str],
        skills2: Set[str],
    ) -> float:
        """Compute overlap coefficient (Szymkiewicz–Simpson coefficient).

        Args:
            skills1: First skill set
            skills2: Second skill set

        Returns:
            Overlap coefficient
        """
        if not skills1 or not skills2:
            return 0.0

        intersection = len(skills1 & skills2)
        min_size = min(len(skills1), len(skills2))

        return intersection / min_size if min_size > 0 else 0.0

    def rank(
        self,
        job_skills: List[str],
        resumes: List[Dict[str, Any]],
        method: str = "jaccard",
        top_k: int = None,
    ) -> List[Tuple[str, float]]:
        """Rank resumes by skill match.

        Args:
            job_skills: Required skills from job description
            resumes: List of resume dictionaries with 'id' and 'skills' keys
            method: Similarity method ('jaccard' or 'overlap')
            top_k: Return only top k results

        Returns:
            List of (resume_id, score) tuples, sorted by score
        """
        jd_skills = self._extract_skills(job_skills)

        rankings = []

        for resume in resumes:
            resume_skills = self._extract_skills(resume.get("skills", []))

            if method == "jaccard":
                score = self.jaccard_similarity(jd_skills, resume_skills)
            elif method == "overlap":
                score = self.overlap_coefficient(jd_skills, resume_skills)
            else:
                raise ValueError(f"Unknown method: {method}")

            rankings.append((resume["id"], score))

        # Sort by score
        rankings.sort(key=lambda x: x[1], reverse=True)

        if top_k is not None:
            rankings = rankings[:top_k]

        return rankings

    def score(
        self,
        resume_skills: List[str],
        job_skills: List[str],
        method: str = "jaccard",
    ) -> float:
        """Score skill match between resume and job.

        Args:
            resume_skills: Skills from resume
            job_skills: Required skills from job
            method: Similarity method

        Returns:
            Similarity score
        """
        resume_set = self._extract_skills(resume_skills)
        job_set = self._extract_skills(job_skills)

        if method == "jaccard":
            return self.jaccard_similarity(job_set, resume_set)
        elif method == "overlap":
            return self.overlap_coefficient(job_set, resume_set)
        else:
            raise ValueError(f"Unknown method: {method}")

    def get_matching_skills(
        self,
        resume_skills: List[str],
        job_skills: List[str],
    ) -> Dict[str, List[str]]:
        """Get skill overlap analysis.

        Args:
            resume_skills: Skills from resume
            job_skills: Required skills from job

        Returns:
            Dictionary with 'matched', 'missing', and 'extra' skills
        """
        resume_set = self._extract_skills(resume_skills)
        job_set = self._extract_skills(job_skills)

        return {
            "matched": list(resume_set & job_set),
            "missing": list(job_set - resume_set),
            "extra": list(resume_set - job_set),
        }
