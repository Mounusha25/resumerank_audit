"""Tests for fairness testing modules."""

import pytest
from src.fairness.perturbations import (
    gender_pronoun_swap,
    redact_names,
    introduce_typos,
)


def test_gender_pronoun_swap():
    """Test pronoun swapping."""
    text = "He is a software engineer. His skills include Python."

    neutral = gender_pronoun_swap(text, "to_neutral")

    assert "he" not in neutral.lower() or "they" in neutral.lower()
    assert "his" not in neutral.lower() or "their" in neutral.lower()


def test_name_redaction():
    """Test name redaction."""
    text = "John Smith\nSoftware Engineer\nExperience at Google"

    redacted = redact_names(text)

    assert "John Smith" not in redacted
    assert "[NAME]" in redacted


def test_typo_introduction():
    """Test typo introduction."""
    text = "This is a test document with several words"

    typo_text = introduce_typos(text, typo_rate=0.2)

    # Text should be different (likely has typos)
    assert typo_text != text

    # Should have similar length
    assert abs(len(typo_text) - len(text)) < 5


def test_counterfactual_stability():
    """Test that minimal perturbations should yield minimal rank changes."""
    # This is a conceptual test - actual implementation would need a real ranker
    # For now, just test that perturbations don't completely destroy text

    original = "Software Engineer with Python experience"
    perturbed = gender_pronoun_swap(original, "to_neutral")

    # Should still contain key information
    assert "Software Engineer" in perturbed or "software engineer" in perturbed.lower()
    assert "Python" in perturbed
