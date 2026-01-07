"""
Hybrid Ranking Model - Production-Realistic Architecture

Combines semantic relevance with structured signals, as real systems do.

Philosophy:
- If a signal matters, make it explicit (not accidental)
- Weights are transparent and auditable
- Can measure exact contribution of each component
"""

from typing import List, Tuple, Dict, Any, Optional
import re
import numpy as np


class HybridRanker:
    """
    Hybrid ranker combining semantic similarity with structured signals.
    
    This reflects how real-world ranking systems work:
    - Semantic relevance captures skills, experience, role match
    - Structured signals capture education, continuity, location, etc.
    
    All weights are explicit and auditable.
    """
    
    # University tier mapping (explicit, auditable)
    UNIVERSITY_TIERS = {
        # Tier 1: Elite institutions
        "IIT": 1.0, "MIT": 1.0, "Stanford": 1.0, "Harvard": 1.0,
        "Berkeley": 1.0, "CMU": 1.0, "Caltech": 1.0,
        "Princeton": 1.0, "Yale": 1.0, "Oxford": 1.0, "Cambridge": 1.0,
        
        # Tier 2: Strong institutions  
        "Georgia Tech": 0.85, "UT Austin": 0.85, "UIUC": 0.85,
        "University of Washington": 0.85, "UCLA": 0.85, "USC": 0.85,
        "Cornell": 0.85, "Columbia": 0.85, "Penn": 0.85,
        
        # Tier 3: Standard institutions
        "State University": 0.6, "Regional University": 0.6,
        
        # Unknown/Not listed
        "Unknown": 0.4
    }
    
    def __init__(
        self,
        semantic_ranker,
        weights: Optional[Dict[str, float]] = None,
        enable_structured_signals: bool = True
    ):
        """
        Initialize hybrid ranker.
        
        Args:
            semantic_ranker: Base semantic similarity model (SBERT, etc.)
            weights: Component weights (default: semantic=0.7, education=0.15, 
                                       continuity=0.10, other=0.05)
            enable_structured_signals: If False, acts as pure semantic model
        """
        self.semantic_ranker = semantic_ranker
        self.enable_structured_signals = enable_structured_signals
        
        # Default weights (production-realistic)
        self.weights = weights or {
            "semantic": 0.70,      # Semantic relevance (skills, experience)
            "education": 0.15,     # University prestige signal
            "continuity": 0.10,    # Employment continuity
            "other": 0.05          # Reserved for location, etc.
        }
        
        # Validate weights sum to 1.0
        total = sum(self.weights.values())
        assert abs(total - 1.0) < 0.01, f"Weights must sum to 1.0, got {total}"
    
    def fit(self, resumes: List[Dict[str, Any]]) -> "HybridRanker":
        """Fit underlying semantic model."""
        self.semantic_ranker.fit(resumes)
        return self
    
    def rank(
        self,
        job_description: str,
        resumes: List[Dict[str, Any]],
        return_components: bool = False
    ) -> List[Tuple[str, float]]:
        """
        Rank resumes using hybrid scoring.
        
        Args:
            job_description: Job description text
            resumes: List of resume dictionaries
            return_components: If True, return score breakdown
            
        Returns:
            List of (resume_id, score) tuples, sorted by score descending
            If return_components=True, returns (resume_id, total_score, components_dict)
        """
        # Get semantic scores
        semantic_rankings = self.semantic_ranker.rank(job_description, resumes)
        semantic_scores = {rid: score for rid, score in semantic_rankings}
        
        # If structured signals disabled, return semantic only
        if not self.enable_structured_signals:
            return semantic_rankings
        
        # Calculate hybrid scores
        hybrid_scores = []
        
        for resume in resumes:
            resume_id = resume["id"]
            
            # Component 1: Semantic relevance (normalized 0-1)
            semantic_score = semantic_scores.get(resume_id, 0.0)
            
            # Component 2: Education signal (explicit, auditable)
            education_score = self._calculate_education_score(resume)
            
            # Component 3: Employment continuity
            continuity_score = self._calculate_continuity_score(resume)
            
            # Component 4: Other signals (placeholder)
            other_score = 0.5  # Neutral default
            
            # Weighted combination (explicit, transparent)
            total_score = (
                self.weights["semantic"] * semantic_score +
                self.weights["education"] * education_score +
                self.weights["continuity"] * continuity_score +
                self.weights["other"] * other_score
            )
            
            if return_components:
                components = {
                    "semantic": semantic_score,
                    "education": education_score,
                    "continuity": continuity_score,
                    "other": other_score,
                    "weights": self.weights
                }
                hybrid_scores.append((resume_id, total_score, components))
            else:
                hybrid_scores.append((resume_id, total_score))
        
        # Sort by total score descending
        hybrid_scores.sort(key=lambda x: x[1], reverse=True)
        
        return hybrid_scores
    
    def _calculate_education_score(self, resume: Dict[str, Any]) -> float:
        """
        Calculate education prestige score (explicit, auditable).
        
        This is NOT hiding bias - it's making it measurable.
        Real systems do this explicitly rather than relying on embedding accidents.
        
        Returns:
            Score between 0.0 and 1.0
        """
        text = resume.get("text", "").lower()
        
        # Extract university mentions
        max_tier_score = 0.4  # Default for unknown
        
        for university, tier_score in self.UNIVERSITY_TIERS.items():
            if university.lower() in text:
                max_tier_score = max(max_tier_score, tier_score)
        
        return max_tier_score
    
    def _calculate_continuity_score(self, resume: Dict[str, Any]) -> float:
        """
        Calculate employment continuity score.
        
        Detects:
        - Employment gaps (explicit mentions)
        - Career breaks
        - Continuous employment
        
        Returns:
            Score between 0.0 and 1.0
        """
        text = resume.get("text", "").lower()
        
        # Gap indicators (negative signals)
        gap_patterns = [
            r"employment gap",
            r"career break",
            r"gap of \d+ months?",
            r"unemployed",
            r"seeking opportunities",
            r"freelance period"  # Sometimes indicates gaps
        ]
        
        gap_count = 0
        for pattern in gap_patterns:
            if re.search(pattern, text):
                gap_count += 1
        
        # Continuity indicators (positive signals)
        continuity_patterns = [
            r"currently employed",
            r"present\b",  # "2020 - Present"
            r"continuous",
            r"\d+ years of experience"
        ]
        
        continuity_count = 0
        for pattern in continuity_patterns:
            if re.search(pattern, text):
                continuity_count += 1
        
        # Score: penalize gaps, reward continuity
        if gap_count > 0:
            score = max(0.3, 1.0 - (gap_count * 0.2))
        elif continuity_count > 0:
            score = min(1.0, 0.7 + (continuity_count * 0.1))
        else:
            score = 0.5  # Neutral (no clear signal)
        
        return score
    
    def get_feature_importance(
        self,
        job_description: str,
        resumes: List[Dict[str, Any]],
        top_k: int = 10
    ) -> Dict[str, Any]:
        """
        Analyze feature importance for top-k ranked resumes.
        
        Returns breakdown showing how much each component contributed.
        This is the transparency that makes the system auditable.
        """
        rankings = self.rank(job_description, resumes, return_components=True)
        top_rankings = rankings[:top_k]
        
        # Aggregate component contributions
        total_semantic = 0.0
        total_education = 0.0
        total_continuity = 0.0
        total_other = 0.0
        
        for _, score, components in top_rankings:
            # Weighted contributions
            total_semantic += components["semantic"] * self.weights["semantic"]
            total_education += components["education"] * self.weights["education"]
            total_continuity += components["continuity"] * self.weights["continuity"]
            total_other += components["other"] * self.weights["other"]
        
        total = total_semantic + total_education + total_continuity + total_other
        
        return {
            "component_contributions": {
                "semantic_relevance": total_semantic / total if total > 0 else 0,
                "education_prestige": total_education / total if total > 0 else 0,
                "employment_continuity": total_continuity / total if total > 0 else 0,
                "other_signals": total_other / total if total > 0 else 0
            },
            "configured_weights": self.weights,
            "top_k": top_k,
            "note": "This shows explicit signal contributions - transparency for audit"
        }
    
    def explain_ranking(
        self,
        resume_id: str,
        job_description: str,
        resumes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Explain why a specific resume received its score.
        
        Returns:
            Detailed breakdown of all scoring components
        """
        rankings = self.rank(job_description, resumes, return_components=True)
        
        for rid, total_score, components in rankings:
            if rid == resume_id:
                rank = rankings.index((rid, total_score, components)) + 1
                
                return {
                    "resume_id": resume_id,
                    "rank": rank,
                    "total_score": total_score,
                    "component_scores": {
                        "semantic_relevance": {
                            "raw_score": components["semantic"],
                            "weight": self.weights["semantic"],
                            "contribution": components["semantic"] * self.weights["semantic"]
                        },
                        "education_prestige": {
                            "raw_score": components["education"],
                            "weight": self.weights["education"],
                            "contribution": components["education"] * self.weights["education"]
                        },
                        "employment_continuity": {
                            "raw_score": components["continuity"],
                            "weight": self.weights["continuity"],
                            "contribution": components["continuity"] * self.weights["continuity"]
                        },
                        "other_signals": {
                            "raw_score": components["other"],
                            "weight": self.weights["other"],
                            "contribution": components["other"] * self.weights["other"]
                        }
                    },
                    "interpretation": self._interpret_scores(components)
                }
        
        return {"error": f"Resume {resume_id} not found"}
    
    def _interpret_scores(self, components: Dict[str, float]) -> str:
        """Generate human-readable interpretation of scores."""
        interpretations = []
        
        if components["semantic"] > 0.7:
            interpretations.append("Strong semantic match (skills/experience align well)")
        elif components["semantic"] < 0.3:
            interpretations.append("Weak semantic match (limited skill overlap)")
        
        if components["education"] > 0.8:
            interpretations.append("Elite institution background")
        elif components["education"] < 0.5:
            interpretations.append("Standard or unlisted institution")
        
        if components["continuity"] > 0.7:
            interpretations.append("Strong employment continuity")
        elif components["continuity"] < 0.5:
            interpretations.append("Employment gaps detected")
        
        return "; ".join(interpretations) if interpretations else "Neutral profile"
