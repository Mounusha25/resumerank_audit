"""BM25 ranking model."""

from typing import List, Tuple, Dict, Any
from rank_bm25 import BM25Okapi
import numpy as np


class BM25Ranker:
    """Rank resumes using BM25 algorithm."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """Initialize BM25 ranker.

        Args:
            k1: Term frequency saturation parameter
            b: Length normalization parameter
        """
        self.k1 = k1
        self.b = b
        self.bm25 = None
        self.resume_ids = None
        self.tokenized_resumes = None

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization.

        Args:
            text: Input text

        Returns:
            List of tokens
        """
        return text.lower().split()

    def fit(self, resumes: List[Dict[str, Any]]) -> "BM25Ranker":
        """Fit BM25 on resume corpus.

        Args:
            resumes: List of resume dictionaries with 'id' and 'text' keys

        Returns:
            self
        """
        self.resume_ids = [r["id"] for r in resumes]
        resume_texts = [r["text"] for r in resumes]

        # Tokenize all resumes
        self.tokenized_resumes = [self._tokenize(text) for text in resume_texts]

        # Initialize BM25
        self.bm25 = BM25Okapi(
            self.tokenized_resumes,
            k1=self.k1,
            b=self.b,
        )

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
            List of (resume_id, bm25_score) tuples, sorted by score
        """
        if resumes is not None:
            # Create new BM25 instance for these resumes
            resume_ids = [r["id"] for r in resumes]
            resume_texts = [r["text"] for r in resumes]
            tokenized = [self._tokenize(text) for text in resume_texts]
            bm25 = BM25Okapi(tokenized, k1=self.k1, b=self.b)
        else:
            # Use fitted corpus
            if self.bm25 is None:
                raise ValueError("Must call fit() first or provide resumes")
            resume_ids = self.resume_ids
            bm25 = self.bm25

        # Tokenize query
        query_tokens = self._tokenize(job_description)

        # Get scores
        scores = bm25.get_scores(query_tokens)

        # Create ranked list
        rankings = list(zip(resume_ids, scores))
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
            BM25 score
        """
        query_tokens = self._tokenize(job_description)
        doc_tokens = self._tokenize(resume["text"])

        # Create single-document BM25
        bm25 = BM25Okapi([doc_tokens], k1=self.k1, b=self.b)
        score = bm25.get_scores(query_tokens)[0]

        return float(score)

    def get_top_matching_terms(
        self,
        resume: Dict[str, Any],
        job_description: str,
        top_n: int = 10,
    ) -> List[Tuple[str, float]]:
        """Get top matching terms between resume and job description.

        Args:
            resume: Resume dictionary
            job_description: Job description text
            top_n: Number of top terms to return

        Returns:
            List of (term, contribution) tuples
        """
        query_tokens = self._tokenize(job_description)
        doc_tokens = self._tokenize(resume["text"])

        # Find common terms
        common_terms = set(query_tokens) & set(doc_tokens)

        # Simple frequency-based scoring
        term_scores = []
        for term in common_terms:
            query_freq = query_tokens.count(term)
            doc_freq = doc_tokens.count(term)
            score = query_freq * doc_freq  # Simple heuristic

            term_scores.append((term, score))

        # Sort and return top N
        term_scores.sort(key=lambda x: x[1], reverse=True)
        return term_scores[:top_n]
