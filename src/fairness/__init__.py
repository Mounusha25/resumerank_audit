"""Fairness testing and counterfactual analysis.

This module provides tools for testing ranking stability under
controlled perturbations WITHOUT inferring sensitive attributes.
"""

from .counterfactual import CounterfactualTester
from .perturbations import (
    PerturbationGenerator,
    gender_pronoun_swap,
    redact_names,
    swap_university,
    insert_gap,
)
from .fairness_metrics import FairnessMetrics

__all__ = [
    "CounterfactualTester",
    "PerturbationGenerator",
    "gender_pronoun_swap",
    "redact_names",
    "swap_university",
    "insert_gap",
    "FairnessMetrics",
]
