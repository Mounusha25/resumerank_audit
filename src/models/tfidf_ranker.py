"""TF-IDF based ranking model."""

from typing import List, Tuple, Dict, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class TFIDFRanker:
    """Rank resumes using TF-IDF cosine similarity."""

    def __init__(
        self,
        max_features: int = 5000,
        ngram_range: Tuple[int, int] = (1, 2),
        min_df: int = 1,
        max_df: float = 0.95,
    ):
        """Initialize TF-IDF ranker.

        Args:
            max_features: Maximum number of features
            ngram_range: N-gram range for vectorization
            min_df: Minimum document frequency
            max_df: Maximum document frequency
        """
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            min_df=min_df,
            max_df=max_df,
            stop_words="english",
        )
        self.resume_vectors = None
        self.resume_ids = None

    def fit(self, resumes: List[Dict[str, Any]]) -> "TFIDFRanker":
        """Fit vectorizer on resume corpus.

        Args:
            resumes: List of resume dictionaries with 'id' and 'text' keys

        Returns:
            self
        """
        self.resume_ids = [r["id"] for r in resumes]
        resume_texts = [r["text"] for r in resumes]

        # Fit and transform resumes
        self.resume_vectors = self.vectorizer.fit_transform(resume_texts)

        return self

    def rank(
        self,
        job_description: str,
        resumes: List[Dict[str, Any]] = None,
        top_k: int = None,
    ) -> List[Tuple[str, float]]:
        """Rank resumes against job description.

        Args:
            job_description: Job description text
            resumes: Optional list of resumes (if not using fitted corpus)
            top_k: Return only top k results

        Returns:
            List of (resume_id, similarity_score) tuples, sorted by score
        """
        if resumes is not None:
            # Transform new resumes
            resume_ids = [r["id"] for r in resumes]
            resume_texts = [r["text"] for r in resumes]
            resume_vectors = self.vectorizer.transform(resume_texts)
        else:
            # Use fitted corpus
            if self.resume_vectors is None:
                raise ValueError("Must call fit() first or provide resumes")
            resume_ids = self.resume_ids
            resume_vectors = self.resume_vectors

        # Transform job description
        jd_vector = self.vectorizer.transform([job_description])

        # Compute similarities
        similarities = cosine_similarity(jd_vector, resume_vectors)[0]

        # Create ranked list
        rankings = list(zip(resume_ids, similarities))
        rankings.sort(key=lambda x: x[1], reverse=True)

        if top_k is not None:
            rankings = rankings[:top_k]

        return rankings

    def score(self, resume: Dict[str, Any], job_description: str) -> float:
        """Score a single resume against job description.

        Args:
            resume: Resume dictionary with 'text' key
            job_description: Job description text

        Returns:
            Similarity score
        """
        resume_vector = self.vectorizer.transform([resume["text"]])
        jd_vector = self.vectorizer.transform([job_description])

        similarity = cosine_similarity(jd_vector, resume_vector)[0, 0]

        return float(similarity)

    def get_feature_names(self) -> List[str]:
        """Get feature names from vectorizer.

        Returns:
            List of feature names
        """
        return self.vectorizer.get_feature_names_out().tolist()

    def get_top_features(
        self,
        resume: Dict[str, Any],
        top_n: int = 10,
    ) -> List[Tuple[str, float]]:
        """Get top TF-IDF features for a resume.

        Args:
            resume: Resume dictionary
            top_n: Number of top features to return

        Returns:
            List of (feature, score) tuples
        """
        resume_vector = self.vectorizer.transform([resume["text"]])
        feature_names = self.get_feature_names()

        # Get non-zero features
        vector_array = resume_vector.toarray()[0]
        top_indices = vector_array.argsort()[-top_n:][::-1]

        top_features = [
            (feature_names[idx], vector_array[idx])
            for idx in top_indices
            if vector_array[idx] > 0
        ]

        return top_features
