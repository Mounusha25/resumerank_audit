"""Fairness metrics for ranking evaluation."""

from typing import List, Dict, Any
import numpy as np


class FairnessMetrics:
    """Calculate fairness-specific metrics."""

    @staticmethod
    def demographic_parity_difference(
        scores_group_a: List[float],
        scores_group_b: List[float],
        threshold: float = 0.5,
    ) -> float:
        """Calculate demographic parity difference.

        Note: This is for evaluation only when proxy groups are explicitly defined,
        NOT for inferring sensitive attributes.

        Args:
            scores_group_a: Scores for group A
            scores_group_b: Scores for group B
            threshold: Threshold for positive outcome

        Returns:
            Demographic parity difference
        """
        rate_a = np.mean([s >= threshold for s in scores_group_a])
        rate_b = np.mean([s >= threshold for s in scores_group_b])

        return abs(rate_a - rate_b)

    @staticmethod
    def rank_position_variance(
        original_ranks: List[int],
        perturbed_ranks: List[int],
    ) -> float:
        """Calculate variance in rank positions after perturbation.

        Args:
            original_ranks: Original ranking positions
            perturbed_ranks: Perturbed ranking positions

        Returns:
            Variance in rank changes
        """
        rank_changes = [abs(o - p) for o, p in zip(original_ranks, perturbed_ranks)]
        return float(np.var(rank_changes))

    @staticmethod
    def consistency_score(
        rank_changes: List[int],
        max_acceptable_change: int = 5,
    ) -> float:
        """Calculate consistency score.

        Args:
            rank_changes: List of rank position changes
            max_acceptable_change: Maximum acceptable rank change

        Returns:
            Consistency score (0-1, higher is better)
        """
        consistent_count = sum(1 for change in rank_changes if change <= max_acceptable_change)
        return consistent_count / len(rank_changes) if rank_changes else 0.0

    @staticmethod
    def fairness_threshold_rate(
        mean_rank_change: float,
        affected_percentage: float,
        rank_threshold: float = 3.0,
        percentage_threshold: float = 15.0,
    ) -> bool:
        """Check if fairness thresholds are met.

        Args:
            mean_rank_change: Mean rank change from perturbation
            affected_percentage: Percentage of significantly affected resumes
            rank_threshold: Maximum acceptable mean rank change
            percentage_threshold: Maximum acceptable affected percentage

        Returns:
            True if thresholds are met
        """
        return (
            mean_rank_change <= rank_threshold and
            affected_percentage <= percentage_threshold
        )
