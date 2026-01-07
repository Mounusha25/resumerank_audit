"""Ranking evaluation metrics.

Implements:
- NDCG@k (Normalized Discounted Cumulative Gain)
- Precision@k
- MRR (Mean Reciprocal Rank)
- Spearman correlation
"""

from typing import List, Dict, Any, Tuple
import numpy as np
from scipy.stats import spearmanr
from sklearn.metrics import ndcg_score


def calculate_ndcg(
    y_true: List[float],
    y_pred: List[float],
    k: int = None,
) -> float:
    """Calculate NDCG@k.

    Args:
        y_true: True relevance scores
        y_pred: Predicted scores
        k: Cutoff rank

    Returns:
        NDCG score
    """
    if k is not None:
        y_true = y_true[:k]
        y_pred = y_pred[:k]

    # Handle case with no relevant items
    if not any(y_true):
        return 0.0

    # scikit-learn expects 2D arrays
    y_true_array = np.array([y_true])
    y_pred_array = np.array([y_pred])

    try:
        score = ndcg_score(y_true_array, y_pred_array)
    except ValueError:
        # Handle edge cases
        return 0.0

    return float(score)


def calculate_precision_at_k(
    y_true: List[float],
    y_pred: List[float],
    k: int,
    relevance_threshold: float = 0.5,
) -> float:
    """Calculate Precision@k.

    Args:
        y_true: True relevance scores
        y_pred: Predicted scores
        k: Cutoff rank
        relevance_threshold: Threshold for considering item relevant

    Returns:
        Precision@k score
    """
    # Get top-k predictions
    top_k_indices = np.argsort(y_pred)[-k:][::-1]

    # Count relevant items in top-k
    relevant_count = sum(1 for idx in top_k_indices if y_true[idx] >= relevance_threshold)

    return relevant_count / k


def calculate_mrr(
    y_true: List[float],
    y_pred: List[float],
    relevance_threshold: float = 0.5,
) -> float:
    """Calculate Mean Reciprocal Rank.

    Args:
        y_true: True relevance scores
        y_pred: Predicted scores
        relevance_threshold: Threshold for considering item relevant

    Returns:
        MRR score
    """
    # Get ranking by predicted scores
    ranked_indices = np.argsort(y_pred)[::-1]

    # Find first relevant item
    for rank, idx in enumerate(ranked_indices, 1):
        if y_true[idx] >= relevance_threshold:
            return 1.0 / rank

    return 0.0


def calculate_spearman(
    ranking1: List[float],
    ranking2: List[float],
) -> float:
    """Calculate Spearman rank correlation.

    Args:
        ranking1: First ranking
        ranking2: Second ranking

    Returns:
        Spearman correlation coefficient
    """
    if len(ranking1) != len(ranking2):
        raise ValueError("Rankings must have same length")

    correlation, _ = spearmanr(ranking1, ranking2)

    return float(correlation)


class RankingMetrics:
    """Compute comprehensive ranking metrics."""

    def __init__(self, k_values: List[int] = [5, 10]):
        """Initialize metrics calculator.

        Args:
            k_values: List of k values for @k metrics
        """
        self.k_values = k_values

    def compute_all(
        self,
        y_true: List[float],
        y_pred: List[float],
        relevance_threshold: float = 0.5,
    ) -> Dict[str, float]:
        """Compute all metrics.

        Args:
            y_true: True relevance scores
            y_pred: Predicted scores
            relevance_threshold: Threshold for relevance

        Returns:
            Dictionary of metric_name -> score
        """
        metrics = {}

        # NDCG@k for each k
        for k in self.k_values:
            ndcg = calculate_ndcg(y_true, y_pred, k=k)
            metrics[f"ndcg@{k}"] = ndcg

        # Precision@k for each k
        for k in self.k_values:
            precision = calculate_precision_at_k(
                y_true,
                y_pred,
                k=k,
                relevance_threshold=relevance_threshold,
            )
            metrics[f"precision@{k}"] = precision

        # MRR
        mrr = calculate_mrr(y_true, y_pred, relevance_threshold=relevance_threshold)
        metrics["mrr"] = mrr

        return metrics

    def compare_rankings(
        self,
        ranking1: List[Tuple[str, float]],
        ranking2: List[Tuple[str, float]],
    ) -> Dict[str, Any]:
        """Compare two rankings.

        Args:
            ranking1: First ranking (id, score) tuples
            ranking2: Second ranking (id, score) tuples

        Returns:
            Comparison metrics
        """
        # Extract scores
        scores1 = [score for _, score in ranking1]
        scores2 = [score for _, score in ranking2]

        # Spearman correlation
        spearman = calculate_spearman(scores1, scores2)

        # Rank agreement
        ids1 = [id for id, _ in ranking1]
        ids2 = [id for id, _ in ranking2]

        # Top-k overlap
        overlaps = {}
        for k in self.k_values:
            top_k1 = set(ids1[:k])
            top_k2 = set(ids2[:k])
            overlap = len(top_k1 & top_k2) / k
            overlaps[f"top{k}_overlap"] = overlap

        return {
            "spearman_correlation": spearman,
            **overlaps,
        }
