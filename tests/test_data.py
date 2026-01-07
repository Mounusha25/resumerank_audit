"""Tests for data processing modules."""

import pytest
from src.data.parser import ResumeParser
from src.data.preprocessor import TextPreprocessor
from src.data.privacy import PIIRedactor


def test_text_preprocessor():
    """Test text preprocessing."""
    preprocessor = TextPreprocessor()

    text = "This   has    multiple     spaces"
    cleaned = preprocessor.clean(text)

    assert "  " not in cleaned
    assert cleaned == "This has multiple spaces"


def test_pii_redactor_email():
    """Test email redaction."""
    redactor = PIIRedactor()

    text = "Contact me at john.doe@example.com for more info"
    redacted = redactor.redact(text)

    assert "john.doe@example.com" not in redacted
    assert "[REDACTED]_EMAIL" in redacted


def test_pii_redactor_phone():
    """Test phone number redaction."""
    redactor = PIIRedactor()

    text = "Call me at 555-123-4567"
    redacted = redactor.redact(text)

    assert "555-123-4567" not in redacted
    assert "[REDACTED]_PHONE" in redacted


def test_pii_detection():
    """Test PII detection."""
    redactor = PIIRedactor()

    text = "Email: test@example.com Phone: 555-1234"
    detected = redactor.detect_pii(text)

    assert "email" in detected
    assert len(detected["email"]) == 1
