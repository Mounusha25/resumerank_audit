"""Text preprocessing and cleaning."""

import re
import string
from typing import List


class TextPreprocessor:
    """Clean and normalize text for processing."""

    def __init__(self, lowercase: bool = False, remove_special_chars: bool = True):
        """Initialize preprocessor.

        Args:
            lowercase: Convert text to lowercase
            remove_special_chars: Remove special characters
        """
        self.lowercase = lowercase
        self.remove_special_chars = remove_special_chars

    def clean(self, text: str) -> str:
        """Clean and normalize text.

        Args:
            text: Input text

        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove special characters if requested
        if self.remove_special_chars:
            # Keep alphanumeric, spaces, and basic punctuation
            text = re.sub(r"[^\w\s.,!?;:()\-]", "", text)

        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace("'", "'").replace("'", "'")

        # Remove multiple periods
        text = re.sub(r"\.{2,}", ".", text)

        # Convert to lowercase if requested
        if self.lowercase:
            text = text.lower()

        return text.strip()

    def normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in text.

        Args:
            text: Input text

        Returns:
            Text with normalized whitespace
        """
        # Replace tabs with spaces
        text = text.replace("\t", " ")

        # Replace multiple spaces with single space
        text = re.sub(r" +", " ", text)

        # Replace multiple newlines with double newline
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    def remove_urls(self, text: str) -> str:
        """Remove URLs from text.

        Args:
            text: Input text

        Returns:
            Text with URLs removed
        """
        url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        text = re.sub(url_pattern, "", text)

        # Also remove www. patterns
        text = re.sub(r"www\.[^\s]+", "", text)

        return text

    def remove_emails(self, text: str) -> str:
        """Remove email addresses from text.

        Args:
            text: Input text

        Returns:
            Text with emails removed
        """
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        return re.sub(email_pattern, "", text)

    def remove_phone_numbers(self, text: str) -> str:
        """Remove phone numbers from text.

        Args:
            text: Input text

        Returns:
            Text with phone numbers removed
        """
        # Match various phone formats
        phone_patterns = [
            r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
            r"\(\d{3}\)\s*\d{3}[-.]?\d{4}",
            r"\+\d{1,3}[-.]?\d{3}[-.]?\d{3}[-.]?\d{4}",
        ]

        for pattern in phone_patterns:
            text = re.sub(pattern, "", text)

        return text

    def tokenize(self, text: str) -> List[str]:
        """Simple tokenization.

        Args:
            text: Input text

        Returns:
            List of tokens
        """
        # Split on whitespace and punctuation
        tokens = re.findall(r"\b\w+\b", text.lower())
        return tokens

    def remove_stopwords(self, tokens: List[str], stopwords: List[str] = None) -> List[str]:
        """Remove common stopwords.

        Args:
            tokens: List of tokens
            stopwords: List of stopwords to remove

        Returns:
            Filtered tokens
        """
        if stopwords is None:
            # Basic English stopwords
            stopwords = {
                "a", "an", "and", "are", "as", "at", "be", "by", "for",
                "from", "has", "he", "in", "is", "it", "its", "of", "on",
                "that", "the", "to", "was", "will", "with", "the", "this",
            }

        return [token for token in tokens if token.lower() not in stopwords]
