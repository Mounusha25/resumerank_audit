"""Tests for evaluation metrics."""

import pytest
import numpy as np
from src.evaluation.metrics import (
    calculate_ndcg,
    calculate_precision_at_k,
    calculate_mrr,
    calculate_spearman,
)


def test_ndcg():
    """Test NDCG calculation."""
    y_true = [3, 2, 1, 0, 0]
    y_pred = [3.0, 2.5, 1.5, 0.5, 0.0]

    ndcg = calculate_ndcg(y_true, y_pred, k=5)

    assert 0 <= ndcg <= 1
    assert ndcg > 0.8  # Should be high for this example


def test_precision_at_k():
    """Test Precision@k calculation."""
    y_true = [1, 1, 0, 1, 0]  # First, second, and fourth are relevant
    y_pred = [5.0, 4.0, 3.0, 2.0, 1.0]  # Perfect ranking

    precision = calculate_precision_at_k(y_true, y_pred, k=3, relevance_threshold=0.5)

    assert precision == 2/3  # 2 relevant in top-3


def test_mrr():
    """Test MRR calculation."""
    y_true = [0, 0, 1, 0, 0]  # Third item is relevant
    y_pred = [5.0, 4.0, 3.0, 2.0, 1.0]  # Third item ranked third

    mrr = calculate_mrr(y_true, y_pred, relevance_threshold=0.5)

    assert mrr == 1/3  # First relevant at position 3


def test_spearman():
    """Test Spearman correlation."""
    ranking1 = [1, 2, 3, 4, 5]
    ranking2 = [1, 2, 3, 4, 5]

    correlation = calculate_spearman(ranking1, ranking2)

    assert correlation == 1.0  # Perfect correlation


def test_spearman_negative():
    """Test Spearman with reversed rankings."""
    ranking1 = [1, 2, 3, 4, 5]
    ranking2 = [5, 4, 3, 2, 1]

    correlation = calculate_spearman(ranking1, ranking2)

    assert correlation == -1.0  # Perfect negative correlation
