"""Text perturbation functions for counterfactual testing.

⚠️ IMPORTANT: These perturbations test proxy attributes, NOT actual sensitive attributes.
We never infer or predict race, gender, age, etc.
"""

import re
from typing import Dict, List, Tuple


def gender_pronoun_swap(text: str, direction: str = "to_neutral") -> str:
    """Swap gendered pronouns.

    Args:
        text: Input text
        direction: 'to_neutral', 'to_male', or 'to_female'

    Returns:
        Text with swapped pronouns
    """
    if direction == "to_neutral":
        # Replace gendered pronouns with they/them
        replacements = {
            r'\bhe\b': 'they',
            r'\bhim\b': 'them',
            r'\bhis\b': 'their',
            r'\bhimself\b': 'themselves',
            r'\bshe\b': 'they',
            r'\bher\b': 'their',
            r'\bhers\b': 'theirs',
            r'\bherself\b': 'themselves',
        }
    elif direction == "to_male":
        replacements = {
            r'\bthey\b': 'he',
            r'\bthem\b': 'him',
            r'\btheir\b': 'his',
            r'\btheirs\b': 'his',
            r'\bthemselves\b': 'himself',
            r'\bshe\b': 'he',
            r'\bher\b': 'his',
            r'\bhers\b': 'his',
            r'\bherself\b': 'himself',
        }
    elif direction == "to_female":
        replacements = {
            r'\bthey\b': 'she',
            r'\bthem\b': 'her',
            r'\btheir\b': 'her',
            r'\btheirs\b': 'hers',
            r'\bthemselves\b': 'herself',
            r'\bhe\b': 'she',
            r'\bhim\b': 'her',
            r'\bhis\b': 'her',
            r'\bhimself\b': 'herself',
        }
    else:
        raise ValueError(f"Unknown direction: {direction}")

    result = text
    for pattern, replacement in replacements.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    return result


def remove_gendered_organizations(text: str) -> str:
    """Remove mentions of gender-coded organizations.

    Args:
        text: Input text

    Returns:
        Text with gendered organization mentions removed
    """
    # Common gendered organization patterns
    gendered_orgs = [
        r'\bWomen in Tech\b',
        r'\bWomen in Engineering\b',
        r'\bGirls Who Code\b',
        r'\bSociety of Women Engineers\b',
        r'\bFraternity\b',
        r'\bSorority\b',
    ]

    result = text
    for pattern in gendered_orgs:
        result = re.sub(pattern, '[ORGANIZATION]', result, flags=re.IGNORECASE)

    return result


def redact_names(text: str, placeholder: str = "[NAME]") -> str:
    """Redact potential name mentions.

    Args:
        text: Input text
        placeholder: Replacement text

    Returns:
        Text with names redacted
    """
    lines = text.split('\n')
    redacted_lines = []

    for i, line in enumerate(lines):
        # First few lines often contain names
        if i < 3 and line.strip():
            # Simple heuristic: capitalized words at start
            if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+$', line.strip()):
                redacted_lines.append(placeholder)
                continue

        redacted_lines.append(line)

    return '\n'.join(redacted_lines)


def swap_university(
    text: str,
    university_tiers: Dict[str, List[str]],
    from_tier: str = "tier1",
    to_tier: str = "tier2",
) -> str:
    """Swap university mentions to test prestige bias.

    Args:
        text: Input text
        university_tiers: Dictionary of tier_name -> list of universities
        from_tier: Source tier
        to_tier: Target tier

    Returns:
        Text with universities swapped
    """
    if from_tier not in university_tiers or to_tier not in university_tiers:
        return text

    from_unis = university_tiers[from_tier]
    to_unis = university_tiers[to_tier]

    result = text

    # Replace universities from from_tier with equivalent from to_tier
    for i, uni in enumerate(from_unis):
        # Use corresponding university from to_tier (cycling if needed)
        replacement = to_unis[i % len(to_unis)]
        result = re.sub(
            rf'\b{re.escape(uni)}\b',
            replacement,
            result,
            flags=re.IGNORECASE
        )

    return result


def insert_gap(
    text: str,
    gap_months: int = 6,
    position: str = "before_last_job",
) -> str:
    """Insert an employment gap in work history.

    Args:
        text: Input text
        gap_months: Length of gap in months
        position: Where to insert gap

    Returns:
        Text with inserted gap (marked)
    """
    # This is a simplified version - in production, would need better parsing
    # For now, just add a marker comment

    gap_text = f"\n[EMPLOYMENT GAP: {gap_months} months]\n"

    if position == "before_last_job":
        # Try to find "Experience" section and insert near the end
        experience_match = re.search(
            r'(experience|employment|work history)',
            text,
            re.IGNORECASE
        )

        if experience_match:
            insert_pos = experience_match.end()
            result = text[:insert_pos] + gap_text + text[insert_pos:]
            return result

    # Fallback: insert in middle of text
    mid_point = len(text) // 2
    return text[:mid_point] + gap_text + text[mid_point:]


def introduce_typos(text: str, typo_rate: float = 0.02) -> str:
    """Introduce random typos for robustness testing.

    Args:
        text: Input text
        typo_rate: Proportion of words to modify

    Returns:
        Text with typos
    """
    import random
    random.seed(42)  # For reproducibility

    words = text.split()
    num_typos = int(len(words) * typo_rate)

    # Select random words to modify
    typo_indices = random.sample(range(len(words)), min(num_typos, len(words)))

    for idx in typo_indices:
        word = words[idx]
        if len(word) > 3:
            # Simple typo: swap two adjacent characters
            pos = random.randint(1, len(word) - 2)
            word_list = list(word)
            word_list[pos], word_list[pos + 1] = word_list[pos + 1], word_list[pos]
            words[idx] = ''.join(word_list)

    return ' '.join(words)


def replace_synonyms(text: str, replacements: Dict[str, List[str]]) -> str:
    """Replace words with synonyms for stability testing.

    Args:
        text: Input text
        replacements: Dictionary of word -> list of synonyms

    Returns:
        Text with synonyms
    """
    result = text

    for word, synonyms in replacements.items():
        if synonyms:
            # Replace with first synonym
            result = re.sub(
                rf'\b{re.escape(word)}\b',
                synonyms[0],
                result,
                flags=re.IGNORECASE
            )

    return result


def remove_formatting(text: str) -> str:
    """Remove formatting (bullets, extra whitespace) for robustness testing.

    Args:
        text: Input text

    Returns:
        Text with formatting removed
    """
    # Remove bullet points
    result = re.sub(r'[•\-\*]\s+', '', text)

    # Remove extra whitespace
    result = re.sub(r'\s+', ' ', result)

    # Remove multiple newlines
    result = re.sub(r'\n+', '\n', result)

    return result.strip()


class PerturbationGenerator:
    """Generate counterfactual perturbations of resumes."""

    def __init__(self, config: Dict = None):
        """Initialize perturbation generator.

        Args:
            config: Configuration dictionary with perturbation settings
        """
        self.config = config or {}

    def apply_perturbation(
        self,
        text: str,
        perturbation_type: str,
        **kwargs
    ) -> str:
        """Apply a perturbation to text.

        Args:
            text: Input text
            perturbation_type: Type of perturbation
            **kwargs: Additional arguments for perturbation

        Returns:
            Perturbed text
        """
        if perturbation_type == "gender_pronoun":
            direction = kwargs.get("direction", "to_neutral")
            return gender_pronoun_swap(text, direction)

        elif perturbation_type == "name_redaction":
            return redact_names(text)

        elif perturbation_type == "university_swap":
            university_tiers = kwargs.get("university_tiers", {})
            return swap_university(text, university_tiers)

        elif perturbation_type == "gap_insertion":
            gap_months = kwargs.get("gap_months", 6)
            return insert_gap(text, gap_months)

        elif perturbation_type == "typos":
            typo_rate = kwargs.get("typo_rate", 0.02)
            return introduce_typos(text, typo_rate)

        elif perturbation_type == "synonym_replacement":
            replacements = kwargs.get("replacements", {})
            return replace_synonyms(text, replacements)

        elif perturbation_type == "formatting_removal":
            return remove_formatting(text)

        else:
            raise ValueError(f"Unknown perturbation type: {perturbation_type}")

    def generate_counterfactuals(
        self,
        resume: Dict,
        perturbation_types: List[str],
    ) -> Dict[str, Dict]:
        """Generate multiple counterfactual versions of a resume.

        Args:
            resume: Original resume dictionary
            perturbation_types: List of perturbation types to apply

        Returns:
            Dictionary of perturbation_type -> perturbed resume
        """
        counterfactuals = {}

        for pert_type in perturbation_types:
            perturbed_text = self.apply_perturbation(
                resume["text"],
                pert_type,
                **self.config.get(pert_type, {})
            )

            counterfactuals[pert_type] = {
                **resume,
                "text": perturbed_text,
                "perturbation": pert_type,
                "original_id": resume["id"],
            }

        return counterfactuals
