"""PII (Personally Identifiable Information) redaction.

Removes or masks sensitive personal information from resumes.
"""

import re
from typing import List, Dict, Pattern


class PIIRedactor:
    """Redact personally identifiable information from text."""

    def __init__(self, redact_names: bool = True, redact_contact: bool = True):
        """Initialize PII redactor.

        Args:
            redact_names: Redact person names
            redact_contact: Redact contact information (email, phone, address)
        """
        self.redact_names = redact_names
        self.redact_contact = redact_contact

        # PII patterns
        self.patterns = self._compile_patterns()

    def _compile_patterns(self) -> Dict[str, Pattern]:
        """Compile regex patterns for PII detection."""
        patterns = {}

        # Email
        patterns["email"] = re.compile(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        )

        # Phone numbers (various formats)
        patterns["phone"] = re.compile(
            r"\b(?:\+\d{1,3}[-.]?)?"  # Optional country code
            r"(?:\(\d{3}\)|\d{3})[-.]?"  # Area code
            r"\d{3}[-.]?\d{4}\b"  # Number
        )

        # SSN (XXX-XX-XXXX)
        patterns["ssn"] = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")

        # Street addresses (simplified)
        patterns["address"] = re.compile(
            r"\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)\b",
            re.IGNORECASE,
        )

        # ZIP codes
        patterns["zip"] = re.compile(r"\b\d{5}(?:-\d{4})?\b")

        return patterns

    def redact(self, text: str, placeholder: str = "[REDACTED]") -> str:
        """Redact all PII from text.

        Args:
            text: Input text
            placeholder: Replacement text for redacted information

        Returns:
            Text with PII redacted
        """
        redacted_text = text

        if self.redact_contact:
            # Redact in order of specificity
            redacted_text = self.patterns["ssn"].sub(f"{placeholder}_SSN", redacted_text)
            redacted_text = self.patterns["email"].sub(f"{placeholder}_EMAIL", redacted_text)
            redacted_text = self.patterns["phone"].sub(f"{placeholder}_PHONE", redacted_text)
            redacted_text = self.patterns["address"].sub(f"{placeholder}_ADDRESS", redacted_text)
            redacted_text = self.patterns["zip"].sub(f"{placeholder}_ZIP", redacted_text)

        if self.redact_names:
            redacted_text = self._redact_names(redacted_text, placeholder)

        return redacted_text

    def _redact_names(self, text: str, placeholder: str) -> str:
        """Redact person names from text.

        This is a simple heuristic-based approach.
        For production use, consider using NER models.

        Args:
            text: Input text
            placeholder: Replacement text

        Returns:
            Text with names redacted
        """
        # This is simplified - in production, use spaCy NER
        # For now, just redact capitalized words at start of lines
        # (likely to be names in resume headers)

        lines = text.split("\n")
        redacted_lines = []

        for i, line in enumerate(lines):
            # First few lines often contain name
            if i < 3 and line.strip():
                # Check if line looks like a name (capitalized words, no numbers)
                if re.match(r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+$", line.strip()):
                    redacted_lines.append(f"{placeholder}_NAME")
                    continue

            redacted_lines.append(line)

        return "\n".join(redacted_lines)

    def anonymize_names(self, text: str, name_map: Dict[str, str] = None) -> str:
        """Replace names with pseudonyms.

        Args:
            text: Input text
            name_map: Dictionary mapping real names to pseudonyms

        Returns:
            Text with names anonymized
        """
        if name_map is None:
            name_map = {}

        anonymized_text = text

        for real_name, pseudonym in name_map.items():
            anonymized_text = re.sub(
                rf"\b{re.escape(real_name)}\b",
                pseudonym,
                anonymized_text,
                flags=re.IGNORECASE,
            )

        return anonymized_text

    def detect_pii(self, text: str) -> Dict[str, List[str]]:
        """Detect PII in text without redacting.

        Args:
            text: Input text

        Returns:
            Dictionary of PII type -> list of found instances
        """
        detected = {}

        for pii_type, pattern in self.patterns.items():
            matches = pattern.findall(text)
            if matches:
                detected[pii_type] = matches

        return detected
