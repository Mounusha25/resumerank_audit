"""Tests for ranking models."""

import pytest
from src.models.tfidf_ranker import TFIDFRanker
from src.models.bm25_ranker import BM25Ranker
from src.models.skill_matcher import SkillMatcher


@pytest.fixture
def sample_resumes():
    """Sample resume data."""
    return [
        {
            "id": "resume_1",
            "text": "Python developer with machine learning experience",
            "skills": ["Python", "Machine Learning", "TensorFlow"],
        },
        {
            "id": "resume_2",
            "text": "Java developer with backend experience",
            "skills": ["Java", "Spring", "SQL"],
        },
    ]


def test_tfidf_ranker(sample_resumes):
    """Test TF-IDF ranker."""
    ranker = TFIDFRanker()
    ranker.fit(sample_resumes)

    jd = "Looking for a Python developer with machine learning skills"
    rankings = ranker.rank(jd)

    assert len(rankings) == 2
    assert rankings[0][0] == "resume_1"  # Should rank Python resume first


def test_bm25_ranker(sample_resumes):
    """Test BM25 ranker."""
    ranker = BM25Ranker()
    ranker.fit(sample_resumes)

    jd = "Python machine learning engineer"
    rankings = ranker.rank(jd)

    assert len(rankings) == 2
    assert rankings[0][0] == "resume_1"


def test_skill_matcher(sample_resumes):
    """Test skill matching."""
    matcher = SkillMatcher()

    job_skills = ["Python", "Machine Learning"]
    rankings = matcher.rank(job_skills, sample_resumes)

    assert len(rankings) == 2
    assert rankings[0][0] == "resume_1"
    assert rankings[0][1] > rankings[1][1]  # First resume should score higher


def test_skill_overlap():
    """Test skill overlap analysis."""
    matcher = SkillMatcher()

    resume_skills = ["Python", "Java", "SQL"]
    job_skills = ["Python", "Machine Learning", "SQL"]

    overlap = matcher.get_matching_skills(resume_skills, job_skills)

    assert "Python" in overlap["matched"]
    assert "SQL" in overlap["matched"]
    assert "Machine Learning" in overlap["missing"]
    assert "Java" in overlap["extra"]
