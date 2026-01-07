"""Semantic similarity model using sentence transformers.

This module provides pretrained embedding-based ranking WITHOUT fine-tuning,
maintaining focus on evaluation infrastructure rather than model optimization.
"""

from typing import List, Tuple, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path


class SemanticRanker:
    """Rank resumes using semantic similarity with sentence transformers.

    Uses pretrained models WITHOUT fine-tuning to maintain focus on
    evaluation and auditing rather than model optimization.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        device: str = "cpu",
        cache_dir: Optional[str] = None,
    ):
        """Initialize semantic ranker.

        Args:
            model_name: Name of sentence transformer model
            device: Device to use ('cpu' or 'cuda')
            cache_dir: Directory to cache models
        """
        self.model_name = model_name
        self.device = device

        # Load pretrained model (NO FINE-TUNING)
        self.model = SentenceTransformer(
            model_name,
            device=device,
            cache_folder=cache_dir,
        )

        # Cache for embeddings
        self.resume_embeddings = None
        self.resume_ids = None

    def encode(
        self,
        texts: List[str],
        batch_size: int = 32,
        show_progress: bool = False,
    ) -> np.ndarray:
        """Encode texts to embeddings.

        Args:
            texts: List of texts to encode
            batch_size: Batch size for encoding
            show_progress: Show progress bar

        Returns:
            Numpy array of embeddings
        """
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
        )

        return embeddings

    def fit(
        self,
        resumes: List[Dict[str, Any]],
        batch_size: int = 32,
    ) -> "SemanticRanker":
        """Cache resume embeddings.

        Args:
            resumes: List of resume dictionaries with 'id' and 'text' keys
            batch_size: Batch size for encoding

        Returns:
            self
        """
        self.resume_ids = [r["id"] for r in resumes]
        resume_texts = [r["text"] for r in resumes]

        # Encode resumes
        self.resume_embeddings = self.encode(
            resume_texts,
            batch_size=batch_size,
            show_progress=True,
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
            resumes: Optional list of resumes (if not using cached embeddings)
            top_k: Return only top k results

        Returns:
            List of (resume_id, similarity_score) tuples, sorted by score
        """
        if resumes is not None:
            # Encode new resumes
            resume_ids = [r["id"] for r in resumes]
            resume_texts = [r["text"] for r in resumes]
            resume_embeddings = self.encode(resume_texts)
        else:
            # Use cached embeddings
            if self.resume_embeddings is None:
                raise ValueError("Must call fit() first or provide resumes")
            resume_ids = self.resume_ids
            resume_embeddings = self.resume_embeddings

        # Encode job description
        jd_embedding = self.encode([job_description])[0]

        # Compute cosine similarities
        similarities = cosine_similarity(
            jd_embedding.reshape(1, -1),
            resume_embeddings,
        )[0]

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
            Cosine similarity score
        """
        resume_embedding = self.encode([resume["text"]])[0]
        jd_embedding = self.encode([job_description])[0]

        similarity = cosine_similarity(
            resume_embedding.reshape(1, -1),
            jd_embedding.reshape(1, -1),
        )[0, 0]

        return float(similarity)

    def get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for a single text.

        Args:
            text: Input text

        Returns:
            Embedding vector
        """
        return self.encode([text])[0]

    def save_embeddings(self, file_path: str) -> None:
        """Save cached embeddings to disk.

        Args:
            file_path: Path to save embeddings
        """
        if self.resume_embeddings is None:
            raise ValueError("No embeddings to save. Call fit() first.")

        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        np.savez(
            file_path,
            embeddings=self.resume_embeddings,
            resume_ids=self.resume_ids,
            model_name=self.model_name,
        )

    def load_embeddings(self, file_path: str) -> None:
        """Load cached embeddings from disk.

        Args:
            file_path: Path to embeddings file
        """
        data = np.load(file_path, allow_pickle=True)

        self.resume_embeddings = data["embeddings"]
        self.resume_ids = data["resume_ids"].tolist()

        # Verify model compatibility
        saved_model = str(data.get("model_name", ""))
        if saved_model and saved_model != self.model_name:
            print(f"Warning: Embeddings were created with {saved_model}, "
                  f"but using {self.model_name}")

    def batch_score(
        self,
        resume_texts: List[str],
        job_description: str,
    ) -> List[float]:
        """Score multiple resumes efficiently.

        Args:
            resume_texts: List of resume texts
            job_description: Job description text

        Returns:
            List of similarity scores
        """
        resume_embeddings = self.encode(resume_texts)
        jd_embedding = self.encode([job_description])[0]

        similarities = cosine_similarity(
            jd_embedding.reshape(1, -1),
            resume_embeddings,
        )[0]

        return similarities.tolist()
