#!/usr/bin/env python
"""
Example: Basic usage of the resume ranking system.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.models.semantic_model import SemanticRanker
from src.fairness.counterfactual import CounterfactualTester
from src.explainability.ablation import AblationExplainer


def main():
    """Run basic example."""
    print("Resume Ranking System - Basic Example")
    print("=" * 60)

    # Create sample data
    sample_resumes = [
        {
            "id": "resume_001",
            "text": """
                Software Engineer with 5 years experience in Python and machine learning.
                Skills: Python, TensorFlow, PyTorch, AWS, Docker
                Education: BS Computer Science from Stanford University
                
                Experience:
                - Built ML models for recommendation systems
                - Deployed models to production using Docker and AWS
                """,
            "skills": ["Python", "TensorFlow", "PyTorch", "AWS", "Docker"],
        },
        {
            "id": "resume_002",
            "text": """
                Data Scientist with 3 years experience in analytics and visualization.
                Skills: Python, SQL, Tableau, pandas, numpy
                Education: MS Data Science from State University
                
                Experience:
                - Analyzed customer data to drive business decisions
                - Created dashboards for stakeholder reporting
                """,
            "skills": ["Python", "SQL", "Tableau", "pandas", "numpy"],
        },
    ]

    sample_jd = """
    Senior Machine Learning Engineer

    We are seeking an experienced ML engineer to join our team.
    
    Required Skills:
    - 5+ years Python experience
    - Deep learning frameworks (TensorFlow, PyTorch)
    - Cloud platforms (AWS, Azure)
    - MLOps and deployment experience

    Responsibilities:
    - Design and implement ML models
    - Deploy models to production
    - Collaborate with data scientists and engineers
    """

    # Initialize semantic ranker
    print("\n1. Initializing Semantic Ranker...")
    ranker = SemanticRanker(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Rank resumes
    print("\n2. Ranking Resumes...")
    rankings = ranker.rank(sample_jd, sample_resumes)

    print("\nRanking Results:")
    for rank, (resume_id, score) in enumerate(rankings, 1):
        print(f"  {rank}. {resume_id}: {score:.4f}")

    # Test fairness
    print("\n3. Running Fairness Test (Gender Proxy)...")
    tester = CounterfactualTester(ranker)

    fairness_result = tester.test_gender_proxy(sample_resumes, sample_jd)

    print(f"\nFairness Test Results:")
    print(f"  Mean Rank Change: {fairness_result['mean_rank_change']:.2f}")
    print(f"  Max Rank Change: {fairness_result['max_rank_change']}")
    print(f"  Affected: {fairness_result['affected_percentage']:.1f}%")

    # Explain ranking
    print("\n4. Explaining Ranking for Top Resume...")
    explainer = AblationExplainer(ranker)

    top_resume = next(r for r in sample_resumes if r["id"] == rankings[0][0])
    explanation = explainer.explain(top_resume, sample_jd)

    print("\nSection Contributions:")
    for section, contribution in explanation.items():
        print(f"  {section}: {contribution:.4f}")

    print("\n" + "=" * 60)
    print("✓ Example complete!")
    print("\nNext steps:")
    print("  1. Add your own resume PDFs to data/raw/resumes/")
    print("  2. Add job descriptions to data/raw/job_descriptions/")
    print("  3. Run: python scripts/prepare_data.py")
    print("  4. Run: python scripts/run_evaluation.py")


if __name__ == "__main__":
    main()
